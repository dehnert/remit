Installing Remit
================

Development installs
--------------------

Installing Remit on a Linux machine for development purposes is quite straightforward:

1. Create and enter a virtualenv for Remit
2. Install Remit and its dependencies
3. Create the config files and initialize the database
4. Run the dev server

As a sequence of commands, this is::

    virtualenv --prompt="(venv/remit)" remit-venv   # create the virtualenv
    cd remit-venv/                                  # enter it (filesystem)
    . bin/activate                                  # enter it (environment)
    pip install --editable git+/mit/remit/remit.git#egg=remit   # install Remit
    cd src/remit/remit/                             # change into the main source directory
    ./settings/init-dev.sh                          # set up for development
    ./runserver 8006                                # run the dev server

Production installs
-------------------

For production installs of Remit, a number of additional factors become important:

- properly integrating with the web server (and not just using Django's server)
- using appropriate email addresses (and actually sending mail)
- using the group's real account structure

As a result, the installation process is much more involved:

1.  At heart, Remit is just another Django application. Do whatever you normally need to do to install a Django application and connect it to your web server.
2.  Create settings/local.py containing:

    - ``SECRET_KEY``
    - ``ADMINS``
    - Database configuration
    - ``SERVER_EMAIL``
    - ``SITE_URL_BASE`` -- full URL (including protocol and hostname; used in emails)
    - Any other settings you want

3.  Create settings/local_after.py (possibly empty)
4.  Run "./manage.py syncdb && ./manage.py migrate" to set up the database
5.  Run "./util/setup.py" to install the basic accounts (Assets, Expenses, Income, plus some common GLs)
6.  Run "./util/add_accounts" to add new accounts

    - First argument: path to the base account --- for example, "Accounts.Assets"
    - Standard input: accounts to add, separated by newline (to specify account numbers, add a tab followed by the account number)

7.  Use the admin interface to set up appropriate BudgetTerm(s)
8.  Make sure that the remit/media/ directory gets served to the web as media
