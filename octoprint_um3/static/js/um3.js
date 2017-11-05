/*
 * View model for OctoPrint-Um3
 *
 * Author: Peter Backx
 * License: AGPLv3
 */
$(function() {
    function Um3ViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        self.currentPrinter = ko.observable();
        self.availablePrinters = ko.observable();

        self.setPrinter = function() {
            self.currentPrinter(this.service_name);
        };

        self.currentPrinter.subscribe(function(newValue) {
            self.settings.settings.plugins.um3.printer(newValue);
        });

        self.onBeforeBinding = function() {
            self.currentPrinter(self.settings.settings.plugins.um3.printer());

            OctoPrint.get('api/plugin/um3').done(function(printers) {
                console.log('UM3 plugin: loaded available printers');
                self.setAvailablePrinters(printers);
            })
        };

        self.onDataUpdaterPluginMessage = function(plugin, printers) {
            if (plugin === 'um3') {
                console.log('UM3 plugin: updated available printers');
                self.setAvailablePrinters(printers);
            }
        };

        self.setAvailablePrinters = function(printers) {
            printers.forEach(function(printer) { printer.nameWithService = printer.name + ' (' + printer.service_name + ')'});
            self.availablePrinters(printers);
        }
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        Um3ViewModel,
        [ "settingsViewModel" ],
        [ "#settings_plugin_um3" ]
    ]);
});
