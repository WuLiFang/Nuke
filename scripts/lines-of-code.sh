#!/bin/bash

git ls-files ./ | grep -v docs/ | grep -v third_party/ | grep -v vendor/ | grep -v typings/ | grep -v pnpm-lock.yaml | xargs wc -l | /usr/bin/sort -n
