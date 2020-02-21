# DartSharp

This is a simple and lightweight dart compiler to C# implemented with python.
Please be noted that. It is NOT intended to work as a full-fledged compiler.
Instead, it is just a tool assisting human being in manual translation.
In another word, this is just a more advanced version of "find and replace".
It only tries to handle most of the easy but tedious work in the translation, to leave only the trickiest differences between dart and C# to human being.

This tool exploits heavily the similarities between dart and C#.
It works by identifying in the code dart features that are not supported in C#, and try to replace it with C# implementation.
It also makes heavy use of the format of the code, i.e. it relies on the code being not only correct, but also well indented and structured.

## Ideas behind this tool

### Elements and Parsers

To avoid tremendous amount of unmaintainable regular expression, this work introduces the idea of `Element`s, and each `Element` comes with a `Parser` that identifies it.
`Parser`s for advanced `Element`s are implemented by a composition of those for simpler `Element`s.
An `Element` is basically a reference to a part of the code, combined with the data describing the code it points to.
For example, a `FunctionHeaderElement` points to the part of the code starting with the function return type and ending with the closing `)`, and contains `WordElement`s which point to the return type, the function name, and the parameters, etc.
A `FunctionHeaderParser` recognizes a dart function header in the code, and produces a `FunctionHeaderElement` that points to the part of the code.

The biggest difference between `Parser`s and regular expressions are that the implementation of a `Parser`s may refer to itself directly or indirectly, which enables it to support recursion.
At the same time, parsers are more flexible and informative.
They are also much much more human friendly to deal with.

### Blocks and Locators

With enough work, maybe I can make the set of `Parser`s and `Element` more and more complex, until they can cover the entire dart code.
Then we almost get a compiler (without the code generation part).
That is unfortunately too much work for me.
It is beyond my ability to extend the `Parser`s to recognize even a complete function.
The most they can do is to recognize some simple features.

Without extending the `Parser`s to recognize complete classes and functions, however, it is difficult to locate the small features the `Parser`s recognizes.
So I just go back to the old "find and replace" way.
To make use of the structure of the code, this tool makes use of another ideas and call them `Block`s and `Locator`s.
For example, the `ClassLocator` searches the code for class headers, then find the closing `}` with the same indentation level of the class header.
Finally, `ClassLocator` produces a `ClassBlock` which points the the code of the class.
The difference between a `Block` and an `Element` is that the block does not "understand" the code it points to, while an `Element` has all the information that describes the complete functionality of the referenced code.
In another word, an `Element` is able to translate the code into another language with all the information it has, while a `Block` must deal with the code carefully.
A `Block` should only translate the part of the code that it can "understand", while leaving others unchanged.

To translate a block, the first thing is to search in it to identify some other smaller blocks and elements.
Those blocks and elements should not intersect with each other.
Then, translate those smaller blocks the elements, replace the part they refer to by what they are translated into.

### Replacer

`Replacer` is a simple class providing the following functionality:

1. Initialized with the original `text`, whose parts will be replaced;
2. Receive update requests by `update(request)` method, each of which specifies a range and the replacement, for example `(5, 8, "Hello")`, telling the `Replacer` to replace `text[5:8]` by `"Hello"`. The requests are not allowed to intersect with each other. The `Replacer` will update its state, by recording these requests without actually performing the replacing;
3. When invoked with `digest()` method, perform all the replacing requests on the original text, and returns the result. This will not change the state of the `Replacer`, which may continue to receive further update requests.

With the help of the above defined `Replacer`, the transpiler works as follows:

1. Locate all class blocks, global function blocks, global variables, etc. i.e. all the "top level" things in the code, perform transpilation on each of them, and submit one update request for each block to the `Replacer`;
2. Call the `digest()` method of the `Replacer` and get the result.

Then everything is done. Except the detail of how to perform transpilation on each "top level" thing. This is solved by applying the above procedure recursively on each block.

## Current State

This transpiler is able to work now!
New functionalities will be added little by little.

Since it is not quite useful with the currently supported functionalities, `setup.py` is not provided.
To try this tool, simply clone this repository, set the `PYTHONPATH` to include the path to this repository in your file system.
Then

```bash
$ cd DartSharp
$ python main.py --help

usage: main.py [-h] [-o OUTPUT] [input_file]

positional arguments:
  input_file            Path to the input file (default stdin)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to the output file (default stdout)

```

## TODO

- Add attribute initialization inside constructor body
- Recognize setters and getters
- Replace all `final` variable declarations inside function
- For required parameters, assert they are not null in the body
- Recognize function typedef and replace function typedefs into delegates
- Find out which libraries are required
- Recognize dart style list
- Replace all double dots syntax
- Transform strings into C# style
- Handle abstract functions
- Handle static functions
- add `new` to invocation of constructors
- Implement `if` and `while` block
- Replace all `for(final...)` with `for(var...)`