#!/usr/bin/env python
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

tool = gxt.Tool(name="aragorn", version="1.2.36", description="tRNA finder",
                executable="aragorn")

inputs = gxtp.Inputs()
outputs = gxtp.Outputs()

# A parameter
param = gxtp.BooleanParam('flag', label='Flag label', help='Flag help')
# Yes I know this is rubbish. Please make a PR!!
param.num_dashes = 1
param.space_between_arg = ' '
inputs.append(param)


# A float
param = gxtp.FloatParam('float', label='Float label',
                        help='Float help', value=0)
param.num_dashes = 1
param.space_between_arg = ' '
inputs.append(param)


param_min = gxtp.IntegerParam('int_min',
                              label='int_min label',
                              help='int_min help', value=0)
param_max = gxtp.IntegerParam('int_max',
                              label='int_max label',
                              help='int_max help', value=0)
param_min.command_line_override = '-i$int_min,$int_max'
param_max.command_line_override = ''
param_min.num_dashes = 1
param_max.num_dashes = 1
param_min.space_between_arg = ' '
param_max.space_between_arg = ' '
inputs.append(param_min)
inputs.append(param_max)


# Outputs
param = gxtp.OutputParameter('output', format="tabular")
param.num_dashes = 1
param.space_between_arg = ' '
outputs.append(param)

tool.inputs = inputs
tool.outputs = outputs
tool.help = 'HI'

data = tool.export()

with open('tool.xml', 'w') as handle:
    handle.write(data)
