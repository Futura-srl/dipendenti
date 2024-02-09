from odoo import api, fields, models, _
from datetime import date

import logging
_logger = logging.getLogger(__name__)


class ImportData(models.Model):
    _inherit = "hr.contract"

    @api.onchange('date_start','date_end')
    def get_contract_state(self):
        _logger.info("Ci provo")
        open = self.env['hr.contract'].search_read([('state', '=', 'close'),'|', ('date_end', '>=', fields.Date.to_string(date.today())),('date_end', '=', False)])
        for record in open:
            _logger.info(record)
            self.env['hr.contract'].browse(record['id']).write({'state': 'open'})
            _logger.info(self.env['hr.contract'].search_read([('id', '=', record['id'])],['id','state']))
    


