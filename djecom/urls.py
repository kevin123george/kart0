from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from core import views
import debug_toolbar
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('',views.board_index,name = 'home'),
    path('__debug__/', include(debug_toolbar.urls)),
]
