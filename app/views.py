from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from .models import URL
import uuid
import pymongo
from pymongo import MongoClient
import os, json
from bson import ObjectId
from bson.json_util import loads, dumps
from Urlshort import settings

client = MongoClient(os.environ.get('mongo'))
db = client[os.environ.get('database')]
coll = db[os.environ.get('collection')]
# Create your views here.
def parse_json(data):
    return json.loads(dumps(data))

# def setcookie(request):
#     html = HttpResponse()
#     html.set_cookie('user', str(uuid.uuid1()), max_age = None)
#     return html


def index(request):
    request.COOKIES['key'] = str(uuid.uuid1())
    response = render(request, 'index.html') 
    response.set_cookie('key', str(uuid.uuid1()))
    return response

def short(request):
    if request.method == 'POST':
        user = request.COOKIES.get('key')
        url = request.POST['link']
        new_url = str(uuid.uuid4())[:4]
        surl = "http://127.0.0.1:8000/i/"+new_url
        sch = URL(uid = user, link = url, new = surl)
        sch.save()
        # return HttpResponse(new_url)
        return render(request, 'index.html', {'user':user, 'url': url, 'new':surl})    

def mailing(request):    
    if request.method == 'POST':        
        mail = request.POST['mail']
        user = request.COOKIES.get('key')
        details = coll.find_one({"uid": user})
        details = parse_json(details)
        surl = details['new']
        try:
            send_mail("Shorten URLs", details['new'], settings.EMAIL_HOST_USER, [mail])
            return render(request, 'index.html', {'user':user, 'new':surl, 'success': True})
        except Exception as e:
            return render(request, 'index.html', {'user':user, 'new':surl, 'success': False})
        
def openurl(request, uid):    
    details = coll.find_one({"new": "http://127.0.0.1:8000/i/"+uid})
    details = parse_json(details)
    full_url = details['link']
    if full_url.startswith("http"):
        return redirect(full_url)
    else:        
        return redirect("http://"+full_url)