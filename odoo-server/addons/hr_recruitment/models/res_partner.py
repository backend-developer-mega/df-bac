# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PartnerStudent(models.Model):
    _inherit = 'res.partner'

    department_id = fields.Many2one('hr.department', string='Departamento', required=True)
    career_id = fields.Many2one('hr.job', string='Carrera')