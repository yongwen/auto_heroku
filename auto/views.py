# Create your views here.
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
import os
from django.template import RequestContext
import heroku

def home(request):
    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    apps = cloud.apps
    app_dict = {}
    for app in apps:
        app_dict[app.name] = app.__dict__
    return render_to_response('index.html',
                              {'apps': app_dict},
                              context_instance=RequestContext(request))

def delete(request):
    myapp = request.POST['appname']
    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    app = cloud.apps[myapp]
    app.destroy()
    return  HttpResponseRedirect(reverse("home", args=()))


def work(request):
    myapp = request.POST['appname']

    app_source = "git://github.com/yongwen/makahiki-min.git"
    clone_cmd = "rm -rf git-tmp; git clone %s git-tmp" % app_source
    print clone_cmd
    os.system(clone_cmd)

    cloud = heroku.from_key(settings.MAKAHIKI_HEROKU_KEY)
    apps = cloud.apps
    print "create app %s" % myapp
    try:
        apps.add(myapp)
    except:
        pass

    app = cloud.apps[myapp]

    app.config['BUILDPACK_URL'] = 'https://github.com/yongwen/makahiki-buildpack.git'
    app.config['MAKAHIKI_USE_MEMCACHED'] = "True"
    app.config['MAKAHIKI_USE_HEROKU'] = "True"
    app.config['MAKAHIKI_USE_S3'] = "True"
    app.config['MAKAHIKI_ADMIN_INFO'] = settings.MAKAHIKI_ADMIN_INFO
    app.config['MAKAHIKI_AWS_ACCESS_KEY_ID'] = settings.MAKAHIKI_AWS_ACCESS_KEY_ID
    app.config['MAKAHIKI_AWS_SECRET_ACCESS_KEY'] = settings.MAKAHIKI_AWS_SECRET_ACCESS_KEY
    app.config['MAKAHIKI_AWS_STORAGE_BUCKET_NAME'] = settings.MAKAHIKI_AWS_STORAGE_BUCKET_NAME

    sshkey_cmd = "mkdir .ssh; ssh-keygen -q -N '' -f .ssh/id_rsa"
    print sshkey_cmd
    os.system(sshkey_cmd)

    knowhosts_cmd = 'echo "|1|v2fAE9r+64rPyeKTVWZamQa95N8=|8cihuAGn19m0ljoDHJITbpNx618= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu8erSx6jh+8ztsfHwkNeFr/SZaSOcvoa8AyMpaerGIPZDB2TKNgNkMSYTLYGDK2ivsqXopo2W7dpQRBIVF80q9mNXy5tbt1WE04gbOBB26Wn2hF4bk3Tu+BNMFbvMjPbkVlC2hcFuQJdH4T2i/dtauyTpJbD/6ExHR9XYVhdhdMs0JsjP/Q5FNoWh2ff9YbZVpDQSTPvusUp4liLjPfa/i0t+2LpNCeWy8Y+V9gUlDWiyYwrfMVI0UwNCZZKHs1Unpc11/4HLitQRtvuk0Ot5qwwBxbmtvCDKZvj1aFBid71/mYdGRPYZMIxq1zgP1acePC1zfTG/lvuQ7d0Pe0kaw==" > .ssh/known_hosts'
    os.system(knowhosts_cmd)

    file = open(".ssh/id_rsa.pub")
    for line in file:
        cloud.keys.add(line)

    push_cmd = "cd git-tmp; git push git@heroku.com:%s.git master &" % myapp
    print push_cmd
    os.system(push_cmd)

    return  HttpResponseRedirect(reverse("home", args=()))
