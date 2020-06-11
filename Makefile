COMMIT=HEAD

setup-pre-commit-hook:
	pre-commit install
	pre-commit install-hooks

setup-post-commit-hook:
	echo 'python ./.travis/validate_commit_message.py HEAD' > .git/hooks/post-commit

install-hooks: setup-post-commit-hook setup-pre-commit

run-post-commit:
	python ./.travis/validate_commit_message.py $(COMMIT)

run-pre-commit:
	pre-commit run --files $$(find -regex '.*\.\(py\|yaml\|yml\|md\)') -v
