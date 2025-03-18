from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement
from genaialogy.tools.llm import OpenAIClient
from genaialogy.tools.gedcom import FamilyTree, format_name

class Biographer:
    """
    Generates a simple textual biography for a person from a GEDCOM file.
    """

    def __init__(self, gedcom_parser_or_file_path):
        self.llm = OpenAIClient(
            system_prompt="You are a biographer."
            "You need to generate a biography based on the information provided.\n"
            "Do NOT make up any information. Only use the information provided.\n"
            "Do NOT embellish the facts. Be concise and to the point.\n"
            "Do NOT add extra information or verbiage.\n"
            # "Do NOT assume that the birth or death place was where the person lived.\n"
            "The biography should be a single paragraph.\n"
            )
        if isinstance(gedcom_parser_or_file_path, str):
            self.gedcom_parser = Parser()
            self.gedcom_parser.parse_file(gedcom_parser_or_file_path)
        elif isinstance(gedcom_parser_or_file_path, Parser):
            self.gedcom_parser = gedcom_parser_or_file_path
        else:
            raise ValueError("Invalid input type. Must be a GEDCOM file path or a GEDCOM parser.")
        self.tree = FamilyTree(self.gedcom_parser)

    def generate_biography(self, person_name, dry_run=False):
        """
        Generate a biography for a person.
        """
        individual = self.tree.find_individual_by_name(person_name)

        if individual is None:
            raise ValueError(f"Individual with name {person_name} not found in GEDCOM file.")

        individual_info = self.tree.dump_individual_info(individual)
        individual_info_str = "\n".join([f"{k}: {v}" for k, v in individual_info.items()])

        print("Individual info:\n", individual_info_str)
        if dry_run:
            return "Not generating biography for dry run."
        response = self.llm.prompt(
            f"Generate a short biography for the following individual:\n{individual_info_str}"
        )
        return response
