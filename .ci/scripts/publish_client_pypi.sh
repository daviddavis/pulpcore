#!/bin/bash

# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github pulpcore' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

set -euv

export PULP_URL="${PULP_URL:-http://pulp}"

# make sure this script runs at the repo root
cd "$(dirname "$(realpath -e "$0")")"/../..

pip install twine

export REPORTED_VERSION=$(http pulp/pulp/api/v3/status/ | jq --arg plugin core --arg legacy_plugin pulpcore -r '.versions[] | select(.component == $plugin or .component == $legacy_plugin) | .version')
export DESCRIPTION="$(git describe --all --exact-match `git rev-parse HEAD`)"
if [[ $DESCRIPTION == 'tags/'$REPORTED_VERSION ]]; then
  export VERSION=${REPORTED_VERSION}
else
  # Daily publishing of development version (ends in ".dev" reported as ".dev0")
  if [ "${REPORTED_VERSION%.dev*}" == "${REPORTED_VERSION}" ]; then
    echo "Refusing to publish bindings. $REPORTED_VERSION does not contain 'dev'."
    exit 1
  fi
  export EPOCH="$(date +%s)"
  export VERSION=${REPORTED_VERSION}${EPOCH}
fi

export response=$(curl --write-out %{http_code} --silent --output /dev/null https://pypi.org/project/pulpcore-client/$VERSION/)

if [ "$response" == "200" ];
then
  echo "pulpcore $VERSION has already been released. Skipping."
  exit
fi

cd ../pulp-openapi-generator

./generate.sh pulpcore python $VERSION
cd pulpcore-client
python setup.py sdist bdist_wheel --python-tag py3
twine check dist/* || exit 1
twine upload dist/* -u pulp -p $PYPI_PASSWORD
exit $?
