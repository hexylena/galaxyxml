import logging
import xml.etree.ElementTree as ET
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GalaxyXmlParser(object):
    """
    Class to import content from an existing Galaxy XML wrapper.
    """

    def _init_tool(self, xml_root):
        """
        Init tool from existing xml tool.

        :param xml_root: root of the galaxy xml file.
        :type xml_root: :class:`xml.etree._Element`
        """
        name = xml_root.attrib['name']
        tool_id = xml_root.attrib['id']
        version = xml_root.attrib['version']
        for child in xml_root:
            if child.tag == 'description':
                description = child.text
                break
        for child in xml_root:
            if child.tag == 'command':
                exe = child.text
                break

        tool = gxt.Tool(name, tool_id, version, description, exe)
        return tool

    def _load_help(self, tool, help_root):
        """
        load the content of the help into the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param requirements_root: root of help tag.
        :type requirements_root: :class:`xml.etree._Element`
        """
        tool.help = help_root.text

    def _load_requirements(self, tool, requirements_root):
        """
        Add requirements to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param requirements_root: root of requirements tag.
        :type requirements_root: :class:`xml.etree._Element`
        """
        tool.requirements = gxtp.Requirements()
        for req in requirements_root:
            req_type = req.attrib['type']
            value = req.text
            version = req.attrib['version']
            tool.requirements.append(gxtp.Requirement(req_type, value, version=version))

    def _load_edam_topics(self, tool, topics_root):
        """
        Add edam_topics to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param topics_root: root of edam_topics tag.
        :type topics_root: :class:`xml.etree._Element`
        """
        tool.edam_topics = gxtp.EdamTopics()
        for edam_topic in topics_root:
            tool.edam_topics.append(gxtp.EdamTopic(edam_topic.text))

    def _load_edam_operations(self, tool, operations_root):
        """
        Add edam_operations to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param operations_root: root of edam_operations tag.
        :type operations_root: :class:`xml.etree._Element`
        """
        tool.edam_operations = gxtp.EdamOperations()
        for edam_op in operations_root:
            tool.edam_operations.append(gxtp.EdamOperation(edam_op.text))

    def _load_configfiles(self, tool, configfiles_root):
        """
        Add citations to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param configfiles_root: root of citations tag.
        :type configfiles_root: :class:`xml.etree._Element`
        """
        tool.configfiles = gxtp.Configfiles()
        for conf in configfiles_root:
            name = conf.attrib['name']
            value = conf.text
            tool.configfiles.append(gxtp.Configfile(name, value))

    def _load_citations(self, tool, citations_root):
        """
        Add citations to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param citations_root: root of citations tag.
        :type citations_root: :class:`xml.etree._Element`
        """
        tool.citations = gxtp.Citations()
        for cit in citations_root:
            cit_type = cit.attrib['type']
            value = cit.text
            tool.citations.append(gxtp.Citation(cit_type, value))

    def _load_inputs(self, tool, inputs_root):
        """
        Add inputs to the tool using the :class:`galaxyxml.tool.import_xml.InputsParser` object.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param inputs_root: root of inputs tag.
        :type inputs_root: :class:`xml.etree._Element`
        """
        tool.inputs = gxtp.Inputs()
        inp_parser = InputsParser()
        inp_parser.load_inputs(tool.inputs, inputs_root)

    def import_xml(self, xml_path):
        """
        Load existing xml into the :class:`galaxyxml.tool.Tool` object.

        :param xml_path: Path of the XML to be loaded.
        :type xml_path: STRING
        :return: XML content in the galaxyxml model.
        :rtype: :class:`galaxyxml.tool.Tool`
        """
        xml_root = ET.parse(xml_path).getroot()
        tool = self._init_tool(xml_root)
        # Now we import each tag's field
        for child in xml_root:
            try:
                getattr(self, '_load_{}'.format(child.tag))(tool, child)
            except AttributeError:
                logger.warning(child.tag + " tag is not processed.")
        return tool


class InputsParser(object):
    """
    Class to parse content of the inputs tag from a Galaxy XML wrapper.
    """

    def _load_data_param(self, root, data_param):
        """
        Add <param type='data'> to the tool.

        :param data_param: root of param tag.
        :type data_param: :class:`xml.etree._Element`
        :return: Data param object instantiated.
        :rtype: :class:`galaxyxml.tool.parameters.DataParam`
        """
        name = data_param.attrib['name']
        optional = data_param.attrib.get('optional', None)
        label = data_param.attrib.get('label', None)
        inp_help = data_param.attrib.get('help', None)
        inp_format = data_param.attrib.get('format', None)
        multiple = data_param.attrib.get('multiple', None)
        root.append(gxtp.DataParam(name, optional=optional, label=label,
                                   help=inp_help, format=inp_format,
                                   multiple=multiple))

    def _load_boolean_param(self, root, bool_param):
        """
        Create boolean param from its xml root.

        :param bool_param: root of param tag.
        :type bool_param: :class:`xml.etree._Element`
        """
        name = bool_param.attrib['name']
        optional = bool_param.attrib.get('optional', None)
        label = bool_param.attrib.get('label', None)
        inp_help = bool_param.attrib.get('help', None)
        checked = bool_param.attrib.get('checked', False)
        truevalue = bool_param.attrib.get('truevalue', None)
        falsevalue = bool_param.attrib.get('falsevalue', None)
        root.append(gxtp.BooleanParam(name, optional=optional, label=label, help=inp_help,
                    checked=checked, truevalue=truevalue, falsevalue=falsevalue))

    def _load_select_param(self, root, sel_param):
        """
        Create :class:`galaxyxml.tool.parameters.SelectParam` from its xml root.

        :param sel_param: root of param type='select' tag.
        :type sel_param: :class:`xml.etree._Element`
        """
        name = sel_param.attrib['name']
        optional = sel_param.attrib.get('optional', None)
        label = sel_param.attrib.get('label', None)
        inp_help = sel_param.attrib.get('help', None)
        data_ref = sel_param.attrib.get('data_ref', None)
        display = sel_param.attrib.get('display', None)
        multiple = sel_param.attrib.get('multiple', None)
        select_param = gxtp.SelectParam(name, optional=optional, label=label, help=inp_help,
                                        data_ref=data_ref, display=display, multiple=multiple)
        # TODO: handle options too and not only option
        for option in sel_param:
            select_param.append(gxtp.SelectOption(option.attrib.get('value', None),
                                                  option.text,
                                                  selected=option.attrib.get('selected', False)))
        root.append(select_param)

    def _load_param(self, root, param_root):
        """
        Method to select which type of param is being added to the root.

        :param root: root to attach param to.
        :param param_root: root of param tag.
        :type param_root: :class:`xml.etree._Element`
        """
        param_type = param_root.attrib['type']
        try:
            getattr(self, '_load_{}_param'.format(param_type))(root, param_root)
        except AttributeError:
            logger.warning(param_type + " tag is not processed for <param>.")

    def _load_when(self, root, when_root):
        """
        Add when to the root.

        :param root: root to append when to.
        :param when_root: root of when tag.
        :type when_root: :class:`xml.etree._Element`
        """
        when = gxtp.When(when_root.attrib['value'])
        self.load_inputs(when, when_root)
        root.append(when)

    def _load_conditional(self, root, conditional_root):
        """
        Add conditional to the root.

        :param root: root to append conditional to.
        :param conditional_root: root of conditional tag.
        :type conditional_root: :class:`xml.etree._Element`
        """
        name = conditional_root.attrib['name']
        # Other optional parameters need to be added to conditional object
        conditional = gxtp.Conditional(name)
        for cond_child in conditional_root:
            try:
                getattr(self, '_load_{}'.format(cond_child.tag))(conditional, cond_child)
            except AttributeError:
                logger.warning(cond_child.tag + " tag is not processed for <conditional>.")
        root.append(conditional)

    def load_inputs(self, root, inputs_root):
        """
        Add inputs to the root.

        :param root: root to attach inputs to (either <inputs> or <when>).
        :param inputs_root: root of inputs tag.
        :type inputs_root: :class:`xml.etree._Element`
        """
        for inp_child in inputs_root:
            try:
                getattr(self, '_load_{}'.format(inp_child.tag))(root, inp_child)
            except AttributeError:
                logger.warning(inp_child.tag + " tag is not processed for <inputs>.")
