#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from classytags import __version__


REQUIREMENTS = [
    'django>=1.11',
    'six'
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django :: 2.1',
    'Framework :: Django :: 2.2',
    'Framework :: Django :: 3.0',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='django-classy-tags',
    version=__version__,
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    url='http://github.com/ojii/django-classy-tags',
    license='BSD',
    description='Class based template tags for Django',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
