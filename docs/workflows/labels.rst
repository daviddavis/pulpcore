Labels
======

.. warning::
   Support for labels is provided as a tech preview in Pulp 3. Functionality may not work or may be
   incomplete. Also, backwards compatibility when upgrading is not guaranteed.

Pulp provides a way to add key/value data to many resources (e.g. repositories, remotes,
distributions) in the form of labels. Labels are also useful for categorizing and filtering
resources. In the API, labels appear as a dictionary field that maps keys (strings) to values (also
strings).

Managing labels
---------------

Creating labels
^^^^^^^^^^^^^^^

To create labels::

    # create a new repository
    pulp file repository create --name myrepo

    # set some labels
    pulp file repository label set --name myrepo --key environment --value production
    pulp file repository label set --name myrepo --key reviewed --value true

    # call show to view the repo's labels
    pulp file repository show --name myrepo

On show, you should see the new labels that have been created::

    {
      "pulp_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/",
      "pulp_created": "2021-01-29T17:54:17.084105Z",
      "versions_href":
      "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/versions/",
      "pulp_labels": {
        "environment": "production",
        "reviewed": "true"
      },
      "latest_version_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/versions/0/",
      "name": "myrepo",
      "description": null,
      "remote": null
    }

Updating labels
^^^^^^^^^^^^^^^

To update an existing label, call set again::

    # update the label
    pulp file repository label set --name myrepo --key reviewed --value false

    # call show to view the repo's labels
    pulp file repository show --name myrepo

On show, you should now see::

    {
      "pulp_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/",
      "pulp_created": "2021-01-29T17:54:17.084105Z",
      "versions_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/versions/",
      "pulp_labels": {
        "environment": "production",
        "reviewed": "false"
      },
      "latest_version_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/versions/0/",
      "name": "myrepo",
      "description": null,
      "remote": null
    }

Unsetting labels
^^^^^^^^^^^^^^^^

To remove a label from a resource, call the unset command::

    # update the label
    pulp file repository label unset --name myrepo --key reviewed

    # call show to view the repo's labels
    pulp file repository show --name myrepo

On show, you should now see::

    {
      "pulp_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/",
      "pulp_created": "2021-01-29T17:54:17.084105Z",
      "versions_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/versions/",
      "pulp_labels": {
        "environment": "production"
      },
      "latest_version_href": "/pulp/api/v3/repositories/file/file/13477a92-b811-4436-a76a-d2469a17a62e/versions/0/",
      "name": "myrepo",
      "description": null,
      "remote": null
    }

Filtering
---------

Pulp provides a ``pulp_label_select`` field for filtering resources by label. The value for this
field must be url-encoded. The following operations are supported:

- ``environment=production`` - environment is production
- ``environment!=production`` - environment is not production
- ``environment~prod`` - environment contains prod (case insensitive)
- ``enviroment`` - has a label with key of environment
- ``!environment`` - does not have a label with a key of environment

Multiple terms can be combined with ``,``:

- ``environment=production,reviewed=true`` - returns resources with labels where environment is
  production AND reviewed is true
- ``environment,reviewed=false`` - returns resources with an environment label and where reviewed is
  false

To filter with httpie::

    http :/pulp/api/v3/repositories/file/file/ pulp_label_select=="environment~prod"
    http :/pulp/api/v3/repositories/file/file/ pulp_label_select=="environment,reviewed=true"

To filter using the CLI::

    pulp file repository list --label-select="environment~prod"
    pulp file repository list --label-select="environment,reviewed=true"
