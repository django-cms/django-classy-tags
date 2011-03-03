#!/bin/bash

./runtests.sh
retcode=$?
if [ $retcode != 0 ]; then
    exit $retcode
fi
./run3rdpartytests.sh
retcode=$?
if [ $retcode != 0 ]; then
    exit $retcode
fi
exit 0