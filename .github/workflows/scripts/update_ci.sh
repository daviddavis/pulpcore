#!/usr/bin/env bash

set -eu

remote="update-ci-destination"

git remote add $remote "https://$GITHUB_USER:$GITHUB_TOKEN@github.com/daviddavis/pulpcore.git"
git fetch $remote

if [ -z $1 ]; then
  branches=$(git for-each-ref --format='%(refname:short)' refs/remotes/$remote/)
else
  branches=("$1")
fi

if [ ! -d ../plugin_template ]; then
  echo "Checking out plugin_template"
  git clone https://github.com/pulp/plugin_template.git ../plugin_template
fi

for branch in $branches
do
  echo "Updating CI for $branch"

  temp_branch="update-ci-files-$branch-$RANDOM"
  git switch -c $temp_branch $remote/$branch

  if [ ! -f "template_config.yml" ]; then
    echo "No template_config.yml detected for $branch. Skipping."
    continue
  fi

  pushd ../plugin_template
  ./plugin-template --github pulpcore
  popd

  if [[ `git status --porcelain` ]]; then
    git add -A
    git commit -m"Update CI files" -m"" -m"[noissue]"
    git push -u $remote $temp_branch
    curl -u $GITHUB_USER:$GITHUB_TOKEN \
         -d "{\"title\":\"Update $branch CI\",\"base\":\"$branch\",\"head\":\"$temp_branch\"}" \
         https://api.github.com/repos/daviddavis/pulpcore/pulls
  else
    echo "No updates needed for $branch"
  fi
done
