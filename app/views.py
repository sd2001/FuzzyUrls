from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
import urllib3
from django.views.decorators.csrf import csrf_exempt
from .models import URL
import uuid
import pymongo
from pymongo import MongoClient
import os, json
from bson import ObjectId
from bson.json_util import loads, dumps
from Urlshort import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status


client = MongoClient(os.environ.get('mongo'))
db = client[os.environ.get('database')]
coll = db[os.environ.get('collection')]
tokendb = db[os.environ.get('tokendb')]

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
        if url.find('davgo') != -1:
            return render(request, 'index.html', {'status': 'Funny'})
        http = urllib3.PoolManager()
        valid = False
        if url.startswith("http"):            
            url = url	
        else:
            url = "http://"+url
        
        try:
            ret = http.request('GET',url)
            if ret.status == 200:
                valid = True
        except Exception as e:
            valid = False
            
        if valid == True:
            new_url = str(uuid.uuid4())[:5]
            surl = "http://davgo.cf/"+new_url
            sch = {'uid' : user, 'link' : url, 'new' : surl}
            coll.insert_one(sch)
            return render(request, 'short.html', {'user':user, 'url': url, 'new':surl}) 
        else:
            return render(request, 'index.html', {'status': False})
    return redirect('/')  
         

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
            return render(request, 'short.html', {'user':user, 'new':surl, 'success': True})
        except Exception as e:
            return render(request, 'short.html', {'user':user, 'new':surl, 'success': False})
    return redirect('/')
        
def openurl(request, uid):  
    if uid != "": 
        details = coll.find_one({"new": "http://davgo.cf/"+uid})
        details = parse_json(details)
        if details:
            full_url = details['link']
            if full_url.startswith("http"):
                return redirect(full_url)
            else:        
                return redirect("http://"+full_url)
        else:
            return HttpResponse(404)
        
def generateToken(request):
    pass

@csrf_exempt
@api_view(["POST"])
def geturl(request):
    # print(request.POST)
    if request.method == 'POST':
        try:    
            url = request.POST["link"]
        except Exception as e:
            return Response({
                    "error":{
                        "status": "Missing Paramater",
                        "additional": "Link not Entered"
                    },
                    "code":400
                }, 
                status = status.HTTP_400_BAD_REQUEST)
            
        try:
            token = request.POST["token"]
        except Exception as e:
            return Response({
                    "error":{
                        "status": "Authentication Error",
                        "additional": "Please provide an API Token"
                    },
                    "code":400
                }, 
                status = status.HTTP_400_BAD_REQUEST)
            
            
               
        details = tokendb.find_one({'token':token})
        
        if details:
            if int(details['frequency']) <= 0:
                return Response({
                    "error":{
                        "status": "Usage Quota Exceeded",
                        "additional": "Max 20 calls allowed per token"
                    },
                    "code":400
                }, 
                status = status.HTTP_400_BAD_REQUEST)
            
            new_url = str(uuid.uuid4())[:5]
            surl = "http://davgo.cf/"+new_url
            sch = {'uid' : "API CALL", 'link' : url, 'new' : surl}
            coll.insert_one(sch) 
            tokendb.update_one({"token":token},{"$set":{"frequency": details['frequency']-1}})
            return Response({
                "Response":{
                    "New Url": surl,
                    "Original Url": url,
                    "API Calls Remaining": details['frequency'],
                },
                "code":200
            },
            status = status.HTTP_200_OK)
        elif details == None:
            return Response({
                    "error":{
                        "status": "Invalid Credentials",
                        "additional": "Token doesn't match our records"
                    },
                    "code": 400,
                }, 
                status = status.HTTP_400_BAD_REQUEST)			
    
  
