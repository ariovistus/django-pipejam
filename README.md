django-amn
==========

Asset dependency resolver on top of Django Pipeline

Overview
========


Settings:
    PIPEJAM_PROCESSORS = {
        'js': {
            'processor': 'pipejam.processors.PipelineScriptProcessor',
        },
        'css': {
            'processor': 'pipejam.processors.PipelineStylesheetProcessor',
            'type': 'text/css',
        },
    }
    PIPELINE_JS = {
        'jquery': {
            'source_files': (
                'js/jquery.js',
                'js/jquery-ui.js',
                'js/jquery-mylib.js',
            ),
            'output_filename': 'js/jquery.bundle.js',
        },
        'app': {
            'source_files': (
                'js/mylib1.js',
                'js/mylib2.js',
                'js/myapp.js',
            ),
            'output_filename': 'js/app.bundle.js',
            'deps': ['jquery', 'jinky-style'],
        }
    }
    PIPELINE_CSS = {
        'jinky-style': {
            'source_files': (
                'css/style1.css',
            ),
            'output_filename': 'css/style.bundle.css',
        },
    }

Template:

    {% load pipejam %}

    <!doctype html>
    <html>
        <head>
        {% assets 'css' %}
        </head>
        <body>
        ...
        {% asset_ref 'app' %}

        {% assets 'js' %}
        </body>
    </html>

Output:

    <!doctype html>
    <html>
        <head>
        <link href="/static/css/style.bundle.css" rel="stylesheet" type="text/css" />
        </head>
        <body>
            ...
            <script src='/static/js/jquery.bundle.js'></script>
            <script src='/static/js/app.bundle.js'></script>
        </body>
    </html>

