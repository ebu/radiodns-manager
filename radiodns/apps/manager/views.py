from django.shortcuts import render, redirect, get_object_or_404

from apps.localization.models import Language, Ecc
from apps.manager.forms import OrganizationForm, LogoImageForm
from apps.manager.models import Organization, LogoImage

from common.utils import scale_image


def SetOrganizationView(request, organization_id):
    for organization in request.user.organizations_list:
        if organization.id == organization_id:
            request.user.current_organization = organization
            request.user.save()
            return redirect("manager:details")
    else:
        return redirect("common:index")


def OrganizationDetailsView(request):
    if request.user.active_organization is None:
        return render("manager/error.html")
    selected_organization = get_object_or_404(
        Organization, id=request.user.active_organization.id
    )
    logo = LogoImage.objects.filter(id=selected_organization.default_image_id).first()
    return render(
        request,
        "manager/home.html",
        context={"organization": selected_organization, "logo": logo},
    )


def EditOrganizationView(request):
    selected_organization = get_object_or_404(
        Organization, id=request.user.active_organization.id
    )
    form = OrganizationForm(instance=selected_organization)
    languages = Language.objects.all()
    countries = Ecc.objects.all()
    if request.method == "POST":
        form = OrganizationForm(request.POST, instance=selected_organization)
        if form.is_valid():
            form.save()
            return redirect("manager:details")
    return render(
        request,
        "manager/edit.html",
        context={"form": form, "languages": languages, "countries": countries,},
    )


def ListImagesView(request):
    images = LogoImage.objects.filter(
        organization__id=request.user.active_organization.id
    )
    return render(request, "manager/list_images.html", context={"images": images})


def EditImageView(request, image_id=None):
    selected_image = None
    if image_id is not None:
        selected_image = get_object_or_404(LogoImage, id=image_id)
    form = LogoImageForm(instance=selected_image)
    if request.method == "POST":
        form = LogoImageForm(request.POST, request.FILES, instance=selected_image)
        if form.is_valid():
            image = form.save(commit=False)
            image.organization = request.user.active_organization
            replace_size = form.cleaned_data["replace_size"]
            if replace_size == "" or replace_size == "All":
                image.scaled32x32 = scale_image(image.file, 32, 32)
                image.scaled112x32 = scale_image(image.file, 112, 32)
                image.scaled128x128 = scale_image(image.file, 128, 128)
                image.scaled320x240 = scale_image(image.file, 320, 240)
                image.scaled600x600 = scale_image(image.file, 600, 600)
            elif replace_size == "32x32":
                image.scaled32x32 = scale_image(image.file, 32, 32)
            elif replace_size == "112x32":
                image.scaled112x32 = scale_image(image.file, 112, 32)
            elif replace_size == "128x128":
                image.scaled128x128 = scale_image(image.file, 128, 128)
            elif replace_size == "320x240":
                image.scaled320x240 = scale_image(image.file, 320, 240)
            elif replace_size == "600x600":
                image.scaled600x600 = scale_image(image.file, 600, 600)
            image.save()
            return redirect("manager:list_images")
    return render(request, "manager/edit_image.html", context={"form": form})


def DeleteImageView(request, image_id):
    image = get_object_or_404(LogoImage, id=image_id)
    image.file.delete()
    image.scaled32x32.delete()
    image.scaled112x32.delete()
    image.scaled128x128.delete()
    image.scaled320x240.delete()
    image.scaled600x600.delete()
    image.delete()

    return redirect("manager:list_images")


def SetDefaultImageView(request, image_id):
    organization = get_object_or_404(
        Organization, id=request.user.active_organization.id
    )
    organization.default_image_id = image_id
    organization.save()
    return redirect("manager:list_images")
