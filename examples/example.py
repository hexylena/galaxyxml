#!/usr/bin/env python
from __future__ import print_function
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

tool = gxt.Tool("aragorn", 'se.lu.mbioekol.mbio-serv2.aragorn',
    "1.2.36", "Aragorn is a tRNA finder", "aragorn.exe", version_command="aragorn.exe --version")

inputs = gxtp.Inputs()
outputs = gxtp.Outputs()

# A parameter
param = gxtp.BooleanParam('flag', label='Flag label', help='Flag help', num_dashes=1)
# Yes I know this is rubbish. Please make a PR!!
param.space_between_arg = ' '
inputs.append(param)


# A float
param = gxtp.FloatParam('float', label='Float label',
                        help='Float help', value=0, num_dashes=1)
param.space_between_arg = ' '
inputs.append(param)

# A conditional
param = gxtp.Conditional('cond', label='Conditional')
param.append(gxtp.SelectParam('Select', options={'hi': '1', 'bye': '2'}))
when_a = gxtp.When(value='hi')
when_b = gxtp.When(value='bye')
when_b.append(gxtp.IntegerParam('some_int', value=0, num_dashes=1, label="Advanced value"))
param.append(when_a)
param.append(when_b)
inputs.append(param)

# Integer parameters
param_min = gxtp.IntegerParam('int_min',
                              label='int_min label',
                              help='int_min help', value=0, num_dashes=1)
param_max = gxtp.IntegerParam('int_max',
                              label='int_max label',
                              help='int_max help', value=0, num_dashes=1)

posint = gxtp.IntegerParam('posint', label='posint label', positional=True,
                           help='posinthelp', value=0, num_dashes=2)

param_min.command_line_override = '-i$int_min,$int_max'
param_max.command_line_override = ''
param_min.space_between_arg = ' '
param_max.space_between_arg = ' '
inputs.append(param_min)
inputs.append(param_max)
inputs.append(posint)

# Add Select with options from_file with columns and filter
param = gxtp.SelectParam('select_local')
options = gxtp.Options(from_file='loc_file.loc')
column_a = gxtp.Column('name', 0)
options.append(column_a)
column_b = gxtp.Column('value', 1)
options.append(column_b)
filter_a = gxtp.Filter('sort_by', name='sorted', column='1')
options.append(filter_a)
param.append(options)
inputs.append(param)

# Configfiles
configfiles = gxtp.Configfiles()
configfiles.append(gxtp.Configfile(
    name="testing",
    text="Hello <> World"
))
configfiles.append(gxtp.ConfigfileDefaultInputs(name="inputs"))

# Outputs
param = gxtp.OutputParameter('output', format="tabular", num_dashes=1)
param.space_between_arg = ' '
outputs.append(param)

tool.inputs = inputs
tool.outputs = outputs
tool.help = 'HI'
tool.configfiles = configfiles

tool.add_comment("This tool descriptor has been generated using galaxyxml.")

print(tool.export().decode('utf-8'))

