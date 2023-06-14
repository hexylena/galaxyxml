#!/usr/bin/env python
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

# examplify the use of MacrosTool

tool = gxt.MacrosTool(
    name="aragorn",
    id="aragorn",
    version="1.2.36",
    description="Aragorn is a tRNA finder",
    executable="aragorn.exe",
    version_command="aragorn.exe --version",
)

inputs = tool.inputs
outputs = tool.outputs

# Add requirements
requirements = gxtp.Requirements()
requirements.append(gxtp.Requirement("package", "samtools", version="1.0.0"))
requirements.append(gxtp.Container("docker", "one_super_image"))
tool.requirements = requirements

# A parameter
param = gxtp.BooleanParam("flag", label="Flag label", help="Flag help", num_dashes=1)
# Yes I know this is rubbish. Please make a PR!!
param.space_between_arg = " "
inputs.append(param)


# A float in a section
section = gxtp.Section("float_section", "Float section")
param = gxtp.FloatParam(
    "float", label="Float label", help="Float help", value=0, num_dashes=1
)
param.space_between_arg = " "
section.append(param)
inputs.append(section)

# A conditional
param = gxtp.Conditional("cond", label="Conditional")
param.append(gxtp.SelectParam("Select", options={"hi": "1", "bye": "2"}))
when_a = gxtp.When(value="hi")
when_b = gxtp.When(value="bye")
when_b.append(
    gxtp.IntegerParam("some_int", value=0, num_dashes=1, label="Advanced value")
)
param.append(when_a)
param.append(when_b)
inputs.append(param)

# Integer parameters
param_min = gxtp.IntegerParam(
    "int_min", label="int_min label", help="int_min help", value=0, num_dashes=1
)
param_max = gxtp.IntegerParam(
    "int_max", label="int_max label", help="int_max help", value=0, num_dashes=1
)

posint = gxtp.IntegerParam(
    "posint",
    label="posint label",
    positional=True,
    help="posinthelp",
    value=0,
    num_dashes=2,
)

param_min.command_line_override = "-i$int_min,$int_max"
param_max.command_line_override = ""
param_min.space_between_arg = " "
param_max.space_between_arg = " "
inputs.append(param_min)
inputs.append(param_max)
inputs.append(posint)

# Add Select with options from_file with columns and filter
param = gxtp.SelectParam("select_local")
options = gxtp.Options(from_file="loc_file.loc")
column_a = gxtp.Column("name", 0)
options.append(column_a)
column_b = gxtp.Column("value", 1)
options.append(column_b)
filter_a = gxtp.Filter("sort_by", name="sorted", column="1")
options.append(filter_a)
param.append(options)
inputs.append(param)

# Configfiles
configfiles = gxtp.Configfiles()
configfiles.append(gxtp.Configfile(name="testing", text="Hello <> World"))
configfiles.append(gxtp.ConfigfileDefaultInputs(name="inputs"))

# Outputs
param = gxtp.OutputData("output", format="tabular", num_dashes=1)
param.space_between_arg = " "
outputs.append(param)
# Collection
collection = gxtp.OutputCollection("supercollection", label="a small label")
discover = gxtp.DiscoverDatasets(
    r"(?P&lt;designation&gt;.+)\.pdf.fasta", format="fasta"
)
collection.append(discover)
outputs.append(collection)

tool.inputs = inputs
tool.outputs = outputs
tool.help = "HI"
tool.configfiles = configfiles

# Add Tests sections
tool.tests = gxtp.Tests()
test_a = gxtp.Test()
param = gxtp.TestParam("float", value=5.4)
test_a.append(param)
test_out = gxtp.TestOutput(name="output", value="file.out")
test_a.append(test_out)
tool.tests.append(test_a)


# Add comment to the wrapper
tool.add_comment("This tool descriptor has been generated using galaxyxml.")

print(tool.export())
