# Create your views here.
from django.shortcuts import render_to_response
import os
import heroku

def home(request):
    return render_to_response('index.html', {})

def work(request):

    clone_cmd = "git clone git://github.com/yongwen/auto_heroku.git git-tmp"
    print clone_cmd
    os.system(clone_cmd)

    myapp = "yxu-myapp"

    cloud = heroku.from_key('2b0e5db1bdbb23a0f4bc8df29822eb271134e2b6')
    apps = cloud.apps
    print "create app %s" % myapp
    try:
        cloud.apps.add(myapp)
    except:
        pass

    sshkey_cmd = "mkdir .ssh; ssh-keygen -q -N '' -f .ssh/id_rsa"
    print sshkey_cmd
    os.system(sshkey_cmd)

    knowhosts_cmd = 'echo "|1|v2fAE9r+64rPyeKTVWZamQa95N8=|8cihuAGn19m0ljoDHJITbpNx618= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu8erSx6jh+8ztsfHwkNeFr/SZaSOcvoa8AyMpaerGIPZDB2TKNgNkMSYTLYGDK2ivsqXopo2W7dpQRBIVF80q9mNXy5tbt1WE04gbOBB26Wn2hF4bk3Tu+BNMFbvMjPbkVlC2hcFuQJdH4T2i/dtauyTpJbD/6ExHR9XYVhdhdMs0JsjP/Q5FNoWh2ff9YbZVpDQSTPvusUp4liLjPfa/i0t+2LpNCeWy8Y+V9gUlDWiyYwrfMVI0UwNCZZKHs1Unpc11/4HLitQRtvuk0Ot5qwwBxbmtvCDKZvj1aFBid71/mYdGRPYZMIxq1zgP1acePC1zfTG/lvuQ7d0Pe0kaw==" > .ssh/known_hosts'
    os.system(knowhosts_cmd)

    file = open(".ssh/id_rsa.pub")
    for line in file:
        cloud.keys.add(line)

    push_cmd = "cd git-tmp; git push git@heroku.com:%s.git master" % myapp
    print push_cmd
    os.system(push_cmd)


    return render_to_response('work.html', {})