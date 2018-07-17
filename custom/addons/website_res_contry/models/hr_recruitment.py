# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from urlparse import urljoin
from werkzeug import url_encode

from odoo import api, fields, models
from odoo.addons.website.models.website import slug
from odoo.tools.translate import html_translate

class country_attachment(models.Model):
    _inherit = 'res.country'

    docume_ids = fields.Many2many('ir.attachment', 'country_attachments_rel', 'country_att_id', 'attachment_id', string='Documentos')

    @api.model
    def create(self, vals):
    	#contry_id = self.env['res.users'].create({'name': vals.get('name'),'code': vals.get('code')})
        return super(country_attachment, self).create(vals)

     


    #@api.model
    #def message_get_reply_to(self, ids, default=None):
    #    """ Override to get the reply_to of the parent project. """
    #    
    #    applicants = { "country": False }
    #    return applicants


