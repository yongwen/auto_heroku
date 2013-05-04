# Create your views here.
import json
import re
from django.utils import timezone
import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
import os
from django.template import RequestContext
import heroku
import requests

COMPLETED_TEXT = "Makahiki instance created successfully!"

def home(request):
    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    apps = cloud.apps
    app_dict = {}
    for app in apps:
        app_info = app.__dict__

        today = timezone.now() - datetime.timedelta(minutes=3)
        complete_status = "complete"
        if app_info["slug_size"] is None or app_info["slug_size"] == 0:
            complete_status = "pending"
        elif app_info["created_at"] >= today:
            # if newly created, ping the app url to see if it is up
            r = requests.get('https://%s.herokuapp.com' % app.name)
            print "%s response code=%d" % (app.name, r.status_code)
            if 200 != r.status_code:
                complete_status = "pending"

        app_info["completed_status"] = complete_status
        app_dict[app.name] = app_info
    keys = sorted(app_dict.keys())
    app_list = []
    for key in keys:
        app_list.append((key, app_dict[key]))

    return render_to_response('index.html',
                              {'apps': app_list},
                              context_instance=RequestContext(request))

def delete(request):
    myapp = request.POST['appname']
    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    app = cloud.apps[myapp]
    app.destroy()
    return HttpResponseRedirect(reverse("home", args=()))


def logs(request, appname):
    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    app = cloud.apps[appname]
    logs = app.logs(num=10).split("\n")

    return render_to_response('logs.html',
                          {'appname': appname,
                           'logs': logs},
                          context_instance=RequestContext(request))

def work(request):
    appname = request.POST['appname']

    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    apps = cloud.apps
    print "create app %s" % appname
    try:
        apps.add(appname)
    except:
        pass

    config_json = {
                   "BUILDPACK_URL" : "https://github.com/yongwen/makahiki-buildpack.git",
                   "MAKAHIKI_USE_MEMCACHED" : "True",
                   "MAKAHIKI_USE_HEROKU" : "True",
                   "MAKAHIKI_USE_S3" : "True",
                   "MAKAHIKI_ADMIN_INFO" : settings.MAKAHIKI_ADMIN_INFO,
                   "MAKAHIKI_AWS_ACCESS_KEY_ID" : settings.MAKAHIKI_AWS_ACCESS_KEY_ID,
                   "MAKAHIKI_AWS_SECRET_ACCESS_KEY" : settings.MAKAHIKI_AWS_SECRET_ACCESS_KEY,
                   "MAKAHIKI_AWS_STORAGE_BUCKET_NAME" : settings.MAKAHIKI_AWS_STORAGE_BUCKET_NAME
                }

    # copy from https://github.com/heroku/heroku.py/blob/master/heroku/models.py
    try:
        cloud._http_resource(
            method='PUT',
            resource=('apps', appname, 'config_vars'),
            data=json.dumps(config_json))
    except:
        pass

    try:
        cloud._http_resource(
            method='POST',
            resource=('apps', appname, 'addons', 'memcache'))
    except:
        pass

    sshkey_cmd = "rm -rf .ssh; mkdir .ssh; ssh-keygen -q -N '' -f .ssh/id_rsa"
    os.system(sshkey_cmd)

    knownhosts_cmd = 'echo "|1|v2fAE9r+64rPyeKTVWZamQa95N8=|8cihuAGn19m0ljoDHJITbpNx618= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu8erSx6jh+8ztsfHwkNeFr/SZaSOcvoa8AyMpaerGIPZDB2TKNgNkMSYTLYGDK2ivsqXopo2W7dpQRBIVF80q9mNXy5tbt1WE04gbOBB26Wn2hF4bk3Tu+BNMFbvMjPbkVlC2hcFuQJdH4T2i/dtauyTpJbD/6ExHR9XYVhdhdMs0JsjP/Q5FNoWh2ff9YbZVpDQSTPvusUp4liLjPfa/i0t+2LpNCeWy8Y+V9gUlDWiyYwrfMVI0UwNCZZKHs1Unpc11/4HLitQRtvuk0Ot5qwwBxbmtvCDKZvj1aFBid71/mYdGRPYZMIxq1zgP1acePC1zfTG/lvuQ7d0Pe0kaw==" > .ssh/known_hosts'
    os.system(knownhosts_cmd)

    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    keys = cloud.keys
    for key in keys:
        if not re.search("== .*@(\w+)\.(\w+)", key):
            keys.delete()

    file = open(".ssh/id_rsa.pub")
    for line in file:
        cloud.keys.add(line)

    print "setup ssh key"

    app_source = "git://github.com/yongwen/makahiki-min.git"
    clone_cmd = "rm -rf git-tmp; git clone %s git-tmp; " % app_source

    push_cmd = 'cd git-tmp; git push git@heroku.com:%s.git master; sleep 5; curl -s -o /dev/null http://%s.herokuapp.com/init/; echo %s' % (appname, appname, COMPLETED_TEXT)

    cmd = 'echo "%s" > /tmp/push.sh' % (clone_cmd + push_cmd)
    os.system(cmd)

    print "git clone and push"
    os.system("/bin/bash /tmp/push.sh &")


    return HttpResponseRedirect(reverse("home", args=()))
