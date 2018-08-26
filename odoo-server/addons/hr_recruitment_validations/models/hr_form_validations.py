# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class AddValidationHr(models.Model):
    _inherit = 'hr.applicant'

    #stage_check = fields.Boolean(related='stage_id.end_stage')
    

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = (record.name[:40] + '...') if len(record.name) > 40 else record.name
            res.append((record.id, name))
        return res

    @api.depends('name')
    def _compute_set_value(self):
        self.department_head = self.department_id.manager_partner_id.id

    @api.onchange('description')
    def _set_description_name(self):
        self.name = self.description

    @api.multi
    def specify_available(self, partner_ids=None):
        if partner_ids:
            try:
                _logger.info('-----specify_available---------->  %s ', partner_ids)
                for line in partner_ids:
                    self.env['res.partner'].sudo().search([('id', '=', line)]).write({'available': False})
                return True
            except AccessError:
                return False

    @api.multi
    def specify_unavailable(self, partner_ids=None):
        if partner_ids:
            try:
                _logger.info('-----specify_available---------->  %s ', partner_ids)
                for line in partner_ids:
                    self.env['res.partner'].sudo().search([('id', '=', line)]).write({'available': True})
                return True
            except AccessError:
                return False


    # @api.depends('stage_id')
    # def _set_student_stage_id(self): 
    #     partner_ids = []
    #     _logger.info('-------------ONCHANGE------------->  %s ', self.student_ids.ids)
    #     if len(self.student_ids) > 0:
    #         sql_query = """DELETE FROM mail_followers WHERE res_model = 'hr.applicant' AND res_id = %s """
    #         params = (int(self.id),)
    #         self.env.cr.execute(sql_query, params)
    #         partner_ids = self.student_ids.ids
    #         _logger.info('----------------------onchange---------------------------------->  %s --- %s', partner_ids, self.student_ids.ids)
    #     if partner_ids:
    #         self.message_subscribe(partner_ids)

    # @api.onchange('student_ids')
    # def _onchange_members_user(self):
    #     partner_ids = []
    #     if len(self.student_ids) > 0:
    #         for r in self:
    #             for line in r.student_ids:
    #                 partner_ids.append(line.id)
    #                 _logger.info('---------------------------------------------------------------->  %s', partner_ids)
    #     if partner_ids:
    #         self.message_subscribe(partner_ids)

    @api.multi
    def write(self, data):
        partner_ids = []
        _logger.info('----------------------CREATE 2---------------------------------->  %s --- %s', data.get('student_ids'), self.student_ids.ids)
        if data.get('student_ids'):
            self.specify_unavailable(self.student_ids.ids)
            sql_query = """DELETE FROM mail_followers WHERE res_model = 'hr.applicant' AND res_id = %s """
            params = (int(self.id),)
            self.env.cr.execute(sql_query, params)
            partner_st = str(data['student_ids']).replace('False', '0').replace('False', '0')
            partner_ids = eval(partner_st)[0][2]
            emails = ''
            template_res_partner = self.env['res.partner']
            for ids_partner in partner_ids: 
                emails = template_res_partner.search([('id', '=',ids_partner)], limit=1).email + ',' +emails
            if emails:
                data['email_cc'] = emails[:len(emails) - 1] 
        res = super(AddValidationHr, self).write(data)
        if data.has_key("stage_id"):
            if data['stage_id'] and data['last_stage_id']:
                if data['last_stage_id'] > data['stage_id']:
                    raise UserError(_("No puede mover a una etapa anterior!"))
                if data['stage_id'] > data['last_stage_id']:
                    if data['stage_id'] == 2:
                        sql_query = """DELETE FROM mail_followers WHERE res_model = 'hr.applicant' AND res_id = %s """
                        params = (int(self.id),)
                        self.env.cr.execute(sql_query, params)
                        partner_ids = self.student_ids.ids
        if partner_ids:
            self.message_subscribe(partner_ids)
            self.specify_available(partner_ids)
        return res

    @api.model
    def create(self, vals):
        vals['partner_id'] = self.department_id.manager_partner_id.id
        data = [x.id for x in self.student_ids]
        if 5 < len(self.student_ids):
            raise UserError(_("El numero de integrantes debe ser igual o menor a 5"))
        partner_ids = []
        if vals.get('student_ids'):
            partner_st = str(vals['student_ids']).replace('False', '0').replace('False', '0')
            partner_ids = eval(partner_st)[0][2]
            emails = ''
            template_res_partner = self.env['res.partner']
            for ids_partner in partner_ids: 
                emails = template_res_partner.search([('id', '=',ids_partner)], limit=1).email + ',' +emails
            if emails:
                vals['email_cc'] = emails[:len(emails) - 1] 
        res = super(AddValidationHr, self).create(vals)
        if partner_ids:
            res.message_subscribe(partner_ids)
            res.message_subscribe(vals['partner_id'])
            self.specify_available(partner_ids)
        return res

    # @api.onchange('name')
    # def _verify_other_applicant(self):
    #     raise UserError(_("""El sistema a determinado que usted tiene un proceso activo 
    #         actualmente en el sistema, no podra guardar ninguna solicitud de tema de grado, 
    #         ya que no puede tener mas de una tema de grado activo en proceso al mismo tiempo."""))

    @api.onchange('student_ids')
    def _verify_valid_count(self):
        if 5 < len(self.student_ids):
            raise ValidationError(_("El numero de integrantes debe ser igual o menor a 5"))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AddValidationHr, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        partner_id_actu = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id.id
        is_personal_adminis = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id.is_company
        sql_query = """SELECT students_lead_id_res 
                        FROM students_lead_tag_rel_res 
                        WHERE students_tag_id_res = %s
                    """
        params = (partner_id_actu,)
        self.env.cr.execute(sql_query, params)
        results = [a for (a,) in self.env.cr.fetchall()]
        end_stage = False
        for line in results:
            result_data = self.env['hr.applicant'].search([('id','=', line)], limit=1).active
            if result_data:
                end_stage = self.env['hr.applicant'].search([('id','=', line)], limit=1).stage_id.end_stage
        if view_type == 'kanban':
            for node_form in doc.xpath("//kanban"):
                node_form.set("create", 'false')
        if view_type == 'form':
            for node_form in doc.xpath("//form"):
                #_logger.info('-############-->  %s ## %s ## %s', len(results), is_personal_adminis, sequence)
                if len(results) > 0 and not is_personal_adminis:
                    node_form.set("create", 'false')
                if len(results) > 0 and not is_personal_adminis and end_stage:
                    node_form.set("create", 'false')
                    node_form.set("edit", 'false')
        if view_type == 'tree':
            for node_form in doc.xpath("//tree"):
                node_form.set("create", 'false')
        res['arch'] = etree.tostring(doc)
        return res

    @api.constrains('student_ids')
    def _check_student_ids(self):
        for r in self:
            if 5 < len(r.student_ids):
                raise ValidationError("El numero de integrantes debe ser igual o menor a 5, quite integrantes o no va a poder guardar")




# class AddPartner(models.Model):
#     _inherit = 'res.partner'

    
#     group_partner_id = fields.Many2one('hr.applicant', string='Tema')

# class AddJob(models.Model):
#     _inherit = 'hr.job'

#     @api.multi
#     def career_filter_kanban(self):
#         partner_id_actu = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id
#         department_actu = self.env['res.partner'].search([('id', '=', partner_id_actu.id)],limit=1).department_id.id
#         domain = [('department_id.id','=',department_actu)]
#         return {
#             'name': _('Carreras'),
#             'domain': domain,
#             'res_model': 'hr.job',
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'view_mode': 'kanban,form',
#             'help': _('''<p class="oe_view_nocontent_create">
#                         Documents are attached to the tasks and issues of your project.</p><p>
#                         Send messages or log internal notes with attachments to link
#                         documents to your project.
#                     </p>'''),
#             'limit': 80,
#             'context': '{}'
#         }

class messageHrDepartment(models.Model):
    _inherit = 'hr.department'

    manager_partner_id = fields.Many2one('res.partner', "Responsable")

    @api.multi
    def write(self, vals):
        return super(messageHrDepartment, self).write(vals)

class ChangeModelJob(models.Model):
    _inherit = 'hr.job'
    _description = "Carreras"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ChangeModelJob, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'kanban':
            for node_form in doc.xpath("//kanban"):
                node_form.set("create", 'false')
        res['arch'] = etree.tostring(doc)
        return res