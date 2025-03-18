"""Tools for working with GEDCOM files."""

from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement

def format_name(name_tuple):
    """Convert a tuple name into a properly formatted string."""
    return " ".join(name_tuple) if isinstance(name_tuple, tuple) else name_tuple

class FamilyTree:
    """
    A class for representing a family tree from a GEDCOM file.
    """
    def __init__(self, parser: Parser):
        self.parser = parser
        self.root_notes = {}
        self.cache_notes()

    def cache_notes(self):
        """
        Cache the notes from the GEDCOM file.
        """
        for element in self.parser.get_root_child_elements():
            if element.get_tag() == 'NOTE':
                pointer = element.get_pointer()
                value = element.get_value()
                if pointer:
                    self.root_notes[pointer] = element

    def find_individual_by_name(self, name):
        """
        Retrieve an IndividualElement object from the GEDCOM file by name.
        """
        for element in self.parser.get_root_child_elements():
            if isinstance(element, IndividualElement):
                element_name = format_name(element.get_name())
                if element_name == name:
                    return element
        return None

    def find_children(self, individual: IndividualElement) -> list:
        """
        Get a list of children for a given person from a GEDCOM file.
        """

        # Find the individual by name
        individual = self.find_individual_by_name(format_name(individual.get_name()))
        if not individual:
            raise ValueError(f"Person '{person_name}' not found in GEDCOM file")

        # Get all families where this person is a parent
        families = self.parser.get_families(individual, "FAMS")

        # Get all children from these families
        children = []
        for family in families:
            family_children = self.parser.get_family_members(family, "CHIL")
            for child in family_children:
                child_name = " ".join(child.get_name()) if isinstance(child.get_name(), tuple) else child.get_name()
                children.append(child_name)

        return children

    def find_parents(self, individual: IndividualElement) -> dict:
        """
        Get the parents of a given person from a GEDCOM file.
        """
        person_name = format_name(individual.get_name())

        # Find the individual by name
        individual = self.find_individual_by_name(person_name)
        if not individual:
            raise ValueError(f"Person '{person_name}' not found in GEDCOM file")

        # Get the family where this person is a child
        families = self.parser.get_families(individual, "FAMC")

        if not families:
            return None  # No parents found

        # Get the parents from the first family (assuming one set of parents)
        family = families[0]
        father = None
        mother = None

        # Get father (HUSB)
        husbands = self.parser.get_family_members(family, "HUSB")
        if husbands:
            father = " ".join(husbands[0].get_name()) if isinstance(husbands[0].get_name(), tuple) else husbands[0].get_name()

        # Get mother (WIFE)
        wives = self.parser.get_family_members(family, "WIFE")
        if wives:
            mother = " ".join(wives[0].get_name()) if isinstance(wives[0].get_name(), tuple) else wives[0].get_name()

        return {
            'father': father,
            'mother': mother
        }

    def find_siblings(self, individual: IndividualElement) -> list:
        """
        Get a list of siblings for a given person from a GEDCOM file.
        """
        person_name = format_name(individual.get_name())

        individual = self.find_individual_by_name(person_name)
        if not individual:
            raise ValueError(f"Person '{person_name}' not found in GEDCOM file")

        families = self.parser.get_families(individual, "FAMC")

        if not families:
            return None  # No siblings found

        family = families[0]

        siblings = []
        for family in families:
            family_members = self.parser.get_family_members(family, "CHIL")
            for member in family_members:
                sibling_name = " ".join(member.get_name()) if isinstance(member.get_name(), tuple) else member.get_name()
                siblings.append(sibling_name)

        return siblings

    def find_spouses(self, individual: IndividualElement) -> list:
        """
        Get all spouses (wives or husbands) of a given person from a GEDCOM file.
        """
        person_name = format_name(individual.get_name())

        # Get all families where this person is a spouse (FAMS)
        families = self.parser.get_families(individual, "FAMS")
        spouses = []

        for family in families:
            # Determine if the individual is husband or wife
            is_husband = any(
                husb.get_pointer() == individual.get_pointer()
                for husb in self.parser.get_family_members(family, "HUSB")
            )

            # Get spouse based on individual's role
            spouse_tag = "WIFE" if is_husband else "HUSB"
            spouse_members = self.parser.get_family_members(family, spouse_tag)

            if spouse_members:
                for spouse in spouse_members:
                    # Get spouse name
                    spouse_name = format_name(spouse.get_name())

                    # Initialize marriage information
                    marriage_info = {
                        'spouse': spouse_name,
                        'marriage date': None,
                        'marriage place': None,
                        'divorce date': None
                    }

                    # Look for marriage and divorce events in family
                    for family_element in family.get_child_elements():
                        if family_element.get_tag() == 'MARR':
                            for marr_element in family_element.get_child_elements():
                                if marr_element.get_tag() == 'DATE':
                                    marriage_info['marriage date'] = marr_element.get_value()
                                elif marr_element.get_tag() == 'PLAC':
                                    marriage_info['marriage place'] = marr_element.get_value()
                        elif family_element.get_tag() == 'DIV':
                            for div_element in family_element.get_child_elements():
                                if div_element.get_tag() == 'DATE':
                                    marriage_info['divorce date'] = div_element.get_value()

                    spouses.append(marriage_info)

        return spouses

    def dump_individual_info(self, individual):
        """
        Get the information for an individual.
        """
        info = {}
        birth_data = individual.get_birth_data()
        info["name"] = format_name(individual.get_name())
        info["gender"] = individual.get_gender()
        info["birth date"] = birth_data[0]
        info["birth place"] = birth_data[1]
        if individual.is_deceased():
            burial_data = individual.get_death_data()
            info["death date"] = burial_data[0]
            info["death place"] = burial_data[1]
        info["occupation"] = individual.get_occupation()  # TODO: Missing from GEDCOM file - no field in FTM?

        children = self.find_children(individual)
        if children:
            info["children"] = ", ".join(children)

        parents = self.find_parents(individual)
        if parents:
            info["father"] = parents["father"]
            info["mother"] = parents["mother"]

        notes = self.find_notes(individual)
        if notes:
            info["notes"] = notes

        siblings = self.find_siblings(individual)
        if siblings:
            info["siblings"] = ", ".join(siblings)

        spouses = self.find_spouses(individual)
        if spouses:
            info["spouses"] = ", ".join([spouse["spouse"] for spouse in spouses])

        # TODO: Add information about the spouse here (birth place, parents, etc.)

        return info

    def find_notes(self, individual: IndividualElement) -> None:
        """
        Print all notes associated with an individual.

        Args:
            parser (Parser): GEDCOM parser instance
            person_name (str): Full name of the person
        """
        note_lines = []
        for element in individual.get_child_elements():
            if element.get_tag() == 'NOTE':
                note_ref = element.get_value()
                if note_ref in self.root_notes:
                    note_element = self.root_notes[note_ref]
                    for child in note_element.get_child_elements():
                        note_lines.append(child.get_value().strip())
        if note_lines:
            return " ".join(note_lines)
        else:
            return None

    def find_path_recursive(
        self,
        current_person,
        target_person,
        path=None,
        visited=None,
        depth=0,
        debug=False,
    ):
        """
        Recursively find a path from an ancestor to a descendant in the family tree.

        :param gedcom_parser: Parsed GEDCOM data.
        :param current_person: The current individual being examined.
        :param target_person: The target descendant to find.
        :param path: The list of individuals forming the path from ancestor to descendant.
        :param visited: A set of visited individuals to prevent infinite loops.
        :param depth: The recursion depth for debugging.
        :return: The path as a list of IndividualElements if found, otherwise None.
        """
        if path is None:
            path = []
        if visited is None:
            visited = set()

        indent = "  " * depth  # Indentation for better readability in debug prints
        name = format_name(current_person.get_name())

        # Debug: Show who we're checking
        if debug:
            print(f"{indent}🔍 Exploring: {name} (Depth {depth})")

        # Prevent infinite recursion by checking if we've visited this person
        if current_person.get_pointer() in visited:
            if debug:
                print(
                    f"{indent}⚠ Already visited {name}, skipping to prevent infinite loop."
                )
            return None

        # Mark this person as visited
        visited.add(current_person.get_pointer())

        path.append(current_person)

        # If we reached the target person, return the path
        if current_person.get_pointer() == target_person.get_pointer():
            if debug:
                print(f"{indent}✔ Found target: {name} → Returning path")
            return path

        # Get families where the current person is a parent (FAMS)
        families = self.parser.get_families(current_person, "FAMS")
        if debug:
            print(f"{indent}→ {len(families)} family record(s) found.")

        # Search through children
        for family in families:
            children = self.parser.get_family_members(family, "CHIL")
            if debug:
                print(f"{indent}  → {len(children)} child(ren) found in this family.")

            for child in children:
                child_name = format_name(child.get_name())
                if debug:
                    print(f"{indent}  ↳ Checking child: {child_name}")

                result = self.find_path_recursive(
                    child, target_person, path[:], visited, depth + 1
                )  # Pass a copy of the path
                if result:
                    if debug:
                        print(
                            f"{indent}✅ Path found through {child_name} → Returning path"
                        )
                    return result  # Return early if the path is found

        if debug:
            print(f"{indent}❌ No path found from {name} → Backtracking")
        return None  # No path found

    def find_path(self, ancestor_name, descendant_name):
        """
        Find and print the path from an ancestor to a descendant in a GEDCOM file.

        :param gedcom_parser: Parsed GEDCOM data.
        :param ancestor_name: The name of the ancestor.
        :param descendant_name: The name of the descendant.
        :return: None (prints the path if found).
        """
        # Retrieve IndividualElement objects for ancestor and descendant
        ancestor = self.find_individual_by_name(ancestor_name)
        descendant = self.find_individual_by_name(descendant_name)

        # Ensure both individuals were found
        if not ancestor or not descendant:
            raise Exception("❌ Error: One or both individuals not found in the GEDCOM file.")

        # Find path
        path = self.find_path_recursive(ancestor, descendant)

        # Print results
        if path:
            formatted_path = [format_name(person.get_name()) for person in path]
            print("\n✅ Path from ancestor to descendant:")
            for name in formatted_path:
                print(f"→ {name}")
        else:
            raise Exception("❌ No path found between the given individuals.")

        return formatted_path
