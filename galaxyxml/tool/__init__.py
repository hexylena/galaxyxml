import copy
import logging

from galaxyxml import GalaxyXML, Util
from galaxyxml.tool.parameters import Expand, Import, Inputs, Macro, Macros, Outputs, XMLParam, Command

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
        command_override=None,
        macros=[],
        profile=None,
    ):

        self.id = id
        self.executable = executable
        self.interpreter = interpreter
        self.command_override = command_override
        self.profile = profile
        kwargs = {
            "name": name,
            "id": id,
            "version": version,
            "hidden": hidden,
            "workflow_compatible": workflow_compatible,
            "profile": profile
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
        if len(macros) > 0:
            self.macros = Macros()
            for m in macros:
                self.macros.append(Import(m))
        self.inputs = Inputs()
        self.outputs = Outputs()
        self.command = Command()

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

    def export(self, keep_old_command=False):
        # see lib/galaxy/tool_util/linters/xml_order.py
        export_xml = copy.deepcopy(self)
        try:
            export_xml.append(export_xml.macros)
        except Exception:
            pass

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
            export_xml.append(Expand(macro="requirements"))

        # Add stdio section - now an XMLParameter
        try:
            stdio_element = export_xml.stdios
        except Exception:
            stdio_element = None
        if stdio_element:
            try:
                export_xml.append(stdio_element)
            except Exception:
                export_xml.append(Expand(macro="stdio"))

        # Append version command
        export_xml.append_version_command()

        if self.command_override:
            command_line = self.command_override
        else:
            command_line = []
            try:
                command_line.append(export_xml.inputs.cli())
            except Exception as e:
                logger.warning(str(e))
                raise
            try:
                command_line.append(export_xml.outputs.cli())
            except Exception:
                pass
        # Add command section
        command_node_text = None
        if keep_old_command:
            if getattr(self, "command", None):
                command_node_text = etree.CDATA(export_xml.command)
            else:
                logger.warning("The tool does not have any old command stored. Only the command line is written.")
                command_node_text = export_xml.executable
        else:
            if self.command_override:
                actual_cli = export_xml.clean_command_string(command_line)
            else:
                actual_cli = "%s %s" % (
                    export_xml.executable,
                    export_xml.clean_command_string(command_line),
                )
            command_node_text = actual_cli.strip()
        export_xml.command_line = command_node_text
        try:
            command_element = export_xml.command
        except Exception:
            command_element = etree.SubElement(export_xml.root, "command", detect_errors=None)
        command_element.node.text = etree.CDATA(command_node_text)
        export_xml.append(command_element)

        try:
            export_xml.append(export_xml.configfiles)
        except Exception:
            pass

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
            export_xml.append(Expand(macro="%s_tests" % self.id))

        help_element = etree.SubElement(export_xml.root, "help")
        help_element.text = etree.CDATA(export_xml.help)
        export_xml.append(help_element)

        try:
            export_xml.append(export_xml.citations)
        except Exception:
            export_xml.append(Expand(macro="citations"))

        return super(Tool, export_xml).export()


class MacrosTool(Tool):
    """
    creates a <macros> tag containing macros and tokens
    for the inputs and outputs:

    for the inputs

    - a macro `<xml name="ID_inmacro">` containing all the inputs
    - a token `<token name="ID_INMACRO">` containing the CLI for the inputs

    where ID is the id used in initialization.

    analogously for the outputs `ID_outmacro` and `ID_OUTMACRO`
    are created.

    TODO all other elements, like requirements are currently ignored
    """

    def __init__(self, *args, **kwargs):
        super(MacrosTool, self).__init__(*args, **kwargs)
        self.root = etree.Element('macros')
        self.inputs = Macro("%s_inmacro" % self.id)
        self.outputs = Macro("%s_outmacro" % self.id)

    def export(self, keep_old_command=False):  # noqa

        export_xml = copy.deepcopy(self)

        try:
            for child in export_xml.macros:
                export_xml.append(child)
        except Exception:
            pass

        command_line = []
        try:
            command_line.append(export_xml.inputs.cli())
        except Exception as e:
            logger.warning(str(e))
            raise

        # Add command section
        command_node = etree.SubElement(export_xml.root, 'token', {"name": "%s_INMACRO" % self.id.upper()})
        actual_cli = "%s" % (export_xml.clean_command_string(command_line))
        command_node.text = etree.CDATA(actual_cli.strip())

        command_line = []
        try:
            command_line.append(export_xml.outputs.cli())
        except Exception:
            pass
        command_node = etree.SubElement(export_xml.root, 'token', {"name": "%s_OUTMACRO" % self.id.upper()})
        actual_cli = "%s" % (export_xml.clean_command_string(command_line))
        command_node.text = etree.CDATA(actual_cli.strip())

        try:
            export_xml.append(export_xml.inputs)
        except Exception:
            pass

        try:
            export_xml.append(export_xml.outputs)
        except Exception:
            pass

        return super(Tool, export_xml).export()
