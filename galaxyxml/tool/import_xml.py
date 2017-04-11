import logging
import xml.etree.ElementTree as ET
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_tool(xml_root):
    """
    Init tool from existing xml tool.
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


def add_requirements(tool, requirements_root):
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


def add_edam_topics(tool, topics_root):
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


def add_edam_operations(tool, operations_root):
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


def add_configfiles(tool, configfiles_root):
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


def add_citations(tool, citations_root):
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


def add_data_param(data_param):
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
    # return DataParam
    return gxtp.DataParam(name, optional=optional, label=label,
                          help=inp_help, format=inp_format,
                          multiple=multiple)


def add_bool_param(bool_param):
    """
    Add boolean param to the tool.

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
    return gxtp.BooleanParam(name, optional=optional, label=label, help=inp_help,
                             checked=checked, truevalue=truevalue, falsevalue=falsevalue)


def add_conditional(conditional_root):
    """
    Add conditional to the tool.

    :param tool: Tool object from galaxyxml.
    :type tool: :class:`galaxyxml.tool.Tool`
    :param conditional_root: root of conditional tag.
    :type conditional_root: :class:`xml.etree._Element`
    """
    name = conditional_root.attrib['name']
    # Other optional parameters need to be added to conditional object
    conditional = gxtp.Conditional(name)
    return conditional


def add_inputs(tool, inputs_root):
    """
    Add inputs to the tool.

    :param tool: Tool object from galaxyxml.
    :type tool: :class:`galaxyxml.tool.Tool`
    :param inputs_root: root of inputs tag.
    :type inputs_root: :class:`xml.etree._Element`
    """
    tool.inputs = gxtp.Inputs()
    for inp in inputs_root:
        if inp.tag == 'param':
            if inp.attrib['type'] == 'data':
                tool.inputs.append(add_data_param(inp))
            elif inp.attrib['type'] == 'boolean':
                tool.inputs.append(add_bool_param(inp))
            else:
                pass
        elif inp.tag == 'conditional':
            tool.inputs.append(add_conditional(inp))
        else:
            pass


def import_galaxyxml(xml_path):
    """
    Load existing xml into the :class:`galaxyxml.tool.Tool` object.

    :param xml_path: Path of the XML to be loaded.
    :type xml_path: STRING
    :return: XML content in the galaxyxml model.
    :rtype: :class:`galaxyxml.tool.Tool`
    """
    xml_root = ET.parse(xml_path).getroot()
    tool = init_tool(xml_root)
    # Now we import each tag's field
    for child in xml_root:
        if child.tag == 'requirements':
            add_requirements(tool, child)
        elif child.tag == 'edam_topics':
            add_edam_topics(tool, child)
        elif child.tag == 'edam_operations':
            add_edam_operations(tool, child)
        elif child.tag == 'configfiles':
            add_configfiles(tool, child)
        elif child.tag == 'inputs':
            add_inputs(tool, child)
        elif child.tag == 'outputs':
            pass
        elif child.tag == 'help':
            tool.help = child.text
        elif child.tag == 'citations':
            add_citations(tool, child)
        # Need to pass for description, stdio and command which are already taken care of
        elif child.tag in ('description', 'stdio', 'command'):
            pass
        # Display warning message for unprocessed TAGs
        else:
            logger.warning(child.tag + " TAG is not processed in the import process.")
    return tool
