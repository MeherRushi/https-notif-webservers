Comparse – Monadic Parsing Library
==================================

_Comparse_ is a functional parsing library written in CoffeeScript. It
is inspired by Haskell monadic parsers
[Parsec](https://wiki.haskell.org/Parsec) or
[attoparsec](https://github.com/bos/attoparsec "attoparsec").

License
-------

Copyright © 2014–2017 Ladislav Lhotka, CZ.NIC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Installation
------------

For a global installation, run

    npm install -g comparse

Root privileges (`sudo`) might be needed.

Leave off `-g` if you prefer a local installation.

Resources
---------

For documentation, see the project
[wiki page](https://github.com/llhotka/comparse/wiki).

The `examples` subdirectory contains examples of simple parsers
written in [Literate CoffeeScript](http://coffeescript.org/#literate "Literate
Coffeescript"). They can be run using the `coffee` interpreter,
formatted versions are [here](https://github.com/llhotka/comparse/wiki/examples).

The _Comparse_ library itself is written in Literate CoffeeScript,
here is the
[annotated source code](https://github.com/llhotka/comparse/wiki/comparse).
