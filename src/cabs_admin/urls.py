from django.conf.urls import patterns, url

from cabs_admin import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^logout/$', views.logoutView, name='logout'),
    url(r'^machines/$', views.machinesPage, name='machinesPage'),
    url(r'^machines/submit/$', views.setMachines, name='setMachines'),
    url(r'^machines/toggle/$', views.toggleMachines, name='toggleMachines'),
    url(r'^machines/toggle/(?P<selected_machine>\w+)/$', views.machinesPage, name='machinesPage'),
    url(r'^machines/comment/$', views.commentMachines, name='commentMachines'),
    url(r'^pools/$', views.poolsPage, name='poolsPage'),
    url(r'^pools/submit/$', views.setPools, name='setPools'),
    url(r'^pools/toggle/$', views.togglePools, name='togglePools'),
    url(r'^pools/toggle/(?P<selected_pool>\w+)/$', views.poolsPage, name='poolsPage'),
    url(r'^pools/comment/$', views.commentPools, name='commentPools'),
    url(r'^settings/$', views.settingsPage, name='settingsPage'),
    url(r'^settings/submit/$', views.setSettings, name='setSettings'),
    url(r'^settings/rm/$', views.rmSettings, name='rmSettings'),
    url(r'^blacklist/$', views.blacklistPage, name='blacklistPage'),
    url(r'^blacklist/submit/$', views.setBlacklist, name='setBlacklist'),
    url(r'^blacklist/toggle/$', views.toggleBlacklist, name='toggleBlacklist'),
    url(r'^whitelist/submit/$', views.setWhitelist, name='setWhitelist'),
    url(r'^whitelist/rm/$', views.rmWhitelist, name='rmWhitelist'),
    url(r'^history/$', views.historyPage, name='historyPage'),
    url(r'^(?P<permission_error>(view)|(edit)|(disable))/$', views.index, name='index'),
)
