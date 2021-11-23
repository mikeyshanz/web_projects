from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = "Qlairbert Administration"
admin.site.site_title = "Qlairbert Admin Portal"
admin.site.index_title = "Welcome to Qlairbert Admin Portal"

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
