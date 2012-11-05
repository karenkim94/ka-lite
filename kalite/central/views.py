import re, json
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404, redirect, get_list_or_404
from django.template import RequestContext
from annoying.decorators import render_to
from central.models import Organization
from central.forms import OrganizationForm, ZoneForm
from securesync.models import Zone
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


import settings

@render_to("central/homepage.html")
def homepage(request):
    if not request.user.is_authenticated():
        return landing_page(request)
    organizations = request.user.get_profile().get_organizations()
    context = {'organizations': organizations}
    return context

@render_to("central/landing_page.html")
def landing_page(request):
    return {}
 
@login_required     
@render_to("central/organization_form.html")
def organization_form(request, id=None):
    if id != "new":
        org = get_object_or_404(Organization, pk=id)
        if org.users.filter(pk=request.user.pk).count() == 0:
            return HttpResponseNotAllowed("You do not have permissions for this organization.")
    else:
        org = None
    if request.method == 'POST':
        form = OrganizationForm(data=request.POST, instance=org)
        if form.is_valid():
            # form.instance.owner = form.instance.owner or request.user 
            form.instance.save(owner=request.user)
            form.instance.users.add(request.user)
            # form.instance.save()
            return HttpResponseRedirect(reverse("homepage"))
    else:
        form = OrganizationForm(instance=org)
    return {
        'form': form
    } 


@login_required
@render_to("central/zone_form.html")
def zone_form(request, id=None, org_id=None):
    org = get_object_or_404(Organization, pk=org_id)
    if org.users.filter(pk=request.user.pk).count() == 0:
        return HttpResponseNotAllowed("You do not have permissions for this organization.")
    if id != "new":
        zone = get_object_or_404(Zone, pk=id)
        if org.zones.filter(pk=zone.pk).count() == 0:
            return HttpResponseNotAllowed("This organization does not have permissions for this zone.")
    else:
        zone = None
    if request.method == 'POST':
        form = ZoneForm(data=request.POST, instance=zone)
        if form.is_valid():
            # form.instance.owner = form.instance.owner or request.user 
            form.instance.save()
            org.zones.add(form.instance)
            # form.instance.save()
            return HttpResponseRedirect(reverse("homepage"))
    else:
        form = ZoneForm(instance=zone)
    return {
        'form': form
    } 