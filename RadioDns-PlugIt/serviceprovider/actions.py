# -*- coding: utf-8 -*-

# Utils
from plugit.utils import action, only_orga_member_user, only_orga_admin_user, PlugItRedirect, json_only

from models import db, ServiceProvider, LogoImage
from plugit.api import PlugItAPI, Orga
import config

import json


@action(route="/serviceprovider/", template="serviceprovider/home.html")
@only_orga_member_user()
def serviceprovider_home(request):
    """Show the serviceprovider."""

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'
    passworded = request.args.get('passworded') == 'yes'

    if sp:
        sp = sp.json

    return {'serviceprovider': sp, 'ebu_codops': orga.codops, 'saved': saved, 'deleted': deleted}


@action(route="/serviceprovider/edit/<id>", template="serviceprovider/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def serviceprovider_edit(request, id):
    """Edit a serviceprovider."""

    object = None
    errors = []

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    if id != '-':
        object = ServiceProvider.query.filter_by(id=id).first()

    if request.method == 'POST':

        if not object:
            object = ServiceProvider(int(request.form.get('ebuio_orgapk')))

        object.codops = orga.codops
        object.short_name = request.form.get('short_name')
        object.medium_name = request.form.get('medium_name')
        object.long_name = request.form.get('long_name')
        object.short_description = request.form.get('short_description')
        object.long_description = request.form.get('long_description')
        object.url_default = request.form.get('url_default')
        object.default_language = request.form.get('default_language')

        # Check errors
        if object.medium_name == '':
            errors.append("Please set a medium name")
        if object.short_description == '':
            errors.append("Please set a short description")


        # If no errors, save
        if not errors:

            if not object.id:
                db.session.add(object)

            db.session.commit()

            return PlugItRedirect('serviceprovider/?saved=yes')

    if object:
        object = object.json

    return {'object': object, 'errors': errors}


@action(route="/serviceprovider/delete/<id>")
@json_only()
@only_orga_admin_user()
def serviceprovider_delete(request, id):
    """Delete a ServiceProvider."""

    object = ServiceProvider.query.filter_by(orga=int(request.args.get('ebuio_orgapk')), id=int(id)).first()
    db.session.delete(object)
    db.session.commit()

    return PlugItRedirect('serviceprovider/?deleted=yes')


@action(route="/serviceprovider/images/", template="serviceprovider/gallery/home.html")
@only_orga_member_user()
def serviceprovider_gallery_home(request):
    """Show the list of images for a service provider."""

    list = []

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    if sp:
        for elem in LogoImage.query.filter_by(service_provider_id = int(sp.id)).order_by(LogoImage.filename).all():
            list.append(elem.json)

    saved = request.args.get('saved') == 'yes'
    deleted = request.args.get('deleted') == 'yes'

    return {'list': list, 'saved': saved, 'deleted': deleted}


@action(route="/serviceprovider/images/edit/<id>", template="serviceprovider/gallery/edit.html", methods=['POST', 'GET'])
@only_orga_admin_user()
def serviceprovider_gallery_edit(request, id):
    """Edit a channel."""

    object = None
    errors = []

    plugitapi = PlugItAPI(config.API_URL)
    orga = plugitapi.get_orga(request.args.get('ebuio_orgapk') or request.form.get('ebuio_orgapk'))

    sp = None
    if orga.codops:
        sp = ServiceProvider.query.filter_by(codops=orga.codops).order_by(ServiceProvider.codops).first()

    if id != '-':
        object = LogoImage.query.filter_by(id=int(id)).first()

    if request.method == 'POST':

        if not object:
            object = LogoImage(int(request.form.get('ebuio_orgapk')))

        object.name = request.form.get('name')

        def add_unique_postfix(fn):
            """__source__ = 'http://code.activestate.com/recipes/577200-make-unique-file-name/'"""
            if not os.path.exists(fn):
                return fn

            path, name = os.path.split(fn)
            name, ext = os.path.splitext(name)

            make_fn = lambda i: os.path.join(path, '%s(%d)%s' % (name, i, ext))

            for i in xrange(2, sys.maxint):
                uni_fn = make_fn(i)
                if not os.path.exists(uni_fn):
                    return uni_fn

            return None

        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            full_path = add_unique_postfix('media/uploads/radioepg/gallery/' + filename)
            file.save(full_path)
            if object.filename:
                try:
                    os.unlink(object.filename)
                except:
                    pass
            object.filename = full_path

        # Check errors
        if object.name == '':
            errors.append("Please set a name")

        if object.filename == '' or object.filename is None:
            errors.append("Please upload an image")
        else:

            if imghdr.what(object.filename) not in ['jpeg', 'png']:
                errors.append("Image is not an png or jpeg image")
                os.unlink(object.filename)
                object.filename = None

        # If no errors, save
        if not errors:

            if not object.id:
                db.session.add(object)
            else:
                import glob
                for f in glob.glob('media/uploads/radioepg/cache/*_L%s.png' % (object.id,)):
                    os.unlink(f)

            db.session.commit()

            return PlugItRedirect('radioepg/gallery/?saved=yes')

    if object:
        object = object.json

    return {'object': object, 'errors': errors}

