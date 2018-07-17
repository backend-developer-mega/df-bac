# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from urlparse import urljoin
from werkzeug import url_encode

from odoo import api, fields, models, _
from odoo.addons.website.models.website import slug
from odoo.tools.translate import html_translate
from odoo.exceptions import ValidationError
from lxml import etree
import logging
_logger = logging.getLogger(__name__)

class EmailPartner(models.Model):
    _inherit = 'res.partner'

    check_department_partner = fields.Boolean(default=False,compute='_compute_check_value')
    template_user = fields.Many2one('res.users', string='Rol de permisos', default=11)
    available = fields.Boolean(default=True)

    @api.onchange('template_user')
    def _onchange_permits_user(self):
        is_new_record = self.id
        if is_new_record:
            user_id = self.env['res.users'].search([('partner_id', '=', self._origin.id)],limit=1).id
            user_template_id = self.template_user.id
            #raise ValidationError(str(user_id)+" "+str(user_template_id))
            _logger.info('-------> Dentro del metodo ONCHANGE variable: user_id (%s) y el user_template_id: (%s) ', user_id, user_template_id)
            sql_query = """DELETE FROM res_groups_users_rel WHERE uid = %s; 
INSERT INTO res_groups_users_rel SELECT gid, %s as uid FROM res_groups_users_rel WHERE uid = %s ORDER BY gid asc
                    """
            params = (int(user_id),int(user_id),int(user_template_id))
            self.env.cr.execute(sql_query, params)

       # values = {'active':True, 'partner_id':self.id, 'login':self.email, 'name':self.name}
       # if self.template_user:
       #     self.template_user.with_context(no_reset_password=True).copy(values)
       #     raise ValidationError(values.items())
        

    @api.depends('name')
    def _compute_check_value(self):
        partner_department_id = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id.department_id.id
        check = False
        for partner in self:
            if partner_department_id == partner.department_id.id:
                check = True
            partner.check_department_partner = check

    @api.multi
    def create_user(self):
        user_id = self.env['res.users'].create({'name': self.name,
        	'login': self.email, 'partner_id':self.id, 'supplier': False, 'partner_share': True})
        if self.template_user:
            user_template_id = self.template_user.id
            sql_query = """DELETE FROM res_groups_users_rel WHERE uid = %s; 
INSERT INTO res_groups_users_rel SELECT gid, %s as uid FROM res_groups_users_rel WHERE uid = %s ORDER BY gid asc
                    """
            params = (int(user_id.id),int(user_id.id),int(user_template_id))
            self.env.cr.execute(sql_query, params)

    @api.multi
    def refuse_user(self):
    	IrModelData = self.env['ir.model.data']
        template_new_applicant = IrModelData.xmlid_to_object('auth_signup.set_refuse_email')
        if template_new_applicant:
            MailTemplate = self.env['mail.template']
            body_html = MailTemplate.render_template(template_new_applicant.body_html, 'res.partner', self.id)
            email_to_1 = ''.join(self.email)
            self.write({'customer': False,'active': False})
            mail = self.env['mail.mail'].create({
                'name': 'Proceso de creación de cuenta',
                'email_from': 'plataformatrabajogrado@gmail.com',
                'email_to': email_to_1,
                'partner_to': '',
                'model_id': 79,
                'subject': 'Rechazo de solicitud',
                'body_html': body_html,
                #'body_html': 'Lamentamos informarque que su solicitud de usuario a la plataforma de trabajos de grado ha sido rechazada, recomendamos que se ponga en contacto para revisar su caso. Saludos cordianles',
            })
            mail.send()

    @api.multi
    def applicant_partner_filter(self):
        department_actu = self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).partner_id.department_id.id
        #domain = [('department_id.id','=',1)]
        domain = [('department_id.id','=',department_actu),('customer','=',1),('supplier','=',1)]
        return {
            'name': _('Solicitudes de usuario'),
            'domain': domain,
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                         Click para agregar una solicitud de usuario.</p><p>
                         Al dar click llene el formulario.
                    </p>.'''),
            'limit': 80,
            'context': '{}'
        }
        
     
    @api.model
    def create(self, vals): 
        if not vals.has_key("is_company"):
            check_student_card = self.env['res.partner'].search([('student_card', '=', vals['student_card'])],limit=1).id
            if check_student_card:
                raise ValidationError("Ya existe un usuario con el mismo carnet")
        check_email = self.env['res.partner'].search([('email', '=', vals['email'])],limit=1).id
        if check_email:
            _logger.info('-----##########################--> EmailPartner {%s}', vals['email'])
            raise ValidationError("Ya existe un usuario con el mismo correo electronico")
        partner = super(EmailPartner, self).create(vals)        
        IrModelData = self.env['ir.model.data']
        models = 79
        template_new_applicant = IrModelData.xmlid_to_object('auth_signup.set_information_email')
        for record in self:
        	models = self.env['ir.model'].search([('model', '=', record.model or 'res.partner')])
        if template_new_applicant:
            MailTemplate = self.env['mail.template']
            body_html = MailTemplate.render_template(template_new_applicant.body_html, 'res.partner', partner.id)
            subject = MailTemplate.render_template(template_new_applicant.subject, 'res.partner', partner.id)
            email_to_1 = ''.join(partner.email)
            mail = self.env['mail.mail'].create({
                'name': 'Proceso de creación de cuenta',
                'email_from': 'plataformatrabajogrado@gmail.com',
                'email_to': email_to_1,
                'partner_to': '',
                'model_id': 79,
                'subject': 'Proceso de usuario',
                'body_html': body_html,
                #'body_html': 'Comunicarte que se esta gestionando tu cuenta para la plataforma de trabajos de grado, te estaremos informando por este medio sobre los avances de la solicitud. Saludos cordianles',
            })
            mail.send()
        return partner



    @api.multi
    def write(self, vals):
        user_id = self.env['res.users'].search([('partner_id', '=', self.id)],limit=1).id
        _logger.info('-------> Dentro del metodo WRITE variable: user_id (%s)', user_id)
        if user_id:
            if vals.has_key("template_user"):
                user_template_id = vals['template_user']
                _logger.info('-------> Dentro del metodo WRITE - IF - variable: user_template_id (%s)', user_template_id)
                sql_query = """DELETE FROM res_groups_users_rel WHERE uid = %s; 
INSERT INTO res_groups_users_rel SELECT gid, %s as uid FROM res_groups_users_rel WHERE uid = %s ORDER BY gid asc
                    """
                params = (int(user_id),int(user_id),int(user_template_id))
                self.env.cr.execute(sql_query, params)
        return super(EmailPartner, self).write(vals)


    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(EmailPartner, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     sql_query = """SELECT uid FROM res_groups_users_rel WHERE uid = %s AND gid = (SELECT id FROM res_groups WHERE name = 'Contact Creation');"""
    #     params = (int(self.env.uid),)
    #     self.env.cr.execute(sql_query, params)
    #     results = [a for (a,) in self.env.cr.fetchall()]
    #     for line in results:
    #         if int(line) != int(self.env.uid):
    #             if view_type == 'tree':
    #                 for node_form in doc.xpath("//tree"):
    #                     node_form.set("create", 'false')
    #             if view_type == 'form':
    #                 for node_form in doc.xpath("//form"):
    #                     node_form.set("create", 'false')
    #     res['arch'] = etree.tostring(doc)
    #     return res