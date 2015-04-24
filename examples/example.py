#!/usr/bin/env python
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


# Outputs
param = gxtp.OutputParameter('output', format="tabular", num_dashes=1)
param.space_between_arg = ' '
outputs.append(param)

tool.inputs = inputs
tool.outputs = outputs
tool.help = 'HI'

print tool.export()

