import copy
import logging

from galaxyxml import GalaxyXML, Util
from galaxyxml.tool.parameters import XMLParam

from lxml import etree

VALID_TOOL_TYPES = ("data_source", "data_source_async")
VALID_URL_METHODS = ("get", "post")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tool(GalaxyXML):

    def __init__(
        self,
        name,
        id,
        version,
        description,
        executable,
        hidden=False,
        tool_type=None,
        URL_method=None,
        workflow_compatible=True,
        interpreter=None,
        version_command="interpreter filename.exe --version",
        command_line_override=None,
    ):

        self.executable = executable
        self.interpreter = interpreter
        self.command_line_override = command_line_override
        kwargs = {
            "name": name,
            "id": id,
            "version": version,
            "hidden": hidden,
            "workflow_compatible": workflow_compatible,
        }
        self.version_command = version_command

        # Remove some of the default values to make tools look a bit nicer
        if not hidden:
            del kwargs["hidden"]
        if workflow_compatible:
            del kwargs["workflow_compatible"]

        kwargs = Util.coerce(kwargs)
        self.root = etree.Element("tool", **kwargs)

        if tool_type is not None:
            if tool_type not in VALID_TOOL_TYPES:
                raise Exception("Tool type must be one of %s" % ",".join(VALID_TOOL_TYPES))
            else:
                kwargs["tool_type"] = tool_type

                if URL_method is not None:
                    if URL_method in VALID_URL_METHODS:
                        kwargs["URL_method"] = URL_method
                    else:
                        raise Exception("URL_method must be one of %s" % ",".join(VALID_URL_METHODS))

        description_node = etree.SubElement(self.root, "description")
        description_node.text = description

    def add_comment(self, comment_txt):
        comment = etree.Comment(comment_txt)
        self.root.insert(0, comment)

    def append_version_command(self):
        version_command = etree.SubElement(self.root, "version_command")
        try:
            version_command.text = etree.CDATA(self.version_command)
        except Exception:
            pass

    def append(self, sub_node):
        if issubclass(type(sub_node), XMLParam):
            self.root.append(sub_node.node)
        else:
            self.root.append(sub_node)

    def clean_command_string(self, command_line):
        clean = []
        for x in command_line:
            if x is not [] and x is not [""]:
                clean.append(x)

        return "\n".join(clean)

    def export(self, keep_old_command=False):  # noqa

        export_xml = copy.deepcopy(self)

        try:
            export_xml.append(export_xml.edam_operations)
        except Exception:
            pass

        try:
            export_xml.append(export_xml.edam_topics)
        except Exception:
            pass

        try:
            export_xml.append(export_xml.requirements)
        except Exception:
            pass

        try:
            export_xml.append(export_xml.configfiles)
        except Exception:
            pass

        if self.command_line_override:
            command_line = self.command_line_override
        else:
            command_line = []
            try:
                command_line.append(export_xml.inputs.cli())
            except Exception as e:
                logger.warning(str(e))

            try:
                command_line.append(export_xml.outputs.cli())
            except Exception:
                pass

        # Add stdio section
        stdio = etree.SubElement(export_xml.root, "stdio")
        etree.SubElement(stdio, "exit_code", range="1:", level="fatal")

        # Append version command
        export_xml.append_version_command()

        # Steal interpreter from kwargs
        command_kwargs = {}
        if export_xml.interpreter is not None:
            command_kwargs["interpreter"] = export_xml.interpreter

        # Add command section
        command_node = etree.SubElement(export_xml.root, "command", **command_kwargs)

        if keep_old_command:
            if getattr(self, "command", None):
                command_node.text = etree.CDATA(export_xml.command)
            else:
                logger.warning("The tool does not have any old command stored. " + "Only the command line is written.")
                command_node.text = export_xml.executable
        else:
            actual_cli = "%s %s" % (export_xml.executable, export_xml.clean_command_string(command_line))
            command_node.text = etree.CDATA(actual_cli.strip())

        try:
            export_xml.append(export_xml.inputs)
        except Exception:
            pass

        try:
            export_xml.append(export_xml.outputs)
        except Exception:
            pass

        try:
            export_xml.append(export_xml.tests)
        except Exception:
            pass

        help_element = etree.SubElement(export_xml.root, "help")
        help_element.text = etree.CDATA(export_xml.help)

        try:
            export_xml.append(export_xml.citations)
        except Exception:
            pass

        return super(Tool, export_xml).export()
