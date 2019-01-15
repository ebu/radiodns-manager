def build_base_parameters(request):
    """Build the list of parameters to forward from the post and get parameters"""

    get_parameters = {}
    post_parameters = {}
    files = {}

    # Copy GET parameters, excluding ebuio_*
    for v in request.GET:
        if v[:6] != 'ebuio_':
            val = request.GET.getlist(v)

            if len(val) == 1:
                get_parameters[v] = val[0]
            else:
                get_parameters[v] = val

    # If using post, copy post parameters and files. Excluding ebuio_*
    if request.method == 'POST':
        for v in request.POST:
            if v[:6] != 'ebuio_':
                val = request.POST.getlist(v)

                if len(val) == 1:
                    post_parameters[v] = val[0]
                else:
                    post_parameters[v] = val

        for v in request.FILES:
            if v[:6] != 'ebuio_':
                files[v] = request.FILES[v]  # .chunks()

    return get_parameters, post_parameters, files


def build_user_requested_parameters(request, meta):
    """Build the list of parameters requested by the plugit server"""

    post_parameters = {}
    get_parameters = {}
    files = {}

    # Add parameters requested by the server
    if meta and 'user_info' in meta:
        for prop in meta['user_info']:

            # Test if the value exist, otherwise return None
            value = getattr(request.user, prop)

            # Add informations to get or post parameters, depending on the current method
            if request.method == 'POST':
                post_parameters['ebuio_u_' + prop] = value
            else:
                get_parameters['ebuio_u_' + prop] = value

    return get_parameters, post_parameters, files


def build_orga_parameters(request, current_orga):
    post_parameters = {}
    get_parameters = {}
    files = {}

    # If orga mode, add the current orga pk
    if current_orga:
        if request.method == 'POST':
            post_parameters['ebuio_orgapk'] = current_orga.pk
        else:
            get_parameters['ebuio_orgapk'] = current_orga.pk
    else:
        if request.method == 'POST':
            post_parameters['ebuio_orgapk'] = -1
        else:
            get_parameters['ebuio_orgapk'] = -1

    return get_parameters, post_parameters, files


def build_parameters(request, meta, current_orga):
    """Return the list of get, post and file parameters to send"""

    post_parameters = {}
    get_parameters = {}
    files = {}

    def update_parameters(data):
        tmp_get_parameters, tmp_post_parameters, tmp_files = data

        get_parameters.update(tmp_get_parameters)
        post_parameters.update(tmp_post_parameters)
        files.update(tmp_files)

    update_parameters(build_base_parameters(request))
    update_parameters(build_user_requested_parameters(request, meta))
    update_parameters(build_orga_parameters(request, current_orga))

    return get_parameters, post_parameters, files
