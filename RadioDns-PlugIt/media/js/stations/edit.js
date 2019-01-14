function StationModuleEdit() {

}

// List of all the client's ids.
StationModuleEdit.prototype.clientsIds = [];

// List of all the stations ids.
StationModuleEdit.prototype.stationsIds = {};

// current number of selected genres in the default tab.
StationModuleEdit.prototype.numberOfExistingDefaultGenre = 0;

// Current active tab.
StationModuleEdit.prototype.currentTab = 0;

// if in edit mode
StationModuleEdit.prototype.onEditMode = [];

// CONSTANTS
StationModuleEdit.prototype.MAX_LENGTH_SHORT_NAME = 8;
StationModuleEdit.prototype.MAX_LENGTH_MEDIUM_NAME = 16;
StationModuleEdit.prototype.MAX_LENGTH_LONG_NAME = 128;


/**
 * Initialize the module. Requires that the clientsIds are initialized properly first.
 */
StationModuleEdit.prototype.init = function () {
    const module = StationModuleEdit.prototype;
    StationModuleEdit.prototype.numbers = new Array(module.clientsIds.length).fill(0);
    $('.genre-select').on('change', function () {
        module.changeGenreSelection($(this));
    });

    module.updateTab(module.clientsIds[0]);
    module.load_countries();

    StationModuleEdit.prototype.inputsTouched = {
        "station-name_": module.initInputsTouchedValue("name"),
        "short_name_": module.initInputsTouchedValue("name"),
        "medium_name_": module.initInputsTouchedValue("name"),
        "long_name_": module.initInputsTouchedValue("name"),
        "short_description_": module.initInputsTouchedValue("name"),
        "default_language_": module.initInputsTouchedValue("language", false),
        "default_url_": module.initInputsTouchedValue("links"),
        "postal_name_": module.initInputsTouchedValue("address"),
        "street_": module.initInputsTouchedValue("address"),
        "zipcode_": module.initInputsTouchedValue("address"),
        "city_": module.initInputsTouchedValue("address"),
        "location_country_": module.initInputsTouchedValue("address", false),
        "phone_number_": module.initInputsTouchedValue("contact"),
        "sms_number_": module.initInputsTouchedValue("contact"),
        "sms_body_": module.initInputsTouchedValue("contact"),
        "sms_description_": module.initInputsTouchedValue("contact"),
        "email_address_": module.initInputsTouchedValue("contact"),
        "email_description_": module.initInputsTouchedValue("contact"),
        genres: module.initInputsTouchedValue("genres", false),
    };

    module.clientsIds.forEach(function (client_id) {
        if (client_id === 0) {
            return;
        }

        if (!["", $('#default_language_0').attr("cval")].includes($(`#default_language_${client_id}`).attr("cval"))) {
             module.updateInputTouchedStatus(client_id, true, "language", "default_language_");
        }
        if (!["", $('#location_country_0').attr("cval")].includes($(`#location_country_${client_id}`).attr("cval"))) {
             module.updateInputTouchedStatus(client_id, true, "address", "location_country_");
        }

        const genreList = module.selectedGenres($(`#genre_list_${client_id}`));
        const genreListDefault = module.selectedGenres($('#genre_list_0'));
        if (!(genreList.length === 1 && genreList[0] === "") &&
            !UtilitiesModule.prototype.arrayEquals(genreList, genreListDefault)
        ) {
            module.updateInputTouchedStatus(client_id, true, "genres", "genres");
        }
    });

    Object.keys(module.inputsTouched).forEach(function (field_id) {
        module.inputsTouched[field_id].defaultValue = $(`#${field_id}0`).val();

        Object.keys(module.inputsTouched[field_id].modified).forEach(function (client_id) {
            if (client_id === 0) {
                return;
            }
            const override_field_value = $(`#${field_id}${client_id}`).val();
            if (override_field_value !== ""
                && override_field_value !== $(`#${field_id}0`).val()
                && module.onEditMode[client_id]) {
                module.updateInputTouchedStatus(client_id, true, module.inputsTouched[field_id].group, field_id);
            }
        });
    });
};

/**
 * Helper function that initialize an object of the shape {[clientId: number]: boolean}.
 * Basically every client ids get associated with a boolean value in this object.
 * @returns {[key: number]: boolean}
 */
StationModuleEdit.prototype.initModifiedObject = function () {
    return StationModuleEdit.prototype.clientsIds.reduce(function (acc, current) {
        acc[current] = false;
        return acc;
    }, {});
};

/**
 * Keep the changes for a specified field along with its group block and input type.
 *
 * @param groupName: The group block that the input is in.
 * @param isInput: if the input type is an input and not a select or anything else.
 * @returns {{modified: *, group: *, defaultValue: string, isInput: boolean}}
 */
StationModuleEdit.prototype.initInputsTouchedValue = function (groupName, isInput = true) {
    return {
        modified: StationModuleEdit.prototype.initModifiedObject(),
        group: groupName,
        defaultValue: "",
        isInput,
    };
};

/**
 * Updates a tab class by adding or removing the override class to a tab being overridden.
 *
 * @param tabId: the tab id.
 */
StationModuleEdit.prototype.updateTabClass = function (tabId) {
    const a = Object.values(StationModuleEdit.prototype.inputsTouched)
        .map(function (inputData) {
            return inputData.modified[tabId];
        })
        .every(function (changed) {
            return !changed;
        });
    if (a) {
        $(`#nav_li_${tabId}`).removeClass('override');
        $(`#is_client_override_${tabId}`).val("False");
    } else {
        $(`#nav_li_${tabId}`).addClass('override');
        $(`#is_client_override_${tabId}`).val("True");
    }
};

/**
 * Resets a group's inputs of a specified tab.
 *
 * @param tabId: The targeted tab.
 * @param group: The group.
 */
StationModuleEdit.prototype.resetTouchedInputs = function (tabId, group) {
    Object.values(StationModuleEdit.prototype.inputsTouched)
        .filter(function (inputData) {
            return inputData.group === group;
        })
        .forEach(function (inputData) {
            return inputData.modified[tabId] = false;
        });
};

/**
 * Updates an input's status if it has been touched (in this context if he is being overridden).
 *
 * @param tabId: The target tab id.
 * @param touched: If the input was changed or not.
 * @param group: The group of the input.
 * @param inputName: The name of the input.
 */
StationModuleEdit.prototype.updateInputTouchedStatus = function (tabId, touched, group, inputName = null) {
    if (tabId !== 0) {
        $(`#dot_grp_${tabId}_${group}`).css({'opacity': Number(touched)});

        if (!!inputName) {
            StationModuleEdit.prototype.inputsTouched[inputName].modified[tabId] = touched;
        } else if (!touched) {
            StationModuleEdit.prototype.resetTouchedInputs(tabId, group);
        }

        StationModuleEdit.prototype.updateTabClass(tabId);
    }
};


/**
 * OnChange event handler that fires when a genre select changes. Replace the contents of the other inputs
 * of a genre inputs row with pre-defined values.
 *
 * @param row: The targeted inputs row.
 */
StationModuleEdit.prototype.changeGenreSelection = function (row) {
    const genreUrn = "urn:tva:metadata:cs:ContentCS:2011:";
    let genre_txt = row.parents('.genre_row').find(".genre-select option:selected").text();
    genre_txt = genre_txt.replace(/\(.*\)/, '').trim();
    row.parents('.genre_row').find('.genre-href').val(genreUrn + row.parents('.genre_row').find('.genre-select').val());
    row.parents('.genre_row').find('.genre-name').val(genre_txt);
};

/**
 * Appends a genre selection row to the current active tab genres.
 */
StationModuleEdit.prototype.append_genre_select = function () {
    const tabId = StationModuleEdit.prototype.currentTab;
    let temp = $('#genre_row_template_' + tabId).clone();
    const ngenres = StationModuleEdit.prototype.numberOfExistingDefaultGenre;
    const number = StationModuleEdit.prototype.numbers[tabId] + ((ngenres - 1) < 0 ? 0 : ngenres);
    temp = temp.show();
    temp = temp.html(function (index, html) {
        let a = html.replace(/genre-select-/g, 'genre-select-' + number);
        a = a.replace(/genre-href-/g, 'genre-href-' + number);
        a = a.replace(/genre-name-/g, 'genre-name-' + number);
        a = a.replace(/genrehref\[\]_[0-9]+/g, `genrehref[]_${tabId}_${number}`);
        a = a.replace(/genrename\[\]_[0-9]+/g, `genrename[]_${tabId}_${number}`);

        return a;
    });
    temp = temp.attr("id", temp.attr("id") + '-' + number);
    temp.find('.genre-select').on('change', function () {
        StationModuleEdit.prototype.changeGenreSelection($(this));
    });

    $('#genre_row_template_' + tabId).parent().append(temp);

    StationModuleEdit.prototype.numbers[tabId]++;
    StationModuleEdit.prototype.updateInputTouchedStatus(tabId, true, "genres", "genres");
};

/**
 * Fetches the list of countries and insert it on every tabs.
 */
StationModuleEdit.prototype.load_countries = function () {
    $.ajax({
        url: ebuio_baseUrl + 'ecc_list',
        dataType: 'json',
        success: function (data) {
            const clientsIds = StationModuleEdit.prototype.clientsIds;
            for (let i = 0; i < clientsIds.length; i++) {
                const countrySelect = $('#location_country_' + clientsIds[i]);
                countrySelect.append('<option value=""></option>');

                $(data.list).each(function (_, el) {
                    const opt = '<option value="' + el.iso.toLowerCase() + '">' + el.name + ' (' + el.iso + ')</option>';
                    countrySelect.append(opt);
                });

                if (countrySelect.attr('cval') !== "") {
                    countrySelect.val(countrySelect.attr('cval'));
                } else {
                    countrySelect.val($('#location_country_0').attr('cval'));
                }
            }
        }
    })
};

/**
 * Deletes a selected genre.
 *
 * @param elem: The genre row to delete.
 * @returns {boolean}
 */
StationModuleEdit.prototype.del_genre = function (elem) {
    $(elem).parent().parent().remove();
    StationModuleEdit.prototype.updateInputTouchedStatus(StationModuleEdit.prototype.currentTab, true, "genres", "genres");
    return false;
};

/**
 * Return all the selected genres (from the selected options) from the specified genre table.
 *
 * @param genreTable:
 * @returns {any[]}
 */
StationModuleEdit.prototype.selectedGenres = function (genreTable) {
    return genreTable
        .find(":selected")
        .toArray()
        .map(function (option) {
            return option.value;
        });
};

/**
 * Copy the content of the genre table of the default tab to a specific tab's genre table.
 *
 * @param destTabId: The id of the destination table.
 * @param targetGenreTable: The recipient of the genre(s) copy operation.
 * @param defaultGenreTable: The source of the genre(s) copy operation.
 */
StationModuleEdit.prototype.copyGenres = function (destTabId, targetGenreTable, defaultGenreTable) {
    const genres = StationModuleEdit.prototype.selectedGenres(defaultGenreTable);

    StationModuleEdit.prototype.numberOfExistingDefaultGenre = genres.length;

    targetGenreTable.find('tr').not(':nth-child(1)').remove();
    defaultGenreTable
        .find('tr')
        .not(':nth-child(1)')
        .clone()
        .each(function (index, value) {
            $(value).show();
            $(value).find('td').find('input').each(function (_, input) {
                input.name = input.name.replace(/(genrehref|genrename)\[\]_[0-9]+_[0-9]+/g, function (_, p1) {
                    return `${p1}[]_${destTabId}_${index}`;
                });
            });
            value.id = value.id.replace(/[0-9]*-[0-9]*/g, `${destTabId}-${index}`);
            $(value).find('.genre-select').on('change', function () {
                StationModuleEdit.prototype.changeGenreSelection($(this));
            });
            targetGenreTable.find('tbody').append(value);
        });
    genres
        .slice(1) // removing first value as the template does not requires a select.
        .forEach(function (optionValue, index) {
            $(`#genre_row_template_${destTabId}-${index}`)
                .find(`option[value="${optionValue}"]`)
                .prop("selected", "true");
        });
};

/**
 * Update the tab. Copy the values of the default tab if it isn't the default tab for overrides and also update the
 * tab visibility if told to do so.
 *
 * @param tabId: The id of the tab to update.
 */
StationModuleEdit.prototype.updateTab = function (tabId) {
    const module = StationModuleEdit.prototype;
    module.currentTab = tabId;

    // if default tab (always 0) we exit here.
    if (tabId === 0) {
        return;
    }

    $(`button[name='reset-override-btn_${tabId}']`).show();

    const current_genre_list = $('#genre_list_' + tabId);
    const default_genre_list = $('#genre_list_0');

    if (!module.inputsTouched["genres"].modified[tabId]) {
        module.copyGenres(tabId, current_genre_list, default_genre_list);
    }

    Object.keys(module.inputsTouched)
        .filter(function (key) {
            return ["default_language_", "location_country_"].includes(key);
        })
        .forEach(function (key) {
            const selectInfo = module.inputsTouched[key];
            if (!selectInfo.modified[tabId]) {
                $(`#${key}${tabId}`).val($(`#${key}0`).val());
            }
        });

    // copy default input values if current tab's input was untouched by user.
    const listOfInputs = [
        'station-name_',
        'short_name_',
        'medium_name_',
        'long_name_',
        'short_description_',
        'default_url_',
        'postal_name_',
        'street_',
        'zipcode_',
        'city_',
        'phone_number_',
        'sms_number_',
        'sms_body_',
        'sms_description_',
        'email_address_',
        'email_description_',
    ];

    listOfInputs.forEach(input => {
        const defaultElement = $('#' + input + "0");
        const inputElement = $('#' + input + tabId);
        const defaultElementValue = defaultElement.val();
        const inputElementValue = inputElement.val();


        if (!inputElementValue) {
            switch (inputElement.prop('nodeName').toLowerCase()) {
                case "input":
                    inputElement.prop(module.onEditMode[tabId] ? "value" : "placeholder", defaultElementValue);
                    break;
                default:
                    console.warn("Copy handler not implemented for this kind of input:", inputElement.prop("nodeName"));
            }
        }
    });
};

/**
 * Deletes a station.
 *
 * @param id - the id of the station.
 */
StationModuleEdit.prototype.deleteStation = function (id) {
    if (confirm('You are about to delete this station\'s override. Are you sure?')) {
        UtilitiesModule.prototype.request(
            `/plugIt/stations/delete/${StationModuleEdit.prototype.stationsIds[id]}`,
            "GET"
        ).then(function () {
            window.location.href = `/plugIt/stations/edit/${StationModuleEdit.prototype.stationsIds[0]}`;
        })
    }
};

/**
 * Attaches the module events listeners to a tab.
 *
 * @param tabId: The tab id.
 * @param station: The station object.
 * @param sp: The service provider object.
 * @param default_radiovis_service: The default radiovis url.
 * @param default_radioepg_service: The default radioepg url.
 * @param default_radiospi_service: The default radiospi url.
 * @param default_radiotag_service: The default radiotag url.
 */
StationModuleEdit.prototype.attachEventsListenerToTab = function (
    tabId,
    station,
    sp,
    default_radiovis_service,
    default_radioepg_service,
    default_radiospi_service,
    default_radiotag_service,
) {

    // select handler

    Object.keys(StationModuleEdit.prototype.inputsTouched)
        .filter(function (key) {
            return ["default_language_", "location_country_"].includes(key);
        })
        .forEach(function (key) {
            $(`#${key}${tabId}`).on('change', function () {
                StationModuleEdit.prototype.inputsTouched[key].modified[tabId] = true;
            });
        });

    // on touched detection handler
    Object.keys(StationModuleEdit.prototype.inputsTouched).forEach(function (field_id) {
        const fieldData = StationModuleEdit.prototype.inputsTouched[field_id];
        $(`#${field_id}${tabId}`).on(fieldData.isInput ? 'keyup' : 'change', function () {
            if (tabId !== 0 && $(`#${field_id}${tabId}`).val() !== fieldData.defaultValue) {
                StationModuleEdit.prototype.updateInputTouchedStatus(tabId, true, fieldData.group, field_id);
            } else {
                fieldData.defaultValue = $(`#dot_grp_${tabId}_${fieldData.group}`).val();
            }
        });
    });

    // reset override buttons
    $('#reset-override-name-btn_' + tabId).click(function () {
        $('#station-name_' + tabId).val('');
        $('#short_name_' + tabId).val('');
        $('#medium_name_' + tabId).val('');
        $('#long_name_' + tabId).val('');
        $('#short_description_' + tabId).val('');
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, false, "name");
        StationModuleEdit.prototype.updateTab(tabId);
    });

    $('#reset-override-language-btn_' + tabId).click(function () {
        $(`#default_language_${tabId} option:first`).prop('selected', true);
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, false, "language");
        StationModuleEdit.prototype.updateTab(tabId);
    });

    $('#reset-override-links-btn_' + tabId).click(function () {
        $('#default_url_' + tabId).val('');
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, false, "links");
        StationModuleEdit.prototype.updateTab(tabId);
    });

    $('#reset-override-address-btn_' + tabId).click(function () {
        $('#postal_name_' + tabId).val('');
        $('#street_' + tabId).val('');
        $('#zipcode_' + tabId).val('');
        $('#city_' + tabId).val('');
        $(`#location_country_${tabId} option:first`).prop('selected', true);
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, false, "address");
        StationModuleEdit.prototype.updateTab(tabId);
    });

    $('#reset-override-contact-btn_' + tabId).click(function () {
        $('#phone_number_' + tabId).val('');
        $('#sms_number_' + tabId).val('');
        $('#sms_body_' + tabId).val('');
        $('#sms_description_' + tabId).val('');
        $('#email_address_' + tabId).val('');
        $('#email_description_' + tabId).val('');
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, false, "contact");
        StationModuleEdit.prototype.updateTab(tabId);
    });

    $('#reset-override-genres-btn_' + tabId).click(function () {
        StationModuleEdit.prototype.copyGenres(tabId, $('#genre_list_' + tabId), $('#genre_list_0'));
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, false, "genres", "genres");
    });

    // Link Copy Address to Button
    $('#copyAddressButton_' + tabId).on('click', function () {
        const $btn = $(this).button('loading');

        $('#postal_name_' + tabId).val(sp.postal_name);
        $('#street_' + tabId).val(sp.street);
        $('#zipcode_' + tabId).val(sp.zipcode);
        $('#city_' + tabId).val(sp.city);
        $('#location_country_' + tabId).val(sp.location_country);

        // Reset Button
        $btn.button('reset')
    });
    $('#keepNameButton_' + tabId).on('click', function () {
        const $btn = $(this).button('loading');

        $('#postal_name_' + tabId).val($('#medium_name_' + tabId).val());

        // Reset Button
        $btn.button('reset')
    });
    // Link Language to Button
    $('#copyLanguageButton_' + tabId).on('click', function () {
        const $btn = $(this).button('loading');

        $('#default_language_' + tabId).val(sp.default_language);

        // Reset Button
        $btn.button('reset')
    });

    if (station.id) {
        const initialName = $('#station-name_' + tabId).val();
        $('#station-name_' + tabId).keypress(function (event) {
            const newName = $('#station-name_' + tabId).val();
            if (initialName !== newName) {
                $('#station-name-change-warning_' + tabId).show();
            } else {
                $('#station-name-change-warning_' + tabId).hide();
            }
        });
        $('#station-name_' + tabId).change(function (event) {
            const newName = $('#station-name_' + tabId).val();
            if (initialName !== newName) {
                $('#station-name-change-warning_' + tabId).show();
            } else {
                $('#station-name-change-warning_' + tabId).hide();
            }
        });
    }

    // Automatic naming
    let short_name_edited = !!station.short_name;
    let medium_name_edited = !!station.medium_name;
    let long_name_edited = !!station.long_name;
    let short_description_edited = !!station.short_description;

    $('#station-name_' + tabId).on('focusout', function () {
        if ($(this).val() !== "") {
            if (!short_name_edited) {
                $('#short_name_' + tabId).val($(this).val().substring(0, StationModuleEdit.prototype.MAX_LENGTH_SHORT_NAME));
            }
            if (!medium_name_edited) {
                $('#medium_name_' + tabId).val($(this).val().substring(0, StationModuleEdit.prototype.MAX_LENGTH_MEDIUM_NAME));
            }
            if (!long_name_edited) {
                $('#long_name_' + tabId).val($(this).val().substring(0, StationModuleEdit.prototype.MAX_LENGTH_LONG_NAME));
            }
            if (!short_description_edited) {
                $('#short_description_' + tabId).val($(this).val());
            }
        }
    });
    $('#short_name_' + tabId).on('focusout', function () {
        if ($(this).val() !== "") {
            short_name_edited = true;
            if (!medium_name_edited) {
                $('#medium_name_' + tabId).val($(this).val().substring(0, StationModuleEdit.prototype.MAX_LENGTH_MEDIUM_NAME));
            }
            if (!long_name_edited) {
                $('#long_name_' + tabId).val($(this).val().substring(0, StationModuleEdit.prototype.MAX_LENGTH_LONG_NAME));
            }
            if (!short_description_edited) {
                $('#short_description_' + tabId).val($(this).val());
            }
        }
    });
    $('#medium_name_' + tabId).on('focusout', function () {
        if ($(this).val() !== "") {
            medium_name_edited = true;
            if (!long_name_edited) {
                $('#long_name_' + tabId).val($(this).val().substring(0, StationModuleEdit.prototype.MAX_LENGTH_LONG_NAME));
            }
            if (!short_description_edited) {
                $('#short_description_' + tabId).val($(this).val());
            }
        }
    });
    $('#long_name_' + tabId).on('focusout', function () {
        if ($(this).val() !== "") {
            long_name_edited = true;
            if (!short_description_edited) {
                $('#short_description_' + tabId).val($(this).val());
            }
        }
    });
    $('#short_description_' + tabId).on('focusout', function () {
        if ($(this).val() !== "") {
            short_description_edited = true;
        }
    });

    // Genres
    const genreRoot = $('#genre_list_' + tabId);
    genreRoot.on('change', function () {
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, true, "genres", "genres");
    });

    genreRoot.on('keyup', function () {
        StationModuleEdit.prototype.updateInputTouchedStatus(tabId, true, "genres", "genres");
    });

    // Services
    $('#radiovis_enabled_' + tabId).click(function () {
        $("#radiovis_enabled_options_" + tabId).toggle(this.checked);
        if (this.checked && $("#radiovis_service_" + tabId).val() === "") {
            $("#radiovis_service_" + tabId).val(default_radiovis_service);
        } else {
            $("#radiovis_service_" + tabId).val('');
        }
    });
    $('#radioepg_enabled_' + tabId).click(function () {
        $("#radioepg_enabled_options_" + tabId).toggle(this.checked);
        $("#radiospi_enabled_options_" + tabId).toggle(this.checked);
        $("#radioepgpi_enabled_options_" + tabId).toggle(this.checked);
        if (this.checked && $("#radioepg_service_" + tabId).val() === "") {
            $("#radioepg_service_" + tabId).val(default_radioepg_service);
        } else {
            $("#radioepg_service_" + tabId).val('');
        }

        if (this.checked && $("#radiospi_service_" + tabId).val() === "") {
            $("#radiospi_service_" + tabId).val(default_radiospi_service);
        } else {
            $("#radiospi_service_" + tabId).val('');
        }
    });
    $('#radiotag_enabled_' + tabId).click(function () {
        $("#radiotag_enabled_options_" + tabId).toggle(this.checked);
        if (this.checked && $("#radiotag_service_" + tabId).val() === "") {
            $("#radiotag_service_" + tabId).val(default_radiotag_service);
        } else {
            $("#radiotag_service_" + tabId).val('');
        }
    });
};