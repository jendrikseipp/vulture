# Contributing to Vulture

## Creating and cloning a fork

Fork the Vulture repository on GitHub by clicking the "fork" button on the
top right. Then clone your fork to your local machine:

    $ git clone https://github.com/USERNAME/vulture.git # Use your GitHub username.
    $ cd vulture

## Installation

We recommend using a Python virtual environment to isolate the
installation of vulture.

### Setting up the virtual environment

You can read more about `virtualenv` in the [virtualenv
documentation](http://virtualenv.readthedocs.org).

To install the `virtualenv` package using `pip`, run:

    $ python3 -m pip install virtualenv

Now you can create your own environment (named `vulture_dev`):

    $ virtualenv vulture_dev

Now, whenever you work on the project, activate the corresponding
environment.

  - On **Unix-based** systems, this can be done with:

        $ source vulture_dev/bin/activate

  - And on **Windows** this is done with:

        $ vulture_dev\scripts\activate

To leave the virtual environment use:

    (vulture_dev)$ deactivate

### Installing vulture

Navigate to your cloned `vulture` directory, and run the following to
install in development mode:

    $ pip install --editable .

### Installing test tools

Vulture uses tox for testing. You can read more about it in the [tox
documentation](https://tox.readthedocs.io).

To install `tox`, run:

    $ pip install tox

It's also recommended that you use `pre-commit` to catch style errors
early:

    $ pip install pre-commit
    $ pre-commit install

## Coding standards

### Creating a new branch

To start working on a pull request, create a new branch to work on. You
should never develop on your main branch because your main branch
should always be synchronized with the main repo’s main branch, which
is challenging if it has new commits. Create a branch using:

    $ git checkout -b your-new-branch

#### Naming branches

Branch names should describe the feature/issue that you want to work on,
but at the same time be short.

### Commits

Each commit should be atomic and its message should adequately describe
the change in a clear manner. Use imperative, e.g., "Fix issue12." instead
of "Fixed issue12.". Please make sure that you only fix the issue at hand
or implement the desired new feature instead of making "drive-by" changes
like adding type hints.

### Formating and linting

Run `pre-commit` using:

    $ pre-commit run --all-files

## Testing

Run `tox` using:

    $ tox

## Pull requests

### How to send a pull request?

Push your changes to your fork with:

    $ git push --set-upstream origin BRANCHNAME

Then visit your fork on GitHub, change the branch to the one you committed
to, and click the `New Pull Request` button.

### Follow-up

In case your PR needs to be updated (tests fail or reviewer requests some
changes), update it by committing on top of your branch. It is not
necessary to amend your previous commit, since we will usually squash all
commits when merging anyway.

### Feedback

Take reviewer feedback positively. It's unlikely for a PR to be merged on
the first attempt, but don’t worry that’s just how it works. It helps to
keep the code clean.
