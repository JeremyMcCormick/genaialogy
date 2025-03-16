"""Test the lineage finder"""

import os
import sys
from io import StringIO
from unittest import TestCase
import tempfile
import shutil

from genaialogy.agents.lineage import LineageCrew
from genaialogy.tests.cache import download_file

class TestLineage(TestCase):

    gedcom_url = "https://www.dropbox.com/scl/fi/wpscc2v4t9wk1zi7fk9be/William-McCormick_2025-03-02.ged?rlkey=wqulry2719fu09svdz10hglt2&st=gjjopgow&dl=0"
    gedcom_name = "William-McCormick.ged"

    """
    ancestor = "William McCormick"
    descendant = "Jeremy Isaac McCormick"

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.gedcom_file = os.path.join(cls.temp_dir, cls.gedcom_name)
        download_file(cls.gedcom_url, cls.gedcom_file)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_path_finder(self):
        finder = PathFinder(self.gedcom_file, self.ancestor, self.descendant)
        path = finder.find_path()
        self.assertIsInstance(path, list)
        self.assertEqual(path[0], self.ancestor)
        self.assertEqual(path[-1], self.descendant)
    """

    def test_lineage_crew(self):
        """Test the CrewAI implementation."""

        download_file(self.gedcom_url, self.gedcom_name)
        crew = LineageCrew("William-McCormick.ged")        # Run function
        crew.run("William McCormick", "Jeremy Isaac McCormick")