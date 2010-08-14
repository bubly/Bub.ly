from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from models import *
from utils import to36
from connect_redis import get_client
redis_ob = get_client()

def shorten_url(request):
    url = request.GET.get('url', None)
    # validate the url here
    if not url: raise Http404
    url_object = UrlModel(url_data={'url':url})
    url_object.save()
    # if authenticated user set url to his account
    if request.session.has_key("user_id"):
        redis_ob.lpush("user:urls:%d" %request.session['user_id'], "url:"+str(url_object.id))
    return HttpResponse(url_object.get_short_url())

def file_upload(request):
    if not request.method == 'POST': raise Http404
    if not request.FILES: raise Http404
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'files')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'files'))
    
    url_id = redis_ob.incr('counter:url')
    temp_file_name = to36(url_id)
    file_data = request.FILES['file']
    sub = file_data.name.split('.')[-1]
    destination = open(os.path.join(settings.MEDIA_ROOT, 'files', temp_file_name+'.'+sub), 'wb+')
     for chunk in file_data.chunks():
        destination.write(chunk)
    url = settings.SHORT_URL+"static/files/"+temp_file_name+'.'+sub
    url_object.save(url_id=url_id)
    # if authenticated user set url to his account
    if request.session.has_key("user_id"):
        redis_ob.lpush("user:urls:%d" %request.session['user_id'], "url:"+str(url_object.id))
    return HttpResponse(url_object.get_short_url())

def expand_url(request, slug):
    try:
        url_id = int(slug, 36)
    except:
        raise Http404

def home(request):
    try: 
        page = int(request.GET.get('page', 1))
        assert page >= 1
    except:
        page = 1
    if request.session.has_key("user_id"):
        user_id = request.session["user_id"]
        if redis_ob.hexists("user:%s" %str(user_id), "email"):
            url_ids = redis_ob.lrange("user:urls:%s" %str(user_id), (page-1)*50, page*50)
            if page > 1 and not url_ids: raise Http404
            urls = []
            for url_id in url_ids:
                urls.append(UrlModel.get_by_id(url_id=url_id))
            return render_to_response('home.html', {'urls': urls}, context_instance=RequestContext(request))
    return render_to_response('landing.html', {}, context_instance=RequestContext(request))
