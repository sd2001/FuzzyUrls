from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('',views.index, name="index"),
     path('s/short',views.short, name="short"),
     path('m/mail', views.mailing, name="mailing"),
     path('api/shorten', views.geturl, name="geturl"),
     path('<str:uid>', views.openurl, name="open"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

