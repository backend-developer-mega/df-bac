# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.website.models.website import slug
from odoo.http import request


# NB: DO NOT FORWARD PORT THE FALSY LEAVES IN 11.0
class WebsiteResCountry(http.Controller):

    @http.route('/country', type='http', auth="public", website=True)
    def jobs_apply(self, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        Country = env['res.country']
        # List jobs available to current UID
        country_ids = Country.search([], order="name asc").ids
        # Browse jobs as superuser, because address is restricted
        countries = Country.sudo().browse(country_ids)

        return request.render("website_res_contry.apply", {
            'countrys': countries,
        })
