#!/bin/bash

sed -r -e 's/^#{1,3} \[/## [/' -i CHANGELOG.md
npx prettier --write CHANGELOG.md
