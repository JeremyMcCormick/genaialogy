from crewai import Agent, Task, Crew
from genaialogy.tools.gedcom import PathFinder  # Use your existing PathFinder implementation

class LineageCrew:
    def __init__(self, gedcom_file: str):
        self.gedcom_file = gedcom_file  # Store the GEDCOM file path

        # Path Finder Agent (Finds the lineage path)
        self.path_finder_agent = Agent(
            role="Path Finder",
            goal="Find a lineage path between two individuals.",
            backstory="You analyze GEDCOM files to determine ancestral paths using PathFinder.",
            verbose=True
        )

        # Biographer Agent (Prints the lineage path)
        self.biographer_agent = Agent(
            role="Biographer",
            goal="Print the lineage path.",
            backstory="You receive a lineage path and print it.",
            verbose=True
        )

        # Task for Path Finder agent
        self.find_path_task = Task(
            description=(
                "Use PathFinder to determine the lineage path between {ancestor} and {descendant}. "
                "Return the path as a list."
            ),
            expected_output="A list of names representing the lineage path.",
            agent=self.path_finder_agent,
            function=self.find_path  # ✅ PathFinder is now executed inside the agent
        )

        # Task for Biographer agent
        self.print_path_task = Task(
            description=(
                "Receive a lineage path and print it in a clear format."
            ),
            expected_output="A formatted printout of the lineage path.",
            agent=self.biographer_agent,
            function=self.print_path  # ✅ Receives path as input from the first task
        )

        # Create the CrewAI workflow
        self.crew = Crew(
            agents=[self.path_finder_agent, self.biographer_agent],
            tasks=[self.find_path_task, self.print_path_task],
            verbose=True
        )

    def find_path(self, ancestor: str, descendant: str) -> list:
        """Agent-executed function: Calls PathFinder to compute the lineage path."""
        path_finder = PathFinder(self.gedcom_file)
        path = path_finder.find_path(ancestor, descendant)  # ✅ This is now executed as part of the CrewAI task
        print(f"[Path Finder] Found lineage path: {path}")
        return path  # ✅ Returns path to pass to the Biographer agent

    def print_path(self, lineage_path: list):
        """Agent-executed function: Biographer agent prints the lineage path."""
        print(f"[Biographer] Received lineage path: {lineage_path}")

    def run(self, ancestor: str, descendant: str):
        """Execute the CrewAI workflow to find and print the lineage path."""
        result = self.crew.kickoff(inputs={"ancestor": ancestor, "descendant": descendant})
        print(result)
