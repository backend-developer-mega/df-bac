#!/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv.expression import get_unaccent_wrapper
from django.utils.encoding import smart_str, smart_unicode

class RecruitmentSettings(models.TransientModel):
    _name = 'hr.recruitment.config.settings'
    _inherit = ['res.config.settings']

    module_hr_recruitment_survey = fields.Selection(selection=[
        (0, "Do not use interview forms"),
        (1, "Use interview forms during the recruitment process")
        ], string='Interview Form')

    general_coordinator = fields.Many2one('res.partner', "Coordinador general")
    direct_meeting = fields.Many2one('res.partner', "Junta Directiva")

    @api.model
    def get_default_general_coordinator_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'general_coordinator': int(conf.get_param('global_settings.general_coordinator')),
        }

    @api.one
    def set_general_coordinator_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('global_settings.general_coordinator', str(self.general_coordinator.id))

    @api.model
    def get_default_direct_meeting_values(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'direct_meeting': int(conf.get_param('global_settings.direct_meeting')),
        }

    @api.one
    def set_direct_meeting_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('global_settings.direct_meeting', str(self.direct_meeting.id))

class ApplicantGlobalSettings(models.Model):
    _inherit = "hr.applicant"

    ROL_EMAIL = [
    ('0', 'Junta Directiva'),
    ('1', 'Coordinador de trabajos de grado'),
    ('2', 'Jefe de departamento'),
    ('3', 'Coordinador de carrera'),
    ('4', 'Docente director')
    ]

    general_coordinator = fields.Many2one('res.partner', "Coordinador general", compute="_get_values_global", store=False)
    direct_meeting = fields.Many2one('res.partner', "Junta Directiva", compute="_get_values_global", store=False)

    addressee_number_email = fields.Selection(ROL_EMAIL, "Destinatario email", related='stage_id.email_data')
    addressee_name_email = fields.Char(compute='_get_name_addressee')

    @api.depends('name')
    def _get_name_addressee(self):
        key = self.addressee_number_email
        choices = {'0': smart_str(self.direct_meeting.name) + ' (Junta Directiva)', 
                   '1': smart_str(self.general_coordinator.name) + ' (Coordinador de trabajos de grado)',
                   '2': smart_str(self.department_head.name) + ' (Jefe de departamento)',
                   '3': smart_str(self.user_id.name) + ' (Coordinador de carrera)',
                   '4': smart_str(self.teacher_director.name) + ' (Docente director)',
        }
        result = choices.get(key, '1')
        self.addressee_name_email = result

    @api.depends('name')
    def _get_values_global(self):
        for x in self:
            x.general_coordinator = int(self.env['ir.config_parameter'].get_param('global_settings.general_coordinator'))
            x.direct_meeting = int(self.env['ir.config_parameter'].get_param('global_settings.direct_meeting'))