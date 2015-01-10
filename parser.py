import re

def start_pattern(string):
    return string.startswith('    -')


CLI = {
    'OUTPUT': (re.compile(r'^\s*(?P<dash>--?)(?P<name>[A-Za-z0-9]+)(?P<space_between_arg>[ ]*)<(?P<args>out[^>]*)>\s+(?P<content>.*)'), {'nargs': 1}),
    'FLAG': (re.compile(r'^\s*(?P<dash>--?)(?P<name>[A-Za-z0-9]+)[ ]{2,}(?P<content>.*)'), {'nargs': 0}),
    'PARAM': (re.compile(r'^\s*(?P<dash>--?)(?P<name>[A-Za-z0-9]+)(?P<space_between_arg>[ ]*)<(?P<args>[^>]*)>\s+(?P<content>.*)'), {'nargs': 1}),
    'PARAM_RANGE': (re.compile(r'^\s*(?P<dash>--?)(?P<name>[A-Za-z0-9]+)(?P<space_between_arg>[ ]*)<(?P<args>[^>]*)>,<(?P<args2>[^>]*)>\s+(?P<content>.*)'), {'nargs': 2}),
}

CLI_GROUPS = ('name', 'args', 'content', 'args2', 'dash', 'space_between_arg')
CLI_DEFAULTS = {
    'space_between_arg': ' '
}

def detect_args(cli):
    for matcher in CLI:
        matches = CLI[matcher][0].search(cli)
        if matches:
            hit = CLI[matcher][1]
            hit['type'] = matcher

            # Apply defaults. Poorly organised.
            for default in CLI_DEFAULTS:
                hit[default] = CLI_DEFAULTS[default]

            # Actual groups in regex
            for group in CLI_GROUPS:
                try:
                    hit[group] = matches.group(group)
                except IndexError:
                    # Ignore missing groups
                    pass
            return hit
    return None

def reflow_block(block):
    single = ' '.join([x.strip() for x in block])
    return detect_args(single)

def blocks(iterable):
    accumulator = []
    for line in iterable:
        if start_pattern(line):
            if accumulator:
                yield reflow_block(accumulator)
                accumulator = [line]
        else:
            accumulator.append(line)
    if accumulator:
        yield reflow_block(accumulator)

import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp

tool = gxt.Tool(name="aragorn", version="1.2.36", description="tRNA finder",
                executable="aragorn")
inputs = gxtp.Inputs()
outputs = gxtp.Outputs()
for line in blocks(open('tmp','r').readlines()):
    if line and line['type'] == 'FLAG':
        param = gxtp.BooleanParam(line['name'], label=line['name'], help=line['content'],
                                 #truevalue=cli_param, falsevalue="")
                                  )
        param.num_dashes = len(line['dash'])
        param.space_between_arg = line['space_between_arg']
        inputs.append(param)
    elif line and line['type'] == 'PARAM':
        print "%(dash)s%(name)s <%(args)s> %(content)s" % line
        answer = raw_input("Is this a FLOAT, INT, or TEXT input? ")
        if 'FLOAT' in answer:
            param = gxtp.FloatParam(line['name'], label=line['name'],
                                    help=line['content'], value=0)
        elif 'INT' in answer:
            param = gxtp.IntegerParam(line['name'], label=line['name'],
                                      help=line['content'], value=0)
        elif 'TEXT' in answer:
            param = gxtp.TextParam(line['name'], label=line['name'],
                                   help=line['content'])
        try:
            param.num_dashes = len(line['dash'])
            param.space_between_arg = line['space_between_arg']
            inputs.append(param)
        except:
            print "Uhoh, bad answer"
        print
    elif line and line['type'] == 'PARAM_RANGE':
        param_min = gxtp.IntegerParam(line['name']+'_min',
                                      label=line['name']+'_min',
                                      help=line['content'], value=0)
        param_max = gxtp.IntegerParam(line['name']+'_max',
                                      label=line['name']+'_max',
                                      help=line['content'], value=0)
        param_min.command_line_override = '-i$i_min,$i_max'
        param_max.command_line_override = ''
        param_min.num_dashes = len(line['dash'])
        param_max.num_dashes = len(line['dash'])
        param_min.space_between_arg = line['space_between_arg']
        param_max.space_between_arg = line['space_between_arg']
        inputs.append(param_min)
        inputs.append(param_max)
    elif line and line['type'] == 'OUTPUT':
        param = gxtp.OutputParameter(line['name'], format="tabular")
        param.num_dashes = len(line['dash'])
        param.space_between_arg = line['space_between_arg']
        outputs.append(param)

tool.inputs = inputs
tool.outputs = outputs
tool.help = 'HI'


data = tool.export()

with open('tool.xml', 'w') as handle:
    handle.write(data)
