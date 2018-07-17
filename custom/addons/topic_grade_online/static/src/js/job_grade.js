odoo.define('topic_grade_online.topic_grade_online', function(require) {
"use strict";

var KanbanRecord = require('web_kanban.Record');

KanbanRecord.include({
    on_card_clicked: function() {
        if (this.model === 'topic.grade.online.topic') {
            this.$('.oe_applications a').first().click();
        } else {
            this._super.apply(this, arguments);
        }
    },
});

});
