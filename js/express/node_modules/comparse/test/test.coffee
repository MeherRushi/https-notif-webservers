P = require ('../lib/comparse')
assert = require('assert')

try
  assert.strictEqual P.string("hello").parse("hello"), "hello", "string"
  assert.strictEqual P.nat0.parse("42"), 42, "number"
  xml_tag = P.letter.bind (car) ->
    P.alphanum.many().bind (cdr) ->
      P.unit car + cdr.join("")
  assert.strictEqual xml_tag.between(P.char("<"), P.char(">")).parse("<foo1>"),
    "foo1", "XML tag"
  console.log "All tests OK."
catch e
  console.log e.message, "test failed: expected",
    e.expected + ", got", e.actual 
