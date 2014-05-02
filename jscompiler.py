#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 
# JSCompiler (c) Prince Cuberdon 2011 and Later <princecuberdon@bandcochon.fr>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# * The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
# * The Software is provided "as is", without warranty of any kind, express or
#   implied, including but not limited to the warranties of merchantability,
#   fitness for a particular purpose and noninfringement. In no event shall the
#   authors or copyright holders be liable for any claim, damages or other liability,
#   whether in an action of contract, tort or otherwise, arising from, out of or in
#   connection with the software or the use or other dealings in the Software.

import argparse
import sys
import re
import os
from cStringIO import StringIO

__version__ = '0.1'
__author__ = "Prince Cuberdon"
__licence__ = "MIT"


def open_file(path):
    """
    Shortcut for opening a file
    Returns the file content
    """
    return open(path, 'r').read()


def replace_strings(content):
    """
    Replace all strings with our to avoid possible conflict.
    """
    find_all = re.findall(r''''.*?'|".*?"''', content)
    count = 0
    for stri in find_all:
        content = content.replace(stri, '__{%d}__' % count)
        count += 1
        
    return content, find_all


def put_strings(content, string_list):
    """ Put the stored strings
    """
    count = 0
    for s in string_list:
        content = content.replace('__{%d}__' % count, s)
        count += 1
    return content


def strip_empty_lines(content):
    """ Remove empty lines
    """
    io = StringIO(content)
    content = ''
    for line in io:
        line = line.strip()
        if len(line) == 0:
            continue
        content += line + '\n'
    return content


def strip_comments(content):
    """ Remove C and C++ comments.
    """
    # take_care = re.findall(r"""(['|"].*?//.*?['|"])""", content)
    # count = 0
    # for str_to_takecare in take_care:
    #     content = re.sub(str_to_takecare, '__{%d}__' % count, content)
    #     count += 1
        
    # I can't find how to replace C like comment in a single pass
    for found in re.findall(r'//.*?\n|/\*.*?\*/', content, re.DOTALL):
        content = content.replace(found, "")
    return content

    content = re.sub(r'/\*.*?\*/', '', content, re.DOTALL)
    
    for comment in re.findall(r'/\*.*\*/', content, re.DOTALL):
        content = content.replace(comment, '')
        
    # content = re.sub(r'//.*?\n', '', content)
    # for str_to_takecare in range(len(take_care)):
    #     content = re.sub(r'__{(%d)}__' % str_to_takecare,
    #                      take_care[str_to_takecare], content)
    #
    return content


def remove_semi_colon(content):
    """ Remove semicolon at the end of the line if the line is empty and double semicolon
    """
    # remove double semi-colon
    while content.find(';;') > -1:
        content = re.sub(r";;", ";", content)
    return content

def remove_eol(content):
    """ Remove the end of line
    """
    return re.sub(r'\r|\r\n|\n', '', content)


def remove_unneeded_semi_colon(content):
    """
    Remove semicolon if it is before a bracket
    """
    return re.sub(r';}', '}', content)


def remove_double_space_or_tabs(content):
    """
    Remove identation
    """
    while re.search(r'\t|\s\s', content):
        content = re.sub(r'\t|\s\s', ' ', content)
    return content


def remove_unneeded_spaces(content):
    """
    Remove uneeded space. In JS var a = 1; is equal to var a=1;
    """
    content = re.sub(r'\s+=\s+', '=', content)
    content = re.sub(r'\s+==\s+', '==', content)
    content = re.sub(r'\s+===\s+', '===', content)
    content = re.sub(r'\s+!=\s+', '!=', content)
    content = re.sub(r'\s+!==\s+', '!==', content)
    content = re.sub(r'\s+>=\s+', '>=', content)
    content = re.sub(r'\s+>==\s+', '>==', content)
    content = re.sub(r'\s+<=\s+', '<=', content)
    content = re.sub(r'\s+<==\s+', '<==', content)
    content = re.sub(r'\s}|\s}\s|}\s', '}', content)    
    content = re.sub(r'\s{|\s{\s|{\s', '{', content)
    content = re.sub(r'\s\(|\s\(\s|\(\s', '(', content)
    content = re.sub(r'\s\)|\s\)\s|\)\s', ')', content)
    content = re.sub(r':\s+|\s+:|\s+:\s+', ':', content)
    
    return content


def remove_trailing_slashes(content):
    """
    Remove \ at the end of a string
    """
    return re.sub(r'\\\n|\\\n\s+|\\\s+\n', '', content)


def get_javascript_files(path):
    """ Get all javascript files in the given path
    Returns a list of string
    """
    _files = []
    if not os.path.exists(path):
        raise Exception(path + " don't exists")

    for a_file in os.listdir(path):
        a_file = os.path.join(path, a_file)
        name, ext = os.path.splitext(a_file)
        if os.path.isdir(a_file):
            _files += get_javascript_files(a_file)
            continue
        elif ext.lower() != '.js':
            continue
        _files.append(a_file)
        
    return _files


def verbose(msg):
    """
    Display processing information if the verbose option is set
    """
    if args.verbose:
        sys.stderr.write('%s\n' % msg)
        

def process_files(file_list):
    """
    Process all the files
    returns a tuple: the size before and the compiled content
    """
    _size_before = 0
    _output = ''
    
    for _file in file_list:
        content = ''
        try:
            verbose('Open %s file' % _file)
            content += open_file(_file)
            _size_before += len(content)
            
            if not args.merge:
                verbose('Substitute strings to avoid conflict')
                content, string_list = replace_strings(content)

                verbose("Strip comments")
                content = strip_comments(content)

                verbose("Strip empty lines")
                content = strip_empty_lines(content)

                verbose('remove unuseful semi colon')
                content = remove_semi_colon(content)

                verbose('Remove trailing slashes for multi line strings')
                content = remove_trailing_slashes(content)
                
                verbose('Remove End Of Line')
                content = remove_eol(content)
                
                verbose('remove unneeded semi colon')
                content = remove_unneeded_semi_colon(content)
                
                verbose('Remove double space or tabs')
                content = remove_double_space_or_tabs(content)
                
                verbose('Finalize to remove uneeded double spaces')
                content = remove_unneeded_spaces(content)
                
                verbose('Restore strings')
                content = put_strings(content, string_list)
            
            verbose('Merging files')
            _output += content + '\n'
            verbose('Done')
        except IOError as e:
            sys.stderr.write("%s\n" % e)
    return size_before, _output


def write_colored(status, string):
    """
    Write the command line with colors
    """
    attr = ['1', ]
    if not status:
        attr.append('31')  # Green
    else:
        attr.append('32')  # red
    sys.stdout.write('\x1b[%sm%s\x1b[0m' % (';'.join(attr), string))


if __name__ == '__main__':
    # The file is executed within a terminal
    size_after = 0
    
    # Create arguments parser
    parser = argparse.ArgumentParser(description="Compile Javascript files",
                                     epilog="""Caution: Javascript syntax is not checked""")
    parser.add_argument('--input', '-i', type=str, dest="input", metavar="COMMA_SEPARATED_FILES",
                        help="Set the input file. For more than one file, separate them with a comma (eg: file1,file2)")
    parser.add_argument('--output', '-o', type=str, dest='output', metavar="OUTPUTFILE",
                        help="Set the output file. It will override the existing one without warnings")
    parser.add_argument('--directory', '-d', type=str, dest="directory",
                        help="Explore the directory")
    parser.add_argument('--recursive', '-r', const=True, action="store_const", default=False,
                        help="Explore the directory recurcivly")
    parser.add_argument('--show-infos', '-s', const=True, action="store_const", default=False,
                        help="Display informations about compilation on stderr")
    parser.add_argument('--join', '-j', const=True, action='store_const', default=False,
                        help="Simply join files")
    parser.add_argument('--makefile', '-f', type=str, dest='makefile', metavar="JSCOMPILER_MAKEFILE",
                        help="Use the makefile instead the command line")
    parser.add_argument('--verbose', '-v', const=True, action="store_const", default=False,
                        help="Be as verbose as possible")
    parser.add_argument('--merge', '-m', const=True, action="store_const", default=False,
                        help="Simply merge files without compiling (useful for minimified libraries)")
    
    # Parse arguments
    global args
    args = parser.parse_args()

    if len(sys.argv) == 1:
        sys.exit("You might at least give an argument")

    if args.directory and args.input:
        sys.exit('--directory and --input exclude one each other')

    # Use makefile ?
    if args.makefile:
        # Yes. Try to understand makefile
        make = eval(open(args.makefile, "r").read())
        for key in make:
            if not 'action' in make[key]:
                make[key]['action'] = 'merge'  # Default
            if not 'files' in make[key]:
                sys.exit("Error : '%s' have no files defined. What can I do with that !" % key)
            if not 'outputdirectory' in make[key]:
                make[key]['outputdirectory'] = os.path.abspath('./')
        
        for key in make:
            output_name = os.path.join(make[key]['outputdirectory'], '%s.js' % key)
            output = ''
            error = False
            for f in make[key]['files']:
                print "Processing: %s" % f
                if make[key]['action'] == 'merge':
                    try:
                        output += open(f, 'r').read()
                    except IOError:
                        write_colored(False, "File not found: %s\n" % f)
                        error = True
                elif make[key]['action'] == 'compile':
                    size, o = process_files([f, ])
                    output += o
                else:
                    sys.exit('Unknow action : %s' % make[key]['action'])

            if not error:
                write_colored(True, "Generating: %s\n" % output_name)
                print
                open(output_name, 'w').write(output)
            else:
                write_colored(False, "Fail to compile %s\n" % output_name)
    else:
        # No. Use command line for options
        files = []
        if args.input:
            files = args.input.split(',')
        elif args.directory:
            files = get_javascript_files(args.directory)
         
        size_before, output = process_files(files)   

        if args.output:
            open(args.output, "w").write(output)
        else:
            sys.stdout.write(output)
            print
    
        if args.show_infos:
            sys.stderr.write("Before : %d\n" % size_before)
            print "After : ", size_after
            gain = (1.0 - (float(size_after) / float(size_before))) * 100
            print "Gain : %.2f %%" % gain
