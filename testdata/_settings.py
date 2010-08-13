DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'SUPPORTS_TRANSACTIONS': False,
    }
}

INSTALLED_APPS = ['testdata']