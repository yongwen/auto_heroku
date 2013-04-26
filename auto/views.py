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
    if not myapp in apps:
        print "create app %s" % myapp
        cloud.apps.add(myapp)

    push_cmd = "cd git-tmp;git push git@heroku.com:%s.git master" % myapp
    print push_cmd
    os.system(push_cmd)


    return render_to_response('work.html', {})