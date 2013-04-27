# Create your views here.
from django.shortcuts import render_to_response
import os
from django.template import RequestContext
import heroku

def home(request):
    return render_to_response('index.html', {}, context_instance=RequestContext(request))

def work(request):
    myapp = request.POST['appname']

    app_source = "git@github.com:yongwen/makahiki-min.git"
    clone_cmd = "git clone %s git-tmp" % app_source
    print clone_cmd
    os.system(clone_cmd)

    cloud = heroku.from_key('2b0e5db1bdbb23a0f4bc8df29822eb271134e2b6')
    apps = cloud.apps
    print "create app %s" % myapp
    try:
        apps.add(myapp)
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

    manage_command = "python makahiki/manage.py"
    fixture = "default_all.json"
    os.system("%s syncdb --noinput --migrate --verbosity 0" % manage_command)

    print "setting up default data..."
    os.system("%s setup_test_data rounds 1" % manage_command)
    os.system("%s loaddata -v 0 %s" % (manage_command, fixture))
    os.system("%s setup_test_data all 2" % manage_command)

    return render_to_response('work.html', {}, context_instance=RequestContext(request))