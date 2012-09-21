# -*- coding: utf-8 -*-
import warnings
import os
import sys

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


ROOT_URLCONF = 'runtests'

def runtests():
    from django.conf import settings
    settings.configure(
        INSTALLED_APPS = INSTALLED_APPS,
        ROOT_URLCONF = ROOT_URLCONF,
        DATABASES = DATABASES,
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner',
        TEMPLATE_DIRS = TEMPLATE_DIRS,
        TEMPLATE_DEBUG = TEMPLATE_DEBUG
    )

    # Run the test suite, including the extra validation tests.
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)

    test_runner = TestRunner(verbosity=1, interactive=False, failfast=False)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        failures = test_runner.run_tests(['classytags'])
    return failures


if __name__ == "__main__":
    failures = runtests()
    if failures:
        sys.exit(bool(failures))
