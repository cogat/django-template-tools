from unextend_template import unextend_template
import pytest


@pytest.mark.parametrize(
    "child_path, expected_result",
    [
        (
            "child_simple",
            """{% extends "mainbase.html" %}

{% block one %}one{% endblock one %}

{% block two %}two{% endblock two %}
""",
        ),
        (
            "child_simple_partial_override",
            """{% extends "mainbase.html" %}

{% block one %}eins{% endblock one %}

{% block two %}two{% endblock two %}
""",
        ),
    ],
)
def test_simples(child_path, expected_result):
    child_source = open(f"tests/templates/{child_path}.html").read()
    parent_source = open("tests/templates/_base_simple.html").read()

    assert (
        unextend_template.unextend_template(child_source, parent_source)
        == expected_result
    )


@pytest.mark.parametrize(
    "child_path, expected_result",
    [
        (
            "child_complex",
            """{% extends "mainbase.html" %}
{% load all the things %}

{% block one %}
    eins {% include "include.html" %}
    {% block yes-one %}
        Y {{ somevar | somefilter }}
    {% endblock yes-one %}
    {{ block.super }}
{% endblock one %}

{% block two %}{% block yes-two %}Y{% endblock yes-two %}two {% include "include.html" %}!{{ somevar | somefilter }}{% endblock two %}
""",
        ),
    ],
)
def test_complex(child_path, expected_result):
    child_source = open(f"tests/templates/{child_path}.html").read()
    parent_source = open("tests/templates/_base_complex.html").read()

    assert (
        unextend_template.unextend_template(child_source, parent_source)
        == expected_result
    )


def test_block_super_not_supported():
    child_source = open(f"tests/templates/child_with_super.html").read()
    parent_source = open("tests/templates/_base_simple.html").read()

    with pytest.raises(ValueError):
        unextend_template.unextend_template(child_source, parent_source)


def test_load_not_supported():
    child_source = open(f"tests/templates/child_with_load.html").read()
    parent_source = open("tests/templates/_base_simple.html").read()

    with pytest.raises(ValueError):
        unextend_template.unextend_template(child_source, parent_source)
