import logging

_logger = logging.getLogger(__name__)

# Da Datetime (UTC) a Date: la data si legge in ora italiana, come fa l'invio a Pwork.
# Le regole correggono i valori nati da errori noti:
#  - 23:00 italiane (caricamento massivo di gennaio 2026): intendevano la mezzanotte del giorno dopo;
#  - fine alle 23:59:59 UTC (00:59/01:59 italiane, vecchio wizard di cessazione): intendevano il giorno prima.
LOCALE = "((%(col)s AT TIME ZONE 'UTC') AT TIME ZONE 'Europe/Rome')"

VALID_FROM = """
    CASE
        WHEN valid_from IS NULL THEN NULL
        WHEN to_char({loc}, 'HH24:MI:SS') = '23:00:00' THEN {loc}::date + 1
        ELSE {loc}::date
    END""".format(loc=LOCALE % {'col': 'valid_from'})

VALID_TO = """
    CASE
        WHEN valid_to IS NULL THEN NULL
        WHEN to_char({loc}, 'HH24:MI:SS') = '23:00:00' THEN {loc}::date + 1
        WHEN to_char(valid_to, 'HH24:MI:SS') = '23:59:59' THEN {loc}::date - 1
        ELSE {loc}::date
    END""".format(loc=LOCALE % {'col': 'valid_to'})


def migrate(cr, version):
    cr.execute("""
        SELECT data_type FROM information_schema.columns
         WHERE table_name = 'hr_badgespwork' AND column_name = 'valid_from'
    """)
    row = cr.fetchone()
    if not row or row[0] == 'date':
        return

    # Copia dei valori originali, per confronto o ripristino
    cr.execute("""
        CREATE TABLE IF NOT EXISTS hr_badgespwork_datetime_backup AS
        SELECT id, valid_from, valid_to FROM hr_badgespwork
    """)
    cr.execute("""
        ALTER TABLE hr_badgespwork
            ALTER COLUMN valid_from TYPE date USING %s,
            ALTER COLUMN valid_to TYPE date USING %s
    """ % (VALID_FROM, VALID_TO))
    cr.execute("SELECT count(*) FROM hr_badgespwork")
    _logger.info("hr.badgespwork: valid_from/valid_to convertiti a data su %s badge", cr.fetchone()[0])
