#!/usr/bin/python

from dartsharp import DartSharpTranspiler, PostProcessor
from engine import flutter_to_uiwidgets, standard_library

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

	engines=[
			flutter_to_uiwidgets,
			standard_library,
		]
	transpiler = DartSharpTranspiler(engines=engines, global_class_name=utils_class_name)
	post_processor = PostProcessor()

	result = transpiler.transpile_dart_code(fin.read())
	result = post_processor.post_process(result)
	for engine in engines:
		result = engine.post_process(result)

	sys.stderr.write("\n".join(transpiler.error_messages))
	if len(transpiler.error_messages) > 0:
		sys.stderr.write("\n")

	if args.output is not None:
		fout = open(args.output, "w")
	else:
		fout = sys.stdout
	fout.write(result)
