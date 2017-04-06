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

def import_galaxyxml(xml_path):
    """
    Load existing xml into the :class:`galaxyxml.tool.Tool` object.

    :param xml_path: Path of the XML to be loaded.
    :type xml_path: STRING
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
            pass
        elif child.tag == 'outputs':
            pass
        elif child.tag == 'help':
            tool.help = child.text
        elif child.tag == 'citations':
            add_citations(tool, child)
        # Need to pass for description, stdio and command which are already taken care of
        elif child.tag == 'description':
            pass
        elif child.tag == 'stdio':
            pass
        elif child.tag == 'command':
            pass
        # Display warning message for unprocessed TAGs
        else:
            logger.warning(child.tag + " TAG is not processed in the import process.")
    return tool
