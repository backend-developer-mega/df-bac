# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Activity(models.Model):

    _name = "topic.grade.online.activity"
    _description = "Actividades del trabajo de grado"
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']
    _mail_mass_mailing = _('Activity')


    def _default_stage_id(self):
        if self._context.get('default_topic_id'):
            ids = self.env['topic.grade.online.stage'].search([
                '|',
                ('topic_id', '=', False),
                ('topic_id', '=', self._context['default_topic_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        return False

    name = fields.Char(string='Actividad', required=True, index=True, translate=True)
    description = fields.Text(string='Descripcion')
    topic_id = fields.Many2one('topic.grade.online.topic', "Tema de Trabajo de grado")
    stage_id = fields.Many2one('topic.grade.online.stage', 'Estado', track_visibility='onchange',
                               domain="['|', ('topic_id', '=', False), ('topic_id', '=', topic_id)]",
                               copy=False, index=True,
                               group_expand='_read_group_stage_ids',
                               default=_default_stage_id)
    last_stage_id = fields.Many2one('topic.grade.online.stage', "Ultimo estado")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'topic.grade.online.activity')], string='Adjunto')
    day_open = fields.Float(compute='_compute_day', string="Fecha abierta")
    day_close = fields.Float(compute='_compute_day', string="Fecha cerrada")
    date_closed = fields.Datetime("Closed", readonly=True, index=True)
    date_open = fields.Datetime("Assigned", readonly=True, index=True)
    date_last_stage_update = fields.Datetime("Last Stage Update", index=True, default=fields.Datetime.now)
    date_action = fields.Date("Next Action Date")
    title_action = fields.Char("Next Action", size=64)
    department_id = fields.Many2one('hr.job', "Department")
    user_id = fields.Many2one('res.users', "Responsible", track_visibility="onchange", default=lambda self: self.env.uid)
    create_date = fields.Datetime("Creation Date", readonly=True, index=True)
    write_date = fields.Datetime("Update Date", readonly=True)
    active = fields.Boolean("Active", default=True)
    evaluations_id = fields.Many2one('topic.grade.online.evaluations')
    #document_ids = fields.One2many('ir.attachment', string="Documentos")

    @api.depends('date_open', 'date_closed')
    @api.one
    def _compute_day(self):
        if self.date_open:
            date_create = datetime.strptime(self.create_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            date_open = datetime.strptime(self.date_open, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            self.day_open = (date_open - date_create).total_seconds() / (24.0 * 3600)

        if self.date_closed:
            date_create = datetime.strptime(self.create_date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            date_closed = datetime.strptime(self.date_closed, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            self.day_close = (date_closed - date_create).total_seconds() / (24.0 * 3600)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        topic_id = self._context.get('default_topic_id')
        search_domain = [('topic_id', '=', False)]
        if topic_id:
            search_domain = ['|', ('topic_id', '=', topic_id)] + search_domain
        if stages:
            search_domain = ['|', ('id', 'in', stages.ids)] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        vals = self._onchange_stage_id_internal(self.stage_id.id)
        if vals['value'].get('date_closed'):
            self.date_closed = vals['value']['date_closed']

    def _onchange_stage_id_internal(self, stage_id):
        if not stage_id:
            return {'value': {}}
        stage = self.env['topic.grade.online.stage'].browse(stage_id)
        if stage.fold:
            return {'value': {'date_closed': fields.datetime.now()}}
        return {'value': {'date_closed': False}}

    @api.onchange('topic_id')
    def onchange_topic_id(self):
        vals = self._onchange_topic_id_internal(self.topic_id.id)
        self.department_id = vals['value']['department_id']
        self.user_id = vals['value']['user_id']
        self.stage_id = vals['value']['stage_id']


    def _onchange_topic_id_internal(self, topic_id):
        department_id = False
        user_id = False
        stage_id = self.stage_id.id
        if topic_id:
            topic = self.env['topic.grade.online.topic'].browse(topic_id)
            department_id = topic.department_id.id
            user_id = topic.docente_director_id.id
            if not self.stage_id:
                stage_ids = self.env['topic.grade.online.stage'].search([
                    '|',
                    ('topic_id', '=', False),
                    ('topic_id', '=', topic.id),
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).ids
                stage_id = stage_ids[0] if stage_ids else False

        return {'value': {
            'department_id': department_id,
            'user_id': user_id,
            'stage_id': stage_id
        }}

    @api.multi
    def action_makeMeeting(self):
        self.ensure_one()
        partners = self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'search_default_partner_ids': self.user_id.name,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name
        }
        return res

    

    @api.model
    def create(self, vals):
        if vals.get('topic_id') or self._context.get('default_topic_id'):
            topic_id = vals.get('topic_id') or self._context.get('default_topic_id')
            for key, value in self._onchange_topic_id_internal(topic_id)['value'].iteritems():
                if key not in vals:
                    vals[key] = value
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        if 'stage_id' in vals:
            vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))['value'])
        return super(Activity, self.with_context(mail_create_nolog=True)).create(vals)

    @api.multi
    def write(self, vals):
        # user_id change: update date_open
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        # stage_id: track last stage before update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            vals.update(self._onchange_stage_id_internal(vals.get('stage_id'))['value'])
            for activity in self:
                vals['last_stage_id'] = activity.stage_id.id
                res = super(Activity, self).write(vals)
        else:
            res = super(Activity, self).write(vals)
        return res