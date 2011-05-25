import sys
import os


def configure_settings(env_name):  # pragma: no cover
    from classytags.test import project
    import classytags

    PROJECT_DIR = os.path.abspath(os.path.dirname(project.__file__))

    MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

    TEMPLATE_DIRS = (
        os.path.join(PROJECT_DIR, 'templates'),
    )

    dirname = os.path.dirname(classytags.__file__)
    JUNIT_OUTPUT_DIR = os.path.join(
        os.path.abspath(dirname), '..', 'junit-%s' % env_name
    )

    ADMINS = tuple()
    DEBUG = False

    gettext = lambda x: x

    from django.conf import settings

    settings.configure(
        PROJECT_DIR=PROJECT_DIR,
        DEBUG=DEBUG,
        TEMPLATE_DEBUG=DEBUG,
        ADMINS=ADMINS,
        CACHE_BACKEND='locmem:///',
        MANAGERS=ADMINS,
        TIME_ZONE='America/Chicago',
        SITE_ID=1,
        USE_I18N=True,
        MEDIA_ROOT=MEDIA_ROOT,
        MEDIA_URL='/media/',
        ADMIN_MEDIA_PREFIX='/media_admin/',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        SECRET_KEY='test-secret-key',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            'django.template.loaders.eggs.Loader',
        ),
        INTERNAL_IPS=('127.0.0.1',),
        ROOT_URLCONF='classytags.test.project.urls',
        TEMPLATE_DIRS=TEMPLATE_DIRS,
        INSTALLED_APPS=(
            'classytags',
            'classytags.test.project',
        ),
        gettext=lambda s: s,
        LANGUAGE_CODE="en-us",
        APPEND_SLASH=True,
        TEST_RUNNER='classytags.test.project.testrunner.TestSuiteRunner',
        JUNIT_OUTPUT_DIR=JUNIT_OUTPUT_DIR
    )

    return settings


def run_tests(*test_args):  # pragma: no cover
    test_args = list(test_args)
    if '--direct' in test_args:
        test_args.remove('--direct')
        dirname = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, os.path.join(dirname, "..", ".."))

    failfast = False

    test_labels = []

    test_args_enum = dict([(val, idx) for idx, val in enumerate(test_args)])

    env_name = ''
    if '--env-name' in test_args:
        env_name = test_args[test_args_enum['--env-name'] + 1]
        test_args.remove('--env-name')
        test_args.remove(env_name)

    if '--failfast' in test_args:
        test_args.remove('--failfast')
        failfast = True

    for label in test_args:
        test_labels.append('classytags.%s' % label)

    if not test_labels:
        test_labels.append('classytags')

    settings = configure_settings(env_name)

    from django.test.utils import get_runner

    runner_class = get_runner(settings)
    runner = runner_class(verbosity=1, interactive=True, failfast=failfast)
    failures = runner.run_tests(test_labels)
    sys.exit(failures)

if __name__ == '__main__':  # pragma: no cover
    run_tests(*sys.argv[1:])
