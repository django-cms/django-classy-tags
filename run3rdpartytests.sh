#!/bin/bash

if [ ! -d 3rdpartytests ]; then
    virtualenv 3rdpartytests --no-site-packages
fi

source 3rdpartytests/bin/activate

pip install PIL

pip uninstall django-classy-tags -y
pip install .

cd 3rdpartytests

if [ ! -d django-cms ]; then 
    git clone https://github.com/divio/django-cms.git
    cd django-cms
else 
    cd django-cms
    git pull origin develop
fi

./runtests.sh --rebuild-env
retcode=$?
if [ $retcode != 0 ]; then
    exit $retcode
fi

cd ..

if [ ! -d django-sekizai ]; then 
    git clone https://github.com/ojii/django-sekizai.git
    cd django-sekizai
else 
    cd django-sekizai
    git pull origin master
fi

./runtests.sh --rebuild-env
retcode=$?
if [ $retcode != 0 ]; then
    exit $retcode
fi

cd ..

exit 0