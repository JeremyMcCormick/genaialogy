
from unittest import TestCase
from genaialogy.tools.biography import Biographer

class BiographyTestCase(TestCase):

    def test_biography(self):
        biographer = Biographer("William-McCormick.ged")
        biography = biographer.generate_biography("Harry Glenn McCormick", dry_run=False)
        print(biography)
