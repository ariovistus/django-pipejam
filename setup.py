from distutils.core import setup


setup(
    name='django-pipejam',
    version='0.0.2',
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
    url='http://github.com/ariovistus/django-pipejam',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

