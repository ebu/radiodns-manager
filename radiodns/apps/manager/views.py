from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.manager.forms import OrganizationForm
from apps.manager.models import Organization


@login_required
def set_organization(request, organization_id):
    for organization in request.user.organizations_list:
        if organization.id == organization_id:
            request.user.current_organization = organization
            request.user.save()
            return redirect("manager:details")
    else:
        return redirect("common:index")


@login_required
def organization_details(request):
    if request.user.active_organization is None:
        return render("manager/error.html")
    selected_organization = get_object_or_404(
        Organization, id=request.user.active_organization.id
    )
    return render(
        request, "manager/home.html", context={"organization": selected_organization}
    )


@login_required
def edit_organization(request):
    selected_organization = get_object_or_404(
        Organization, id=request.user.active_organization.id
    )
    form = OrganizationForm(instance=selected_organization)
    if request.method == "POST":
        form = OrganizationForm(request.POST, instance=selected_organization)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect("manager:details")
    return render(request, "manager/edit.html", context={"form": form})


# TODO Add Image views
