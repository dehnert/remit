#!/bin/bash

baseurl=${1:-http://localhost:8001/finance_core/reporting/?term=2010-spring}
dirname=$(mktemp -d /tmp/remit.XXXXXX)
methods="annotate aggregate"
cd $dirname
wget -O default.html "$baseurl"
for method in $methods; do
    wget -O $method.html  "$baseurl&compute_method=$method"
done
for method in $methods; do
    diff -q --report-identical-files default.html $method.html
done
