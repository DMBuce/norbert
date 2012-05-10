#!/usr/bin/env python
#
# Editor for NBT
# http://web.archive.org/web/20110723210920/http://www.minecraft.net/docs/NBT.txt

import optparse
import sys
from nbt import nbt

VERSION = 0.1

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
    desc  = "Edits or displays an NBT formatted file. "
    parser = optparse.OptionParser(version=VERSION, usage=usage, description=desc)
    parser.add_option("-i", "--input-file",
                      dest="infile",
                      default="level.dat",
                      help="The file to read. Default is level.dat.")
    parser.add_option("-o", "--output-file",
                      dest="outfile",
                      default=None,
                      help="The file to write to. If not provided and there are arguments of the form <tag>=<value>, the file that would have been written will be printed to stdout.")

    (options, args) = parser.parse_args()

    norbert(options, args)

def norbert(options, args):

    nbtfile = None
    try:
        nbtfile = nbt.NBTFile(options.infile)
    except IOError as e:
        err("Could not open file: " + options.infile)
        return

    write_file = False

    if len(args) == 0:
        print_tag(get_tag(nbtfile, None))

    for arg in args:
        namevalue = arg.split('=')
        if len(namevalue) == 1:
            print_tag(get_tag(nbtfile, namevalue[0]))
        else:
            name = namevalue.pop(0)
            value = '='.join(namevalue)

            tag = get_tag(nbtfile, name)
            write_file = set_tag(tag, value)

    if write_file:
        if options.outfile is None:
            print_tag(nbtfile)
        else:
            nbtfile.write_file(options.outfile)

def print_tag(tag, verbosity=1):
    if not tag:
        return

    print(tag.pretty_tree())

def get_tag(tag, name):
    if name is not None and name != "":
        for i in name.split('.'):
            try:
                tag = tag[i]
            except KeyError as e:
                err("Tag not found: " + name)
                return None

    return tag

def set_tag(tag, value):
    if tag is None:
        return False

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
        err("Writing for " + tag_types[tag.id] + " not implemented yet.")
        return False

    return True

def err(message):
    #print(message, file=sys.stderr)
    sys.stderr.write(message + '\n')

def printTree(tag, sp):
	if tag.value is None:
		
		#print(sp + tag.name + ": " + str(tag))
		print(sp + tag.tag_info())
		for i in tag.tags:
			printTree(i, sp + "  ")
			#print(sp + tag.name + ": " + str(tag.value))
	else:
		print(sp + tag.tag_info())
		#print(sp + tag.name + ": " + str(tag.value))

def fmttag1(tag):
    return tag.tag_info()

def fmttag2(tag):
    return tag.name + ": " + str(tag.value)

if __name__ == "__main__":
    main()

