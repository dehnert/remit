from distutils.core import setup

setup(
    name = "remit",
    version = "0.7.0",
    packages = ["remit"],
    install_requires = [
        "pysapweb",
        "django",
        "django-treebeard",
    ],

    author = "Alex Dehnert",
    author_email = "remit@mit.edu",
    url = "https://remit.scripts.mit.edu/trac/",
    description = 'Tool for helping MIT student groups reimburse members ("remit" money to them)',
    license = "LICENSE.txt",

    keywords = ["mit", "accounting"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
)
