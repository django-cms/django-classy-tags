#!/usr/bin/env python
from setuptools import find_packages, setup


REQUIREMENTS = [
    'django>=2.2',
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Framework :: Django',
    'Framework :: Django :: 2.2',
    'Framework :: Django :: 3.1',
    'Framework :: Django :: 3.2',
    'Framework :: Django :: 4.0',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='django-classy-tags',
    version='3.0.0',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    maintainer='Django CMS Association and contributors',
    maintainer_email='info@django-cms.org',
    url='http://github.com/ojii/django-classy-tags',
    license='BSD',
    description='Class based template tags for Django',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
