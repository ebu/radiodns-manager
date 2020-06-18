function StationModuleDetails() {
}
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
