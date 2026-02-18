from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("trading/", include("trading.urls")),
    path("users_authentication/", include("users_authentication.urls")), 
    path("admin/", admin.site.urls),
]