# Contributing to Vulture

## Creating and cloning a fork

Fork the repository on GitHub and do the following:

    $ git clone https://github.com/jendrikseipp/vulture.git
    $ cd vulture
    $ git remote add origin https://github.com/USERNAME/vulture # Use your GitHub username.

## Installation

We recommend using `virtualenv` to isolate the installation of vulture.

### Setting up virtualenv

You can read more about `virtualenv` in the [virtualenv
documentation](http://virtualenv.readthedocs.org).

To install the `virtualenv` package using `pip`, run:

    $ pip install virtualenv

Once you have `virtualenv` installed, create your own environment (named
`vulture_dev`):

    $ virtualenv vulture_dev

Now, whenever you work on the project, activate the corresponding
environment.

  - On **Unix-based** systems, this can be done with:

        $ source vulture_dev/bin/activate

  - And on **Windows** this is done with:

        $ vulture_dev\scripts\activate

For deactivation, use:

    (vulture_dev)$ deactivate

### Installing vulture

Navigate to your cloned `vulture` directory, and run the following to
install in development mode:

    $ pip install -e .

### Installing tox

Vulture uses tox for testing. You can read more about it in the [tox
documentation](https://tox.readthedocs.io).

To install `tox`, run:

    $ pip install tox

## Coding standards

### Creating a new branch

To start working on a pull request, create a new branch to work on. You
should never develop on your master branch because your master branch
should always be synchronized with the main repo’s master branch, which
is challenging if it has new commits. Create a branch using:

    $ git checkout -b your-new-branch

#### Naming branches

Branch names should describe the feature/issue that you want to work on,
but at the same time be short.

### Commits

Each commit should be atomic and its message should adequately describe
the change in a clear manner. Use imperative, e.g., "Fix issue12."
instead of "Fixed issue12.".

## Testing

Run `tox` using:

    $ tox

## Pull requests

### How to send a pull request?

Visit your fork on GitHub, change the branch to the one you committed
to, and click the `New Pull Request` button.

### Follow-up

In case your PR needs to be updated (tests fail or reviewer requests
some changes), update it by either committing atop your branch or
amending your previous commit (using `git commit --amend`, and then `git
push -f` to force push your changes).

### Feedback

Take reviewer feedback positively, it’s unlikely for a PR to be merged
on first attempt -- but don’t worry that’s just how it works. It helps
keep the code clean.
