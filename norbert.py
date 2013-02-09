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
DEFAULT_INPUTFORMAT = "nbt"
DEFAULT_SEP = ".#"

# errors
GENERAL_ERROR = 1
INVALID_OPTION = 2
TAG_NOT_FOUND = 4
TAG_NOT_IMPLEMENTED = 5
TAG_CONVERSION_ERROR = 6

formatters = {}
readers = {}

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
    nbt.TAG_COMPOUND:   "TAG_Compound",

    "TAG_End":        nbt.TAG_END,
    "TAG_Byte":       nbt.TAG_BYTE,
    "TAG_Short":      nbt.TAG_SHORT,
    "TAG_Int":        nbt.TAG_INT,
    "TAG_Long":       nbt.TAG_LONG,
    "TAG_Float":      nbt.TAG_FLOAT,
    "TAG_Double":     nbt.TAG_DOUBLE,
    "TAG_Byte_Array": nbt.TAG_BYTE_ARRAY,
    "TAG_String":     nbt.TAG_STRING,
    "TAG_List":       nbt.TAG_LIST,
    "TAG_Compound":   nbt.TAG_COMPOUND
}

complex_tag_types = [
    nbt.TAG_BYTE_ARRAY,
    nbt.TAG_LIST,
    nbt.TAG_COMPOUND
]

def main():
    usage = "%prog [option] [tag[=value]] [tag2[=value2]] ..."
    desc  = "Edits or displays an NBT file. " \
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
    parser.add_option("-i", "--input-format",
                      dest="inputformat",
                      default=DEFAULT_INPUTFORMAT,
                      help="Format of the input file. " \
                           "Valid values are \"nbt\" and \"norbert\". " \
                           "Default is \"" + DEFAULT_INPUTFORMAT + "\".")
    parser.add_option("-d", "--depth",
                      dest="maxdepth",
                      type="int",
                      default=DEFAULT_MAXDEPTH,
                      help="Set the maximum recursion depth. Default is " \
                           + str(DEFAULT_MAXDEPTH) + ".")
    parser.add_option("-s", "--separator",
                      dest="sep",
                      default=DEFAULT_SEP,
                      help="Set the tag separator for norbert-formatted " \
                           "arguments, input, and output. " \
                           "The argument to this option must be " \
                           "a string of one or two characters. " \
                           "The first character is used to delimit tag " \
                           "names, and the second character is used to " \
                           "delimit list items. Default is '" + DEFAULT_SEP + \
                           "'")
    #parser.add_option("-i", "--input-format", # "nbt", "json", "norbert"
    #parser.add_option("-c", "--create",

    (options, args) = parser.parse_args()

    # if no tags are given, print starting from the top-level tag
    if len(args) == 0:
        args.append("")

    if len(options.sep) == 0 or len(options.sep) > len(DEFAULT_SEP):
        err("Argument to -s must be 1 or 2 characters: " + options.sep)
        return INVALID_OPTION
    else:
        options.sep += DEFAULT_SEP[ len(options.sep) : len(DEFAULT_SEP) ]
        norbert_print_pre.sep = options.sep

    # validate input format
    if options.format not in formatters:
        err("Unknown format: " + options.format)
        return INVALID_OPTION

    # open file
    try:
        nbtfile = read_file(options, args)
    except IOError as e:
        err(e.strerror)
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

def read_file(options, args):
    try:
        if options.inputformat in readers:
            reader = readers[options.inputformat]
            nbtfile = reader(options)
        else:
            err("Input format not recognized: " + options.inputformat)
            return None
    except IOError as e:
        # make sure error has strerror, errno
        if e.strerror is None:
            e.strerror = str(e)

        if options.infile not in e.strerror:
            e.strerror += ": '" + options.infile + "'"

        if e.errno is None or e.errno == 0:
            e.errno = GENERAL_ERROR

        raise e

    return nbtfile

def nbt_read_file(options):
    return nbt.NBTFile(options.infile)

readers["nbt"] = nbt_read_file

def norbert_read_file(options):
    nbtfile = nbt.NBTFile()
    with open(options.infile) as f:
        for line in f:
            norbert_create_subtags(nbtfile, line, sep=options.sep)

    return nbtfile

readers["norbert"] = norbert_read_file

def norbert_create_subtags(nbtfile, line, sep=DEFAULT_SEP):
    tag = nbtfile
    fullname, value, tagtype = split_line(line)
    names = fullname.split(sep[0])
    name = names.pop()

    # create compound tags
    for n in names:
        tag = norbert_create_subtag(tag, n, sep=sep)

    # create leaf tag
    tag = norbert_create_subtag(tag, name, value=value, sep=sep, tagtype=tag_types[tagtype])

# creates a named tag or list and adds it as a child of tag.
#
# name can be "tagname" or "tagname#2#3#4" (but not "parent.tagname")
#
def norbert_create_subtag(tag, name, value=None, sep=DEFAULT_SEP, tagtype=nbt.TAG_COMPOUND):
    # if tag already exists, return it
    testtag = get_tag(tag, name, sep)
    if testtag != None:
        return testtag

    name, indexes = split_name(name, sep[1])
    if len(indexes) > 0:
        # create list nodes
        tag = norbert_create_childtag(tag, name, sep=sep, tagtype=nbt.TAG_LIST)
        lastindex = indexes.pop()
        for i in indexes:
            tag = norbert_create_childtag(tag, i, sep=sep, tagtype=nbt.TAG_LIST)

        i = lastindex
    else:
        i = name

    tag = norbert_create_childtag(tag, i, value=value, sep=sep, tagtype=tagtype)
    return tag

# creates a direct child of tag
#
# i should be a string (to add to a compound tag) or an int (to insert into a list)
#
def norbert_create_childtag(tag, i, value=None, sep=DEFAULT_SEP, tagtype=nbt.TAG_COMPOUND):
    # create new compound tag
    if tagtype == nbt.TAG_LIST:
        newtag = nbt.TAG_List()
    elif tagtype == nbt.TAG_COMPOUND:
        newtag = nbt.TAG_Compound()
    else:
        newtag = nbt.TAGLIST[tagtype]()
        set_tag(newtag, value)

    # insert newtag into list
    if tag.id == nbt.TAG_LIST:
        tag.tags.insert(i, newtag)
    # insert into compound tag
    elif tag.id == nbt.TAG_COMPOUND:
        newtag.name = i
        tag.tags.append(newtag)

    return tag[i]

#def norbert_create_subtags2(nbtfile, line, sep=DEFAULT_SEP):
#    tag = nbtfile
#    fullname, value, tagtype = split_line(line)
#    names = fullname.split(sep[0])
#    name = names.pop()
#
#    for i in names:
#        i, indexes = split_name(i, sep[1])
#        if len(indexes) == 0:
#            # insert compound tag
#            newtag = nbt.TAG_Compound()
#            newtag.name = i
#            tag.tags.append(newtag)
#            tag = tag[i]
#        else:
#            # insert list
#            newtag = nbt.TAG_List(nbt.TAG_LIST, name=i)
#            tag.tags.append(newtag)
#            tag = tag[i]
#
#            lastindex = indexes.pop()
#            for j in indexes:
#                newtag = nbt.TAG_List(nbt.TAG_LIST)
#                tag.tags.insert(j, newtag)
#                tag = tag[j]
#
#            newtag = nbt.TAG_Compound()
#            tag.tags.insert(lastindex, newtag)
#            tag = tag[lastindex]
#
#    # insert a tag of the correct type using name, tagtype
#    i, indexes = split_name(name, sep[1])
#    if len(indexes) == 0:
#        tag_id = tag_types[tagtype]
#        newtag = nbt.TAGLIST[tag_id](name=i, value=value)
#        tag.tags.append(newtag)
#    else:
#        # insert list
#        newtag = nbt.TAG_List(nbt.TAG_LIST, name=i)
#        tag.tags.append(newtag)
#        tag = tag[i]
#
#        lastindex = indexes.pop()
#        for j in indexes:
#            newtag = nbt.TAG_List(nbt.TAG_LIST)
#            tag.tags.insert(j, newtag)
#            tag = tag[j]
#
#        tag_id = tag_types[tagtypes]
#        newtag = nbt.TAGLIST[tag_id](name=i, value=value)
#        tag.tags.insert(lastindex, newtag)
#        tag = tag[lastindex]

def split_line(line):
    name, typevalue = split_arg(line)
    name = name.strip()
    typevalue = typevalue.strip()

    tagtype, value = typevalue.split(' ')
    tagtype = tagtype.lstrip('(').rstrip(')')

    return name, value, tagtype

def norbert(nbtfile, options, arg):
    name, value = split_arg(arg)

    tag = get_tag(nbtfile, name, sep=options.sep)
    if tag is None:
        err("Tag not found: " + name)
        return TAG_NOT_FOUND

    if value == None:
        # print the tag and its subtags
        print_subtags(tag, maxdepth=options.maxdepth, format=options.format)
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

def get_tag(tag, fullname, sep=DEFAULT_SEP):
    if fullname == "":
        return tag

    try:
        for i in fullname.split(sep[0]):
            try:
                tag = tag[i]
            except TypeError as e:
                tag = tag[int(i)]
            except KeyError as e:
                (i, indexes) = split_name(i, sep[1])
                tag = tag[i]
                for j in indexes:
                    tag = tag[j]
    except (KeyError, ValueError, TypeError) as e:
        return None

    return tag

def split_name(nameindexlist, sep):
    nameindex = nameindexlist.split(sep)
    name = nameindex.pop(0)
    indexes = [ int(i) for i in nameindex ]

    return (name, indexes)

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
            if cur.id in complex_tag_types and len(cur.tags) != 0:
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

def print_subtags(tag, maxdepth=DEFAULT_MAXDEPTH, format=DEFAULT_PRINTFORMAT):
    (print_tag_init, print_tag_pre, print_tag_post, print_tag_done) = \
        formatters[format]
    print_tag_init(tag)
    traverse_subtags(tag, maxdepth=maxdepth,
                     pre_action=print_tag_pre, post_action=print_tag_post)
    print_tag_done(tag)



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
    sep = norbert_print_pre.sep
    if tag.id in complex_tag_types:
        # TODO: for i, child in enumerate(tag.tags):
        for i in range(len(tag.tags)):
            child = tag.tags[i]
            if tag.fullname == "":
                child.fullname = child.name
            elif tag.id == nbt.TAG_COMPOUND:
                child.fullname = tag.fullname + sep[0] + child.name
            elif tag.id == nbt.TAG_LIST:
                child.fullname = tag.fullname + sep[1] + str(i)
    else:
        value = '(' + tag_types[tag.id] + ') ' + tag.valuestr()
        print(tag.fullname + ' = ' + value)

norbert_print_pre.sep = DEFAULT_SEP

formatters["norbert"] = \
    (norbert_print_init, norbert_print_pre, nothing, nothing)



if __name__ == "__main__":
    sys.exit(main())

