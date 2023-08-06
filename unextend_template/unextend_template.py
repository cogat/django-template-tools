from django import template
from django.template import base
from django.utils import safestring
from unextend_template import templatetags


class PartialParser(base.Parser):
    def parse(self, parse_until=None):
        """
        A version of the Django template parser that basically treats all nodes as
        static, except {% block %} which are parsed into substructures as normal.
        """
        if parse_until is None:
            parse_until = []
        nodelist = base.NodeList()
        while self.tokens:
            token = self.next_token()
            # Use the raw values here for TokenType.* for a tiny performance boost.
            token_type = token.token_type.value
            if token_type == 0:  # TokenType.TEXT
                self.extend_nodelist(nodelist, base.TextNode(token.contents), token)
            elif token_type == 1:  # TokenType.VAR
                # - treat filters as text - don't try to resolve
                self.extend_nodelist(
                    nodelist, base.TextNode(f"{{{{ {token.contents} }}}}"), token
                )
            elif token_type == 2:  # TokenType.BLOCK
                try:
                    command = token.contents.split()[0]
                except IndexError:
                    raise self.error(token, "Empty block tag on line %d" % token.lineno)
                if command in parse_until:
                    # A matching token has been reached. Return control to
                    # the caller. Put the token back on the token list so the
                    # caller knows where it terminated.
                    self.prepend_token(token)
                    return nodelist
                # Add the token to the command stack. This is used for error
                # messages if further parsing fails due to an unclosed block
                # tag.
                self.command_stack.append((command, token))
                # Get the tag callback function from the ones registered with
                # the parser.
                try:
                    compile_func = {
                        "block": templatetags.do_block,
                        # "extends": templatetags.do_extends,
                    }[command]
                except KeyError:
                    compile_func = templatetags.do_verbatim
                # Compile the callback into a node object and add it to
                # the node list.
                try:
                    compiled_result = compile_func(self, token)
                except Exception as e:
                    breakpoint()
                    raise self.error(token, e)
                self.extend_nodelist(nodelist, compiled_result, token)
                # Compile success. Remove the token from the command stack.
                self.command_stack.pop()
        if parse_until:
            self.unclosed_block_tag(parse_until)
        return nodelist


def _parse_string(s):
    child_tokens = base.DebugLexer(s).tokenize()
    child_parser = PartialParser(child_tokens)
    return child_parser.parse()


def _render(nodelist) -> str:
    c = template.Context()
    rendered_nodes = [node.render(c) for node in nodelist]
    return safestring.SafeString("".join(rendered_nodes))


BLOCK_SUPER = "{{ block.super"
LOAD_TAG = "{% load"


def unextend_template(child_source: str, parent_source: str) -> str:
    """
    Return a string that is the contents of the parent template,
    with {% block %} sections replaced by the contents of the child template.

    This helps with refactoring templates that no longer usefully extend
    their parents (ie with workarounds).

    Django's template engine doesn't allow much control over partial rendering
    of templates, so we need to reimplement some of the parsing.
    """
    if BLOCK_SUPER in child_source:
        # TODO: implement {{ block.super }}
        raise ValueError("Cannot unextend a template that uses {{ block.super }}")
    if LOAD_TAG in child_source:
        raise ValueError("Cannot unextend a template that uses {% load %}")
    child_nodelist = _parse_string(child_source)
    child_blocks = {
        n.name: n for n in child_nodelist if isinstance(n, templatetags.BlockNode)
    }

    parent_nodelist = _parse_string(parent_source)
    # replace the parent block nodes with the child block nodes
    for node in parent_nodelist:
        if isinstance(node, templatetags.BlockNode) and node.name in child_blocks:
            node.nodelist = child_blocks[node.name].nodelist

    return _render(parent_nodelist)
