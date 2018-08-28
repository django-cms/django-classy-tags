from setuptools import setup, find_packages

version = __import__('classytags').__version__

setup(
    name = 'django-classy-tags',
    version = version,
    description = 'Class based template tags for Django',
    author = 'Jonas Obrist',
    author_email = 'ojiidotch@gmail.com',
    url = 'http://github.com/ojii/django-classy-tags',
    packages = find_packages(),
    zip_safe=False,
    install_requires=['Django>=1.11'],
    test_suite='runtests.main',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Framework :: Django",
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
)
