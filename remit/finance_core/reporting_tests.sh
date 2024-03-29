#!/bin/bash

methods="annotate aggregate"
baseurl=${1:-http://localhost:8001/finance_core/reporting/?a=b}
baseurls="$baseurl&term=2010-spring $baseurl&area=13 $baseurl&layer=30"
for testbaseurl in $baseurls; do
    echo $testbaseurl
    dirname=$(mktemp -d /tmp/remit.XXXXXX)
    cd $dirname
    wget -q -O default.html "$baseurl"
    for method in $methods; do
        wget -q -O $method.html  "$baseurl&compute_method=$method"
    done
    for method in $methods; do
        diff -q --report-identical-files default.html $method.html
    done
done
