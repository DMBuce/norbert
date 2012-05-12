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

VERSION = 0.2
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
                           "Valid values are \"human\" and \"nbt-txt\". " \
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
    #parser.add_option("-i", "--input-format", # "nbt", "json", "human"
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
        print_tag.fmt = options.format

    # open file
    nbtfile = None
    try:
        nbtfile = nbt.NBTFile(options.infile)
        nbtfile.name = nbtfile.filename
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

def traverse_subtags(tag, maxdepth=DEFAULT_MAXDEPTH, pre_action=nothing):
    stack = []
    tag.depth = 0
    cur = None

    stack.append(tag)
    while len(stack) != 0:
        cur = stack.pop()

        # prevent infinite recursion
        if cur.depth >= maxdepth:
            continue

        pre_action(cur, cur.depth)

        if cur.value is None:
            for i in reversed(cur.tags):
                i.depth = cur.depth + 1
                stack.append(i)

# does a traversal of a tag and its subtags
#
# parameters
# ----------
#   tag:           the root tag to start traversing from
#   pre_action:    preorder action
#   post_action:   postorder action
#   maxdepth:      maximum depth level
def traverse_subtags2(tag, maxdepth=DEFAULT_MAXDEPTH,
                     pre_action=nothing, post_action=nothing):
    if tag == None:
        return
    
    stack = [ tag ]
    pre_action(tag, len(stack))
    prev = None
    
    while len(stack) != 0:
        # get cur from top of the stack
        cur = stack[-1]

        # if cur is the root or a child of prev
        if len(stack) != maxdepth and \
           ( prev == None or (prev.value is None and cur in prev.tags) ):
            if cur.value is None:
                # push cur's first child on stack
                stack.append(cur.tags[0])
                cur.tags[0].sibling = 1
                # perform preorder action on newly added item
                pre_action(stack[-1], len(stack))

        # if prev is a child of cur
        elif len(stack) != maxdepth and cur.value is None and prev in cur.tags:
            # push cur's next child on stack
            if prev.sibling is not None:
                try:
                    i = prev.sibling
                    stack.append(cur.tags[i])
                    cur.tags[i].sibling = i + 1
                    # do preorder action on newly added item
                    pre_action(stack[-1], len(stack))

                except IndexError as e:
                    pass

        # cur and prev are identical
        else:
            # do postorder action on cur and pop it
            post_action(cur, len(stack))
            stack.pop()
    
        prev = cur


def print_subtags(tag, maxdepth=DEFAULT_MAXDEPTH):
    traverse_subtags2(tag, pre_action=print_tag, maxdepth=maxdepth)
    #traverse_subtags(tag, pre_action=print_tag, maxdepth=maxdepth)

def print_tag(tag, depth):
    print(format_tag(tag, print_tag.fmt, depth))

print_tag.fmt = DEFAULT_PRINTFORMAT

def format_tag(tag, format, depth=0):
    formatter = formatters[format]
    return '    ' * (depth - 1) + formatter(tag)

def format_tag_human(tag):
    if tag.name is None:
        return ": " + tag.valuestr()
    else:
        return tag.name + ": " + tag.valuestr()

formatters["human"] = format_tag_human

def format_tag_nbt_txt(tag):
    if tag.name is None or tag.name == "":
        return tag_types[tag.id] + ": " + tag.valuestr()
    else:
        return tag_types[tag.id] + "('" + tag.name + "'): " + tag.valuestr()

formatters["nbt-txt"] = format_tag_nbt_txt

# dead code
#
#def printTree(tag, sp):
#	if tag.value is None:
#		
#		#print(sp + tag.name + ": " + str(tag))
#		print(sp + tag.tag_info())
#		for i in tag.tags:
#			printTree(i, sp + "  ")
#			#print(sp + tag.name + ": " + str(tag.value))
#	else:
#		print(sp + tag.tag_info())
#		#print(sp + tag.name + ": " + str(tag.value))
#
#def fmttag1(tag):
#    return tag.tag_info()
#
#def fmttag2(tag):
#    return tag.name + ": " + str(tag.value)

if __name__ == "__main__":
    sys.exit(main())

