from odoo import fields, models


class ImportData(models.Model):
    _name = "import.data"
    _description = "Importazione dati"

    number_data_import = fields.Integer()

class HrBadges(models.Model):
    _name = "hr.badgespwork"
    _description = "Hr badges"


    name = fields.Char()
    active = fields.Boolean()
    valid_from = fields.Datetime()
    valid_to = fields.Datetime()
    pin = fields.Char()
    hr_id = fields.Many2one('hr.employee', string="Dipendenti")
    
class HrUpdate(models.Model):
    _inherit = "hr.employee"

    pwork_uid = fields.Char(track_visibility='onchange', groups='base.group_erp_manager', readonly='True')
    pwork_cf = fields.Char(track_visibility='onchange')
    pwork_azienda_id = fields.Integer(track_visibility='onchange', groups='base.group_erp_manager', readonly='True')
    pwork_dipendente_id = fields.Integer(track_visibility='onchange', groups='base.group_erp_manager', readonly='True')
    first_name = fields.Char(track_visibility='onchange')
    last_name = fields.Char(track_visibility='onchange')
    interinale = fields.Many2one('hr.interinale', track_visibility='onchange', readonly='True')
    badge_pwork_ids = fields.One2many('hr.badgespwork', 'hr_id' )

class ResPartnerUpdate(models.Model):
    _inherit = "res.partner"

    first_name = fields.Char(track_visibility='onchange')
    last_name = fields.Char(track_visibility='onchange')
    access_code_employee = fields.Char(string="Employee password", track_visibility='onchange')
    email_personale = fields.Char()

    has_matching_employee = fields.Integer(compute='_compute_has_matching_employee')

    def _compute_has_matching_employee(self):
        for partner in self:
            matching_employees = self.env['hr.employee'].search_count([
            ('address_home_id.id', '=', self.id),
            ('active', 'in', [True, False])
        ])
            partner.has_matching_employee = matching_employees


    def action_open_employees(self):
        self.ensure_one()
        return {
            'name': ('Dipendenti relativi'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form',
            'domain': ['|', '&', ('address_home_id', '=', self.id), ('active', '=', False), '&', ('address_home_id', '=', self.id), ('active', '=', True)],



        }


class PworkSetting(models.Model):
    _name = "pwork.setting"
    _description = "Pwork setting"

    token = fields.Char()

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    stato_veicolo = fields.Selection([('ATTIVO', 'ATTIVO'),('IN ARRIVO', 'IN ARRIVO'),('INCIDENTATO','INCIDENTATO'),('RESTITUITO','RESTITUITO')], default="ATTIVO")
    euro = fields.Char()

class HrInterinale(models.Model):
    _name = "hr.interinale"
    _description = "Dipendenti interinali"

    name = fields.Char(string="Nome azienda interinale")
    res_partner_id = fields.Many2one('res.partner', string="Contatto azienda interinale")
    res_company_id = fields.Many2one('res.company', string="Azienda interna collegata")


class HrInterinaleContatti(models.Model):
    _name = "hr.interinale.contatti"
    _description = "Contatti aziende interinali"

    res_partner_id = fields.Many2one('res.partner', string="Contatto azienda interinale")
    res_cdc_id = fields.Many2one('res.partner', string="Centro di costo", domain=[('type', '=', 'delivery'), ('company_type', '=', 'company')])
    email = fields.Char()

class HrContract(models.Model):
    _inherit = "hr.contract"

    pwork_reference = fields.Integer(track_visibility='onchange')
