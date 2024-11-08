# xparse

Flexible expression parser for computing user defined conditionals

You can reference annotated source code
[here](./src/xparse.litcoffee).

## Usage

```bash
$ npm install xparse
```

```javascript
const xparse = require('xparse');

var expr = xparse("25 * 4");
expr() // returns 100
```

## Dynamic Variables

```javascript
var variables = {
  hello: 70
}
var resolver = (key) => variables[key]
var expr = xparse("hello < 25 * 4");
expr(resolver) // returns true (since 70 is less than 25 * 4)

variables.hello = 125
expr(resolver) // returns false (since 125 is not less than 25 * 4)
```

## Dynamic Functions

```javascript
var functions = {
  increment: (arg) => { arg + 1 }
  decrement: (arg) => { arg - 1 }
}
var resolver = (key, arg) => { functions[key](arg) }
var expr = xparse("increment(70) < 25 * 4");
expr(resolver) // returns true (since 71 is less than 25 * 4)

functions.increment = (arg) => { arg + 100 }
expr(resolver) // returns false (since 170 is not less than 25 * 4)
```

## License
  [Apache 2.0](LICENSE)

This software is brought to you by
[Corenova Technologies](http://www.corenova.com). We'd love to hear
your feedback.  Please feel free to reach me at <peter@corenova.com>
anytime with questions, suggestions, etc.
