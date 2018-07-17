# -*- coding: utf-8 -*-
# Part of UES. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.website.models.website import slug
from odoo.http import request

class WebsiteResUsers(http.Controller):

    @http.route('/userapplicant', type='http', auth="public", website=True)
    def users_apply(self, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        Department = env['hr.department']
        department_ids = Department.search([], order="name asc").ids
        departments = Department.sudo().browse(department_ids)
        Career = env['hr.job']
        career_ids = Career.search([], order="name asc").ids
        careers = Career.sudo().browse(career_ids)

        return request.render("website_res_partner.apply", {
            'departments': departments,
            'careers': careers,
        })
