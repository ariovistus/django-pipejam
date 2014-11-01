
from importlib import import_module
from toposort import toposort_flatten
import os.path

from django.conf import settings
from django.utils.html import escape
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.template import Context


class Processor(object):
    def __init__(self, config):
        self.config = config


def _lookup_namespace_config(namespace):
    return getattr(settings, 'PIPELINE_' + namespace.upper(), {})


class AssetRegistry(object):

    def __init__(self):
        self.processor_config = getattr(settings,'PIPEJAM_PROCESSORS')
        self.namespaces = self.processor_config.keys()
        self.config = dict([(nm, _lookup_namespace_config(nm)) for nm in self.namespaces])
        self.assets = dict([(nm, dict()) for nm in self.namespaces])

    def _lookup_bundle(self, bundlename):
        for namespace, config in self.config.items():
            if bundlename in config:
                yield (bundlename, namespace)

    def _load_deps(self, bundlename, namespace):
        if not namespace:
            for bundlename1, namespace1 in self._lookup_bundle(bundlename):
                self._load_deps(bundlename, namespace1)
        else:
            if bundlename not in self.assets[namespace]:
                bundleconfig = self.config[namespace][bundlename];
                deps = set()
                for dep0 in bundleconfig.get('deps', []):
                    if isinstance(dep0, tuple):
                        deps.add(dep0)
                    else:
                        for dep in self._lookup_bundle(dep0):
                            deps.add(dep)
                self.assets[namespace][bundlename] = set(dep for dep in deps if dep[1] == namespace)
                for bundlename1, namespace1 in deps:
                    self._load_deps(bundlename1, namespace1)

    def add_asset_reference(self, bundlename, namespace=None):
        self._load_deps(bundlename, namespace)

    def mode_for_file(self, filename):
        _, ext = os.path.splitext(filename)
        mode = ext.lstrip('.')
        return self.mode_map.get(mode, mode)

    def get_processor(self, namespace):
        config = self.processor_config[namespace]

        mod, cls = config['processor'].rsplit('.', 1)
        module = import_module(mod)
        return getattr(module, cls)(config)

    def render(self, context, namespace):
        result = []
        asset_map = dict((key, set(str(value[0]) for value in depset)) for (key,depset) in self.assets[namespace].items())
        assets = toposort_flatten(asset_map)
        processor = self.get_processor(namespace)
        for asset in assets:
            result.extend(processor.render(context, asset, self.config[namespace][asset], self.processor_config[namespace]))

        return result


#
# Default processors
#


class PipelineScriptProcessor(Processor):
    def render(self, context, bundlename, config, processor_config):
        from pipeline.templatetags.compressed import CompressedJSNode
        return CompressedJSNode("'{0}'".format(bundlename)).render(context)

class PipelineStylesheetProcessor(Processor):
    def render(self, context, bundlename, config, processor_config):
        from pipeline.templatetags.compressed import CompressedCSSNode
        return CompressedCSSNode("'{0}'".format(bundlename)).render(context)


