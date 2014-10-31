
from django import template
from django.utils.safestring import mark_safe

from ..processors import AssetRegistry
from django.template.base import TagHelperNode, generic_tag_compiler


register = template.Library()


class AssetsNode(TagHelperNode):
    def __init__(self, takes_context, args, kwargs):
        super(AssetsNode, self).__init__(takes_context, args, kwargs)
        self.namespace = str(args[0]).strip('"').strip("'")
        self.nodelist = None

    def render(self, context):
        r = context.get('request', None)
        if not getattr(r, 'PIPEJAM', None):
            r.PIPEJAM = AssetRegistry()

        registry = r.PIPEJAM
        content = self.nodelist.render(context)
        extra_tags = registry.render(context, self.namespace)
        return mark_safe(''.join(extra_tags)) + content


@register.tag
def assets(parser, token):
    '''
    bundlespace -- bundle space to be rendered
    '''
    node = generic_tag_compiler(
        parser=parser, token=token, params=['bundlespace'], 
        varargs=None, varkw=None, defaults=None,
        name='assets', takes_context=False,node_class=AssetsNode)
    node.nodelist = parser.parse()
    return node


@register.simple_tag(takes_context=True)
def asset_ref(context, bundlename, **kwargs):
    '''
    {% asset bundlename %}

    bundlename == name of django-pipeline bundle
    namespace == bundle namespace to use (e.g. 'js')
    '''
    namespace = kwargs.get('namespace', None)
    if namespace:
        namespace = str(args[0]).strip('"').strip("'")

    r = context.get('request', None)
    registry = r.PIPEJAM
    registry.add_asset_reference(bundlename, namespace)
    return ''
