from odoo import fields, models, api, _
import logging, re, random
from datetime import datetime, time, timedelta
from markupsafe import Markup

_logger = logging.getLogger(__name__)
now = datetime.now()


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
    pin = fields.Char(default="0000")
    hr_id = fields.Many2one('hr.employee', string="Dipendenti")
    contract_ids = fields.Many2many('hr.contract', string="Contratti associati")

    # Modifico la funzione write affinche quando viene modificato un badge, venga aggiornato anche il campo last_update_badge del contratto associato
    def write(self, vals):
        # Scrivo badge normalmente
        res = super().write(vals)

        # Aggiorna contratti solo se non siamo nel contesto di aggiornamento dei badge da contratto
        if not self.env.context.get('skip_contract_update'):
            for badge in self:
                for contract in badge.contract_ids:
                    contract.with_context(skip_badge_update=True).last_update_badge = fields.Datetime.now()
        return res


class HrUpdate(models.Model):
    _inherit = "hr.employee"

    pwork_uid = fields.Char(track_visibility='onchange', groups='base.group_erp_manager', readonly='True')
    pwork_cf = fields.Char(track_visibility='onchange')
    pwork_azienda_id = fields.Integer(track_visibility='onchange', groups='base.group_erp_manager', readonly='True')
    pwork_dipendente_id = fields.Integer(track_visibility='onchange', groups='base.group_erp_manager', readonly='True')
    first_name = fields.Char(track_visibility='onchange')
    last_name = fields.Char(track_visibility='onchange')
    interinale = fields.Many2one('hr.interinale', readonly='True')
    badge_pwork_ids = fields.One2many('hr.badgespwork', 'hr_id' )
    address_home_id = fields.Many2one('res.partner')



    def _create_work_contacts(self):
        # Non crea il res.partner una volta creato il dipendente
        return False


    @api.model_create_multi
    def create_only_employee(self, vals_list):
        for vals in vals_list:
            if vals.get('user_id'):
                user = self.env['res.users'].browse(vals['user_id'])
                vals.update(self._sync_user(user, bool(vals.get('image_1920'))))
                vals['name'] = vals.get('name', user.name)
                self._remove_work_contact_id(user, vals.get('company_id'))
        employees = super(HrUpdate, self.with_context(skip_work_contact=True)).create(vals_list)
        for employee_sudo in employees.sudo():
            # creating 'svg/xml' attachments requires specific rights
            if not employee_sudo.image_1920 and self.env['ir.ui.view'].sudo(False).has_access('write'):
                employee_sudo.image_1920 = employee_sudo._avatar_generate_svg()
                employee_sudo.work_contact_id.image_1920 = employee_sudo.image_1920
        if self.env.context.get('salary_simulation'):
            return employees
        employee_departments = employees.department_id
        if employee_departments:
            self.env['discuss.channel'].sudo().search([
                ('subscription_department_ids', 'in', employee_departments.ids)
            ])._subscribe_users_automatically()
        onboarding_notes_bodies = {}
        hr_root_menu = self.env.ref('hr.menu_hr_root')
        for employee in employees:
            # Launch onboarding plans
            url = '/odoo/%s/action-hr.plan_wizard_action?active_model=hr.employee&menu_id=%s' % (
            employee.id, hr_root_menu.id)
            onboarding_notes_bodies[employee.id] = Markup(_(
                '<b>Congratulations!</b> May I recommend you to setup an <a href="%s">onboarding plan?</a>',
            )) % url
        employees._message_log_batch(onboarding_notes_bodies)
        return employees

    # Creo una funzione che dato il nome del department e la company, effettua il controllo per vedere se esiste. Se esiste restituisce l'id, altrimenti lo crea e restituisce l'id
    def get_department_id(self, department_name, pwork_company_id):
        company_id = self.env['hr.interinale'].search([('res_company_id', '=', pwork_company_id)]).res_company_id.id
        department = self.env['hr.department'].search([('name', '=', department_name), ('company_id', '=', company_id)])
        if department:
            return department.id
        else:
            department = self.env['hr.department'].create({'name': department_name, 'company_id': company_id})
            return department.id


class ResPartnerUpdate(models.Model):
    _inherit = "res.partner"

    first_name = fields.Char(track_visibility='onchange')
    last_name = fields.Char(track_visibility='onchange')
    login_user = fields.Char(compute='_compute_get_login_user')
    access_code_employee = fields.Char(string="Employee password", track_visibility='onchange')
    email_personale = fields.Char()
    is_employee = fields.Boolean(string='Is Employee', default=False)

    def _compute_get_login_user(self):
        for partner in self:
            partner.login_user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1).login

    has_matching_employee = fields.Integer(compute='_compute_has_matching_employee')

    def _compute_has_matching_employee(self):
        for partner in self:
            matching_employees = self.env['hr.employee'].search_count([
            ('address_home_id', '=', partner.id),
            ('active', 'in', [True, False])
        ])
            partner.has_matching_employee = matching_employees
            _logger.info(partner.has_matching_employee)


    def action_open_employees(self):
        self.ensure_one()
        return {
            'name': ('Dipendenti relativi'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form',
            'domain': ['|', '&', ('address_home_id', '=', self.id), ('active', '=', False), '&', ('address_home_id', '=', self.id), ('active', '=', True)],
            'context': {
                'default_address_home_id': self.id,
                'default_first_name': self.firstname,
                'default_last_name': self.lastname,
                'default_work_email': self.email,
                'default_pwork_cf': self.fiscalcode,
                'default_private_email': self.email_personale,
            },


        }


class PworkSetting(models.Model):
    _name = "pwork.setting"
    _description = "Pwork setting"

    token = fields.Char()

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    stato_veicolo = fields.Selection([('ATTIVO', 'ATTIVO'),('IN ARRIVO', 'IN ARRIVO'),('INCIDENTATO','INCIDENTATO'),('RESTITUITO','RESTITUITO')], default="ATTIVO")
    #euro = fields.Char()

class HrInterinale(models.Model):
    _name = "hr.interinale"
    _description = "Dipendenti interinali"

    name = fields.Char(string="Nome azienda interinale")
    res_partner_id = fields.Many2one('res.partner', string="Contatto azienda interinale")
    res_company_id = fields.Many2one('res.company', string="Azienda interna collegata")
    pwork_az_id = fields.Integer(string="ID Pwork azienda interinale")


class HrInterinaleContatti(models.Model):
    _name = "hr.interinale.contatti"
    _description = "Contatti aziende interinali"

    res_partner_id = fields.Many2one('res.partner', string="Contatto azienda interinale")
    res_cdc_id = fields.Many2one('res.partner', string="Centro di costo", domain=[('type', '=', 'delivery'), ('company_type', '=', 'company')])
    email = fields.Char()

class HrContract(models.Model):
    _inherit = "hr.contract"

    pwork_reference = fields.Integer(track_visibility='onchange')
    last_update_badge = fields.Datetime()


class Company(models.Model):
    _inherit = "res.company"

    pwork_company_id = fields.Integer(string="ID Pwork azienda", default=0)
