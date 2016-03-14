from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', include('cabs_admin.urls', namespace='cabs_admin')),
    url(r'', include('cabs_admin.urls', namespace='cabs_admin')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
