import json

from src.app.sql_tools import get_db_connection


def save_invoice_data(data):
    """Сохранить callback от CryptoCloud в таблицу automatic_postback и обновить статус счета."""
    if not isinstance(data, dict):
        return

    result = data.get('result', data)
    invoice_uuid = (result.get('uuid') or data.get('uuid') or data.get('invoice_uuid') or '').strip()
    amount = result.get('amount', data.get('amount'))
    amount_usd = result.get('amount_usd', data.get('amount_usd'))
    amount_in_fiat = result.get('amount_in_fiat', data.get('amount_in_fiat'))
    currency = result.get('currency')
    if isinstance(currency, dict):
        currency_name = currency.get('code') or currency.get('fullcode') or currency.get('name') or ''
    else:
        currency_name = currency or ''
    status = data.get('status') or result.get('status') or 'unknown'
    invoice_id = result.get('invoice_id') or data.get('invoice_id')
    created = result.get('created') or data.get('created')
    address = result.get('address') or data.get('address')
    expiry_date = result.get('expiry_date') or data.get('expiry_date')
    invoice_status = result.get('status') or data.get('status') or status
    is_email_required = result.get('is_email_required', data.get('is_email_required'))
    link = result.get('link') or data.get('link')
    project = result.get('project') or {}
    project_name = project.get('name') if isinstance(project, dict) else ''
    test_mode = result.get('test_mode', data.get('test_mode'))

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO automatic_postback (
                status,
                invoice_id,
                amount_crypto,
                amount_usd,
                amount_in_fiat,
                currency,
                invoice_uuid,
                invoice_created,
                invoice_address,
                invoice_expiry_date,
                invoice_status,
                invoice_is_email_required,
                invoice_link,
                invoice_project_name,
                invoice_test_mode,
                raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                status,
                invoice_id,
                amount,
                amount_usd,
                amount_in_fiat,
                currency_name,
                invoice_uuid,
                created,
                address,
                expiry_date,
                invoice_status,
                1 if is_email_required else 0,
                link,
                project_name,
                1 if test_mode else 0,
                json.dumps(data, ensure_ascii=False)
            )
        )
        conn.commit()

    if invoice_uuid:
        with get_db_connection() as conn:
            matches = conn.execute(
                "SELECT id FROM invoice_creation_responses WHERE uuid = ? ORDER BY id DESC",
                (invoice_uuid,)
            ).fetchall()
            if len(matches) == 1:
                conn.execute(
                    "UPDATE invoice_creation_responses SET isPaid = 1 WHERE uuid = ?",
                    (invoice_uuid,)
                )
                conn.commit()
