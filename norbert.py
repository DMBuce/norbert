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
    usage = "%prog [option] [tag[=value]]"
    desc  = "Edits or displays an NBT formatted file."
    parser = optparse.OptionParser(version=VERSION, usage=usage, description=desc)
    parser.add_option("-i", "--input-file",
                      dest="infile",
                      default="level.dat",
                      help="The file to read. Default is level.dat.")
    parser.add_option("-o", "--output-file",
                      dest="outfile",
                      default=None,
                      help="The file to write to. If not provided and there are arguments of the form <tag>=<value>, the file that would have been written will be printed to stdout.")
    parser.add_option("-f", "--format",
                      dest="format",
                      default="human",
                      help="Format to print output in. Valid values are \"human\" and \"nbt\". Default is \"human\""),

    (options, args) = parser.parse_args()

    # if no tags are given, print starting from the top-level tag
    if len(args) == 0:
        args.append("")
        #print_tag(get_tag(nbtfile, None))

    # open file
    nbtfile = None
    try:
        nbtfile = nbt.NBTFile(options.infile)
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
        namevalue = arg.split('=')
        if len(namevalue) == 1:
            # print the tag
            name = namevalue[0]
            print_tag(nbtfile, name=name, format=options.format)
        else:
            # set the tag
            name = namevalue.pop(0)
            value = '='.join(namevalue)
            options.needs_write = True

            has_changed = set_tag(nbtfile, value, name=name)
            change_attempts.append(has_changed)

            # if no output file given and tag successfully set,
            if options.outfile is None \
               and has_changed == True:
                # we won't be writing these changes,
                # so just print them for viewing
                print_tag(nbtfile, name=name, format=options.format)

    # if any attempts to change a tag failed,
    # make sure we don't try to write out the changes
    if False in change_attempts:
        options.needs_write = False

def print_tag(nbtfile, name="", verbosity=1, format="human"):
    tag = get_tag(nbtfile, name)

    if tag is None:
        return

    if format == "nbt":
        print(tag.pretty_tree())
    elif format == "human":
        print_tag_human(tag)
    else:
        err("Unknown format: " + format)
        sys.exit(1)

def get_tag(tag, name):
    if name != "":
        for i in name.split('.'):
            try:
                tag = tag[i]
            except (KeyError, TypeError) as e:
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

def print_tag_human(tag, pre=""):
    stack = []
    tag.pre = pre
    stack.append(tag)

    cur = None

    while len(stack) != 0:
        cur = stack.pop()

        # prevent infinite recursion
        #if len(cur.pre) > 10:
        #    return

        if cur.value is None:

            # reverse cur.tags so they're printed in the correct order
            try:
                cur.tags.reverse()
            except TypeError as e:
                pass

            for i in cur.tags:
                i.pre = cur.pre + "  "
                stack.append(i)

            # reverse cur.tags so they're back in the original order
            try:
                cur.tags.reverse()
            except TypeError as e:
                pass

        print(_human_tag_name(cur))
        

def _human_tag_name(tag):
    if tag.value is None:
        return tag.pre + tag.name + ":" #+ str(tag)
    else:
        if tag.name is None:
            return tag.pre + ": " + str(tag.value)
        else:
            return tag.pre + tag.name + ": " + str(tag.value)

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

