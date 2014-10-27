from distutils.core import setup


setup(
    name='django-pipejam',
    version='0.0.1',
    description='Dependency management on top of Django Pipeline.',
    author='Ellery Newcomer',
    author_email='ellery-newcomer@utulsa.edu',
    keywords=['django', 'assets',],
    packages=[
        'pipejam',
        'pipejam.templatetags',
    ],
    zip_safe=False,
    install_requires=[
        'django>=1.5',
        'django-pipeline>=1.3',
        'toposort>=1.1',
    ],
)

