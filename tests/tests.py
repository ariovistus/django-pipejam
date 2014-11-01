
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ImproperlyConfigured

from django.test.utils import setup_test_template_loader, override_settings
from django.template import Context, TemplateSyntaxError
from django.template.loader import get_template
from pipejam.processors import AssetRegistry
from bs4 import BeautifulSoup
import bs4.element

TEMPLATES = {
    'pipeline/css.html': '<link href="{{ url }}" rel="stylesheet" type="{{ type }}"{% if media %} media="{{ media }}"{% endif %}{% if title %} title="{{ title|default:"all" }}"{% endif %}{% if charset %} charset="{{ charset }}"{% endif %} />',
    'pipeline/js.html': '<script{% if async %} async{% endif %}{% if defer %} defer{% endif %} type="{{ type }}" src="{{ url }}" charset="utf-8"></script>',
    'pipejam/script.html': get_template('pipejam/script.html'),

    'basetag': '''{% load pipejam %}{% assets 'js' %}{% assets 'css' %}''',
    'test_one': '''
    {% load pipejam %}
    {% assets "js" %}
    {% assets "css" %}

    {% asset_ref "angular" %}
    {% asset_ref "style1" %}
    ''',

    'test_two': '''
    {% load pipejam %}
    {% assets 'js' %}
    {% assets 'css' %}

    {% asset_ref 'style1' %}
    {% asset_ref 'angular' %}
    ''',

    'base': '''
    {% load pipejam %}
    {% assets "js" %}
    {% assets "css" %}
    {% block bs %}
    {% endblock %}
    ''',

    'extends': '''
    {% extends 'base' %}
    {% load pipejam %}
    {% block bs %}
    {% asset_ref "style1" %}
    {% asset_ref "angular" %}
    {% endblock %}
    ''',

    'extends_outofblock': '''
    {% extends 'base' %}
    {% load pipejam %}
    {% asset_ref "style1" %}
    {% asset_ref "angular" %}
    ''',

}


setup_test_template_loader(TEMPLATES)

DEFAULT_SETTINGS = {
    'STATIC_URL': '/static/',

    'PIPEJAM_PROCESSORS': {
        'js': {
            'processor': 'pipejam.processors.PipelineScriptProcessor',
        },
        'css': {
            'processor': 'pipejam.processors.PipelineStylesheetProcessor',
            'type': 'text/css',
        },
    },
    'PIPELINE_JS': {
        'angular': {
            'source_files': (
                'js/angular.js',
            ),
            'output_filename': 'js/angular.bundle.js',
            'deps': ['style1'],
        },
    },
    'PIPELINE_CSS': {
        'style1': {
            'source_files': (
                'css/style1.css',
            ),
            'output_filename': 'css/style1.bundle.css',
        },
    },
}


def render_with_request(template):
    return template.render(Context({'request': RequestFactory()}))

@override_settings(**DEFAULT_SETTINGS)
class TagTests(TestCase):

    def test_it(self):
        registry = AssetRegistry()
        registry.add_asset_reference('angular', 'js')
        self.assertIn('angular', registry.assets['js'])
        self.assertIn('style1', registry.assets['css'])

    def test_simple(self):
        t = get_template('basetag')
        render_with_request(t)

    def test_one(self):
        t = get_template('test_one')
        vark = render_with_request(t)
        bs = BeautifulSoup(vark)
        a = (bs.find_all('script'))
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].attrs["src"], "/static/js/angular.bundle.js")
        a = (bs.find_all('link'))
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].attrs["href"], "/static/css/style1.bundle.css")

    def test_two(self):
        t = get_template('test_two')
        vark = render_with_request(t)
        bs = BeautifulSoup(vark)
        a = [x for x in bs.children if type(x) == bs4.element.Tag]
        self.assertEqual(a[0].name, "script")
        self.assertEqual(a[0].attrs["src"], "/static/js/angular.bundle.js")
        self.assertEqual(a[1].name, "link")
        self.assertEqual(a[1].attrs["href"], "/static/css/style1.bundle.css")

    def test_extends(self):
        t = get_template('extends')
        vark = render_with_request(t)
        bs = BeautifulSoup(vark)
        a = [x for x in bs.children if type(x) == bs4.element.Tag]
        self.assertEqual(a[0].name, "script")
        self.assertEqual(a[0].attrs["src"], "/static/js/angular.bundle.js")
        self.assertEqual(a[1].name, "link")
        self.assertEqual(a[1].attrs["href"], "/static/css/style1.bundle.css")

    def test_extends_outofblock(self):
        t = get_template('extends_outofblock')
        vark = render_with_request(t)
        # this no worky. why this no worky?
        self.assertEqual(vark.strip(), '')


SETTINGS2 = {
    'STATIC_URL': '/static/',

    'PIPEJAM_PROCESSORS': {
        'js': {
            'processor': 'pipejam.processors.ScriptProcessor',
        },
    },
    'PIPELINE_JS': {
        'angular': {
            'source_files': (
                'js/angular.js',
            ),
            'output_filename': 'js/angular.bundle.js',
        },
        'angular-resource': {
            'source_files': (
                'js/angular-resource.js',
            ),
            'output_filename': 'js/angular-resource.bundle.js',
            'deps': ['angular'],
        },
    },
}


@override_settings(**SETTINGS2)
class AssetRegistryTests2(TestCase):

    def test_it(self):
        registry = AssetRegistry()
        registry.add_asset_reference('angular-resource', 'js')
        self.assertIn('angular-resource', registry.assets['js'])
        self.assertEqual(registry.assets['js']['angular-resource'], set([('angular','js')]))
        self.assertIn('angular', registry.assets['js'])
        self.assertEqual(registry.assets['js']['angular'], set())


SETTINGS3 = {
    'STATIC_URL': '/static/',

    'PIPEJAM_PROCESSORS': {
        'js': {
            'processor': 'pipejam.processors.ScriptProcessor',
        },
    },
    'PIPELINE_JS': {
        'angular': {
            'source_files': (
                'js/angular.js',
            ),
            'output_filename': 'js/angular.bundle.js',
        },
        'angular-resource': {
            'source_files': (
                'js/angular-resource.js',
            ),
            'output_filename': 'js/angular-resource.bundle.js',
            'deps': ['angular'],
        },
    },
}


@override_settings(**SETTINGS3)
class AssetRegistryTests3(TestCase):

    def test_it(self):
        registry = AssetRegistry()
        registry.add_asset_reference('angular-resource', 'js')
        self.assertIn('angular-resource', registry.assets['js'])
        self.assertEqual(registry.assets['js']['angular-resource'], set([('angular','js')]))
        self.assertIn('angular', registry.assets['js'])
        self.assertEqual(registry.assets['js']['angular'], set())


SETTINGS4 = {
    'STATIC_URL': '/static/',

    'PIPEJAM_PROCESSORS': {
        'js': {
            'processor': 'pipejam.processors.ScriptProcessor',
        },
    },
    'PIPELINE_JS': {
        'angular': {
            'source_files': (
                'js/angular.js',
            ),
            'output_filename': 'js/angular.bundle.js',
        },
        'angular-resource': {
            'source_files': (
                'js/angular-resource.js',
            ),
            'output_filename': 'js/angular-resource.bundle.js',
            'deps': [('angular','js')],
        },
    },
}


@override_settings(**SETTINGS4)
class AssetRegistryTests4(TestCase):

    def test_it(self):
        registry = AssetRegistry()
        registry.add_asset_reference('angular-resource', 'js')
        self.assertIn('angular-resource', registry.assets['js'])
        self.assertEqual(registry.assets['js']['angular-resource'], set([('angular','js')]))
        self.assertIn('angular', registry.assets['js'])
        self.assertEqual(registry.assets['js']['angular'], set())
