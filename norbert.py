#!/usr/bin/env python
#
#   norbert.py - command line NBT editor
#
#   Copyright (C) 2012 DMBuce <dmbuce@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import optparse
import sys
from nbt import nbt

VERSION = "0.2"
DEFAULT_MAXDEPTH = 5
DEFAULT_PRINTFORMAT = "human"

# errors
GENERAL_ERROR = 1
INVALID_OPTION = 2
TAG_NOT_FOUND = 4
TAG_NOT_IMPLEMENTED = 5
TAG_CONVERSION_ERROR = 6

formatters = {}

tag_types = {
    nbt.TAG_END:        "TAG_End",
    nbt.TAG_BYTE:       "TAG_Byte",
    nbt.TAG_SHORT:      "TAG_Short",
    nbt.TAG_INT:        "TAG_Int",
    nbt.TAG_LONG:       "TAG_Long",
    nbt.TAG_FLOAT:      "TAG_Float",
    nbt.TAG_DOUBLE:     "TAG_Double",
    nbt.TAG_BYTE_ARRAY: "TAG_Byte_Array",
    nbt.TAG_STRING:     "TAG_String",
    nbt.TAG_LIST:       "TAG_List",
    nbt.TAG_COMPOUND:   "TAG_Compound"
}

complex_tag_types = [
    nbt.TAG_BYTE_ARRAY,
    nbt.TAG_LIST,
    nbt.TAG_COMPOUND
]

def main():
    usage = "%prog [option] [tag[=value]]  [tag2[=value2] ... ]"
    desc  = "Edits or displays an NBT formatted file. " \
            "Nested <tag>s can be referenced " \
            "by separating their names with a '.' character. " \
            "List items are referenced by their place in the list. " \
            "For example, \"Inventory.1.id\" refers to the block id of the " \
            "first inventory item in a typical Minecraft player.dat file."
    parser = optparse.OptionParser(version=VERSION, usage=usage,
                                   description=desc)
    parser.add_option("-f", "--input-file",
                      dest="infile",
                      default="level.dat",
                      help="The file to read. Default is level.dat.")
    parser.add_option("-o", "--output-file",
                      dest="outfile",
                      default=None,
                      help="The file to write to. Note: if not provided, " \
                           "any arguments of the form <tag>=<value> " \
                           "won't be written to disk.")
    parser.add_option("-p", "--print-format",
                      dest="format",
                      default=DEFAULT_PRINTFORMAT,
                      help="Format to print output in. " \
                           "Valid values are \"human\", \"nbt-txt\" " \
                           "and \"norbert\". " \
                           "Default is \"" + DEFAULT_PRINTFORMAT + "\".") #TODO: add "nbt", "json"
    parser.add_option("-r", "--recursive",
                      action="store_true",
                      dest="recursive",
                      default=False,
                      help="Print tags recursively.")
    parser.add_option("-d", "--depth",
                      dest="maxdepth",
                      type="int",
                      default=DEFAULT_MAXDEPTH,
                      help="When used with -r, " \
                           "set the maximum recursion depth. Default is " \
                           + str(DEFAULT_MAXDEPTH) + "."),
    #parser.add_option("-i", "--input-format", # "nbt", "json", "norbert"
    #parser.add_option("-c", "--create",

    (options, args) = parser.parse_args()

    # if no tags are given, print starting from the top-level tag
    if len(args) == 0:
        args.append("")

    # if -r not specified, depth is 1
    if not options.recursive:
        options.maxdepth = 1

    # validate input format
    if options.format not in formatters:
        err("Unknown format: " + options.format)
        return INVALID_OPTION
    else:
        print_subtags.format = options.format

    # open file
    nbtfile = None
    try:
        nbtfile = nbt.NBTFile(options.infile)
    except IOError as e:
        # oh god why
        if e.strerror is None:
            e.strerror = str(e)

        if options.infile not in e.strerror:
            err(e.strerror + ": '" + options.infile + "'")
        else:
            err(e.strerror)

        if e.errno is None or e.errno == 0:
            e.errno = GENERAL_ERROR

        return e.errno

    # read and/or set tags
    retval = 0
    for arg in args:
        r = norbert(nbtfile, options, arg)
        if r > retval:
            retval = r

    if retval != 0:
        return retval

    # write file if necessary
    if options.outfile is not None:
            nbtfile.write_file(options.outfile)

    return 0

def norbert(nbtfile, options, arg):
    name, value = split_arg(arg)

    tag = get_tag(nbtfile, name)
    if tag is None:
        err("Tag not found: " + name)
        return TAG_NOT_FOUND

    if value == None:
        # print the tag and its subtags
        print_subtags(tag, maxdepth=options.maxdepth)
        return 0
    else:
        # set the tag
        return set_tag(tag, value)

def split_arg(namevaluepair):
    namevalue = namevaluepair.split('=')
    name = namevalue.pop(0)
    if len(namevalue) == 0:
        value = None
    else:
        value = '='.join(namevalue)
    return (name, value)

def get_tag(tag, name):
    if name != "":
        for i in name.split('.'):
            try:
                tag = tag[i]
            except TypeError as e:
                # see if tag is a list
                try:
                    i = int(i) - 1
                    tag = tag[i]
                except ValueError as e:
                    return None
            except KeyError as e:
                return None

    return tag

# sets the value of a tag
#
# returns: 0 if the tag is successfully set,
#          TAG_NOT_IMPLEMENTED if tag type not implemented,
#          TAG_CONVERSION_ERROR if value couldn't be converted
def set_tag(tag, value):
    try:
        if tag.id == nbt.TAG_BYTE:
            # convert to integer
            tag.value = int(value)
        elif tag.id == nbt.TAG_SHORT:
            # convert to integer
            tag.value = int(value)
        elif tag.id == nbt.TAG_INT:
            # convert to integer
            tag.value = int(value)
        elif tag.id == nbt.TAG_LONG:
            # convert to integer
            tag.value = int(value)
        elif tag.id == nbt.TAG_FLOAT:
            # convert to float
            tag.value = float(value)
        elif tag.id == nbt.TAG_DOUBLE:
            # convert to float
            tag.value = float(value)
        elif tag.id == nbt.TAG_STRING:
            # no conversion needed
            tag.value = value
        else:
            err("Writing for " + tag_types[tag.id] + " not implemented.")
            return TAG_NOT_IMPLEMENTED
    except ValueError as e:
        err("Couldn't convert " + value + " to " + tag_types[tag.id] + '.')
        return TAG_CONVERSION_ERROR

    return 0

# print a message to stderr
def err(message):
    sys.stderr.write(message + '\n')

# do nothing with a tag
#
# parameters:
#   tag: the tag to do nothing with
#   depth: the depth from the root ancestor tag
def nothing(tag, depth=None):
    pass

def is_parent_of(parent, child):
    return parent.id in complex_tag_types and child in parent.tags

# does a traversal of a tag and its subtags
#
# parameters
# ----------
#   tag:           the root tag to start traversing from
#   pre_action:    preorder action
#   post_action:   postorder action
#   maxdepth:      maximum depth level
def traverse_subtags(tag, maxdepth=DEFAULT_MAXDEPTH,
                     pre_action=nothing, post_action=nothing):
    # stack: a list of (tag, int) pairs
    # cur:   the current tag
    # prev:  the previous tag
    # c:     the index to the sibling to cur's right
    # p:     the index to the sibling to prev's right
    #
    #       
    #     parent
    #      / \
    #   cur   parent.tags[c]
    #

    if tag == None:
        return
    
    stack = [ (tag, None) ]
    pre_action(tag)
    (prev, p) = (None, None)
    
    while len(stack) != 0:
        # get cur from top of the stack
        (cur, c) = stack[-1]

        # if cur is the root or a child of prev
        if len(stack) != maxdepth and \
           ( prev == None or is_parent_of(prev, cur) ):
            if cur.id in complex_tag_types:
                # push cur's first child on stack
                push_child(stack, cur, 0)

                # perform preorder action on newly added item
                pre_action(stack[-1][0])

        # if prev is a child of cur
        elif len(stack) != maxdepth and is_parent_of(cur, prev):
            # push cur's next child (prev's sibling) on stack
            if p is not None:
                push_child(stack, cur, p)

                # perform preorder action on newly added item
                pre_action(stack[-1][0])

        # cur and prev are identical
        else:
            # perform postorder action on cur and pop it
            post_action(cur)
            stack.pop()
    
        (prev, p) = (cur, c)

# pushes a child and the index of the next child (if any) on the stack
def push_child(stack, parent, i):
    if len(parent.tags) > i + 1:
        stack.append( (parent.tags[i], i + 1) )
    else:
        stack.append( (parent.tags[i], None) )

def print_subtags(tag, maxdepth=DEFAULT_MAXDEPTH):
    (print_tag_init, print_tag_pre, print_tag_post, print_tag_done) = \
        formatters[print_subtags.format]
    print_tag_init(tag)
    traverse_subtags(tag, maxdepth=maxdepth,
                     pre_action=print_tag_pre, post_action=print_tag_post)
    print_tag_done(tag)

print_subtags.format = DEFAULT_PRINTFORMAT



def human_print_init(tag):
    tag.depth = 0

def human_print_pre(tag):
    if tag.id in complex_tag_types:
        for child in tag.tags:
            child.depth = tag.depth + 1

    if tag.name is None:
        print('    ' * tag.depth + ": " + tag.valuestr())
    else:
        print('    ' * tag.depth + tag.name + ": " + tag.valuestr())

formatters["human"] = (human_print_init, human_print_pre, nothing, nothing)



def nbt_txt_print_init(tag):
    try:
        filename = tag.filename # throws error if tag isn't an NBTFile
        tag.depth = -1
    except AttributeError as e:
        tag.depth = 0

def nbt_txt_print_pre(tag):
    if tag.id in complex_tag_types:
        for child in tag.tags:
            child.depth = tag.depth + 1

    if tag.depth < 0:
        return

    if tag.name is None or tag.name == "":
        print('   ' * tag.depth + tag_types[tag.id] + ": " + tag.valuestr())
    else:
        print('   ' * tag.depth + tag_types[tag.id] + "(\"" + tag.name + "\"): " + tag.valuestr())

    if tag.id in complex_tag_types:
        print('   ' * tag.depth + '{')

def nbt_txt_print_post(tag):
    try:
        filename = tag.filename # throws error if tag isn't an NBTFile
    except AttributeError as e:
        if tag.id in complex_tag_types:
            print('   ' * tag.depth + '}')

formatters["nbt-txt"] = \
    (nbt_txt_print_init, nbt_txt_print_pre, nbt_txt_print_post, nothing)



def norbert_print_init(tag):
    try:
        filename = tag.filename # throws error if tag isn't an NBTFile
        tag.fullname = ""
    except AttributeError as e:
        tag.fullname = tag.name

def norbert_print_pre(tag):
    if tag.id in complex_tag_types:
        for i in range(len(tag.tags)):
            child = tag.tags[i]
            if tag.fullname == "":
                child.fullname = child.name
            elif tag.id == nbt.TAG_COMPOUND:
                child.fullname = tag.fullname + '.' + child.name
            elif tag.id == nbt.TAG_LIST:
                child.fullname = tag.fullname + '[' + str(i) + ']'
    else:
        value = tag_types[tag.id] + '(' + tag.valuestr() + ')'
        print(tag.fullname + ' = ' + value)

formatters["norbert"] = \
    (norbert_print_init, norbert_print_pre, nothing, nothing)



if __name__ == "__main__":
    sys.exit(main())

