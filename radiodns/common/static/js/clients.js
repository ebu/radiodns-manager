function ClientModule() {
}

// current state of the inputs
ClientModule.prototype.clientEditInputsState = {};
ClientModule.prototype.clientEditSavedInputsState = {};

// ==================================== UTILITIES ====================================


/**
 * Toggles the client creation mode.
 */
ClientModule.prototype.toggleClientCreation = function () {
    const newClientContainer = $('#new_client');
    const toggleButton = $('#client_creation_toggle_button');
    ClientModule.prototype.resetInputsValidity('new');

    if (newClientContainer.is(":visible")) {
        toggleButton.text("Add a new client");
        toggleButton.removeClass('btn-danger');
        newClientContainer.hide();
    } else {
        toggleButton.text("Cancel");
        toggleButton.addClass('btn-danger');
        newClientContainer.show();
        ClientModule.prototype.updateInputsValidity('new');
    }
};

/**
 * Generate a delete and a edit button with the correct bindings to edit and delete a client.
 * @param id: the id of a client.
 * @returns {string}: the string to be insterted in dom.
 */
ClientModule.prototype.genEditDeleteBtn = function (id) {
    return `<div>
                <button id="toggle_edit_btn_${id}" type="button" class="btn btn-sm btn-primary" onclick="ClientModule.prototype.enterClientUpdateMode(${id});">Edit</>
                <button id="cancel_edit_btn_${id}" type="button" class="btn btn-sm btn-mr btn-danger" onclick="ClientModule.prototype.deleteClient(${id});">Delete</>
            </div>`
};

/**
 * Generate a save and a cancel button with the correct bindings to save the modifications done to a client or cancel those
 * modifications.
 * @param id: the id of a client.
 * @returns {string}: the string to be insterted in dom.
 */
ClientModule.prototype.genSaveCancelBtn = function (id) {
    return `<button
                type="button"
                id="update_save_btn_${id}"
                class="btn btn-sm btn-primary"
                onclick="ClientModule.prototype.updateClient(${id});"
                >Save</button>
            <button
                id="cancel_update_save_btn_${id}"
                type="button" class="btn btn-sm btn-danger"
                onclick="ClientModule.prototype.leaveClientUpdateMode(${id});"
                >Cancel</button>`
};

/**
 * Adds a new row to the client table.
 * @param client: the client to be added.
 */
ClientModule.prototype.addNewRow = function (client) {
    const newTr = $($('#radiodns-clients-table').DataTable().row.add([
        ClientModule.prototype.genClientTextRow(client.name),
        ClientModule.prototype.genClientTextRow(client.email),
        ClientModule.prototype.genClientTextRowCopyButton(client.id, client.identifier),
        ClientModule.prototype.genEditDeleteBtn(client.id),
    ]).node());
    newTr.prop('id', `client_row_${client.id}`);
    const tds = newTr.children();
    $(tds[0]).prop('id', `client_name_td_${client.id}`);
    $(tds[1]).prop('id', `client_email_td_${client.id}`);
    $(tds[2]).prop('id', `client_identifier_td_${client.id}`);
    $(tds[3]).prop('id', `client_options_td_${client.id}`);

    ClientModule.prototype.updateSearchTable();
};

/**
 * Handles errors returned from the server.
 *
 * Note: Currently the PlugIt api does not allow any other status code than 200 when generating json response.
 * So that is why the status codes are included in the response.
 *
 * @param error: The request error.
 */
ClientModule.prototype.requestErrorHandler = function (error) {
    const errorDisplay = $('#ajax_error_display');
    switch (error.status) {
        case 409:
            errorDisplay.append(`<li>${error.msg}</li>`);
            break;
        case 422:
            errorDisplay.append('<li>The server didn\'t received any payload. Please contact an administrator.</li>');
            break;
        default:
            errorDisplay.append('<li>An unexpected error has occured. Please contact an administrator.</li>');
    }
    const clientOperationResultDisplay = $('#client_operation_success');
    clientOperationResultDisplay.empty();
    clientOperationResultDisplay.hide();
};

/**
 * Display a success message at the top of the screen.
 * @param msg: The message to be displayed.
 */
ClientModule.prototype.displaySuccessText = function (msg) {
    const clientOperationResultDisplay = $('#client_operation_success');
    clientOperationResultDisplay.show();
    clientOperationResultDisplay.empty();
    clientOperationResultDisplay.append(msg);
};

/**
 * Transforms a client row into an editable one.
 * @param id: The client id that will be modified.
 */
ClientModule.prototype.enterClientUpdateMode = function (id) {
    const nameTd = $('#client_name_td_' + id);
    const emailTd = $('#client_email_td_' + id);
    const identifierTd = $('#client_identifier_td_' + id);
    const identifierValue = $('#client_identifier_value_' + id);
    const optionsContainer = $('#client_options_td_' + id);

    ClientModule.prototype.clientEditInputsState[id] = {
        name: nameTd.text(),
        email: emailTd.text(),
        identifier: identifierValue.text()
    };

    ClientModule.prototype.clientEditSavedInputsState[id] = {
        name: nameTd.text(),
        email: emailTd.text(),
        identifier: identifierValue.text()
    };

    nameTd.empty();
    emailTd.empty();
    identifierTd.empty();

    nameTd.append(ClientModule.prototype.genClientEditInput(id, 'name', ClientModule.prototype.clientEditInputsState[id].name));
    emailTd.append(ClientModule.prototype.genClientEditInput(id, 'email', ClientModule.prototype.clientEditInputsState[id].email));
    identifierTd.append(ClientModule.prototype.genClientEditInput(id, 'identifier', ClientModule.prototype.clientEditInputsState[id].identifier));

    $(`#client_name_${id}`).keyup(ClientModule.prototype.onInputChange(id));
    $(`#client_email_${id}`).keyup(ClientModule.prototype.onInputChange(id));
    $(`#client_identifier_${id}`).keyup(ClientModule.prototype.onInputChange(id));

    optionsContainer.empty();
    optionsContainer.append(ClientModule.prototype.genSaveCancelBtn(id));
    ClientModule.prototype.updateInputsValidity(id);
};

/**
 * Transforms a client editable row into a static one. Will use the clientEditSavedInputsState of this module if no newValues
 * are specified.
 * @param id: The client id.
 * @param newValues: the new values that the row will have.
 */
ClientModule.prototype.leaveClientUpdateMode = function (id, newValues = undefined) {
    const module = ClientModule.prototype;

    $("td:has(input)").toArray().forEach(function (td) {
        $(td).addClass("identifier-container");
        $(td).css({"vertical-align": ""});
    });

    const nameTd = $('#client_name_td_' + id);
    const emailTd = $('#client_email_td_' + id);
    const identifierTd = $('#client_identifier_td_' + id);
    const optionsContainer = $('#client_options_td_' + id);

    nameTd.empty();
    emailTd.empty();
    identifierTd.empty();

    nameTd.append(module.genClientTextRow(newValues ? newValues.name : module.clientEditSavedInputsState[id].name));
    emailTd.append(module.genClientTextRow(newValues ? newValues.email : module.clientEditSavedInputsState[id].email));
    identifierTd.append(module.genClientTextRowCopyButton(id, newValues ? newValues.identifier : module.clientEditSavedInputsState[id].identifier));

    optionsContainer.empty();
    optionsContainer.append(module.genEditDeleteBtn(id));
};

/**
 * Generates a parameterizable editable input to edit a client.
 * @param id: the id of the client that will be edited.
 * @param name: the name of the input.
 * @param value: the value that will initialize the input.
 * @returns {string}
 */
ClientModule.prototype.genClientEditInput = function (id, name, value) {
    return `
            <div class="validated_input_container">
                <input
                    id="client_${name}_${id}"
                    type="text"
                    name="${name}"
                    class="form-control"
                    value="${value}"
                >
                <div id="client_edit_error_display_${name}_${id}" class="error_message_container"></div>
             </div>`;
};

/**
 * Generates a container for some text to be added in a tab <td>.
 * @param text: The text.
 * @returns {string}
 */
ClientModule.prototype.genClientTextRow = function (text) {
    return `<div class="identifier-container">${text}</div>`
};

/**
 * Generates a container for some text and a copy button to copy the text to be added in a tab <td>.
 * @param text: The text.
 * @returns {string}
 */
ClientModule.prototype.genClientTextRowCopyButton = function (client_id, text) {
    return `<div class="identifier-wrapper">
                <button type="button" class="btn btn-default btn-sm btn-default btn-sm"
                    onclick="ClientModule.prototype.copyIdentifier(${client_id})">Copy</button>
                <div class="identifier-container" id="client_identifier_value_${client_id}">${text}</div>
            </div>`
};

// ==================================== CRUD ====================================

/**
 * Make the http request to create a client based on the new client form's inputs and handle the server's response.
 */
ClientModule.prototype.postClient = function () {
    const saveButton = $('#new_client_save_btn');
    const errorDisplay = $('#ajax_error_display');

    const clientNameInput = $('#client_name_new');
    const clientEmailInput = $('#client_email_new');
    const clientIdentifier = $('#client_identifier_new');

    errorDisplay.empty();
    saveButton.text("Saving...");
    saveButton.prop("disabled", true);
    UtilitiesModule.prototype.request(ebuio_baseUrl + 'clients/add', 'post', {
        name: clientNameInput.val(),
        email: clientEmailInput.val(),
        identifier: clientIdentifier.val(),
    })
        .then(function (response) {
            clientNameInput.val('');
            clientEmailInput.val('');
            clientIdentifier.val('');
            ClientModule.prototype.addNewRow(response.client);
            ClientModule.prototype.displaySuccessText("The client has been successfully created.");
            ClientModule.prototype.updateSearchTable();
            ClientModule.prototype.resetInputsValidity('new');
        })
        .catch(function (error) {
            ClientModule.prototype.requestErrorHandler(error)
        })
        .then(function () {
            saveButton.text("Submit");
            saveButton.prop("disabled", false);
        });
};

/**
 * Make the http request to update a client based on the client row form's input and handle the server's response.
 * @param id: The id of the client to update.
 */
ClientModule.prototype.updateClient = function (id) {
    const module = ClientModule.prototype;
    const errorDisplay = $('#ajax_error_display');
    const saveButton = $('#update_save_btn_' + id);

    if (module.clientEditInputsState[id].identifier !== module.clientEditSavedInputsState[id].identifier
        && !confirm('By changing the client identifier, third party devices may not be able to access your stations ' +
            'overrides. Do you really want to proceed?')) {
        return;
    }

    errorDisplay.empty();
    saveButton.text("Saving...");
    saveButton.prop("disabled", true);

    UtilitiesModule.prototype.request(`${ebuio_baseUrl}clients/patch/${id}`, 'post', {
        name: module.clientEditInputsState[id].name,
        email: module.clientEditInputsState[id].email,
        identifier: module.clientEditInputsState[id].identifier,
    })
        .then(function (response) {
            module.displaySuccessText("The client has been successfully updated.");
            module.leaveClientUpdateMode(id, {
                name: response.client.name,
                email: response.client.email,
                identifier: response.client.identifier,
            });
            ClientModule.prototype.updateSearchTable();
            ClientModule.prototype.resetInputsValidity(id);
        })
        .catch(function (error) {
            module.requestErrorHandler(error)
        })
        .then(function () {
            saveButton.text("Submit");
            saveButton.prop("disabled", false);
        });
};

/**
 * Make the http request to delete a client and handle the server's response.
 * @param id: The id of the client to delete.
 */
ClientModule.prototype.deleteClient = function (id) {
    if (confirm('Are you sure ? All station overrides related to this client will be deleted as well.')) {
        UtilitiesModule.prototype.request(`${ebuio_baseUrl}clients/delete/${id}`, 'delete')
            .then(function () {
                ClientModule.prototype.displaySuccessText("The client has been successfully deleted.");
                $('#radiodns-clients-table').DataTable()
                    .row($('#client_row_' + id))
                    .remove()
                    .draw();
            });
    }
};

// ==================================== INPUTS ====================================

/**
 * Returns a function that update the css for a valid text input.
 * @param input: The text input.
 * @param errorDisplay: The div that serves as an error display.
 * @returns {Function}: The validation function.
 */
ClientModule.prototype.updateValidInputClass = function (input, errorDisplay) {
    return function () {
        input.removeClass("input_invalid");
        input.addClass("input_valid");
        errorDisplay.empty();
    };
};

/**
 * Returns a function that update the css for an invalid text input.
 * @param input: The text input.
 * @param errorDisplay: The div that serves as an error display.
 * @returns {Function}: The validation function.
 */
ClientModule.prototype.updateInvalidInputClass = function (input, errorDisplay) {
    return function (errorMsg) {
        input.removeClass("input_valid");
        input.addClass("input_invalid");
        errorDisplay.empty();
        errorDisplay.append(errorMsg)
    };
};

/**
 * Updates inputs validity for a client. Applies the correct classes for each input + disable submit button while
 * at least one input is not valid.
 * @param id: The client id.
 */
ClientModule.prototype.updateInputsValidity = function (id) {
    const module = ClientModule.prototype;
    const clientNameInput = $(`#client_name_${id}`);
    const clientNameErrorDisplay = $(`#client_edit_error_display_name_${id}`);

    const clientEmailInput = $(`#client_email_${id}`);
    const clientEmailErrorDisplay = $(`#client_edit_error_display_email_${id}`);

    const clientIdentifierInput = $(`#client_identifier_${id}`);
    const clientIdentifierErrorDisplay = $(`#client_edit_error_display_identifier_${id}`);

    const nameValid = InputsValidation.prototype.checkInputValidity(
        module.clientEditInputsState[id]['name'],
        [
            InputsValidation.prototype.inputCannotBeEmpty("name"),
            InputsValidation.prototype.inputCannotBeLongerThan("name", 255),
        ],
        module.updateInvalidInputClass(clientNameInput, clientNameErrorDisplay),
        module.updateValidInputClass(clientNameInput, clientNameErrorDisplay)
    );
    const emailValid = InputsValidation.prototype.checkInputValidity(
        module.clientEditInputsState[id]['email'],
        [
            InputsValidation.prototype.inputCannotBeEmpty("email"),
            InputsValidation.prototype.inputCannotBeLongerThan("email", 255),
            InputsValidation.prototype.emailValid,
        ],
        module.updateInvalidInputClass(clientEmailInput, clientEmailErrorDisplay),
        module.updateValidInputClass(clientEmailInput, clientEmailErrorDisplay)
    );
    const identifierValid = InputsValidation.prototype.checkInputValidity(
        module.clientEditInputsState[id]['identifier'],
        [
            InputsValidation.prototype.inputCannotBeShorterThan("identifier", 16),
            InputsValidation.prototype.inputCannotBeLongerThan("identifier", 128),
            InputsValidation.prototype.onlyAlphanumeric("identifier"),
        ],
        module.updateInvalidInputClass(clientIdentifierInput, clientIdentifierErrorDisplay),
        module.updateValidInputClass(clientIdentifierInput, clientIdentifierErrorDisplay)
    );

    if (nameValid && emailValid && identifierValid) {
        $('#update_save_btn_' + id).prop("disabled", false);
    } else {
        $('#update_save_btn_' + id).prop("disabled", true);
    }

    $("td:has(input)").toArray().forEach(function (td) {
        $(td).css({"vertical-align": "top"});
    });
};

/**
 * Resets a client inputs along with their validity.
 * @param id: The client id.
 */
ClientModule.prototype.resetInputsValidity = function (id) {
    const module = ClientModule.prototype;

    module.clientEditInputsState[id]['name'] = '';
    module.clientEditInputsState[id]['email'] = '';
    module.clientEditInputsState[id]['identifier'] = '';

    $(`#client_name_${id}`).removeClass("input_invalid input_valid");
    $(`#client_email_${id}`).removeClass("input_invalid input_valid");
    $(`#client_identifier_${id}`).removeClass("input_invalid input_valid");

    $(`#client_edit_error_display_name_${id}`).empty();
    $(`#client_edit_error_display_email_${id}`).empty();
    $(`#client_edit_error_display_identifier_${id}`).empty();

    module.updateInputsValidity(id)
};


/**
 * OnChange event handler factory. The target input MUST have a name corresponding to a key of the clientEditInputsState
 * object of this module. For instance, if you name your input 'name' the corresponding value will be set in the
 * clientEditInputsState and you can retrieve it under the client id that it is stored.
 * @param id: The id of the client. If it is a new client, by convention the id will be 'new'.
 * @returns {Function}
 */
ClientModule.prototype.onInputChange = function (id) {
    return function (event) {
        ClientModule.prototype.clientEditInputsState[id][event.target.name] = event.target.value;
        ClientModule.prototype.updateInputsValidity(id);
    };
};

// ==================================== MISC ====================================

/**
 * Copies the identifier of a specific client into the paper clip.
 * @param client_id: The specific client's id.
 */
ClientModule.prototype.copyIdentifier = function (client_id) {
    const copyEventListener = function (e) {
        e.clipboardData.setData('text/plain', $(`#client_identifier_value_${client_id}`).text());
        e.preventDefault();
    };
    document.addEventListener('copy', copyEventListener);
    document.execCommand("copy");
    document.removeEventListener('copy', copyEventListener);
};

/**
 * Triggers a re-draw off the Datatable.
 */
ClientModule.prototype.updateSearchTable = function () {
    $('#radiodns-clients-table').DataTable().draw();
};


/**
 * Makes a identifier suggestion.
 *
 * Note: This function does not verify the availability of the randomly generated string.
 *
 * @param length: The length that the string will have.
 */
ClientModule.prototype.makeIdentifierSuggestion = function (length = 128) {
    let text = "";
    const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (let i = 0; i < length; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    $('#client_identifier_new').val(text);
    ClientModule.prototype.clientEditInputsState['new']['identifier'] = text;
    ClientModule.prototype.updateInputsValidity('new');
};

/**
 * Module initialization. Attaches the event listeners for inputs and fetches the existing list of clients.
 */
$(document).ready(function () {
    const client_display = $('#clients_display');

    ClientModule.prototype.clientEditInputsState['new'] = {};
    $("#client_name_new").keyup(ClientModule.prototype.onInputChange('new'));
    $("#client_email_new").keyup(ClientModule.prototype.onInputChange('new'));
    $("#client_identifier_new").keyup(ClientModule.prototype.onInputChange('new'));

    const table = $('#radiodns-clients-table').DataTable({
        "retrieve": true,
        "paging": false,
        "ordering": true,
        "info": true,
        columnDefs: [{orderable: false, targets: [3]},
            {"bSearchable": false, "aTargets": [3]}],
    });

    UtilitiesModule.prototype.request(ebuio_baseUrl + 'clients/list', 'get')
        .then(function (data) {
            data.clients.forEach(function (client) {
                ClientModule.prototype.addNewRow(client);
            });
            if (data.clients.length === 0) {
                table.clear().draw();
            }
        })
        .catch(function (_) {
            client_display.empty();
            client_display.append('<tr><td>Failed to retrieve the client list.</tr></td>');
        })
        .then(function () {
            $('#loading_tr').hide();
        });
});
