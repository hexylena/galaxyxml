import xml.etree.ElementTree as ET
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

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
            pass
        elif child.tag == 'edam_topics':
            pass
        elif child.tag == 'edam_operations':
            pass
        elif child.tag == 'inputs':
            pass
        elif child.tag == 'outputs':
            pass
        elif child.tag == 'help':
            tool.help = child.text
        elif child.tag == 'citations':
            pass
        else:
            print(child.tag, "is not processed in the import process.")
    return tool
