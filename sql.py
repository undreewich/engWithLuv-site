import sqlite3 as sq


with sq.connect('mydatabase.db') as con:
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            email TEXT,
            lessons_repaid INTEGER,
            lessons_done INTEGER,
            cash_prepaid REAL,
            cash_done REAL,
            is_active INTEGER,
            age INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            amount REAL,
            isPaid BOOLEAN,
            date_issue TEXT,
            date_paid TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    # Automatic POSTBACK SQL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS automatic_postback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            invoice_id TEXT,
            amount_crypto REAL,
            amount_usd REAL,
            amount_in_fiat REAL,
            currency TEXT,
            order_id TEXT,
            token TEXT,
            invoice_uuid TEXT,
            invoice_created TEXT,
            invoice_address TEXT,
            invoice_expiry_date TEXT,
            invoice_status TEXT,
            invoice_is_email_required INTEGER,
            invoice_link TEXT,
            invoice_project_name TEXT,
            invoice_test_mode INTEGER,
            raw_json TEXT
        )
    """)

    # Invoice Creation Response SQL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice_creation_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            status TEXT,
            uuid TEXT,
            created TEXT,
            address TEXT,
            expiry_date TEXT,
            side_commission TEXT,
            side_commission_service TEXT,
            type_payments TEXT,
            amount REAL,
            amount_usd REAL,
            amount_in_fiat REAL,
            fee REAL,
            fee_usd REAL,
            service_fee REAL,
            service_fee_usd REAL,
            fiat_currency TEXT,
            invoice_status TEXT,
            is_email_required INTEGER,
            link TEXT,
            invoice_id TEXT,
            currency_id INTEGER,
            currency_code TEXT,
            currency_fullcode TEXT,
            network_code TEXT,
            network_id INTEGER,
            network_icon TEXT,
            network_fullname TEXT,
            currency_name TEXT,
            currency_is_email_required INTEGER,
            currency_stablecoin INTEGER,
            currency_icon_base TEXT,
            currency_icon_network TEXT,
            currency_icon_qr TEXT,
            currency_order INTEGER,
            project_id INTEGER,
            project_name TEXT,
            project_fail TEXT,
            project_success TEXT,
            project_logo TEXT,
            test_mode INTEGER,
            isPaid BOOLEAN DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)


