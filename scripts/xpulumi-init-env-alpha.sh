#! /bin/bash

set -eo pipefail

echo "Please be patient..." >&2
# We need to use command substitution rather than a simple pipe here because
# The final script needs to read config answers fro stdin
python3 <(curl http://public.mckelvie.org/vpyapp.py) \
  -v --tb run --update git+https://github.com/sammck/xpulumi-installer.git \
  xpulumi-installer --tb install --package git+https://github.com/sammck/xpulumi.git
