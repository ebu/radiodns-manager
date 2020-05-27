function VisibilityModule() {
}

function noop() {

}

/**
 * Initialize the visibility module.
 * @param defaultTabId: The default tab id (or root id).
 * @param clientsIds: an array of all tabs ids.
 * @param onUpdate: Event that fires when the targeted tab must be updated.
 */
VisibilityModule.prototype.init = function (defaultTabId, clientsIds, onUpdate = noop) {
    const defaultTab = $('#nav_tab_' + defaultTabId);
    defaultTab.parent().addClass("active");
    defaultTab.addClass("active");

    clientsIds.forEach(function (clientId) {
        const currentTab = $('#nav_tab_' + clientId);
        currentTab.on('click', function (e) {
            e.preventDefault();
            $(".nav").find(".active").removeClass("active");
            currentTab.parent().addClass("active");
            currentTab.addClass("active");
            VisibilityModule.prototype.updateTabVisibility(clientId, clientsIds, onUpdate);
        });
    });

    VisibilityModule.prototype.updateTabVisibility(defaultTabId, clientsIds, onUpdate);
};

/**
 * Updates the visibility of the visibility module. Typically when you want to change the active tab.
 * @param tabId: The tab you want to make active.
 * @param clientsIds: an array of all tabs ids.
 * @param onUpdate: Event that fires when the targeted tab must be updated.
 */
VisibilityModule.prototype.updateTabVisibility = function (tabId, clientsIds, onUpdate) {
    $('#tab_wrapper_' + tabId).show();
    for (let i = 0; i < clientsIds.length; i++) {
        if (tabId !== clientsIds[i]) {
            $('#tab_wrapper_' + clientsIds[i]).hide();
        } else {
             onUpdate(clientsIds[i]);
        }
    }
};
