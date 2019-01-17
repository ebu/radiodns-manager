from django import template
from django.template.base import Template, TemplateSyntaxError

from lpp.settings import PLUGIT_APP_URL
from plugIt.bridge.bridge import Bridge

register = template.Library()


class PlugItIncludeNode(template.Node):
    def __init__(self, action):
        self.action = action

    def render(self, context):
        action = self.action.resolve(context)

        # Load plugIt object
        bridge = Bridge(PLUGIT_APP_URL)

        return Template(bridge.get_template(action)).render(context)


@register.tag(name="plugitInclude")
def plug_it_include(parser, token):
    """
        Load and render a template, using the same context of a specific action.

        Example: {% plugitInclude "/menuBar" %}
    """
    bits = token.split_contents()

    if len(bits) != 2:
        raise TemplateSyntaxError("'plugitInclude' tag takes one argument: the template's action to use")

    action = parser.compile_filter(bits[1])

    return PlugItIncludeNode(action)


@register.filter
def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')
