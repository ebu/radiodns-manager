function ChannelsModule() {
}

ChannelsModule.prototype.typesIds = [];
ChannelsModule.prototype.default_country = '';

/**
 * Loads the available counties.
 */
ChannelsModule.prototype.load_countries = function () {
    $.ajax({
        url: `${ebuio_baseUrl}ecc_list`,
        dataType: 'json',
        success: function (data) {
            let cc = $('#cc');
            let eec = $('#ecc');
            let cc_val = cc.attr('cval');
            let cc_id = '';

            $(data.list).each(function (_, el) {
                const opt = '<option value="' + el.id + '">' + el.name + ' (' + el.iso + ') [' + el.pi + el.ecc + ']</option>';

                //Find cc id (as we store the cc and not the id to the country)
                if (cc_val === (el.pi + el.ecc)) {
                    cc_id = el.id;
                }

                cc.append(opt);
                eec.append(opt);
            });

            cc.val(cc_id);
            let default_country = eec.attr('cval');
            if (!default_country)
                default_country = ChannelsModule.prototype.default_country;
            eec.val(default_country);
        }
    })
};

/**
 * Updates the inputs field of the channel creation for the selected type of channel.
 */
ChannelsModule.prototype.update_display = function () {
    const opblk = $('.opblk');
    opblk.hide();

    const cVal = $('#type').val();

    ChannelsModule.prototype.typesIds.forEach(function (typeId) {
        if (cVal === typeId[0]) {
            typeId[2].forEach(function (v) {
                $(`.opblk_${v}`).show();
            });
            const opblk_fqdn = $('.opblk_fqdn');
            const opblk_serviceIdentifier = $('.opblk_serviceIdentifier');
            if (typeId[0] === "id") {
                opblk_fqdn.find('input').prop('readOnly', true);
                opblk_fqdn.find('input').val($('#station_select option:selected').data('stationfqdn'));
                opblk_serviceIdentifier.find('input').prop('readOnly', true);
                opblk_serviceIdentifier.find('input').val($('#station_select option:selected').data('stationserviceid'));
            } else {
                opblk_fqdn.find('input').prop('readOnly', false);
                opblk_fqdn.find('input').val('');
                opblk_serviceIdentifier.find('input').prop('readOnly', false);
                opblk_serviceIdentifier.find('input').val('');
            }
            $('#id_mime_type').show();
            $('#dab_mime_type').hide();
        }
    });

    opblk.each(function (_, el) {
        if ($(el).css('display') === 'none') {
            $(el).find('input').val('');
            $(el).find('select').val('');
        }
    });
};
