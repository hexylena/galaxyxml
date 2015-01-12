from lxml import etree
from galaxyxml import Util, GalaxyXML
from galaxyxml.tool.parameters import XMLParam

VALID_TOOL_TYPES = ('data_source', 'data_source_async')
VALID_URL_METHODS = ('get', 'post')


class Tool(GalaxyXML):

    def __init__(self, name, id, version, description, executable, hidden=False,
                 tool_type=None, URL_method=None, workflow_compatible=True,
                 force_history_refresh=False, interpreter=None):

        self.executable = executable
        self.interpreter = interpreter
        kwargs = {
            'name': name,
            'id': id,
            'version': version,
            'hidden': hidden,
            'workflow_compatible': workflow_compatible,
            'force_history_refresh': force_history_refresh,
        }
        kwargs = Util.coerce(kwargs)
        self.root = etree.Element('tool', **kwargs)

        if tool_type is not None:
            if tool_type not in VALID_TOOL_TYPES:
                raise Exception("Tool type must be one of %s" % ','.join(VALID_TOOL_TYPES))
            else:
                kwargs['tool_type'] = tool_type

                if URL_method is not None:
                    if URL_method in VALID_URL_METHODS:
                        kwargs['URL_method'] = URL_method
                    else:
                        raise Exception("URL_method must be one of %s" %
                                        ','.join(VALID_URL_METHODS))

        description_node = etree.SubElement(self.root, 'description')
        description_node.text = description

    def version_command(self, command_string):
        version_command = etree.SubElement(self.root, 'version_command')
        version_command.text = version_command

    def append(self, sub_node):
        if issubclass(type(sub_node), XMLParam):
            self.root.append(sub_node.node)
        else:
            self.root.append(sub_node)

    def clean_command_string(self, command_line):
        clean = []
        for x in command_line:
            if x is not [] and x is not ['']:
                clean.append(x)

        return '\n'.join(clean)

    def export(self):
        command_line = []
        try:
            command_line.append(self.inputs.cli())
        except Exception, e:
            print e

        try:
            command_line.append(self.outputs.cli())
        except:
            pass

        # Add stdio section
        stdio = etree.SubElement(self.root, 'stdio')
        etree.SubElement(stdio, 'exit_code', range='1:', level='fatal')

        # Steal interpreter from kwargs
        command_kwargs = {}
        if self.interpreter is not None:
            command_kwargs['interpreter'] = self.interpreter

        # Add command section
        command_node = etree.SubElement(self.root, 'command', **command_kwargs)

        actual_cli = "%s %s" % (self.executable, self.clean_command_string(command_line))
        command_node.text = etree.CDATA(actual_cli.strip())


        try:
            self.append(self.inputs)
        except:
            pass

        try:
            self.append(self.outputs)
        except:
            pass

        help_element = etree.SubElement(self.root, 'help')
        help_element.text = etree.CDATA(self.help)

        return super(Tool, self).export()
