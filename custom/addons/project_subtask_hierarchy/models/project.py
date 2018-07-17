# -- coding: utf-8 --
# Copyright (C) 2017-present Technaureus Info Solutions(http://www.technaureus.com/).

from odoo import api, fields, models

class Task(models.Model):
    _inherit = "project.task"
    
    parent_id = fields.Many2one('project.task', string='Parent Task')
    subtask_ids = fields.One2many('project.task', 'parent_id', string='Sub Tasks')
    
