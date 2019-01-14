function StationModuleDetails() {
}

/**
 * Makes an http request to check a station and handles the response from the server.
 * @param id: The id of the station to check.
 */
StationModuleDetails.prototype.checkStation = function (id) {
    $.ajaxq("rdns-stationq", {
        url: `${ebuio_baseUrl}stations/check/` + id,
        dataType: 'json',
        success: function (data) {
            if (data.isvalid) {
                $('#radiodns-station-status').html('Success');
                $('#radiodns-station-status').removeClass('label-default');
                $('#radiodns-station-status').addClass('label-success');
            } else {
                $('#radiodns-station-status').html('Failed');
                $('#radiodns-station-status').removeClass('label-default');
                $('#radiodns-station-status').addClass('label-danger');
            }

            if (data.radiovis) {
                if (data.radiovis.enabled) {
                    $('#vis-' + id).html('<small>VIS</small> ' + data.radiovis.fqdn);
                    if (data.radiovis.isvalid) {
                        $('#vis-' + id).addClass('text-success');
                    }
                } else {
                    $('#vis-' + id).addClass('text-muted');
                    $('#vis-' + id).html('<small>VIS</small> ' + 'vis disabled');
                }
            } else {
                $('#vis-' + id).addClass('text-danger');
                $('#vis-' + id).html('<small>VIS</small> ' + 'missing vis information');
            }
            if (data.radioepg) {
                if (data.radioepg.enabled) {
                    $('#epg-' + id).html('<small>EPG</small> ' + data.radioepg.fqdn);
                    if (data.radioepg.isvalid) {
                        $('#epg-' + id).addClass('text-success');
                    }
                } else {
                    $('#epg-' + id).addClass('text-muted');
                    $('#epg-' + id).html('<small>EPG</small> ' + 'epg disabled');
                }
            } else {
                $('#epg-' + id).addClass('text-danger');
                $('#epg-' + id).html('<small>EPG</small> ' + 'missing epg information');
            }
            if (data.radiospi) {
                if (data.radiospi.enabled) {
                    $('#spi-' + id).html('<small>SPI</small> ' + data.radiospi.fqdn);
                    if (data.radiospi.isvalid) {
                        $('#spi-' + id).addClass('text-success');
                    }
                } else {
                    $('#spi-' + id).addClass('text-muted');
                    $('#spi-' + id).html('<small>SPI</small> ' + 'spi disabled');
                }
            } else {
                $('#spi-' + id).addClass('text-danger');
                $('#spi-' + id).html('<small>spi</small> ' + 'missing SPI information');
            }
            if (data.radiotag) {
                if (data.radiotag.enabled) {
                    $('#tag-' + id).html('<small>TAG</small> ' + data.radiotag.fqdn);
                    if (data.radiotag.isvalid) {
                        $('#tag-' + id).addClass('text-success');
                    }
                } else {
                    $('#tag-' + id).addClass('text-muted');
                    $('#tag-' + id).html('<small>TAG</small> ' + 'tag disabled');
                }
            } else {
                $('#tag-' + id).addClass('text-danger');
                $('#tag-' + id).html('<small>TAG</small> ' + 'missing tag information');
            }

        }
    });

    // Tool Tips
    $('[data-toggle="tooltip"]').tooltip({html: true});
};

/**
 * Makes the http call to change the default logo of a station.
 * @param id: The id of the station.
 * @param val: the value of the select logo input.
 * @param elemToBlink: Reference to the element to blink in green in case of success.
 */
StationModuleDetails.prototype.switch_default = function (id, val, elemToBlink) {
    $.ajax({
        url: `${ebuio_baseUrl}radioepg/logos/set/` + id + '/' + val,
        success: function () {
            elemToBlink.css('backgroundColor', 'green');
            elemToBlink.css('opacity', '0.25');
            elemToBlink.animate({opacity: 1}, 500, function () {
                elemToBlink.css('backgroundColor', '#ffffff');
            });
            // Update inline image
            if (val === 0) {
                $('#station-img-' + id).hide();
            } else {
                $('#station-img-' + id).show();
                var selected = elemToBlink.find('option:selected');
                var new_public_url = selected.data('public_url');
                $('#station-img-' + id).attr("src", new_public_url);
            }
        }
    })
};
                        