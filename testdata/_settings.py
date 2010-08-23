import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'SUPPORTS_TRANSACTIONS': False,
    }
}

INSTALLED_APPS = ['testdata']

TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), 'templates')]