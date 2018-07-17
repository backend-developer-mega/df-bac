# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MailArchiveMessage(models.Model):
    _inherit = ['mail.message']
    _rec_name = 'subject'
    
    archive_recepient = fields.Many2many('res.partner', 'mail_message_partner_archive_rel', string = 'Recepients')
    origin_doc = fields.Html('Source document', compute='_get_alias', store=True)
    
    @api.depends('model','res_id')
    def _get_alias(self):
        for x in self:
            alias = self.env['ir.config_parameter'].get_param('web.base.url') or ''
            alias += '/'
            if x.model and x.res_id:
                if x.model == 'mail.channel':
                    action = self.env.ref('mail.mail_channel_action_client_chat')[0].id
                    alias += 'web#action='+str(action)+'&active_id='+str(x.res_id)
                else:    
                    alias += 'web#id='+str(x.res_id)+'&model='+x.model
                x.origin_doc = '<a href="'+alias+'" target="_blank">'+x.record_name+'</a>'

    
    @api.model
    def create(self, vals):
        recepient = []
        if vals.get('partner_ids'):
            for x in vals.get('partner_ids'):
                if x not in recepient:
                    recepient.append(x)
        if vals.get('needaction_partner_ids'):
            for x in vals.get('needaction_partner_ids'):
                if x not in recepient:
                    recepient.append(x)
        if vals.get('channel_ids'):
            for x in vals.get('channel_ids'): 
                channel = self.env['mail.channel'].browse(x) 
                for y in channel.channel_partner_ids.mapped('id'):
                    if y not in recepient and y != vals.get('author_id'):
                        recepient.append(y)
        vals['archive_recepient'] = recepient
        
        return super(MailArchiveMessage, self).create(vals)
      
    @api.multi
    def write(self, vals):
        recepient = self.archive_recepient.mapped('id') or []
        if vals.get('partner_ids'):
            for x in vals.get('partner_ids')[0][2]:
                if x not in recepient:
                    recepient.append(x)
        if vals.get('needaction_partner_ids'):
            for x in vals.get('needaction_partner_ids')[0][2]:
                if x not in recepient:
                    recepient.append(x)
        if vals.get('channel_ids'):
            for x in vals.get('channel_ids')[0][2]:
                channel = self.env['mail.channel'].browse(x)
                for y in channel.channel_partner_ids.mapped('id'):
                    if y not in recepient and y != self.author_id.id:
                        recepient.append(y)
        vals['archive_recepient'] = [(6, 0, recepient)]

        return super(MailArchiveMessage, self).write(vals)
    
    def after_install(self):
        messages = self.env['mail.message'].search([('id','>',0)])
        for m in messages:
            m.write({
                'partner_ids':[(6,0,m.partner_ids.mapped('id'))],
                'needaction_partner_ids':[(6,0,m.needaction_partner_ids.mapped('id'))],
                'channel_ids':[(6,0,m.channel_ids.mapped('id'))],
              })
