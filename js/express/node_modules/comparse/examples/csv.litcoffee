Comma-Separated Values
======================

This example shows a simple parser for comma-separated values. The
input text consists of zero or more lines, and each line contains a
series of cells (values) separated by commas. The result of the CSV
parser is an array of arrays (matrix) containing the cell values as
strings.

For simplicity, we assume the values themselves can contain neither
commas nor end-of-line characters. Also, the parser only handles
Unix-style line breaks (`'\n'`). Generalizing the parser to handle
quoting and/or escapes, or alternative end-of-line markers, is left as
an exercise.

First, import the _Comparse_ library.

    P = require('../lib/comparse')

This is the parser for a single cell (zero or more characters except
comma or `'\n'`):

    cell = P.noneOf(',\n').concat()

A line contains one or more cells separated by commas.

    line = cell.sepBy P.char ','

And, finally, CSV text consists of zero or more lines separated by
end-of-line characters. The last line may or may not be followed by
the end-of-line character.

    csv = line.sepEndBy P.char '\n'

Now, we can test the parser:
    
    try
      console.log csv.parse 'foo,bar\nbaz,mek,42'
    catch e
      console.log e.name, 'at offset', e.offset

The result should be `[ [ 'foo', 'bar' ], [ 'baz', 'mek', '42' ] ]`.

