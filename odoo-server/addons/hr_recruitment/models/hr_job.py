# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class Job(models.Model):
    _name = "hr.job"
    _inherit = ["mail.alias.mixin", "hr.job"]

    @api.model
    def _default_address_id(self):
        return self.env.user.company_id.partner_id

    address_id = fields.Many2one(
        'res.partner', "Job Location", default=_default_address_id,
        help="Address where employees are working")
    application_ids = fields.One2many('hr.applicant', 'job_id', "Applications")
    application_count = fields.Integer(compute='_compute_application_count', string="Applications")
    manager_id = fields.Many2one(
        'hr.employee', related='department_id.manager_id', string="Department Manager",
        readonly=True, store=True)
    user_id = fields.Many2one('res.users', "Recruitment Responsible", track_visibility='onchange')
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Applications")
    documents_count = fields.Integer(compute='_compute_document_ids', string="Documents")
    alias_id = fields.Many2one(
        'mail.alias', "Alias", ondelete="restrict", required=True,
        help="Email alias for this job position. New emails will automatically create new applicants for this job position.")
    color = fields.Integer("Color Index")

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids').filtered(lambda self: not self.emp_id)
        app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([
            '|',
            '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'hr.applicant':
                result[app_to_job[attachment.res_id]] |= attachment
            else:
                result[attachment.res_id] |= attachment

        for job in self:
            job.document_ids = result[job.id]
            job.documents_count = len(job.document_ids)

    @api.multi
    def _compute_application_count(self):
        data = True
        #read_group_result = self.env['hr.applicant'].read_group([('job_id', '=', self.id)], ['job_id'], ['job_id'])
        #result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        #for job in self:
        #    job.application_count = result.get(job.id, 0)

    def get_alias_model_name(self, vals):
        return 'hr.applicant'

    def get_alias_values(self):
        values = super(Job, self).get_alias_values()
        values['alias_defaults'] = {'job_id': self.id}
        return values

    @api.model
    def create(self, vals):
        return super(Job, self.with_context(mail_create_nolog=True)).create(vals)

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'open':
            return 'hr_recruitment.mt_job_new'
        return super(Job, self)._track_subtype(init_values)

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id, )
        action['domain'] = ['|', '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids), '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.mapped('application_ids').ids)]
        return action

    @api.multi
    def action_set_no_of_recruitment(self, value):
        return self.write({'no_of_recruitment': value})

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


    @api.multi
    def career_filter_kanban(self):
        partner_id_actu = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id
        department_actu = self.env['res.partner'].search([('id', '=', partner_id_actu.id)],limit=1).department_id.id
        domain = []
        _logger.info('-----self.env.uid---------->  %s ', self.env.uid)
        if self.env.uid != 15:
            domain = [('department_id.id','=',department_actu)]
        return {
            'name': _('Carreras'),
            'domain': domain,
            'res_model': 'hr.job',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': '{}'
        }

    @api.multi
    def applications_filter_kanban(self):
        active_record = self._context['active_id']
        partner_id_actu = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id.id
        sql_query = """SELECT students_lead_id_res 
                        FROM students_lead_tag_rel_res 
                        WHERE students_tag_id_res = %s
                    """
        params = (partner_id_actu,)
        self.env.cr.execute(sql_query, params)
        results = [a for (a,) in self.env.cr.fetchall()]
        view_mode = 'kanban,tree,form,graph,calendar'
        _logger.info('-----applications_filter_kanban---------->  %s ', len(results))
        if len(results) == 0:
            view_mode = 'form'
        domain = [('id','in',results)]
        contex = "{'search_default_job_id': %s, 'default_job_id': %s}" % (active_record, active_record)
        return {
            'name': _('Solicitudes'),
            'domain': domain,
            'res_model': 'hr.applicant',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': view_mode,
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': contex
        }




class PartnerStudent(models.Model):
    _inherit = "res.partner"

    department_id = fields.Many2one('hr.department', string='Departamento')
    career_id = fields.Many2one('hr.job', string='Carrera')
                


