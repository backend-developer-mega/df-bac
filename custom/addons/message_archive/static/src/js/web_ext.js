odoo.define('html_in_tree_field.web_ext', function (require) {
    "use strict";
    var Listview = require('web.ListView');
    var formats = require('web.formats');

    Listview.Column.include({
        _format: function (row_data, options) {
        // Removed _.escape() function to display html content.
        // Before : return _.escape(formats.format_value(row_data[this.id].value, this, options.value_if_empty));
        return formats.format_value(row_data[this.id].value, this, options.value_if_empty);
        }
    });
});