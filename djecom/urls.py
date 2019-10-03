
from django.contrib import admin
from django.urls import path, include
from core import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('',views.board_index,name = 'home')
]
