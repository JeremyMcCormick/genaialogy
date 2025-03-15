"""Tools for working with GEDCOM files."""

from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement


class PathFinder:

    def __init__(self, gedcom_file, ancestor_name, descendant_name):
        self.parser = Parser()
        self.parser.parse_file(gedcom_file)
        self.ancestor_name = ancestor_name
        self.descendant_name = descendant_name

    @classmethod
    def format_name(cls, name_tuple):
        """Convert a tuple name into a properly formatted string."""
        return " ".join(name_tuple) if isinstance(name_tuple, tuple) else name_tuple

    def get_individual_by_name(self, name):
        """
        Retrieve an IndividualElement object from the GEDCOM file by name.

        :param gedcom_parser: Parsed GEDCOM data.
        :param name: Full name of the individual to find.
        :return: The IndividualElement object or None if not found.
        """
        for element in self.parser.get_root_child_elements():
            if isinstance(element, IndividualElement):
                element_name = self.format_name(element.get_name())
                if element_name == name:
                    return element
        return None

    def find_path(
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
        name = self.format_name(current_person.get_name())

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
                child_name = self.format_name(child.get_name())
                if debug:
                    print(f"{indent}  ↳ Checking child: {child_name}")

                result = self.find_path(
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

    def run(self):
        """
        Find and print the path from an ancestor to a descendant in a GEDCOM file.

        :param gedcom_parser: Parsed GEDCOM data.
        :param ancestor_name: The name of the ancestor.
        :param descendant_name: The name of the descendant.
        :return: None (prints the path if found).
        """
        # Retrieve IndividualElement objects for ancestor and descendant
        ancestor = self.get_individual_by_name(self.ancestor_name)
        descendant = self.get_individual_by_name(self.descendant_name)

        # Ensure both individuals were found
        if not ancestor or not descendant:
            print("❌ Error: One or both individuals not found in the GEDCOM file.")
            return

        # Find path
        self.path = self.find_path(ancestor, descendant)

        # Print results
        if self.path:
            print("\n✅ Path from ancestor to descendant:")
            for person in self.path:
                print(f"→ {self.format_name(person.get_name())}")
        else:
            print("❌ No path found between the given individuals.")
