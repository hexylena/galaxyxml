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
        version_cmd = None
        description = None
        for child in xml_root:
            if child.tag == "description":
                description = child.text
            elif child.tag == "command":
                executable = child.text.split()[0]
                command = child.text
            elif child.tag == "version_command":
                version_cmd = child.text

        tool = gxt.Tool(
            xml_root.attrib["name"],
            xml_root.attrib["id"],
            xml_root.attrib.get("version", None),
            description,
            executable,
            hidden=xml_root.attrib.get("hidden", False),
            tool_type=xml_root.attrib.get("tool_type", None),
            URL_method=xml_root.attrib.get("URL_method", None),
            workflow_compatible=xml_root.attrib.get("workflow_compatible", True),
            version_command=version_cmd,
        )
        tool.command = command
        return tool

    def _load_description(self, tool, desc_root):
        """
        <description> is already loaded during initiation.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param desc_root: root of <description> tag.
        :type desc_root: :class:`xml.etree._Element`
        """
        logger.info("<description> is loaded during initiation of the object.")

    def _load_version_command(self, tool, vers_root):
        """
        <version_command> is already loaded during initiation.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param vers_root: root of <version_command> tag.
        :type vers_root: :class:`xml.etree._Element`
        """
        logger.info("<version_command> is loaded during initiation of the object.")

    def _load_stdio(self, tool, stdio_root):
        """

        :param tool: <test> root to append <stdio> to.
        :param stdio_root: root of <param> tag.
        :param stdio_root: :class:`xml.etree._Element`
        """
        tool.stdios = gxtp.Stdios()
        for std in stdio_root:
            slevel = std.attrib['level']
            srange = std.attrib['range']
            tool.stdios.append(gxtp.Stdio(level=slevel, range=srange))
        logger.info("<stdio> loaded.")

    def _load_command(self, tool, desc_root):
        """
        <command> is already loaded during initiation.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param desc_root: root of <command> tag.
        :type desc_root: :class:`xml.etree._Element`
        """
        logger.info("<command> is loaded during initiation of the object.")

    def _load_help(self, tool, help_root):
        """
        Load the content of the <help> into the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param requirements_root: root of <help> tag.
        :type requirements_root: :class:`xml.etree._Element`
        """
        tool.help = help_root.text

    def _load_requirements(self, tool, requirements_root):
        """
        Add <requirements> to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param requirements_root: root of <requirements> tag.
        :type requirements_root: :class:`xml.etree._Element`
        """
        tool.requirements = gxtp.Requirements()
        for req in requirements_root:
            req_type = req.attrib["type"]
            value = req.text
            if req.tag == "requirement":
                version = req.attrib.get("version", None)
                tool.requirements.append(gxtp.Requirement(req_type, value, version=version))
            elif req.tag == "container":
                tool.requirements.append(gxtp.Container(req_type, value))
            else:
                logger.warning(req.tag + " is not a valid tag for requirements child")

    def _load_edam_topics(self, tool, topics_root):
        """
        Add <edam_topics> to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param topics_root: root of <edam_topics> tag.
        :type topics_root: :class:`xml.etree._Element`
        """
        tool.edam_topics = gxtp.EdamTopics()
        for edam_topic in topics_root:
            tool.edam_topics.append(gxtp.EdamTopic(edam_topic.text))

    def _load_edam_operations(self, tool, operations_root):
        """
        Add <edam_operations> to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param operations_root: root of <edam_operations> tag.
        :type operations_root: :class:`xml.etree._Element`
        """
        tool.edam_operations = gxtp.EdamOperations()
        for edam_op in operations_root:
            tool.edam_operations.append(gxtp.EdamOperation(edam_op.text))

    def _load_configfiles(self, tool, configfiles_root):
        """
        Add <configfiles> to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param configfiles_root: root of <configfiles> tag.
        :type configfiles_root: :class:`xml.etree._Element`
        """
        tool.configfiles = gxtp.Configfiles()
        for conf in configfiles_root:
            name = conf.attrib["name"]
            value = conf.text
            tool.configfiles.append(gxtp.Configfile(name, value))

    def _load_citations(self, tool, citations_root):
        """
        Add <citations> to the tool.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param citations_root: root of <citations> tag.
        :type citations_root: :class:`xml.etree._Element`
        """
        tool.citations = gxtp.Citations()
        for cit in citations_root:
            cit_type = cit.attrib["type"]
            value = cit.text
            tool.citations.append(gxtp.Citation(cit_type, value))

    def _load_inputs(self, tool, inputs_root):
        """
        Add <inputs> to the tool using the :class:`galaxyxml.tool.import_xml.InputsParser` object.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param inputs_root: root of <inputs> tag.
        :type inputs_root: :class:`xml.etree._Element`
        """
        tool.inputs = gxtp.Inputs()
        inp_parser = InputsParser()
        inp_parser.load_inputs(tool.inputs, inputs_root)

    def _load_outputs(self, tool, outputs_root):
        """
        Add <outputs> to the tool using the :class:`galaxyxml.tool.import_xml.OutputsParser` object.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param outputs_root: root of <outputs> tag.
        :type outputs_root: :class:`xml.etree._Element`
        """
        tool.outputs = gxtp.Outputs()
        out_parser = OutputsParser()
        out_parser.load_outputs(tool.outputs, outputs_root)

    def _load_tests(self, tool, tests_root):
        """
        Add <tests> to the tool using the :class:`galaxyxml.tool.import_xml.TestsParser` object.

        :param tool: Tool object from galaxyxml.
        :type tool: :class:`galaxyxml.tool.Tool`
        :param tests_root: root of <tests> tag.
        :type tests_root: :class:`xml.etree._Element`
        """
        tool.tests = gxtp.Tests()
        tests_parser = TestsParser()
        tests_parser.load_tests(tool.tests, tests_root)

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
                getattr(self, "_load_{}".format(child.tag))(tool, child)
            except AttributeError:
                logger.warning(child.tag + " tag is not processed.")
        return tool


class InputsParser(object):
    """
    Class to parse content of the <inputs> tag from a Galaxy XML wrapper.
    """

    def _load_text_param(self, root, text_param):
        """
        Add <param type="text" /> to the root.

        :param root: root to append the param to.
        :param text_param: root of <param> tag.
        :type text_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.TextParam(
                text_param.attrib["name"],
                optional=text_param.get("optional", None),
                label=text_param.get("label", None),
                help=text_param.get("help", None),
                value=text_param.get("value", None),
            )
        )

    def _load_data_param(self, root, data_param):
        """
        Add <param type="data" /> to the root.

        :param root: root to append the param to.
        :param data_param: root of <param> tag.
        :type data_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.DataParam(
                data_param.attrib["name"],
                optional=data_param.attrib.get("optional", None),
                label=data_param.attrib.get("label", None),
                help=data_param.attrib.get("help", None),
                format=data_param.attrib.get("format", None),
                multiple=data_param.attrib.get("multiple", None),
            )
        )

    def _load_boolean_param(self, root, bool_param):
        """
        Add <param type="boolean" /> to the root.

        :param root: root to append the param to.
        :param bool_param: root of <param> tag.
        :type bool_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.BooleanParam(
                bool_param.attrib["name"],
                optional=bool_param.attrib.get("optional", None),
                label=bool_param.attrib.get("label", None),
                help=bool_param.attrib.get("help", None),
                checked=bool_param.attrib.get("checked", False),
                truevalue=bool_param.attrib.get("truevalue", None),
                falsevalue=bool_param.attrib.get("falsevalue", None),
            )
        )

    def _load_integer_param(self, root, int_param):
        """
        Add <param type="integer" /> to the root.

        :param root: root to append the param to.
        :param int_param: root of <param> tag.
        :type int_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.IntegerParam(
                int_param.attrib["name"],
                int_param.attrib.get("value", None),
                optional=int_param.attrib.get("optional", None),
                label=int_param.attrib.get("label", None),
                help=int_param.attrib.get("help", None),
                min=int_param.attrib.get("min", None),
                max=int_param.attrib.get("max", None),
            )
        )

    def _load_float_param(self, root, float_param):
        """
        Add <param type="float" /> to the root.

        :param root: root to append the param to.
        :param float_param: root of <param> tag.
        :type float_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.FloatParam(
                float_param.attrib["name"],
                float_param.attrib.get("value", None),
                optional=float_param.attrib.get("optional", None),
                label=float_param.attrib.get("label", None),
                help=float_param.attrib.get("help", None),
                min=float_param.attrib.get("min", None),
                max=float_param.attrib.get("max", None),
            )
        )

    def _load_option_select(self, root, option):
        """
        Add <option> to the root (usually <param type="select" />).

        :param root: root to append the param to.
        :param option: root of <option> tag.
        :type float_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.SelectOption(
                option.attrib.get("value", None), option.text, selected=option.attrib.get("selected", False)
            )
        )

    def _load_column_options(self, root, column):
        """
        Add <column> to the root (usually <options>).

        :param root: root to append the param to.
        :param option: root of <column> tag.
        :type float_param: :class:`xml.etree._Element`
        """
        root.append(gxtp.Column(column.attrib["name"], column.attrib["index"]))

    def _load_filter_options(self, root, filter):
        """
        Add <filter> to the root (usually <options>).

        :param root: root to append the param to.
        :param option: root of <filter> tag.
        :type float_param: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.Filter(
                filter.attrib["type"],
                column=filter.attrib.get("column", None),
                name=filter.attrib.get("name", None),
                ref=filter.attrib.get("ref", None),
                key=filter.attrib.get("key", None),
                multiple=filter.attrib.get("multiple", None),
                separator=filter.attrib.get("separator", None),
                keep=filter.attrib.get("keep", None),
                value=filter.attrib.get("value", None),
                ref_attribute=filter.attrib.get("ref_attribute", None),
                index=filter.attrib.get("index", None),
            )
        )

    def _load_options_select(self, root, options):
        """
        Add <options> to the root (usually <param type="select" />).

        :param root: root to append the param to.
        :param option: root of <options> tag.
        :type float_param: :class:`xml.etree._Element`
        """
        opts = gxtp.Options(
            from_dataset=options.attrib.get("from_dataset", None),
            from_file=options.attrib.get("from_file", None),
            from_data_table=options.attrib.get("from_data_table", None),
            from_parameter=options.attrib.get("from_parameter", None),
        )
        # Deal with child nodes (usually filter and column)
        for opt_child in options:
            try:
                getattr(self, "_load_{}_options".format(opt_child.tag))(opts, opt_child)
            except AttributeError:
                logger.warning(opt_child.tag + " tag is not processed for <options>.")
        root.append(opts)

    def _load_select_param(self, root, sel_param):
        """
        Add <param type="select" /> to the root.

        :param root: root to append the param to.
        :param sel_param: root of <param> tag.
        :type sel_param: :class:`xml.etree._Element`
        """
        select_param = gxtp.SelectParam(
            sel_param.attrib["name"],
            optional=sel_param.attrib.get("optional", None),
            label=sel_param.attrib.get("label", None),
            help=sel_param.attrib.get("help", None),
            data_ref=sel_param.attrib.get("data_ref", None),
            display=sel_param.attrib.get("display", None),
            multiple=sel_param.attrib.get("multiple", None),
        )
        # Deal with child nodes (usually option and options)
        for sel_child in sel_param:
            try:
                getattr(self, "_load_{}_select".format(sel_child.tag))(select_param, sel_child)
            except AttributeError:
                logger.warning(sel_child.tag + " tag is not processed for <param type='select'>.")
        root.append(select_param)

    def _load_param(self, root, param_root):
        """
        Method to select which type of <param> is being added to the root.

        :param root: root to attach param to.
        :param param_root: root of <param> tag.
        :type param_root: :class:`xml.etree._Element`
        """
        param_type = param_root.attrib["type"]
        try:
            getattr(self, "_load_{}_param".format(param_type))(root, param_root)
        except AttributeError:
            logger.warning(param_type + " tag is not processed for <param>.")

    def _load_when(self, root, when_root):
        """
        Add <when> to the root (usually <conditional>).

        :param root: root to append when to.
        :param when_root: root of <when> tag.
        :type when_root: :class:`xml.etree._Element`
        """
        when = gxtp.When(when_root.attrib["value"])
        # Deal with child nodes
        self.load_inputs(when, when_root)
        root.append(when)

    def _load_conditional(self, root, conditional_root):
        """
        Add <conditional> to the root.

        :param root: root to append conditional to.
        :param conditional_root: root of <conditional> tag.
        :type conditional_root: :class:`xml.etree._Element`
        """
        value_ref_in_group = conditional_root.attrib.get("value_ref_in_group", None)
        # Other optional parameters need to be added to conditional object
        conditional = gxtp.Conditional(
            conditional_root.attrib["name"],
            value_from=conditional_root.attrib.get("value_from", None),
            value_ref=conditional_root.attrib.get("value_ref", None),
            value_ref_in_group=value_ref_in_group,
            label=conditional_root.attrib.get("label", None),
        )
        # Deal with child nodes
        self.load_inputs(conditional, conditional_root)
        root.append(conditional)

    def _load_section(self, root, section_root):
        """
        Add <section> to the root.

        :param root: root to append conditional to.
        :param section_root: root of <section> tag.
        :type section_root: :class:`xml.etree._Element`
        """
        section = gxtp.Section(
            section_root.attrib["name"],
            section_root.attrib["title"],
            expanded=section_root.attrib.get("expanded", None),
            help=section_root.attrib.get("help", None),
        )
        # Deal with child nodes
        self.load_inputs(section, section_root)
        root.append(section)

    def _load_repeat(self, root, repeat_root):
        """
        Add <repeat> to the root.

        :param root: root to append repeat to.
        :param repeat_root: root of <repeat> tag.
        :param repeat_root: :class:`xml.etree._Element`
        """
        repeat = gxtp.Repeat(
            repeat_root.attrib["name"],
            repeat_root.attrib["title"],
            min=repeat_root.attrib.get("min", None),
            max=repeat_root.attrib.get("max", None),
            default=repeat_root.attrib.get("default", None),
        )
        # Deal with child nodes
        self.load_inputs(repeat, repeat_root)
        root.append(repeat)

    def load_inputs(self, root, inputs_root):
        """
        Add <inputs.tag> to the root (it can be any tags with children such as
        <inputs>, <repeat>, <section> ...)

        :param root: root to attach inputs to (either <inputs> or <when>).
        :param inputs_root: root of <inputs> tag.
        :type inputs_root: :class:`xml.etree._Element`
        """
        for inp_child in inputs_root:
            try:
                getattr(self, "_load_{}".format(inp_child.tag))(root, inp_child)
            except AttributeError:
                logger.warning(inp_child.tag + " tag is not processed for <" + inputs_root.tag + "> tag.")


class OutputsParser(object):
    """
    Class to parse content of the <outputs> tag from a Galaxy XML wrapper.
    """

    def _load_data(self, outputs_root, data_root):
        """
        Add <data> to <outputs>.

        :param outputs_root: <outputs> root to append <data> to.
        :param data_root: root of <data> tag.
        :param data_root: :class:`xml.etree._Element`
        """
        data = gxtp.OutputData(
            data_root.attrib.get("name", None),
            data_root.attrib.get("format", None),
            format_source=data_root.attrib.get("format_source", None),
            metadata_source=data_root.attrib.get("metadata_source", None),
            label=data_root.attrib.get("label", None),
            from_work_dir=data_root.attrib.get("from_work_dir", None),
            hidden=data_root.attrib.get("hidden", False),
        )
        # Deal with child nodes
        for data_child in data_root:
            try:
                getattr(self, "_load_{}".format(data_child.tag))(data, data_child)
            except AttributeError:
                logger.warning(data_child.tag + " tag is not processed for <data>.")
        outputs_root.append(data)

    def _load_change_format(self, root, chfmt_root):
        """
        Add <change_format> to root (<data>).

        :param root: root to append <change_format> to.
        :param chfm_root: root of <change_format> tag.
        :param chfm_root: :class:`xml.etree._Element`
        """
        change_format = gxtp.ChangeFormat()
        for chfmt_child in chfmt_root:
            change_format.append(
                gxtp.ChangeFormatWhen(
                    chfmt_child.attrib["input"], chfmt_child.attrib["format"], chfmt_child.attrib["value"]
                )
            )
        root.append(change_format)

    def _load_collection(self, outputs_root, coll_root):
        """
        Add <collection> to <outputs>.

        :param outputs_root: <outputs> root to append <collection> to.
        :param coll_root: root of <collection> tag.
        :param coll_root: :class:`xml.etree._Element`
        """
        collection = gxtp.OutputCollection(
            coll_root.attrib["name"],
            type=coll_root.attrib.get("type", None),
            label=coll_root.attrib.get("label", None),
            format_source=coll_root.attrib.get("format_source", None),
            type_source=coll_root.attrib.get("type_source", None),
            structured_like=coll_root.attrib.get("structured_like", None),
            inherit_format=coll_root.attrib.get("inherit_format", None),
        )
        # Deal with child nodes
        for coll_child in coll_root:
            try:
                getattr(self, "_load_{}".format(coll_child.tag))(collection, coll_child)
            except AttributeError:
                logger.warning(coll_child.tag + " tag is not processed for <collection>.")
        outputs_root.append(collection)

    def _load_discover_datasets(self, root, disc_root):
        """
        Add <discover_datasets> to root (<collection>).

        :param root: root to append <collection> to.
        :param disc_root: root of <discover_datasets> tag.
        :param disc_root: :class:`xml.etree._Element`
        """
        root.append(
            gxtp.DiscoverDatasets(
                disc_root.attrib["pattern"],
                directory=disc_root.attrib.get("directory", None),
                format=disc_root.attrib.get("format", None),
                ext=disc_root.attrib.get("ext", None),
                visible=disc_root.attrib.get("visible", None),
            )
        )

    def _load_filter(self, root, filter_root):
        """
        Add <filter> to root (<collection> or <data>).

        :param root: root to append <collection> to.
        :param coll_root: root of <filter> tag.
        :param coll_root: :class:`xml.etree._Element`
        """
        root.append(gxtp.OutputFilter(filter_root.text))

    def load_outputs(self, root, outputs_root):
        """
        Add <outputs> to the root.

        :param root: root to attach <outputs> to (<tool>).
        :param tests_root: root of <outputs> tag.
        :type tests_root: :class:`xml.etree._Element`
        """
        for out_child in outputs_root:
            try:
                getattr(self, "_load_{}".format(out_child.tag))(root, out_child)
            except AttributeError:
                logger.warning(out_child.tag + " tag is not processed for <outputs>.")


class TestsParser(object):
    """
    Class to parse content of the <tests> tag from a Galaxy XML wrapper.
    """

    def _load_param(self, test_root, param_root):
        """
        Add <param> to the <test>.

        :param root: <test> root to append <param> to.
        :param repeat_root: root of <param> tag.
        :param repeat_root: :class:`xml.etree._Element`
        """
        test_root.append(
            gxtp.TestParam(
                param_root.attrib["name"],
                value=param_root.attrib.get("value", None),
                ftype=param_root.attrib.get("ftype", None),
                dbkey=param_root.attrib.get("dbkey", None),
            )
        )

    def _load_output(self, test_root, output_root):
        """
        Add <output> to the <test>.

        :param root: <test> root to append <output> to.
        :param repeat_root: root of <output> tag.
        :param repeat_root: :class:`xml.etree._Element`
        """
        test_root.append(
            gxtp.TestOutput(
                name=output_root.attrib.get("name", None),
                file=output_root.attrib.get("file", None),
                ftype=output_root.attrib.get("ftype", None),
                sort=output_root.attrib.get("sort", None),
                value=output_root.attrib.get("value", None),
                md5=output_root.attrib.get("md5", None),
                checksum=output_root.attrib.get("checksum", None),
                compare=output_root.attrib.get("compare", None),
                lines_diff=output_root.attrib.get("lines_diff", None),
                delta=output_root.attrib.get("delta", None),
            )
        )

    def load_tests(self, root, tests_root):
        """
        Add <tests> to the root.

        :param root: root to attach <tests> to (<tool>).
        :param tests_root: root of <tests> tag.
        :type tests_root: :class:`xml.etree._Element`
        """
        for test_root in tests_root:
            test = gxtp.Test()
            for test_child in test_root:
                try:
                    getattr(self, "_load_{}".format(test_child.tag))(test, test_child)
                except AttributeError:
                    logger.warning(test_child.tag + " tag is not processed within <test>.")
            root.append(test)
