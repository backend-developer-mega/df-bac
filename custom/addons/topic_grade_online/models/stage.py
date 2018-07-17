# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class TopicActivityStage(models.Model):
    _name = "topic.grade.online.stage"
    _description = "Estados de las actividades"
    _order = 'sequence'

    name = fields.Char("Nombre del estado", required=True, translate=True)
    sequence = fields.Integer(
        "Secuencia", default=10)
    topic_id = fields.Many2one('topic.grade.online.topic', string='Tema de grado',
                             ondelete='cascade')
    fold = fields.Boolean("Agrupar")
    active = fields.Boolean("Active", default=True)

    @api.model
    def default_get(self, fields):
        if self._context and self._context.get('default_topic_id') and not self._context.get('topic_grade_online_stage_mono', False):
            context = dict(self._context)
            context.pop('default_topic_id')
            self = self.with_context(context)
        return super(TopicActivityStage, self).default_get(fields)