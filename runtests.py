# -*- coding: utf-8 -*-
import warnings
import os
import sys
from django import VERSION

urlpatterns = []

TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}


INSTALLED_APPS = [
    'classytags',
    'classytags.test.project',
]

TEMPLATE_DIRS = [
    os.path.join(os.path.dirname(__file__), 'test_templates'),
]

if VERSION >= (1,6):
    TEST_RUNNER = 'django.test.runner.DiscoverRunner'
else:
    TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

ROOT_URLCONF = 'runtests'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'test_templates'),
        ],
        'OPTIONS': {
            'debug': True,
        },
    },
]

def main():
    import django
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS = INSTALLED_APPS,
        ROOT_URLCONF = ROOT_URLCONF,
        DATABASES = DATABASES,
        TEST_RUNNER = TEST_RUNNER,
        TEMPLATE_DIRS = TEMPLATE_DIRS,
        TEMPLATE_DEBUG = TEMPLATE_DEBUG,
        MIDDLEWARE_CLASSES = [],
        TEMPLATES=TEMPLATES,
    )

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    warnings.simplefilter("ignore")
    if django.VERSION >= (1, 7):
        django.setup()
    failures = test_runner.run_tests(['classytags'])
    sys.exit(failures)


if __name__ == "__main__":
    main()
