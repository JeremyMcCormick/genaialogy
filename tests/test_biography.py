
from unittest import TestCase
from genaialogy.tools.biography import Biographer

class BiographyTestCase(TestCase):

    # def test_biography(self):
    #     biographer = Biographer("William-McCormick.ged")
    #     biography = biographer.generate_biography("Harry Glenn McCormick", dry_run=False)
    #     print(biography)

    # def test_biography_dry_run(self):
    #     biographer = Biographer("William-McCormick.ged")
    #     biography = biographer.generate_biography("Harry Glenn McCormick", dry_run=True)
    #     print(biography)

    def test_lineage_report(self):
        biographer = Biographer("William-McCormick.ged")
        with open("lineage_report.txt", "w") as f:
            biographer.write_lineage_report("William McCormick", "Jeremy Isaac McCormick", f)
