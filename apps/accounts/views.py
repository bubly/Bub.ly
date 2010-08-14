from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.hashcompat import md5_constructor
from forms import RegisterForm, LoginForm, SettingsForm

from connect_redis import get_client
redis_ob = get_client()

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user_id = form.save()
            request.session['user_id'] = user_id
            return HttpResponseRedirect("/")
    else:
        form = RegisterForm()
    return render_to_response("register.html", {'form': form}, context_instance=RequestContext(request))

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # get the id of the user and set session
            user_id = redis_ob.get("user:email:%s" %md5_constructor(form.cleaned_data['email']).hexdigest())
            request.session['user_id'] = user_id
            return HttpResponseRedirect("/")
    else:
        # if user is already logged in redirect to /
        if request.session.has_key('user_id'): return HttpResponseRedirect("/")
        form = LoginForm()
    return render_to_response("landing.html", {'form': form}, context_instance=RequestContext(request))

def logout(request):
    request.session.flush()
    return HttpResponseRedirect("/")

def settings(request):
    # if user is not logged in raise 404
    if not request.session.has_key("user_id"): raise Http404
    user_id = request.session["user_id"]
    if request.method == "POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            pass # set the email and password of the user
    elif request.method =="DELETE":
        # delete user related data from redis
        user_email = redis_ob.hget("user:%s" %user_id, "email")
        redis_ob.delete(["user:email:%s" %md5_constructor(user_email).hexdigest(), "user:%s" %user_id, "user:urls:%s" %user_id])
        # logout the user
        request.session.flush()
        return HttpResponse("success", mimetype="application/javascript")
    else:
        email = redis_ob.hget("user:%s" %user_id, "email")
        form = SettingsForm(initial={'email': email})
    return render_to_response('settings.html', {'form': form}, context_instance=RequestContext(request))
