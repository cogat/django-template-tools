from django.template import base, loader_tags, exceptions
from django.utils import safestring


class VerbatimBlockTagNode(base.Node):
    # A node that renders its own source
    def __init__(self, content):
        self.content = content

    def render(self, context):
        return f"{{% {self.content} %}}"


def do_verbatim(parser, token):
    return VerbatimBlockTagNode(token.contents)


class BlockNode(loader_tags.BlockNode):
    # Extend default behaviour to render the {% block %} {% endblock %} tags
    # as well as the block contents. Basically outputs its own source.
    def render(self, context):
        result = super().render(context)
        return f"{{% block {self.name} %}}{result}{{% endblock {self.name} %}}"


def do_block(parser, token):
    """
    Define a block that can be overridden by child templates.
    """
    # token.split_contents() isn't useful here because this tag doesn't accept
    # variable as arguments.
    bits = token.contents.split()
    if len(bits) != 2:
        raise exceptions.TemplateSyntaxError(
            "'%s' tag takes only one argument" % bits[0]
        )
    block_name = bits[1]
    # Keep track of the names of BlockNodes found in this template, so we can
    # check for duplication.
    try:
        if block_name in parser.__loaded_blocks:
            raise exceptions.TemplateSyntaxError(
                "'%s' tag with name '%s' appears more than once" % (bits[0], block_name)
            )
        parser.__loaded_blocks.append(block_name)
    except AttributeError:  # parser.__loaded_blocks isn't a list yet
        parser.__loaded_blocks = [block_name]
    nodelist = parser.parse(("endblock",))

    # This check is kept for backwards-compatibility. See #3100.
    endblock = parser.next_token()
    acceptable_endblocks = "endblock", f"endblock {block_name}"
    if endblock.contents not in acceptable_endblocks:
        parser.invalid_block_tag(endblock, "endblock", acceptable_endblocks)

    return BlockNode(block_name, nodelist)
