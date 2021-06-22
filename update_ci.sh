branches="$1"

git remote add upstream "https://{$GITHUB_USER}:{$GITHUB_TOKEN}@github.com/pulpcore.git"

if [ -z $branches ]; then
  branches=$(git branch)
fi

git clone https://github.com/pulp/plugin_template.git ../plugin_template

for branch in $branches
do
  temp_branch="update-ci-files-$branch-$RANDOM"
  git switch -c $temp_branch $branch
  pushd ../plugin_template
  ./plugin_template --github pulpcore
  popd
  git commit -am"Update CI files\n\n[noissue]"
  git push upstream $br:update-ci-files-$(uuidgen)
  curl -u $GITHUB_USER:$GITHUB_TOKEN \
       -d "{\"title\":\"Update $branch CI\",\"base\":\"$branch\", \"head\":\"$temp_branch\"}"
    https://api.github.com/repos/pulp/pulpcore/pulls
done

