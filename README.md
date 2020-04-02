# template-engine

A template engine for django-like template syntax, inspired by [500lines/template-engine](https://github.com/aosabook/500lines).

Improvement:

- template >> AST >> render function;
- a monadic parser combinators inspired by [this paper](http://103.230.96.7:82/2Q2W308CA76585B8F49B5F4406625CE5CE46A6D8B589_unknown_22BCF56F891E45CA0B1C99B92EF636F046C57D62_6/www.cs.nott.ac.uk/~pszgmh/monparsing.pdf);
- implememt `elif` and bool expressions (`and`, `or` and `not`) in `if`;
