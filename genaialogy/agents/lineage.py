from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import List

class LineagePath(BaseModel):
    lineage: List[str] = Field(..., description="An ordered list of lineage names from ancestor to descendant.")

class LineageFinder:
    @staticmethod
    def find_lineage(gedcom_file: str, ancestor: str, descendant: str) -> LineagePath:
        from path_finder import PathFinder
        path_finder = PathFinder(gedcom_file, ancestor, descendant)
        path = path_finder.find_path()
        return LineagePath(lineage=path)

class LineageIdentifierAgent(Agent):
    def __init__(self, gedcom_file: str):
        super().__init__(
            role="Genealogy Expert",
            goal="Trace lineage paths between ancestors and descendants",
            backstory="You are a skilled genealogist specializing in lineage research.",
            verbose=True,
            context={"gedcom_file": gedcom_file},
            output_pydantic=LineagePath
        )

    def find_lineage_path(self, ancestor: str, descendant: str) -> LineagePath:
        gedcom_file = self.context["gedcom_file"]
        return LineageFinder.find_lineage(gedcom_file, ancestor, descendant)

class LineageTask(Task):
    def __init__(self, agent: LineageIdentifierAgent):
        super().__init__(
            description="Identify the lineage path from {ancestor} to {descendant}.",
            agent=agent,
            expected_output="A JSON object containing an ordered list of lineage names.",
            context_variables=["ancestor", "descendant"]
        )

class LineageCrew:
    def __init__(self, gedcom_file: str):
        self.lineage_agent = LineageIdentifierAgent(gedcom_file)
        self.lineage_task = LineageTask(self.lineage_agent)

        self.crew = Crew(
            agents=[self.lineage_agent],
            tasks=[self.lineage_task],
            verbose=True
        )

    def run(self, ancestor: str, descendant: str):
        return self.crew.kickoff(inputs={"ancestor": ancestor, "descendant": descendant})
