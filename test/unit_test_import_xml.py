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

    def test_load_help(self):
        self.assertEqual(self.tool.help, 'help')

    def test_load_requirements(self):
        requirement = self.tool.requirements.children[0].node
        self.assertEqual(requirement.text, 'magic_package')
        self.assertEqual(requirement.attrib['type'], 'package')
        self.assertEqual(requirement.attrib['version'], '1')
        container = self.tool.requirements.children[1].node

    def test_load_edam_topics(self):
        topic = self.tool.edam_topics.children[0].node
        self.assertEqual(topic.text, 'topic_0003')

    def test_load_edam_operations(self):
        operation = self.tool.edam_operations.children[0].node
        self.assertEqual(operation.text, 'operation_0004')

    def test_load_configfiles(self):
        configfile = self.tool.configfiles.children[0].node
        self.assertEqual(configfile.text, 'Hello <> World')
        self.assertEqual(configfile.attrib['name'], 'testing')

    def test_load_citations(self):
        citation = self.tool.citations.children[0].node
        self.assertEqual(citation.text, '10.1007/s10009-015-0392-z')
        self.assertEqual(citation.attrib['type'], 'doi')


class TestInputParser(TestImport):

    def test_load_data_param(self):
        param = self.tool.inputs.children[0].node
        self.assertEqual(param.attrib['name'], 'interval_file')
        self.assertEqual(param.attrib['type'], 'data')
        self.assertEqual(param.attrib['format'], 'interval')
        self.assertEqual(param.attrib['label'], 'near intervals in')

    def test_load_boolean_param(self):
        param = self.tool.inputs.children[1].node
        self.assertEqual(param.attrib['checked'], 'false')
        self.assertEqual(param.attrib['help'], 'a help')
        self.assertEqual(param.attrib['label'], 'a label')
        self.assertEqual(param.attrib['name'], 'bool')
        self.assertEqual(param.attrib['type'], 'boolean')
        self.assertEqual(param.attrib['truevalue'], '--bool')
        self.assertEqual(param.attrib['falsevalue'], '')

    def test_load_integer_param(self):
        param = self.tool.inputs.children[2].node
        self.assertEqual(param.attrib['name'], 'int_size')
        self.assertEqual(param.attrib['type'], 'integer')
        self.assertEqual(param.attrib['value'], '1')
        self.assertEqual(param.attrib['label'], 'a label')

    def test_load_float_param(self):
        param = self.tool.inputs.children[3].node
        self.assertEqual(param.attrib['name'], 'float_size')
        self.assertEqual(param.attrib['type'], 'float')
        self.assertEqual(param.attrib['value'], '1')
        self.assertEqual(param.attrib['label'], 'a label')

    def test_load_select_param(self):
        param = self.tool.inputs.children[4].node
        self.assertEqual(param.attrib['name'], 'upstream_or_down')
        self.assertEqual(param.attrib['type'], 'select')
        self.assertEqual(param.attrib['label'], 'Get')
        # test options
        self.assertEqual(param[0].attrib['value'], 'u')
        self.assertEqual(param[0].text, 'Upstream')
        self.assertEqual(param[1].attrib['value'], 'd')
        self.assertEqual(param[1].text, 'Downstream')

    def test_load_conditional(self):
        condi = self.tool.inputs.children[5].node
        self.assertEqual(condi.attrib['label'], 'Conditional')
        self.assertEqual(condi.attrib['name'], 'cond')
        # test when
        self.assertEqual(condi[1].attrib['value'], 'hi')
        self.assertEqual(condi[2].attrib['value'], 'bye')

    def test_load_section(self):
        section = self.tool.inputs.children[6].node 
        self.assertEqual(section.attrib['name'], 'adv')
        self.assertEqual(section.attrib['title'], 'Advanced')
        self.assertEqual(section.attrib['expanded'], 'False')
        # test param within section
        self.assertEqual(section[0].attrib['name'], 'param_sec')
        self.assertEqual(section[0].attrib['type'], 'data')
        self.assertEqual(section[0].attrib['label'], 'Section param')

    def test_load_select_options(self):
        options = self.tool.inputs.children[7].node[0]
        self.assertEqual(options.attrib['from_data_table'], 'snpsift_dbnsfps')
        # test one column and one filter
        self.assertEqual(options[0].attrib['name'], 'name')
        self.assertEqual(options[0].attrib['index'], '4')
        self.assertEqual(options[2].attrib['type'], 'param_value')
        self.assertEqual(options[2].attrib['ref'], 'dbnsfp')
        self.assertEqual(options[2].attrib['column'], '3')

    def test_load_text_param(self):
        text_param = self.tool.inputs.children[8].node
        self.assertEqual(text_param.attrib['name'], 'xlab')
        self.assertEqual(text_param.attrib['size'], '30')
        self.assertEqual(text_param.attrib['type'], 'text')
        self.assertEqual(text_param.attrib['value'], 'V1')

    def test_load_repeat(self):
        repeat = self.tool.inputs.children[9].node
        self.assertEqual(repeat.attrib['name'], 'series')
        self.assertEqual(repeat.attrib['title'], 'Series')
        # test param within repeat
        self.assertEqual(repeat[0].attrib['name'], 'input')
        self.assertEqual(repeat[0].attrib['type'], 'data')
