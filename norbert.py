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

formatters = {}

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
        return 2
    else:
        print_tag.fmt = options.format

    # open file
    nbtfile = None
    try:
        nbtfile = nbt.NBTFile(options.infile)
        nbtfile.name = nbtfile.filename
    except IOError as e:
        err("Could not open file: " + options.infile)
        return

    # read and/or set tags
    norbert(nbtfile, options, args)

    # write file if necessary
    if options.needs_write is True \
       and options.outfile is not None:
            nbtfile.write_file(options.outfile)

def norbert(nbtfile, options, args):
    options.needs_write = False
    change_attempts = []

    for arg in args:
        name, value = split_arg(arg)
        if value == None:
            # print the tag
            print_subtags(nbtfile, name=name, format=options.format,
                      maxdepth=options.maxdepth)
        else:
            # set the tag
            options.needs_write = True

            has_changed = set_tag(nbtfile, value, name=name)
            change_attempts.append(has_changed)

    # if any attempts to change a tag failed,
    # make sure we don't try to write out the changes
    if False in change_attempts:
        options.needs_write = False

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
                    err("Tag not found: " + name)
                    return None
            except KeyError as e:
                err("Tag not found: " + name)
                return None

    return tag

# sets the value of a tag
#
# returns True if the value is successfully changed,
#         False otherwise
def set_tag(nbtfile, value, name=""):
    tag = get_tag(nbtfile, name)

    if tag is None:
        return False

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
            return False
    except ValueError as e:
        err("Couldn't convert " + value + " to " + tag_types[tag.id] + '.')
        return False

    return True

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

# traverses tag and its subtags
#
# parameters
# ----------
#   tag:           the root tag to start traversing from
#   pre_action:    preorder action
#   in_action:     in-order action (this doesn't work properly afaict)
#   post_action:   postorder action
#   maxdepth:      maximum depth level
def traverse_subtags(tag, pre_action=nothing, in_action=nothing,
                     post_action=nothing, maxdepth=DEFAULT_MAXDEPTH):
    stack = []
    tag.depth = 0
    stack.append(tag)
    in_action(tag, tag.depth)

    cur = None

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
                in_action(cur, cur.depth)

        post_action(cur, cur.depth)

def print_subtags(nbtfile, name="", format=DEFAULT_PRINTFORMAT, maxdepth=DEFAULT_MAXDEPTH):
    tag = get_tag(nbtfile, name)

    if tag is None:
        return

    traverse_subtags(tag, post_action=print_tag, maxdepth=maxdepth)

def print_tag(tag, depth):
    print(format_tag(tag, print_tag.fmt, depth))

print_tag.fmt = DEFAULT_PRINTFORMAT

def format_tag(tag, format, depth=0):
    formatter = formatters[format]
    return '    ' * depth + formatter(tag)

def format_tag_human(tag):
    if tag.name is None:
        return ": " + tag.valuestr()
    else:
        return tag.name + ": " + tag.valuestr()

formatters["human"] = format_tag_human

def format_tag_nbt_txt(tag):
    if tag.name is None:
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
    main()

