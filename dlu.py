#!/usr/bin/env python3

import sys, os

global dictionary_name, sought_word, display_envs, x_reads, reads, wordmod, standard_page_remap, load_dictionary, open_dictionary

## Parse command line.
def usage():
    print('Usage: dlu (-l | DICTIONARY WORD)', file = sys.stderr)
    sys.exit(1)
f_list = False
i, n = 1, len(sys.argv)
while i < n:
    if sys.argv[i] == '-l':
        if f_list:
            usage()
        f_list = True
    elif sys.argv[i] == '--':
        i += 1
        break
    elif sys.argv[i].startswith('-'):
        usage()
    else:
        break
    i += 1
if f_list:
    if i != len(sys.argv):
        usage()
else:
    if i + 2 != len(sys.argv):
        usage()
    dictionary_name = sys.argv[i]
    sought_word = sys.argv[i + 1]

# Default functions, can be overriden by configurations on call to load_dictionary.
if not f_list:
    display_envs = ['MDS_DISPLAY', 'MIR_DISPLAY', 'WAYLAND_DISPLAY', 'DISPLAY']
    x_reads = [
        (lambda f, p : ['atril', f, '-i', p]),
        (lambda f, p : ['evince', f, '-i', p]),
        (lambda f, p : ['xpdf', f, p]),
    ]
    reads = dict((disp, list(x_reads)) for disp in display_envs)
    reads[None] = [lambda f, p : ['jfbview', '-p', p, '--', f]]
    wordmod = lambda x : x.lower()
    def standard_page_remap(offset, multiple = 1, multiple_offset = 0):
        return lambda p : (0 if p < multiple_offset else p - multiple_offset) // multiple + offset
    def open_dictionary(filename, page):
        disps = [disp for disp in display_envs if disp in os.environ] + [None]
        for command_lambda in reads[disps[0]]:
            command = command_lambda(filename, str(page));
            os.execvp(command[0], command)
        print("%s: could find any viewer to use." % sys.argv[0], file = sys.stderr)
        print("%s:   file to open: %s" % (sys.argv[0], filename), file = sys.stderr)
        print("%s:   page to open: %i" % (sys.argv[0], page), file = sys.stderr)
        sys.exit(1)

## Load configurations, which holds data needed to perform the lookup.
g, l = globals(), dict(locals())
for key in l:
    g[key] = l[key]
# Possible auto-selected configuration scripts,
# earlier ones have precedence, we can only select one.
config_file = None
for file in ('$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc', '$~/.config/%/%rc', '$~/.%rc', '/etc/%rc'):
    # Expand short-hands
    file = file.replace('/', os.sep).replace('%', 'dlu')
    # Expand environment variables
    for arg in ('XDG_CONFIG_HOME', 'HOME'):
        # Environment variables are prefixed with $
        if '$' + arg in file:
            if arg in os.environ:
                # To be sure that do so no treat a $ as a variable prefix
                # incorrectly we replace any $ in the value of the variable
                # with NUL which is not a value pathname character.
                file = file.replace('$' + arg, os.environ[arg].replace('$', '\0'))
            else:
                file = None
                break
    # Proceed if there where no errors.
    if file is not None:
        # With use $~ (instead of ~) for the user's proper home
        # directroy. HOME should be defined, but it could be missing.
        # It could also be set to another directory.
        if file.startswith('$~'):
            import pwd
            # Get the home (also known as initial) directory
            # of the real user, and the rest of the path.
            file = pwd.getpwuid(os.getuid()).pw_dir + file[2:]
        # Now that we are done we can change back any NUL to $:s.
        file = file.replace('\0', '$')
        # If the file we exists,
        if os.path.exists(file):
            # select it,
            config_file = file
            # and stop trying files with lower precedence.
            break
if config_file is not None:
    code = None
    # Read configuration script file.
    with open(config_file, 'rb') as script:
        code = script.read()
    # Decode configurion script file and add a line break
    # at the end to ensure that the last line is empty.
    # If it is not, we will get errors.
    code = code.decode('utf-8', 'strict') + '\n'
    # Compile the configuration script,
    code = compile(code, config_file, 'exec')
    # and run it, with it have the same
    # globals as this module, so that it can
    # not only use want we have defined, but
    # also redefine it for us.
    exec(code, g)
else:
    print('%s: no configuration file found' % sys.argv[0], file = sys.stderr)
    sys.exit(1)

## List available dictionaries.
if f_list:
    for d in list_dictionaries():
        print(d)
    sys.exit(0)

## Perform lookup.
if not load_dictionary(dictionary_name):
    print('%s: dictionary not found: %s' % (sys.argv[0], dictionary_name), file = sys.stderr)
    sys.exit(1)

sought_word = wordmod(sought_word)
filename, lasts, page_remap = get()
lasts = [(i, word) for i, word in enumerate(lasts)]

for i, word in lasts:
    word = wordmod(word)
    if sought_word <= word:
        page = i
        break
else:
    page = lasts[-1][0]

page = page_remap(page)
open_dictionary(filename, page)
