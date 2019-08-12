#!/bin/bash

ALL_TESTS=($(find tests -type f -name "*.py"))

for TEST in "${ALL_TESTS[@]}"
do
  if [[ "$TEST" == *__init__.py ]]; then
    continue
  fi
  TEST=${TEST//.py/}
  TEST=${TEST//\//.}
  echo
  echo Running tests on file: $TEST
  python3 -m unittest $TEST
done
