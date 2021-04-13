import logging
from builtins import (
    object,
    str
)

from galaxy.tool_util.parser.util import _parse_name

from galaxyxml import Util

from lxml import etree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XMLParam(object):
    name = "node"

    def __init__(self, *args, **kwargs):
        # http://stackoverflow.com/a/12118700
        self.children = []
        self.parent = None
        kwargs = {k: v for k, v in list(kwargs.items()) if v is not None}
        kwargs = Util.coerce(kwargs, kill_lists=True)
        kwargs = Util.clean_kwargs(kwargs, final=True)
        self.node = etree.Element(self.name, **kwargs)

    def __getattr__(self, name):
        """
        Allow to access keys of the node "attributes" (i.e. the dict
        self.node.attrib) as attributes.
        """
        # https://stackoverflow.com/questions/47299243/recursionerror-when-python-copy-deepcopy
        if name == "__setstate__":
            raise AttributeError(name)
        try:
            return self.node.attrib[name]
        except KeyError:
            raise AttributeError(name)

    def append(self, sub_node):
        if self.acceptable_child(sub_node):
            # If one of ours, they aren't etree nodes, they're custom objects
            if issubclass(type(sub_node), XMLParam):
                self.node.append(sub_node.node)
                self.children.append(sub_node)
                self.children[-1].parent = self
            else:
                raise Exception(
                    "Child was unacceptable to parent (%s is not appropriate for %s)" % (type(self), type(sub_node))
                )
        else:
            raise Exception(
                "Child was unacceptable to parent (%s is not appropriate for %s)" % (type(self), type(sub_node))
            )

    def validate(self):
        # Very few need validation, but some nodes we may want to have
        # validation routines on. Should only be called when DONE.
        for child in self.children:
            # If any child fails to validate return false.
            if not child.validate():
                return False
        return True

    def cli(self):
        lines = []
        for child in self.children:
            lines.append(child.command_line())
        return "\n".join(lines)

    def command_line(self, mako_path=None):
        """
        genetate the command line for the node (and its childres)

        mako_path override the path to the node
        """
        return None


class Stdios(XMLParam):
    name = "stdio"

    def acceptable_child(self, child):
        return isinstance(child, Stdio)


class Stdio(XMLParam):
    name = "exit_code"

    def __init__(self, range="1:", level="fatal", **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Stdio, self).__init__(**params)


class Macros(XMLParam):
    name = "macros"

    def acceptable_child(self, child):
        return isinstance(child, (Macro, Import))


class Macro(XMLParam):
    name = "xml"

    def __init__(self, name):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs['name'] = params['name']
        super(Macro, self).__init__(**passed_kwargs)

    def acceptable_child(self, child):
        return issubclass(type(child), XMLParam) and not isinstance(child, Macro)


class Import(XMLParam):
    name = "import"

    def __init__(self, value):
        super(Import, self).__init__()
        self.node.text = value

    def acceptable_child(self, child):
        return issubclass(type(child), XMLParam) and not isinstance(child, Macro)


class Expand(XMLParam):
    """
    <expand macro="...">
    """
    name = "expand"

    def __init__(self, macro):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs['macro'] = params['macro']
        super(Expand, self).__init__(**passed_kwargs)

    def command_line(self, mako_path=None):
        """
        need to define empty command line contribution
        since Expand can be child of Inputs/Outputs
        """
        return ""


class ExpandIO(Expand):
    """
    macro expasion like for Expand
    but an additional token with the same name but in upper case is added to
    the command section. can only be used in Inputs and Outputs
    """
    name = "expand"

    def __init__(self, macro):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs['macro'] = params['macro']
        super(Expand, self).__init__(**passed_kwargs)

    def command_line(self, mako_path=None):
        return "@%s@" % self.node.attrib["macro"].upper()


class RequestParamTranslation(XMLParam):
    name = "request_param_translation"

    def __init__(self, **kwargs):
        self.node = etree.Element(self.name)

    def acceptable_child(self, child):
        return isinstance(child, RequestParamTranslation) \
            or isinstance(child, Expand)


class RequestParam(XMLParam):
    name = "request_param"

    def __init__(self, galaxy_name, remote_name, missing, **kwargs):
        # TODO: bulk copy locals into self.attr?
        self.galaxy_name = galaxy_name
        # http://stackoverflow.com/a/1408860
        params = Util.clean_kwargs(locals().copy())
        super(RequestParam, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, AppendParam) and self.galaxy_name == "URL" \
            or isinstance(child, Expand)


class AppendParam(XMLParam):
    name = "append_param"

    def __init__(self, separator="&amp;", first_separator="?", join="=", **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(AppendParam, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, AppendParamValue)


class AppendParamValue(XMLParam):
    name = "value"

    def __init__(self, name="_export", missing="1", **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(AppendParamValue, self).__init__(**params)

    def acceptable_child(self, child):
        return False


class EdamOperations(XMLParam):
    name = "edam_operations"

    def acceptable_child(self, child):
        return issubclass(type(child), EdamOperation) \
            or isinstance(child, Expand)

    def has_operation(self, edam_operation):
        """
        Check the presence of a given edam_operation.

        :type edam_operation: STRING
        """
        for operation in self.children:
            if operation.node.text == edam_operation:
                return True
        return False


class EdamOperation(XMLParam):
    name = "edam_operation"

    def __init__(self, value):
        super(EdamOperation, self).__init__()
        self.node.text = str(value)


class EdamTopics(XMLParam):
    name = "edam_topics"

    def acceptable_child(self, child):
        return issubclass(type(child), EdamTopic) \
            or isinstance(child, Expand)

    def has_topic(self, edam_topic):
        """
        Check the presence of a given edam_topic.

        :type edam_topic: STRING
        """
        for topic in self.children:
            if topic.node.text == edam_topic:
                return True
        return False


class EdamTopic(XMLParam):
    name = "edam_topic"

    def __init__(self, value):
        super(EdamTopic, self).__init__()
        self.node.text = str(value)


class Requirements(XMLParam):
    name = "requirements"
    # This bodes to be an issue -__-

    def acceptable_child(self, child):
        return issubclass(type(child), Requirement) \
            or issubclass(type(child), Container) \
            or isinstance(child, Expand)


class Requirement(XMLParam):
    name = "requirement"

    def __init__(self, type, value, version=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs["version"] = params["version"]
        passed_kwargs["type"] = params["type"]
        super(Requirement, self).__init__(**passed_kwargs)
        self.node.text = str(value)


class Container(XMLParam):
    name = "container"

    def __init__(self, type, value, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs["type"] = params["type"]
        super(Container, self).__init__(**passed_kwargs)
        self.node.text = str(value)


class Configfiles(XMLParam):
    name = "configfiles"

    def acceptable_child(self, child):
        return issubclass(type(child), Configfile) \
            or issubclass(type(child), ConfigfileDefaultInputs) \
            or isinstance(child, Expand)


class Configfile(XMLParam):
    name = "configfile"

    def __init__(self, name, text, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs["name"] = params["name"]
        super(Configfile, self).__init__(**passed_kwargs)
        self.node.text = etree.CDATA(str(text))


class ConfigfileDefaultInputs(XMLParam):
    name = "inputs"

    def __init__(self, name, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        passed_kwargs = {}
        passed_kwargs["name"] = params["name"]
        super(ConfigfileDefaultInputs, self).__init__(**passed_kwargs)


class Inputs(XMLParam):
    name = "inputs"
    # This bodes to be an issue -__-

    def __init__(self, action=None, check_value=None, method=None, target=None, nginx_upload=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Inputs, self).__init__(**params)

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter) \
            or issubclass(type(child), Expand) \
            or issubclass(type(child), ExpandIO)


class InputParameter(XMLParam):
    def __init__(self, name, **kwargs):
        # TODO: look at
        if "argument" in kwargs and kwargs['argument']:
            self.flag_identifier = kwargs['argument'].lstrip()
            self.num_dashes = len(kwargs['argument']) - len(self.flag_identifier)
            self.mako_identifier = _parse_name(name, kwargs['argument'])
        else:
            self.flag_identifier = name
            self.mako_identifier = name

        # We use kwargs instead of the usual locals(), so manually copy the
        # name to kwargs
        if name is not None:
            kwargs = dict([("name", name)] + list(kwargs.items()))

        # Handle positional parameters
        if "positional" in kwargs and kwargs["positional"]:
            self.positional = True
        else:
            self.positional = False

        if "num_dashes" in kwargs:
            self.num_dashes = kwargs["num_dashes"]
            del kwargs["num_dashes"]
        else:
            self.num_dashes = 0

        self.space_between_arg = " "

        # Not sure about this :(
        # https://wiki.galaxyproject.org/Tools/BestPractices#Parameter_help
        if "label" in kwargs:
            # TODO: replace with positional attribute
            if len(self.flag()) > 0:
                if kwargs["label"] is None:
                    kwargs["label"] = "Author did not provide help for this parameter... "
#                 if not self.positional and "argument" not in kwargs:
#                     kwargs["argument"] = self.flag()

        super(InputParameter, self).__init__(**kwargs)

    def command_line(self, mako_path=None):
        before = self.command_line_before(mako_path)
        cli = self.command_line_actual(mako_path)
        after = self.command_line_after()

        complete = [x for x in (before, cli, after) if x is not None]
        return "\n".join(complete)

    def command_line_before(self, mako_path):
        return None

    def command_line_after(self):
        return None

    def command_line_actual(self, mako_path=None):
        try:
            return self.command_line_override
        except Exception:
            if self.positional:
                return self.mako_name(mako_path)
            else:
                return "%s%s%s" % (self.flag(), self.space_between_arg, self.mako_name(mako_path))

    def mako_name(self, mako_path=None):
        if mako_path:
            path = mako_path + "."
        else:
            parent_identifiers = []
            p = self.parent
            while p is not None and hasattr(p, "mako_identifier"):
                # exclude None identifiers -- e.g. <when> tags
                if p.mako_identifier is not None:
                    parent_identifiers.append(p.mako_identifier)
                p = p.parent
            if len(parent_identifiers) > 0:
                parent_identifiers.append("")
            path = ".".join(parent_identifiers)
        return "$" + path + self.mako_identifier

    def flag(self):
        flag = "-" * self.num_dashes
        return flag + self.flag_identifier


class Section(InputParameter):
    name = "section"

    def __init__(self, name, title, expanded=None, help=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Section, self).__init__(**params)

    def command_line(self, mako_path=None):
        cli = []
        for child in self.children:
            cli.append(child.command_line(mako_path))
        return "\n".join(cli)

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter) \
            or isinstance(child, Expand)


class Repeat(InputParameter):
    name = "repeat"

    def __init__(self, name, title, min=None, max=None, default=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Repeat, self).__init__(**params)

    def command_line_before(self, mako_path):
        return "#for $i_%s in %s" % (self.name, self.mako_name(mako_path))

    def command_line_after(self):
        return "#end for"

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter) \
            or isinstance(child, Expand)

    def command_line_actual(self, mako_path):
        lines = []
        for c in self.children:
            lines.append(c.command_line(mako_path="i_%s" % self.name))
        return "\n".join(lines)


class Conditional(InputParameter):
    name = "conditional"

    def __init__(self, name, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Conditional, self).__init__(**params)

    def acceptable_child(self, child):
        if isinstance(child, Expand):
            return True
        elif len(self.children) == 0 and issubclass(type(child), SelectParam):
            return True
        elif len(self.children) > 0 and issubclass(type(child), When):
            return True
        else:
            return False
#         return issubclass(type(child), InputParameter) and not isinstance(child, Conditional)

    def command_line(self, mako_path=None):
        lines = []
        for c in self.children[1:]:
            if len(c.children) == 0:
                continue
            lines.append('#if str(%s) == "%s"' % (self.children[0].mako_name(mako_path), c.value))
            lines.append(c.cli())
            lines.append('#end if')
        return "\n".join(lines)

    def validate(self):
        # Find a way to check if one of the kids is a WHEN
        pass


class When(InputParameter):
    name = "when"

    def __init__(self, value):
        params = Util.clean_kwargs(locals().copy())
        super(When, self).__init__(None, **params)

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter) \
            or isinstance(child, Expand)


class Param(InputParameter):
    name = "param"

    # This...isn't really valid as-is, and shouldn't be used.
    def __init__(self, name, argument=None, value=None, optional=None, label=None, help=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        params = dict([("name", params["name"]),
                      ("argument", params["argument"]),
                      ("type", self.type)] + list(params.items()))
        super(Param, self).__init__(**params)

        if type(self) == Param:
            raise Exception("Param class is not an actual parameter type, use a subclass of Param")

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter) \
            or isinstance(child, ValidatorParam) \
            or isinstance(child, Expand)


class TextParam(Param):
    type = "text"

    def __init__(self, name, argument=None, optional=None, value=None, label=None, help=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(TextParam, self).__init__(**params)

    def command_line_actual(self, mako_path=None):
        # TODO same as parent class
        try:
            return self.command_line_override
        except Exception:
            if self.positional:
                return self.mako_name(mako_path)
            else:
                return f"{self.flag()}{self.space_between_arg}'{self.mako_name()}'"


class _NumericParam(Param):
    def __init__(self, name, value, argument=None, optional=None, min=None, max=None, label=None, help=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(_NumericParam, self).__init__(**params)


class IntegerParam(_NumericParam):
    type = "integer"


class FloatParam(_NumericParam):
    type = "float"


class BooleanParam(Param):
    type = "boolean"

    def __init__(
        self, name, argument=None, optional=None, checked=False, truevalue=None, falsevalue=None, label=None, help=None, **kwargs
    ):
        params = Util.clean_kwargs(locals().copy())

        super(BooleanParam, self).__init__(**params)
        if truevalue is None:
            # If truevalue and falsevalue are None, then we use "auto", the IUC
            # recommended default.
            #
            # truevalue is set to the parameter's value, and falsevalue is not.
            #
            # Unfortunately, mako_identifier is set as a result of the super
            # call, which we shouldn't call TWICE, so we'll just hack around this :(
            # params['truevalue'] = '%s%s' % (self.)
            self.node.attrib["truevalue"] = self.flag()

        if falsevalue is None:
            self.node.attrib["falsevalue"] = ""

    def command_line_actual(self, mako_path=None):
        if hasattr(self, "command_line_override"):
            return self.command_line_override
        else:
            return "%s" % self.mako_name(mako_path)


class DataParam(Param):
    type = "data"

    def __init__(self, name, argument=None, optional=None, format=None, multiple=None, label=None, help=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(DataParam, self).__init__(**params)


class SelectParam(Param):
    type = "select"

    def __init__(
        self,
        name,
        argument=None,
        optional=None,
        data_ref=None,
        display=None,
        multiple=None,
        options=None,
        default=None,
        label=None,
        help=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        del params["options"]
        del params["default"]

        super(SelectParam, self).__init__(**params)

        if options is not None and default is not None:
            if default not in options:
                raise Exception("Specified a default that isn't in options")

        if options:
            for k, v in list(sorted(options.items())):
                selected = k == default
                self.append(SelectOption(k, v, selected=selected))

    def acceptable_child(self, child):
        return issubclass(type(child), SelectOption) \
            or issubclass(type(child), Options) \
            or isinstance(child, Expand)


class SelectOption(InputParameter):
    name = "option"

    def __init__(self, value, text, selected=False, **kwargs):
        params = Util.clean_kwargs(locals().copy())

        passed_kwargs = {}
        if selected:
            passed_kwargs["selected"] = "true"
        passed_kwargs["value"] = params["value"]

        super(SelectOption, self).__init__(None, **passed_kwargs)
        self.node.text = str(text)


class Options(InputParameter):
    name = "options"

    def __init__(self, from_dataset=None, from_file=None, from_data_table=None, from_parameter=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Options, self).__init__(None, **params)

    def acceptable_child(self, child):
        return issubclass(type(child), Column) \
            or issubclass(type(child), Filter) \
            or isinstance(child, Expand)


class Column(InputParameter):
    name = "column"

    def __init__(self, name, index, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Column, self).__init__(**params)


class Filter(InputParameter):
    name = "filter"

    def __init__(
        self,
        type,
        column=None,
        name=None,
        ref=None,
        key=None,
        multiple=None,
        separator=None,
        keep=None,
        value=None,
        ref_attribute=None,
        index=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        super(Filter, self).__init__(**params)


class ValidatorParam(InputParameter):
    name = "validator"

    def __init__(
        self,
        type,
        message=None,
        filename=None,
        metadata_name=None,
        metadata_column=None,
        line_startswith=None,
        min=None,
        max=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        super(ValidatorParam, self).__init__(**params)


class Outputs(XMLParam):
    name = "outputs"

    def acceptable_child(self, child):
        return isinstance(child, OutputData) \
            or isinstance(child, OutputCollection) \
            or isinstance(child, Expand) \
            or isinstance(child, ExpandIO)


class OutputData(XMLParam):
    """Copypasta of InputParameter, needs work
    """

    name = "data"

    def __init__(
        self,
        name,
        format,
        format_source=None,
        metadata_source=None,
        label=None,
        from_work_dir=None,
        hidden=False,
        **kwargs,
    ):
        # TODO: validate format_source&metadata_source against something in the
        # XMLParam children tree.
        self.mako_identifier = name
        if "num_dashes" in kwargs:
            self.num_dashes = kwargs["num_dashes"]
            del kwargs["num_dashes"]
        else:
            self.num_dashes = 0
        self.space_between_arg = " "
        params = Util.clean_kwargs(locals().copy())

        super(OutputData, self).__init__(**params)

    def command_line(self, mako_path=None):
        if hasattr(self, "command_line_override"):
            return self.command_line_override
        else:
            return "%s%s%s" % (self.flag(), self.space_between_arg, self.mako_name(mako_path))

    def mako_name(self):
        return "'$" + self.mako_identifier + "'"

    def flag(self):
        flag = "-" * self.num_dashes
        return flag + self.mako_identifier

    def acceptable_child(self, child):
        return isinstance(child, OutputFilter) \
            or isinstance(child, ChangeFormat) \
            or isinstance(child, DiscoverDatasets) \
            or isinstance(child, Expand)


class OutputFilter(XMLParam):
    name = "filter"

    def __init__(self, text, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        del params["text"]
        super(OutputFilter, self).__init__(**params)
        self.node.text = text

    def acceptable_child(self, child):
        return False


class ChangeFormat(XMLParam):
    name = "change_format"

    def __init__(self, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(ChangeFormat, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, ChangeFormatWhen) \
            or isinstance(child, Expand)


class ChangeFormatWhen(XMLParam):
    name = "when"

    def __init__(self, input, format, value, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(ChangeFormatWhen, self).__init__(**params)

    def acceptable_child(self, child):
        return False


class OutputCollection(XMLParam):
    name = "collection"

    def __init__(
        self,
        name,
        type=None,
        label=None,
        format_source=None,
        type_source=None,
        structured_like=None,
        inherit_format=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        super(OutputCollection, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, OutputData) or isinstance(child, OutputFilter) or isinstance(child, DiscoverDatasets)

    def command_line_before(self, mako_path):
        return "<output_collection name = '%s'>" % self.name

    def command_line_after(self):
        return "</output_collection>"

    def command_line_actual(self, mako_path):
        lines = []
        for child in self.children:
            lines.append(child.command_line())
        return "\n".join(lines)


class DiscoverDatasets(XMLParam):
    name = "discover_datasets"

    def __init__(self, pattern, directory=None, format=None, ext=None, visible=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(DiscoverDatasets, self).__init__(**params)


class Tests(XMLParam):
    name = "tests"

    def acceptable_child(self, child):
        return issubclass(type(child), Test) \
            or isinstance(child, Expand)


class Test(XMLParam):
    name = "test"

    def acceptable_child(self, child):
        return isinstance(child, TestParam) \
            or isinstance(child, TestOutput) \
            or isinstance(child, TestOutputCollection) \
            or isinstance(child, TestRepeat) \
            or isinstance(child, Expand)


class TestParam(XMLParam):
    name = "param"

    def __init__(self, name, value=None, ftype=None, dbkey=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(TestParam, self).__init__(**params)


class TestOutput(XMLParam):
    name = "output"

    def __init__(
        self,
        name=None,
        file=None,
        ftype=None,
        sort=None,
        value=None,
        md5=None,
        checksum=None,
        compare=None,
        lines_diff=None,
        delta=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        super(TestOutput, self).__init__(**params)


class TestOCElement(XMLParam):
    name = "element"

    def __init__(self, name=None, file=None, ftype=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(TestOCElement, self).__init__(**params)


class TestOutputCollection(XMLParam):
    name = "output_collection"

    def __init__(
        self,
        name=None,
        ftype=None,
        sort=None,
        value=None,
        compare=None,
        lines_diff=None,
        delta=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        super(TestOutputCollection, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, TestOCElement)

    def command_line_before(self, mako_path):
        return "<output_collection name = '%s'>" % self.name

    def command_line_after(self):
        return "</output_collection>"

    def command_line_actual(self, mako_path):
        lines = []
        for child in self.children:
            lines.append(child.command_line())
        return "\n".join(lines)


class TestRepeat(XMLParam):
    name = "repeat"

    def __init__(
        self,
        name=None,
        ftype=None,
        sort=None,
        value=None,
        compare=None,
        lines_diff=None,
        delta=None,
        **kwargs,
    ):
        params = Util.clean_kwargs(locals().copy())
        super(TestRepeat, self).__init__(**params)

    def acceptable_child(self, child):
        return issubclass(type(child), TestParam) \
            or issubclass(type(child), TestOutput) \
            or issubclass(type(child), TestOutputCollection)

    def command_line_before(self, mako_path):
        return "<repeat name = '%s'>" % self.name

    def command_line_after(self):
        return "</repeat>"

    def command_line_actual(self, mako_path):
        lines = []
        for child in self.children:
            lines.append(child.command_line())
        return "\n".join(lines)


class Citations(XMLParam):
    name = "citations"

    def acceptable_child(self, child):
        return issubclass(type(child), Citation) \
            or isinstance(child, Expand)

    def has_citation(self, type, value):
        """
        Check the presence of a given citation.

        :type type: STRING
        :type value: STRING
        """
        for citation in self.children:
            if citation.node.attrib['type'] == type \
               and citation.node.text == value:
                return True
        return False


class Citation(XMLParam):
    name = "citation"

    def __init__(self, type, value):
        passed_kwargs = {}
        passed_kwargs["type"] = type
        super(Citation, self).__init__(**passed_kwargs)
        self.node.text = str(value)
