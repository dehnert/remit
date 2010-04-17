#!/usr/bin/python

import os
import subprocess
import sys
import re
import datetime
from mechanize import Browser

pdfviewer = 'evince'
django_username = 'downloader'

from settings import *


def id_predicate(value):
    def _predicate(form):
        if 'id' in form.attrs:
            if form.attrs['id'] == value:
                return True
        return False
    return _predicate

def login2Admin(br):
    # Log in to the admin interface
    br.open(baseurl + 'admin/')
    assert br.viewing_html()
    sys.stderr.write("Viewing '%s'\n" % (br.title(), ))
    assert br.title() == "Log in | Django site admin"
    br.select_form(predicate=id_predicate('login-form'))
    # Browser passes through unknown attributes (including methods)
    # to the selected HTMLForm (from ClientForm).
    br["username"] = django_username  # (the method here is __setitem__)
    br["password"] = password  # (the method here is __setitem__)
    response2 = br.submit()  # submit current form

def getLaTeX(br, latex_file, ):
    br.open(baseurl + 'vouchers/generate/')
    if br.viewing_html():
        print br.response().get_data()
        assert not br.viewing_html()
    latex_file.write(br.response().get_data())

if __name__ == '__main__':
    label = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    texpath  = pathtpl % { 'label':label, 'ext':'tex' }
    pdfpath  = pathtpl % { 'label':label, 'ext':'pdf' }
    texdir, texfile = os.path.split(texpath)

    br = Browser()
    login2Admin(br)
    texfileobj = open(texpath, 'w')
    getLaTeX(br, texfileobj, )
    texfileobj.close()

    subprocess.check_call(['pdflatex', texfile], cwd=texdir)
    subprocess.check_call(['pdflatex', texfile], cwd=texdir)
    subprocess.check_call([pdfviewer, pdfpath])
