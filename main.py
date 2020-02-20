#!/usr/bin/python

from dartsharp import DartSharpTranspiler
from engine import flutter_to_uiwidgets

import argparse, sys, os

def to_camel_case(snake_str):
	return ''.join(x.title() for x in snake_str.split('_'))

def basename_without_extension(filename):
	return os.path.basename(filename).split('.')[0]

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file", help="Path to the input file (default stdin)", nargs='?')
	parser.add_argument("-o", "--output", help="Path to the output file (default stdout)")
	args = parser.parse_args()

	if args.input_file is not None:
		fin = open(args.input_file, "r")
		utils_class_name = "%sUtils" % to_camel_case(basename_without_extension(args.input_file))
	else:
		fin = sys.stdin
		utils_class_name = "Utils"

	transpiler = DartSharpTranspiler(engines=[flutter_to_uiwidgets], global_class_name=utils_class_name)

	result = transpiler.transpile_dart_code(fin.read())
	sys.stderr.write("\n".join(transpiler.error_messages))
	if len(transpiler.error_messages) > 0:
		sys.stderr.write("\n")

	if args.output is not None:
		fout = open(args.output, "w")
	else:
		fout = sys.stdout
	fout.write(result)
