from odoo import http
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)

class CustomerPortalInherit(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id", "email_personale"]
    
    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        _logger.info(post.get('email_personale'))

        if post.get('email_personale') != None:
            # Aggiungi anche 'email_personale' ai valori da aggiornare nel modello del partner
            values = {'email_personale': post.get('email_personale')}
            # values.update({'email_personale': post.get('email_personale')})
            
            partner.sudo().write(values)

        res = super(CustomerPortalInherit, self).account(redirect=redirect, **post)
        return res


