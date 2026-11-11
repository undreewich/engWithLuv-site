import sqlite3 as sq


with sq.connect('mydatabase.db') as con:
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.executescript("""
        DROP TABLE IF EXISTS students;
        DROP TABLE IF EXISTS admins;
        DROP TABLE IF EXISTS payments;
        DROP TABLE IF EXISTS refresh_tokens;
        DROP TABLE IF EXISTS refresh_tokens_admins;
        DROP TABLE IF EXISTS invoice_creation_responses;
        DROP TABLE IF EXISTS automatic_postback;
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            email TEXT NOT NULL UNIQUE,
            lessons_prepaid INTEGER,
            lessons_done INTEGER,
            cash_prepaid REAL,
            cash_done REAL,
            is_active INTEGER,
            age INTEGER,
            password TEXT NOT NULL,
            is_confirmed INTEGER,
            privacyConsent DATETIME DEFAULT CURRENT_TIMESTAMP,
            termsConsent DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            surname TEXT,
            email TEXT,
            password TEXT,
            is_confirmed INTEGER
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
    cur.execute("""
    CREATE TABLE refresh_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)
    cur.execute("""
    CREATE TABLE refresh_tokens_admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY (user_id) REFERENCES admins (id)
    );
    """)
    cur.execute("""
        INSERT INTO admins (name, surname, email, password) 
        VALUES (?, ?, ?, ?)
        """,
        (
            'Admin',
            'User',
            'admin@mail',
            'scrypt:32768:8:1$CHv6hdnefms3oOS0$5eceda35bd6a1b1d3b98b8ad7a686ebcfa77fa8f457ce104f3ae7cc0e29b97ec83755188b6a7c91f9e11d44a3be7a09c469a967a7cf53c63b897bb75a174948a'
        )
    )
    con.commit()





    # # Automatic POSTBACK SQL
    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS automatic_postback (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         status TEXT,
    #         invoice_id TEXT,
    #         amount_crypto REAL,
    #         amount_usd REAL,
    #         amount_in_fiat REAL,
    #         currency TEXT,
    #         order_id TEXT,
    #         token TEXT,
    #         invoice_uuid TEXT,
    #         invoice_created TEXT,
    #         invoice_address TEXT,
    #         invoice_expiry_date TEXT,
    #         invoice_status TEXT,
    #         invoice_is_email_required INTEGER,
    #         invoice_link TEXT,
    #         invoice_project_name TEXT,
    #         invoice_test_mode INTEGER,
    #         raw_json TEXT
    #     )
    # """)

    # # Invoice Creation Response SQL
    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS invoice_creation_responses (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         student_id INTEGER,
    #         status TEXT,
    #         uuid TEXT,
    #         created TEXT,
    #         address TEXT,
    #         expiry_date TEXT,
    #         side_commission TEXT,
    #         side_commission_service TEXT,
    #         type_payments TEXT,
    #         amount REAL,
    #         amount_usd REAL,
    #         amount_in_fiat REAL,
    #         fee REAL,
    #         fee_usd REAL,
    #         service_fee REAL,
    #         service_fee_usd REAL,
    #         fiat_currency TEXT,
    #         invoice_status TEXT,
    #         is_email_required INTEGER,
    #         link TEXT,
    #         invoice_id TEXT,
    #         currency_id INTEGER,
    #         currency_code TEXT,
    #         currency_fullcode TEXT,
    #         network_code TEXT,
    #         network_id INTEGER,
    #         network_icon TEXT,
    #         network_fullname TEXT,
    #         currency_name TEXT,
    #         currency_is_email_required INTEGER,
    #         currency_stablecoin INTEGER,
    #         currency_icon_base TEXT,
    #         currency_icon_network TEXT,
    #         currency_icon_qr TEXT,
    #         currency_order INTEGER,
    #         project_id INTEGER,
    #         project_name TEXT,
    #         project_fail TEXT,
    #         project_success TEXT,
    #         project_logo TEXT,
    #         test_mode INTEGER,
    #         isPaid BOOLEAN DEFAULT 0,
    #         FOREIGN KEY(student_id) REFERENCES students(id)
    #     )
    # """)