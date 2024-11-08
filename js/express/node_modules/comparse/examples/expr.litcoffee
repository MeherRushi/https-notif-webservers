Parser for Arithmetic Expressions
=================================

This example shows a parser for restricted arithmetic expressions
defined by the following grammar:

1. _expr_ ⟶ _term_ ("+" _expr_ | 𝜆) 
1. _term_ ⟶ _factor_ ("*" _term_ | 𝜆)
1. _factor_ ⟶ "(" _expr_ ")" | _nat_
1. _nat_ ⟶ "0" | "1" | "2" | …

The CoffeeScript source code below define three parsers that closely
mimick the grammar rules 1, 2 and 3. The parsers not only analyze
arithmetic expressions, taking into account the precedence of
operations, but also compute the numeric result.

An important point to note is that the rules are mutually recursive –
_expr_ depends on _term_, _term_ depends on _factor_, and _factor_
depends on _expr_. Due to the lexical scoping rules of JavaScript, we
have to encapsulate the parsers in functions.

The resulting parser doesn't allow any whitespace inside the
expressions. This simple extension is left as an exercise.

First, import the _Comparse_ library.

    P = require('../lib/comparse')

The `expr` parser uses the `option` method: if the plus sign and
second operand are not present, the default value of 0 is used as the
second operand.

    expr = -> term().bind (t) ->
      (P.char('+').bind -> expr()).option(0).bind (e) ->
        P.unit t + e

The `term` parser is almost identical to `expr`, only addition is
replaced by multiplication.

    term = -> factor().bind (f) ->
      (P.char('*').bind -> term()).option(1).bind (t) ->
        P.unit f * t

Finally, `factor` parses either an expression in parentheses or a
non-negative integer (the `nat0` parser is provided by the _Comparse_ library). 

    factor = -> (P.char('(').bind -> expr().bind (e) ->
      P.char(')').bind -> P.unit e).orElse P.nat0

Now, we can test the parser. The result should be 222.

    console.log expr().parse '(42+1)*5+7'
