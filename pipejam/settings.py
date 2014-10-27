from django.conf import settings

# Map of namespace -> processor config
#   {
#       'js': {
#           'processor': 'pipeline.processors.ScriptProcessor',
#           'aliases': {},
#       },
#   }
PROCESSORS = getattr(settings, 'PIPEJAM_PROCESSORS', {})

