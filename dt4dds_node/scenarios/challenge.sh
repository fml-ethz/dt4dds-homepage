#!/bin/bash
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
set -e
set -x

# run the challenge
"$BASE_PATH"/dt4dds-challenges/bin/dt4dds-challenges "$1" "$2" "$3" "$4" --strict

# zip the output
gzip "$3"
gzip "$4"

# remove intermediate files
rm -f "$3"
rm -f "$4"

exit