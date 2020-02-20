#!/usr/bin/python

from dartsharp import DartSharpTranspiler
import argparse, sys

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file", help="Path to the input file (default stdin)", nargs='?')
	parser.add_argument("-o", "--output", help="Path to the output file (default stdout)")
	args = parser.parse_args()

	if args.input_file is not None:
		fin = open(args.input_file, "r")
	else:
		fin = sys.stdin

	transpiler = DartSharpTranspiler()
	result = transpiler.transpile_dart_code(fin.read())
	sys.stderr.write("\n".join(transpiler.error_messages))
	if len(transpiler.error_messages) > 0:
		sys.stderr.write("\n")

	if args.output is not None:
		fout = open(args.output, "w")
	else:
		fout = sys.stdout
	fout.write(result)
