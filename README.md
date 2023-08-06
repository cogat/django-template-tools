# Tools for manipulating Django templates

## `unextend_template`

Statically apply the `{% extends %}` tag of a child template, meaning the parent
template is no longer needed by the child template.

This is useful to refactor templates where the parent is no longer useful, ie
if there are a large number of workarounds or inconsistencies.

### How it works

- Parse both child and parent templates into Nodes.
- Replace the `{% block %}` nodes of the parent with the block nodes of the child.
- Return the source of the parent, which now contains overridden blocks.

### Restrictions

- The tool does not assess templates for more than syntactic validity. Any
  libraries or filter names are passed through.
- The tool requires raw strings to be passed for child and parent templates. The
  path to the template in the `{% extends %}` tag is ignored.
- The tool does not yet work with `{{ block.super }}`.
- The tool does not yet transfer `{% load %}` outside of {% block %} tags in the
  child template.

## Install

```shell
poetry install
```

## To run tests

```shell
poentry run pytest
```
