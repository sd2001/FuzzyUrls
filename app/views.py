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

client = MongoClient("mongodb+srv://sd:sddb@cluster0.3kt8t.mongodb.net/SD_URLS?retryWrites=true&w=majority")
db = client["SD_URLS"]
coll = db["urls"]
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
        surl = "http://davgo.cf/"+new_url
        sch = {'uid' : user, 'link' : url, 'new' : surl}
        coll.insert_one(sch)
        # return HttpResponse(new_url)
        return render(request, 'index.html', {'user':user, 'url': url, 'new':surl})    

def mailing(request):    
    if request.method == 'POST':        
        mail = request.POST['mail']
        user = request.COOKIES.get('key')
        details = coll.find_one({"uid": user})
        details = parse_json(details)
        mssg = f"Hey,\nThanks for using http://davgo.cf/.\nThe new url for {details['link']} is:\n{details['new']}.\nRegards,\nSwarnabha Das\n(Ph No : 9836088355)"
        surl = details['new']
        try:
            send_mail("Shorten URLs", mssg, settings.EMAIL_HOST_USER, [mail])
            return render(request, 'index.html', {'user':user, 'new':surl, 'success': True})
        except Exception as e:
            return render(request, 'index.html', {'user':user, 'new':surl, 'success': False})
        
def openurl(request, uid):  
    if uid is not None:  
        details = coll.find_one({"new": "http://davgo.cf/"+uid})
        details = parse_json(details)
        full_url = details['link']
        if full_url.startswith("http"):
            return redirect(full_url)
        else:        
            return redirect("http://"+full_url)