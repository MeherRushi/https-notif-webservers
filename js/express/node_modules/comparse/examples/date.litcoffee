Parser for Dates
================

This example presents a parser for dates in the format `dd-Mmm-yyyy`,
for instance `24-Jun-2014`. It demonstrates how verification of
semantic constraints can be included in the parser code – in this case
it is the number of days in each month including the leap day.

First, import the _Comparse_ library and define an array with the
abbreviations of months.

    P = require('../lib/comparse')
    
    months = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun"
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ] 
    
This is the parser for the separator character (hyphen):

    sep = P.char '-'

The parser for day reads a natural number and fails if it is not
between 1 and 31.

    day = P.nat0.bind (num) ->
      if 1 <= num <= 31 then P.unit num else P.failure

The parser for month reads one uppercase and two lowercase letters
(the default number of repetitions of the `repeat` combinator is
2). If the result is found in the `months` array, it is returned,
otherwise the parser fails.

    month = P.upper.bind (fst) ->
      P.lower.repeat().bind (rest) ->
        res = months.indexOf fst + rest.join('')
        if res >= 0 then P.unit res else P.failure

And here is the complete parser for dates that checks whether the
given day is possible in the given month and year. 

    date = day.bind (d) -> sep.bind -> month.bind (m) ->
      if d > 30 and m in [1, 3, 5, 8, 10] or d > 29 and m is 1
        P.failure
      else
        sep.bind -> P.nat0.bind (y) ->
          # check leap day
          if m is 1 and d is 29 and (y % 4 != 0 or
          y % 100 == 0 and y % 400 != 0)
            P.failure
          else
            P.unit new Date(y,m,d) 

Now we can test the parser:

    try
      console.log date.parse '24-Jun-2014'
    catch e
      console.log e.name, 'at offset', e.offset

The result should be `Tue Jun 24 2014 00:00:00 GMT+0200 (CEST)`,
possibly with another timezone.
