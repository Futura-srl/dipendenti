from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)


class CustomerPortalInherit(CustomerPortal):

    # In Odoo 19 non esiste piu' MANDATORY_BILLING_FIELDS: i campi obbligatori del form
    # indirizzo si dichiarano qui, e il salvataggio passa da /my/address/submit invece che
    # dall'override di /my/account.
    def _get_mandatory_address_fields(self, country_sudo):
        return super()._get_mandatory_address_fields(country_sudo) | {'email_personale'}
