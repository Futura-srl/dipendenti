{
    'name': 'dipendenti',
    'version': '16.0.0.1',
    'author': "Luca Cocozza",
    'application': True,
    'description': "Aggiunge nome e cognome al res.partner e al hr.employee, mostra un bottone di collegamento hai hr.employee associati al res.partner",
    'depends': ['hr', 'fleet', 'gtms_fleet_organization', 'fleet_limited_traffic_zone', 'gtms_fleet_service_with_deduction', 'fleet_replacement', 'portal'],
    'data': [
        # # Settaggi per accesso ai contenuti
        'data/ir.model.access.csv',
        # # Caricamento delle view,
        # 'view/hr_update.xml',
        'view/fleet_vehicle_update.xml',
        'view/hr_employee_update.xml',
        'view/hr_interinale_view.xml',
        'view/res_partner_update.xml',
        'view/hr_interinale_contatti_view.xml',
        'view/portal_view.xml',
        'view/hr_badgespwork_view.xml',
        # Menu
        'view/menu.xml',
    ],
    'i18n': [
        'i18n/it.po',
    ],
}
