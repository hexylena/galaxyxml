"""
Unit tests for the import of existing Galaxy XML to galaxyxml.
"""

import unittest
from galaxyxml.tool.import_xml import GalaxyXmlParser

class TestImport(unittest.TestCase):

    def setUp(self):
        gxp = GalaxyXmlParser()
        self.tool = gxp.import_xml('test/import_xml.xml')

    def test_init_tool(self):
        xml_root = self.tool.root
        self.assertEqual(xml_root.attrib['id'], 'import_test')
        self.assertEqual(xml_root.attrib['name'], 'Import')
        self.assertEqual(xml_root.attrib['version'], '1.0')
        self.assertEqual(xml_root[0].text, 'description')
        self.assertEqual(self.tool.command, 'command')
        self.assertEqual(self.tool.help, 'help')
