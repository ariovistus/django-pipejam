
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ImproperlyConfigured

from django.test.utils import setup_test_template_loader, override_settings
from django.template import Context, TemplateSyntaxError
from django.template.loader import get_template
from pipejam.processors import AssetRegistry
from bs4 import BeautifulSoup

TEMPLATES = {
    'pipeline/css.html': '<link href="{{ url }}" rel="stylesheet" type="{{ type }}"{% if media %} media="{{ media }}"{% endif %}{% if title %} title="{{ title|default:"all" }}"{% endif %}{% if charset %} charset="{{ charset }}"{% endif %} />',
    'pipeline/js.html': '<script{% if async %} async{% endif %}{% if defer %} defer{% endif %} type="{{ type }}" src="{{ url }}" charset="utf-8"></script>',
    'pipejam/script.html': get_template('pipejam/script.html'),

    'basetag': '''{% load pipejam %}{% assets 'js' %}{% assets 'css' %}{% assets 'ng' %}''',
    'test_one': '''
    {% load pipejam %}
    {% assets "js" %}
    {% assets "css" %}
    {% assets "ng" %}

    {% asset_ref "angular" %}
    {% asset_ref "style1" %}
    {% asset_ref "template1" %}
    ''',

    'test_two': '''
    {% load pipejam %}
    {% assets 'js' %}
    {% assets 'css' %}
    {% assets 'ng' %}

    {% asset_ref 'style1' %}
    {% asset_ref 'angular' %}
    {% asset_ref 'template1' %}
    ''',

    'base': '''
    {% load pipejam %}
    {% assets "js" %}
    {% assets "css" %}
    {% assets "ng" %}
    {% block bs %}
    {% endblock %}
    ''',

    'extends': '''
    {% extends 'base' %}
    {% load pipejam %}
    {% block bs %}
    {% asset_ref "style1" %}
    {% asset_ref "angular" %}
    {% asset_ref "template1" %}
    {% endblock %}
    ''',

    'extends_outofblock': '''
    {% extends 'base' %}
    {% load pipejam %}
    {% asset_ref "style1" %}
    {% asset_ref "angular" %}
    {% asset_ref "template1" %}
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
        'ng': {
            'processor': 'pipejam.processors.ScriptProcessor',
            'type': 'text/ng-template',
            'id': lambda bundlename, path: path,
        },
    },
    'PIPELINE_JS': {
        'angular': {
            'source_files': (
                'js/angular.js',
            ),
            'output_filename': 'js/angular.bundle.js',
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
    'PIPELINE_NG': {
        'template1': {
            'source_files': (
                'ng/template1.html',
            ),
            'output_filename': 'ng/template1.bundle.html',
        },
    },
}



@override_settings(**DEFAULT_SETTINGS)
class AssetRegistryTests(TestCase):

    def test_script_processor(self):
        registry = AssetRegistry()
        registry.add_asset_reference('template1', 'ng')

        a = registry.render(None, 'ng')
        self.assertEqual(len(a), 1)
        script = BeautifulSoup(a[0]).find_all('script')[0]
        self.assertIn('id',script.attrs)
        self.assertIn('type',script.attrs)
        self.assertIn('src',script.attrs)
        self.assertEqual(script.attrs['id'], "/static/ng/template1.bundle.html")
        self.assertEqual(script.attrs['type'], "text/ng-template")
        self.assertEqual(script.attrs['src'], "/static/ng/template1.bundle.html")


def render_with_request(template):
    return template.render(Context({'request': RequestFactory()}))

@override_settings(**DEFAULT_SETTINGS)
class TagTests(TestCase):

    def test_simple(self):
        t = get_template('basetag')
        render_with_request(t)

    def test_one(self):
        t = get_template('test_one')
        vark = render_with_request(t)
        bs = BeautifulSoup(vark)
        script = [x for x in bs.find_all("script") if x.attrs['type'] == 'text/ng-template'][0]
        self.assertIn('id',script.attrs)
        self.assertIn('type',script.attrs)
        self.assertIn('src',script.attrs)
        self.assertEqual(script.attrs['id'], "/static/ng/template1.bundle.html")
        self.assertEqual(script.attrs['type'], "text/ng-template")
        self.assertEqual(script.attrs['src'], "/static/ng/template1.bundle.html")

    def test_extends(self):
        t = get_template('extends')
        vark = render_with_request(t)
        bs = BeautifulSoup(vark)
        script = [x for x in bs.find_all("script") if x.attrs['type'] == 'text/ng-template'][0]
        self.assertIn('id',script.attrs)
        self.assertIn('type',script.attrs)
        self.assertIn('src',script.attrs)
        self.assertEqual(script.attrs['id'], "/static/ng/template1.bundle.html")
        self.assertEqual(script.attrs['type'], "text/ng-template")
        self.assertEqual(script.attrs['src'], "/static/ng/template1.bundle.html")

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
        'ng': {
            'processor': 'pipejam.processors.ScriptProcessor',
            'type': 'text/ng-template',
        },
    },
    'PIPELINE_JS': {
        'angular': {
            'source_files': (
                'js/angular.js',
            ),
            'output_filename': 'js/angular.bundle.js',
            'deps': ['template1'],
        },
        'angular-resource': {
            'source_files': (
                'js/angular-resource.js',
            ),
            'output_filename': 'js/angular-resource.bundle.js',
            'deps': ['angular'],
        },
    },
    'PIPELINE_NG': {
        'template1': {
            'source_files': (
                'ng/template1.html',
            ),
            'output_filename': 'ng/template1.bundle.html',
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
        self.assertIn('template1', registry.assets['ng'])


SETTINGS3 = {
    'STATIC_URL': '/static/',

    'PIPEJAM_PROCESSORS': {
        'js': {
            'processor': 'pipejam.processors.ScriptProcessor',
        },
        'ng': {
            'processor': 'pipejam.processors.ScriptProcessor',
            'type': 'text/ng-template',
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
    'PIPELINE_NG': {
        'angular': {
            'source_files': (
                'ng/template1.html',
            ),
            'output_filename': 'ng/template1.bundle.html',
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
        self.assertIn('angular', registry.assets['ng'])
        self.assertEqual(registry.assets['ng']['angular'], set())


SETTINGS4 = {
    'STATIC_URL': '/static/',

    'PIPEJAM_PROCESSORS': {
        'js': {
            'processor': 'pipejam.processors.ScriptProcessor',
        },
        'ng': {
            'processor': 'pipejam.processors.ScriptProcessor',
            'type': 'text/ng-template',
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
    'PIPELINE_NG': {
        'angular': {
            'source_files': (
                'ng/template1.html',
            ),
            'output_filename': 'ng/template1.bundle.html',
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
        self.assertNotIn('angular', registry.assets['ng'])
