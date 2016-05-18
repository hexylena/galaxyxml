from builtins import str
from builtins import object
from lxml import etree
from galaxyxml import Util

class XMLParam(object):
    name = 'node'

    def __init__(self, *args, **kwargs):
        # http://stackoverflow.com/a/12118700
        self.children = []
        kwargs = {k: v for k, v in list(kwargs.items()) if v is not None}
        kwargs = Util.coerce(kwargs, kill_lists=True)
        kwargs = Util.clean_kwargs(kwargs, final=True)
        self.node = etree.Element(self.name, **kwargs)

    def append(self, sub_node):
        if self.acceptable_child(sub_node):
            # If one of ours, they aren't etree nodes, they're custom objects
            if issubclass(type(sub_node), XMLParam):
                self.node.append(sub_node.node)
                self.children.append(sub_node)
            else:
                raise Exception("Child was unacceptable to parent (%s is not appropriate for %s)" % (type(self), type(sub_node)))
        else:
            raise Exception("Child was unacceptable to parent (%s is not appropriate for %s)" % (type(self), type(sub_node)))

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
            #lines += child.command_line()
        return '\n'.join(lines)

    def command_line(self):
        return None


class RequestParamTranslation(XMLParam):
    name = 'request_param_translation'

    def __init__(self, **kwargs):
        self.node = etree.Element(self.name)

    def acceptable_child(self, child):
        return isinstance(child, RequestParamTranslation)


class RequestParam(XMLParam):
    name = 'request_param'

    def __init__(self, galaxy_name, remote_name, missing, **kwargs):
        #TODO: bulk copy locals into self.attr?
        self.galaxy_name = galaxy_name
        # http://stackoverflow.com/a/1408860
        params = Util.clean_kwargs(locals().copy())
        super(RequestParam, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, AppendParam) and self.galaxy_name == "URL"


class AppendParam(XMLParam):
    name = 'append_param'

    def __init__(self, separator="&amp;", first_separator="?", join="=", **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(AppendParam, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, AppendParamValue)


class AppendParamValue(XMLParam):
    name = 'value'

    def __init__(self, name="_export", missing="1", **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(AppendParamValue, self).__init__(**params)

    def acceptable_child(self, child):
        return False


class Inputs(XMLParam):
    name = 'inputs'
    # This bodes to be an issue -__-

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter)


class InputParameter(XMLParam):

    def __init__(self, name, **kwargs):
        # TODO: look at
        self.mako_identifier = name
        # We use kwargs instead of the usual locals(), so manually copy the
        # name to kwargs
        if name is not None:
            kwargs['name'] = name

        # Handle positional parameters
        if 'positional' in kwargs and kwargs['positional']:
            self.positional = True
        else:
            self.positional = False

        if 'num_dashes' in kwargs:
            self.num_dashes = kwargs['num_dashes']
            del kwargs['num_dashes']
        else:
            self.num_dashes = 0

        self.space_between_arg = " "

        # Not sure about this :(
        # https://wiki.galaxyproject.org/Tools/BestPractices#Parameter_help
        if 'label' in kwargs:
            # TODO: replace with positional attribute
            if len(self.flag()) > 0:
                if kwargs['label'] is None:
                    kwargs['label'] = 'Author did not provide help for this parameter... '
                if not self.positional:
                    if kwargs['help'] is None:
                        kwargs['help'] = '(%s)' % self.flag()
                    else:
                        kwargs['help'] += ' (%s)' % self.flag()

        super(InputParameter, self).__init__(**kwargs)

    def command_line(self):
        before = self.command_line_before()
        cli = self.command_line_actual()
        after = self.command_line_after()

        complete = [x for x in (before, cli, after) if x is not None]
        return '\n'.join(complete)

    def command_line_before(self):
        try:
            return self.command_line_before_override
        except:
            return None

    def command_line_after(self):
        try:
            return self.command_line_after_override
        except:
            return None

    def command_line_actual(self):
        try:
            return self.command_line_override
        except:
            if self.positional:
                return self.mako_name()
            else:
                return "%s%s%s" % (self.flag(), self.space_between_arg, self.mako_name())

    def mako_name(self):
        # TODO: enhance logic to check up parents for things like repeat>condotion>param
        return '$' + self.mako_identifier

    def flag(self):
        flag = '-' * self.num_dashes
        return flag + self.mako_identifier


class Repeat(InputParameter):
    name = 'repeat'

    def __init__(self, name, title, min=None, max=None, default=None,
            **kwargs):
        params = Util.clean_kwargs(locals().copy())
        # Allow overriding
        self.command_line_before_override = '#for $i in $%s:' % name
        self.command_line_after_override = '#end for'
        #self.command_line_override
        super(Repeat, self).__init__(**params)

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter)

    def command_line_actual(self):
        if hasattr(self, 'command_line_override'):
            return self.command_line_override
        else:
            return "%s" % self.mako_name()

class Conditional(InputParameter):
    name = 'conditional'

    def __init__(self, name, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(Conditional, self).__init__(**params)

    def acceptable_child(self, child):
        return issubclass(type(child), InputParameter) \
            and not isinstance(child, Conditional)

    def validate(self):
        # Find a way to check if one of the kids is a WHEN
        pass


class Param(InputParameter):
    name = 'param'

    # This...isn't really valid as-is, and shouldn't be used.
    def __init__(self, name, optional=None, label=None, help=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        params['type'] = self.type
        super(Param, self).__init__(**params)

        if type(self) == Param:
            raise Exception("Param class is not an actual parameter type, use a subclass of Param")

    def acceptable_child(self, child):
        return issubclass(type(child, InputParameter) or isinstance(child), ValidatorParam)


class TextParam(Param):
    type = 'text'

    def __init__(self, name, optional=None, label=None, help=None, size=None,
            area=False, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(TextParam, self).__init__(**params)


class _NumericParam(Param):

    def __init__(self, name, value, optional=None, label=None, help=None,
            min=None, max=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(_NumericParam, self).__init__(**params)


class IntegerParam(_NumericParam):
    type = 'integer'


class FloatParam(_NumericParam):
    type = 'float'


class BooleanParam(Param):
    type = 'boolean'

    def __init__(self, name, optional=None, label=None, help=None,
                 checked=False, truevalue=None, falsevalue=None, **kwargs):
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
            #params['truevalue'] = '%s%s' % (self.)
            self.node.attrib['truevalue'] = self.flag()

        if falsevalue is None:
            self.node.attrib['falsevalue'] = ""

    def command_line_actual(self):
        if hasattr(self, 'command_line_override'):
            return self.command_line_override
        else:
            return "%s" % self.mako_name()


class DataParam(Param):
    type = 'data'

    def __init__(self, name, optional=None, label=None, help=None, format=None,
                 multiple=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(DataParam, self).__init__(**params)


class SelectParam(Param):
    type = None

    def __init__(self, name, optional=None, label=None, help=None,
            data_ref=None, display=None, multiple=None, options=None,
            default=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        del params['options']
        del params['default']

        super(SelectParam, self).__init__(**params)

        if options is not None and default is not None:
            if default  not in options:
                raise Exception("Specified a default that isn't in options")

        for k,v  in options.items():
            selected = (k == default)
            self.append(SelectOption(k, v, selected=selected))

    def acceptable_child(self, child):
        return issubclass(type(child), SelectOption)


class SelectOption(InputParameter):
    name = 'option'

    def __init__(self, value, text, selected=False, **kwargs):
        params = Util.clean_kwargs(locals().copy())

        passed_kwargs = {}
        if selected:
            passed_kwargs['selected'] = "true"
        passed_kwargs['value'] = params['value']

        super(SelectOption, self).__init__(None, **passed_kwargs)
        self.node.text = str(text)


class ValidatorParam(InputParameter):
    name = 'validator'

    def __init__(self, type, message=None, filename=None, metadata_name=None,
                 metadata_column=None, line_startswith=None, min=None,
                 max=None, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(ValidatorParam, self).__init__(**params)


class Outputs(XMLParam):
    name = 'outputs'

    def acceptable_child(self, child):
        return issubclass(type(child), OutputParameter)


class OutputParameter(XMLParam):
    """Copypasta of InputParameter, needs work
    """
    name = 'data'

    def __init__(self, name, format, format_source=None, metadata_source=None,
                 label=None, from_work_dir=None, hidden=False, **kwargs):
        # TODO: validate format_source&metadata_source against something in the
        # XMLParam children tree.
        self.mako_identifier = name
        if 'num_dashes' in kwargs:
            self.num_dashes = kwargs['num_dashes']
            del kwargs['num_dashes']
        else:
            self.num_dashes = 0
        self.space_between_arg = " "
        params = Util.clean_kwargs(locals().copy())

        super(OutputParameter, self).__init__(**params)

    def command_line(self):
        if hasattr(self, 'command_line_override'):
            return self.command_line_override
        else:
            return "%s%s%s" % (self.flag(), self.space_between_arg, self.mako_name())

    def mako_name(self):
        return '$' + self.mako_identifier

    def flag(self):
        flag = '-' * self.num_dashes
        return flag + self.mako_identifier

    def acceptable_child(self, child):
        return isinstance(child, OutputFilter) or isinstance(child, ChangeFormat)

class OutputFilter(XMLParam):
    name = 'filter'

    def __init__(self, text, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        del params['text']
        super(OutputFilter, self).__init__(**params)
        self.node.text = text

    def acceptable_child(self, child):
        return False

class ChangeFormat(XMLParam):
    name = 'change_format'

    def __init__(self, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(ChangeFormat, self).__init__(**params)

    def acceptable_child(self, child):
        return isinstance(child, ChangeFormatWhen)


class ChangeFormatWhen(XMLParam):
    name = 'when'

    def __init__(self, input, format, value, **kwargs):
        params = Util.clean_kwargs(locals().copy())
        super(ChangeFormatWhen, self).__init__(**params)

    def acceptable_child(self, child):
        return False
