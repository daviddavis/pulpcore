#!/bin/bash

# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github pulpcore' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

set -euv

# make sure this script runs at the repo root
cd "$(dirname "$(realpath -e "$0")")"/../../..

export PULP_URL="${PULP_URL:-http://pulp}"

export REPORTED_VERSION=$(http pulp/pulp/api/v3/status/ | jq --arg plugin core --arg legacy_plugin pulpcore -r '.versions[] | select(.component == $plugin or .component == $legacy_plugin) | .version')
export DESCRIPTION="$(git describe --all --exact-match `git rev-parse HEAD`)"
if [[ $DESCRIPTION == 'tags/'$REPORTED_VERSION ]]; then
  export VERSION=${REPORTED_VERSION}
else
  export EPOCH="$(date +%s)"
  export VERSION=${REPORTED_VERSION}${EPOCH}
fi

export response=$(curl --write-out %{http_code} --silent --output /dev/null https://rubygems.org/gems/pulpcore_client/versions/$VERSION)

if [ "$response" == "200" ];
then
  echo "pulpcore client $VERSION has already been released. Installing from RubyGems.org."
  gem install pulpcore_client -v $VERSION
  touch pulpcore_client-$VERSION.gem
  tar cvf ruby-client.tar ./pulpcore_client-$VERSION.gem
  exit
fi

cd ../pulp-openapi-generator

./generate.sh pulpcore ruby $VERSION
cd pulpcore-client
gem build pulpcore_client
gem install --both ./pulpcore_client-$VERSION.gem
tar cvf ../../pulpcore/ruby-client.tar ./pulpcore_client-$VERSION.gem
