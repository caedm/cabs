from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import views
from django.contrib.auth.decorators import login_required, user_passes_test

from cabs_admin.models import Machines
from cabs_admin.models import Current
from cabs_admin.models import Pools
from cabs_admin.models import Settings
from cabs_admin.models import Blacklist
from cabs_admin.models import Whitelist
from cabs_admin.models import Log

from django.conf import settings

import collections
import logging
import logging.handlers

logger = logging.getLogger("interface:views.py")
logger.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address='/dev/log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def can_view(user):
    if len(settings.CABS_LDAP_CAN_VIEW_GROUPS) == 0:
        return True
    can = False
    for group in settings.CABS_LDAP_CAN_VIEW_GROUPS:
        can = can or user.groups.filter(name=group).count() > 0
    
    if not can:
        can = can or can_disable(user)
    
    return can 

def can_disable(user):
    if len(settings.CABS_LDAP_CAN_DISABLE_GROUPS) == 0:
        return True
    can = False
    for group in settings.CABS_LDAP_CAN_DISABLE_GROUPS:
        can = can or user.groups.filter(name=group).count() > 0
    
    if not can:
        can = can or can_edit(user)
    
    return can 

def can_edit(user):
    if len(settings.CABS_LDAP_CAN_EDIT_GROUPS) == 0:
        return True
    can = False
    for group in settings.CABS_LDAP_CAN_EDIT_GROUPS:
        can = can or user.groups.filter(name=group).count() > 0
 
    return can

def index(request, permission_error=None):
    context = {}
    if not request.user.is_authenticated():
        template_response = views.login(request, template_name='cabs_admin/logindex.html', 
                current_app='cabs_admin', extra_context=context)
        return template_response
    else:
        if can_view(request.user):
            permissions = (" view pages")
            permissions += (",{0} disable items".format("" if can_edit(request.user) else "and")
                    if can_disable(request.user) else "")
            permissions += (", and edit or create items" if can_edit(request.user) else "")
            user_string = "You have permissions to {0}.".format(permissions)
        else:
            user_string = "You have no administrator permissions."
        
        context['permissions'] = user_string
        context['section_name'] = "Welcome {0}".format(request.user.get_username()) 
        if permission_error:
            context['permission_error'] = "You do not have permissions to " + permission_error + "."
        else:
            context['permission_error'] = None

        context['pools'] = settings.AGGREGATE_GRAPHS + \
                [pool.name for pool in Pools.objects.using('cabs').all()]
        return render(request, 'cabs_admin/index.html', context)

def logoutView(request):
    template_response = views.logout(request, template_name='cabs_admin/index.html', current_app='cabs_admin')
    return template_response

@login_required
@user_passes_test(can_view, login_url='/admin/view/')
def graphsPage(request, selected=None):
    context = {}
    if selected == None:
        selected = settings.AGGREGATE_GRAPHS[0]
    context['selected'] = selected
    pools = settings.AGGREGATE_GRAPHS + [pool.name for pool in Pools.objects.using('cabs').all()]
    context['pools'] = {pool: pool.replace("_", " ") for pool in pools}
    context['lengths'] = settings.GRAPH_LENGTHS
    return render(request, 'cabs_admin/graphs.html', context)

@login_required
@user_passes_test(can_view, login_url='/admin/view/')
def machinesPage(request, selected_machine=None):
    c_list = Current.objects.using('cabs').all()
    m_list = Machines.objects.using('cabs').all()
    
    machine_info = collections.namedtuple('machine',
            ['machine', 'name', 'active', 'user', 'loginTime', 'deactivated', 'reason', 'status'])
    machine_list = []
    reported = []
    
    # TODO: figure out the idiomatic way to do the analog of an SQL join.
    for m in m_list: 
        user = ''
        loginTime = ''
        for c in c_list:
            if m.machine == c.machine:
                user = c.user
                loginTime = c.connecttime
                reported.append(c)
                break
        #active = "Active" if m.active else "Awaiting Response"
        item = machine_info(machine=m.machine, name=m.name, active=m.active, user=user, loginTime=loginTime,
                            deactivated=m.deactivated, reason=m.reason,
                            status=(m.status if m.status is not None else ""))
        machine_list.append(item)
    #if there are left over users logged into machines we don't track, let's report those as well
    for c in c_list:
        if c not in reported:
            item = machine_info(machine=c.machine, name='No Pool', active=True, user=c.user,
                                deactivated=False, reason="", status="")
            machine_list.append(item)

    mainkey = lambda x: x.machine
    if request.GET.get('sort'):
        sortby = request.GET.get('sort')
        if sortby == "pool":
            mainkey = lambda x: x.name
        elif sortby == "user":
            mainkey = lambda x: x.user
        elif sortby == "loginTime":
            mainkey = lambda x: x.loginTime
        elif sortby == "status":
            mainkey = lambda x: x.status
        elif sortby == "active":
            mainkey = lambda x: (x.active, not x.deactivated)
        elif sortby == "disabled":
            mainkey = lambda x: (not x.deactivated, x.active)
    # Put empty fields at the bottom.
    sortkey = lambda x : (mainkey(x) == "", mainkey(x), x.machine)
    machine_list = sorted(machine_list, key=sortkey)
    
    pool_list = Pools.objects.using('cabs').all().order_by('name')
    
    context = {'section_name': 'Machines', 'machine_list': machine_list, 'selected_machine': selected_machine, 
               'pool_list': pool_list}
    return render(request, 'cabs_admin/machines.html', context)

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def setMachines(request):
    try: 
        new_name = request.POST['name']
        new_machine = request.POST['machine']
        if (new_machine == '') or (new_name == ''):
            raise KeyError('This value cannot be empty')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:machinesPage'))
    else:
        try:
            s = Machines.objects.using('cabs').get(machine=new_machine)
            s.name = new_name
        except:
            s = Machines(name=new_name, machine=new_machine, active=False, deactivated=False)
        s.save(using='cabs')
        return HttpResponseRedirect(reverse('cabs_admin:machinesPage'))

@login_required
@user_passes_test(can_disable, login_url='/admin/disable/')
def toggleMachines(request):
    try:
        selected_machine = ""
        chosen_machine = request.POST['machine']
        s = Machines.objects.using('cabs').get(machine=chosen_machine)
        if 'rm' in request.POST and can_edit(request.user):
            s.delete(using='cabs')
        else:
            msg = "{} was ".format(chosen_machine)
            if s.deactivated:
                s.deactivated = False;
                s.reason = ""
                msg += "enabled"
            else:
                s.deactivated = True;
                #add a location for commenting on reason
                selected_machine = s.machine;
                msg += "disabled"
            s.save(using='cabs')
            Log(msg_type="INFO", message=msg).save(using='cabs')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:machinesPage'))
    else:
        if selected_machine:
            return HttpResponseRedirect(reverse('cabs_admin:machinesPage')+"toggle/"+selected_machine+"/")
        else:
            return HttpResponseRedirect(reverse('cabs_admin:machinesPage'))

@login_required
@user_passes_test(can_disable, login_url='/admin/disable/')
def commentMachines(request):
    try:
        chosen_machine = request.POST['machine']
        new_reason = request.POST['reason']
        s = Machines.objects.using('cabs').get(machine=chosen_machine)
        s.reason = new_reason
        s.save(using='cabs')
        # TODO don't find machine by message text. Get a parameter from toggleMachines() instead.
        logMsg = Log.objects.using('cabs').filter(message="{} was disabled".format(chosen_machine)).order_by(
                '-id')[0]
        logMsg.message += ". Reason: {}".format(new_reason)
        logMsg.save()
    except:
        return HttpResponseRedirect(reverse('cabs_admin:machinesPage'))
    else:
        return HttpResponseRedirect(reverse('cabs_admin:machinesPage'))

@login_required
@user_passes_test(can_view, login_url='/admin/view/')
def poolsPage(request, selected_pool=None):
    pool_list = Pools.objects.using('cabs').all().order_by('name')
    context = {'section_name': 'Pools', 'pool_list': pool_list, 'selected_pool': selected_pool}
    return render(request, 'cabs_admin/pools.html', context)

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def setPools(request):
    try:
        new_pool = request.POST['name']
        new_description = request.POST['description']
        new_secondary = request.POST['secondary']
        new_groups = request.POST['groups']
        if new_pool == '':
            raise KeyError('This value cannot be empty')
        if new_description == '':
            new_description = None;
        if new_secondary == '':
            new_secondary = None;
        if new_groups == '':
            new_groups = None;
    except:
        return HttpResponseRedirect(reverse('cabs_admin:poolsPage'))
    else:
        try:
            s = Pools.objects.usint('cabs').get(name = new_pool)
            s.description = new_desc
            s.secondary = new_secondary
            s.groups = new_groups
        except:
            s = Pools(name=new_pool, description=new_description, secondary=new_secondary, groups=new_groups, deactivated=False)
        s.save(using='cabs')
        return HttpResponseRedirect(reverse('cabs_admin:poolsPage'))

@login_required
@user_passes_test(can_disable, login_url='/admin/disable/')
def togglePools(request): 
    try:
        selected_pool = ""
        chosen_pool = request.POST['pool']
        s = Pools.objects.using('cabs').get(name=chosen_pool)
        if 'rm' in request.POST and can_edit(request.user):
            s.delete(using='cabs')
        else:
            msg = "Pool {} was ".format(chosen_pool)
            if s.deactivated:
                s.deactivated = False;
                s.reason = ""
                msg += "enabled"
            else:
                s.deactivated = True;
                selected_pool = s.name;
                msg += "disabled"
            s.save(using='cabs')
            Log(msg_type="INFO", message=msg).save(using='cabs')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:poolsPage'))
    else:
        if selected_pool:
            return HttpResponseRedirect(reverse('cabs_admin:poolsPage')+"toggle/"+selected_pool+"/")
        else:
            return HttpResponseRedirect(reverse('cabs_admin:poolsPage'))

@login_required
@user_passes_test(can_disable, login_url='/admin/disable/')
def commentPools(request):
    try:
        chosen_pool = request.POST['pool']
        new_reason = request.POST['reason']
        s = Pools.objects.using('cabs').get(name=chosen_pool)
        s.reason = new_reason
        s.save(using='cabs')
        # TODO don't find machine by message text. Get a parameter from togglePools() instead.
        logMsg = Log.objects.using('cabs').filter(message="Pool {} was disabled".format(chosen_pool)).order_by(
                '-id')[0]
        logMsg.message += ". Reason: {}".format(new_reason)
        logMsg.save()
    except:
        return HttpResponseRedirect(reverse('cabs_admin:poolsPage'))
    else:
        return HttpResponseRedirect(reverse('cabs_admin:poolsPage'))

@login_required 
@user_passes_test(can_view, login_url='/admin/view/')
def settingsPage(request):
    settings_list = Settings.objects.using('cabs').all()
    try:
        option_chosen = request.GET['setting']
    except:
        option_chosen = None
    context = {'section_name': 'Change Settings', 'settings_list': settings_list, 'option_choosen': option_chosen}
    return render(request, 'cabs_admin/settings.html', context)

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def setSettings(request):
    try:
        new_value = request.POST['value']
        new_setting = request.POST['setting']
        if ((new_value == '') and (not new_setting.endswith('fix'))) or (new_setting == ''):
            raise KeyError('This value cannot be empty')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:settingsPage'))
    else:
        try:
            s = Settings.objects.using('cabs').get(setting=new_setting)
            s.value = new_value
        except:
            s = Settings(setting=new_setting, value=new_value)
        s.save(using='cabs')
        return HttpResponseRedirect(reverse('cabs_admin:settingsPage'))

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def rmSettings(request):
    try:
        chosen_setting = request.POST['setting']
        s = Settings.objects.using('cabs').get(setting=chosen_setting)
        s.delete(using='cabs')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:settingsPage'))
    else:
        return HttpResponseRedirect(reverse('cabs_admin:settingsPage'))

@login_required
@user_passes_test(can_view, login_url='/admin/view/')
def blacklistPage(request):
    black_list = Blacklist.objects.using('cabs').all().order_by('-banned')
    white_list = Whitelist.objects.using('cabs').all()
    context = {'section_name': 'Blacklist', 'black_list': black_list, 'white_list': white_list}
    return render(request, 'cabs_admin/blacklist.html', context)

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def setBlacklist(request):
    try:
        new_address = request.POST['address']
        if new_address == '':
            raise KeyError('This value cannot be empty')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))
    else:
        try:
            s = Blacklist.objects.using('cabs').get(address=new_address)
            s.banned=True
        except:
            s = Blacklist(address=new_address, banned=True, attempts=0)
        s.save(using='cabs')
        ss = Whitelist.objects.using('cabs').filter(address=new_address)
        ss.delete()
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def toggleBlacklist(request): 
    try:
        chosen_address = request.POST['address']
        s = Blacklist.objects.using('cabs').get(address=chosen_address)
        if 'rm' in request.POST:
            s.delete(using='cabs')
        elif 'whitelist' in request.POST:
            s.delete(using='cabs')
            try:
                ss = Whitelist.objects.using('cabs').get(address=chosen_address)
            except:
                ss = Whitelist(address=chosen_address)
            ss.save(using='cabs')
        else:
            if s.banned:
                s.banned = False;
            else:
                s.banned = True;
            s.save(using='cabs')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))
    else:
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def setWhitelist(request):
    try:
        new_address = request.POST['address']
        if new_address == '':
            raise KeyError('This value cannot be empty')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))
    else:
        try:
            s = Whitelist.objects.using('cabs').get(address=new_address)
        except:
            s = Whitelist(address=new_address)
        s.save(using='cabs')
        ss = Blacklist.objects.using('cabs').filter(address=new_address)
        ss.delete()
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))

@login_required
@user_passes_test(can_edit, login_url='/admin/edit/')
def rmWhitelist(request):
    try:
        chosen_address = request.POST['address']
        s = Whitelist.objects.using('cabs').get(address=chosen_address)
        s.delete(using='cabs')
    except:
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))
    else:
        return HttpResponseRedirect(reverse('cabs_admin:blacklistPage'))

@login_required
@user_passes_test(can_view, login_url='/admin/view/')
def historyPage(request):
    if request.GET.get('position'):
        i = int(request.GET.get('position'))
    else:
        i = 0
    if request.GET.get('filter'):
        searchterm = request.GET.get('filter')
    else:
        searchterm = ""
    if request.GET.get('sort'):
        sortby = request.GET.get('sort')
    else:
        sortby = ""

    items_per_page = 50
    links_above_below = 3
    
    if sortby == "level":
        logger_list = Log.objects.using('cabs').filter(message__contains=searchterm).order_by(
                '-msg_type', '-timestamp', '-id')
    else:
        logger_list = Log.objects.using('cabs').filter(message__contains=searchterm).order_by(
                '-timestamp', '-id')

    page = collections.namedtuple('page', ['index', 'pos'])
    number_items = len(logger_list)
    logger_list = logger_list[i:(i+items_per_page)]

    page_list = []
    page_list.append(page(index=0, pos=0))
    
    current_page = i / items_per_page
    last = number_items / items_per_page
    last_pos = (number_items - items_per_page if number_items > items_per_page else None)
    
    highest = current_page + links_above_below
    highest = ((last - 1) if highest >= last else highest)
    lowest = current_page - links_above_below
    lowest = (1 if highest <= 0 else lowest)
    for j in range(1, (number_items / items_per_page) ):
        if lowest <= j <= highest:
            p = page(index=j, pos=(j*items_per_page))
            page_list.append(p) 
    
    if last_pos is not None:
        page_list.append(page(index=last, pos=last_pos))

    context = {'section_name': 'History', 'logger_list': logger_list, 'current_page': current_page,
               'page_list': page_list, 'filter': searchterm, 'sort': sortby}
    return render(request, 'cabs_admin/history.html', context)

