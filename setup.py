from setuptools import setup, find_packages

version = __import__('classytags').__version__

setup(
    name = 'django-classy-tags',
    version = version,
    description = 'Class based template tags for Django',
    author = 'Jonas Obrist',
    author_email = 'jonas.obrist@divio.ch',
    url = 'http://github.com/ojii/django-classy-tags',
    packages = find_packages(),
    zip_safe=False,
    test_suite='tests.suite',
)