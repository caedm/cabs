from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #url(r'(^$)|(^admin/)', include('cabs_admin.urls', namespace='cabs_admin', app_name='cabs_admin')),
    url(r'^admin/', include('cabs_admin.urls', namespace='cabs_admin')),
    url(r'^$', include('cabs_admin.urls', namespace='cabs_admin')),
)
