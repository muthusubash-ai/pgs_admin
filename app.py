"""
Pavishna Global Service - Flask Backend
PostgreSQL Version for Render Deployment
- SQLite for local development
- PostgreSQL for production (Render)
- Auto-fix admin password
- No loading delay
Run: python app.py
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pavishna_global_service_secret_key_2024')
CORS(app)

# ==================== Database Configuration ====================
# Check if running on Render (PostgreSQL) or Local (SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production: PostgreSQL on Render
    # Fix for Render's postgres:// vs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DB_TYPE = 'postgresql'
    print("🐘 Using PostgreSQL Database")
else:
    # Local Development: SQLite
    import sqlite3
    DB_TYPE = 'sqlite'
    DB_FILE = 'gsb_clients.db'
    print("📁 Using SQLite Database")

# ==================== Password Functions ====================

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN123_HASH = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'

def verify_password(input_password, stored_password):
    """Smart password verification"""
    input_hash = hash_password(input_password)
    if len(stored_password) == 64:
        return input_hash == stored_password
    if input_password == stored_password:
        return True
    return False

# ==================== Database Connection ====================

def get_db():
    """Get database connection based on environment"""
    if DB_TYPE == 'postgresql':
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Execute query with proper parameter placeholder handling"""
    conn = get_db()
    
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Convert ? to %s for PostgreSQL
        query = query.replace('?', '%s')
    else:
        cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
            if DB_TYPE == 'sqlite' and result:
                result = dict(result)
        elif fetch:
            results = cursor.fetchall()
            if DB_TYPE == 'sqlite':
                results = [dict(row) for row in results]
            else:
                results = [dict(row) for row in results]
            result = results
        else:
            result = cursor.lastrowid if DB_TYPE == 'sqlite' else None
            conn.commit()
        
        return result
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# ==================== Database Initialization ====================

def init_db():
    """Initialize database tables"""
    print("\n🔄 Initializing database...")
    
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor()
        auto_increment = 'SERIAL'
        text_type = 'TEXT'
        real_type = 'DECIMAL(12,2)'
        timestamp_default = 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    else:
        cursor = conn.cursor()
        auto_increment = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        text_type = 'TEXT'
        real_type = 'REAL'
        timestamp_default = 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    
    # Create admin_users table
    if DB_TYPE == 'postgresql':
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Create clients table
    if DB_TYPE == 'postgresql':
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                district TEXT DEFAULT '',
                job_role TEXT DEFAULT '',
                country TEXT DEFAULT '',
                passport_no TEXT DEFAULT '',
                passport_submit_date TEXT DEFAULT '',
                passport_submitted_by TEXT DEFAULT 'self',
                passport_fee DECIMAL(12,2) DEFAULT 0,
                passport_payment_mode TEXT DEFAULT '',
                passport_payment_status TEXT DEFAULT 'pending',
                passport_payment_date TEXT DEFAULT '',
                passport_payment_reference TEXT DEFAULT '',
                interview_date TEXT DEFAULT '',
                interview_time TEXT DEFAULT '',
                interview_location TEXT DEFAULT '',
                interview_status TEXT DEFAULT 'pending',
                interview_reschedule_date TEXT DEFAULT '',
                interview_remarks TEXT DEFAULT '',
                offer_letter_status TEXT DEFAULT 'pending',
                offer_letter_date TEXT DEFAULT '',
                offer_letter_reference TEXT DEFAULT '',
                employer_company TEXT DEFAULT '',
                offered_salary TEXT DEFAULT '',
                contract_duration TEXT DEFAULT '',
                advance_payment DECIMAL(12,2) DEFAULT 0,
                advance_payment_mode TEXT DEFAULT '',
                advance_payment_status TEXT DEFAULT 'pending',
                advance_payment_date TEXT DEFAULT '',
                advance_payment_time TEXT DEFAULT '',
                advance_payment_reference TEXT DEFAULT '',
                medical_status TEXT DEFAULT 'pending',
                medical_date TEXT DEFAULT '',
                medical_report_no TEXT DEFAULT '',
                mofa_status TEXT DEFAULT 'not_applied',
                mofa_number TEXT DEFAULT '',
                mofa_date TEXT DEFAULT '',
                vfs_status TEXT DEFAULT 'not_applied',
                vfs_appointment_date TEXT DEFAULT '',
                vfs_reference_no TEXT DEFAULT '',
                takamual_status TEXT DEFAULT 'not_required',
                takamual_date TEXT DEFAULT '',
                takamual_certificate_no TEXT DEFAULT '',
                visa_status TEXT DEFAULT 'not_applied',
                visa_number TEXT DEFAULT '',
                visa_expiry_date TEXT DEFAULT '',
                agreement_process TEXT DEFAULT 'not_created',
                agreement_date TEXT DEFAULT '',
                agreement_number TEXT DEFAULT '',
                client_signed TEXT DEFAULT 'no',
                witness_name TEXT DEFAULT '',
                full_payment DECIMAL(12,2) DEFAULT 0,
                full_payment_mode TEXT DEFAULT '',
                full_payment_date TEXT DEFAULT '',
                flying_date TEXT DEFAULT '',
                flight_details TEXT DEFAULT '',
                ticket_status TEXT DEFAULT 'not_booked',
                remarks TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                district TEXT DEFAULT '',
                job_role TEXT DEFAULT '',
                country TEXT DEFAULT '',
                passport_no TEXT DEFAULT '',
                passport_submit_date TEXT DEFAULT '',
                passport_submitted_by TEXT DEFAULT 'self',
                passport_fee REAL DEFAULT 0,
                passport_payment_mode TEXT DEFAULT '',
                passport_payment_status TEXT DEFAULT 'pending',
                passport_payment_date TEXT DEFAULT '',
                passport_payment_reference TEXT DEFAULT '',
                interview_date TEXT DEFAULT '',
                interview_time TEXT DEFAULT '',
                interview_location TEXT DEFAULT '',
                interview_status TEXT DEFAULT 'pending',
                interview_reschedule_date TEXT DEFAULT '',
                interview_remarks TEXT DEFAULT '',
                offer_letter_status TEXT DEFAULT 'pending',
                offer_letter_date TEXT DEFAULT '',
                offer_letter_reference TEXT DEFAULT '',
                employer_company TEXT DEFAULT '',
                offered_salary TEXT DEFAULT '',
                contract_duration TEXT DEFAULT '',
                advance_payment REAL DEFAULT 0,
                advance_payment_mode TEXT DEFAULT '',
                advance_payment_status TEXT DEFAULT 'pending',
                advance_payment_date TEXT DEFAULT '',
                advance_payment_time TEXT DEFAULT '',
                advance_payment_reference TEXT DEFAULT '',
                medical_status TEXT DEFAULT 'pending',
                medical_date TEXT DEFAULT '',
                medical_report_no TEXT DEFAULT '',
                mofa_status TEXT DEFAULT 'not_applied',
                mofa_number TEXT DEFAULT '',
                mofa_date TEXT DEFAULT '',
                vfs_status TEXT DEFAULT 'not_applied',
                vfs_appointment_date TEXT DEFAULT '',
                vfs_reference_no TEXT DEFAULT '',
                takamual_status TEXT DEFAULT 'not_required',
                takamual_date TEXT DEFAULT '',
                takamual_certificate_no TEXT DEFAULT '',
                visa_status TEXT DEFAULT 'not_applied',
                visa_number TEXT DEFAULT '',
                visa_expiry_date TEXT DEFAULT '',
                agreement_process TEXT DEFAULT 'not_created',
                agreement_date TEXT DEFAULT '',
                agreement_number TEXT DEFAULT '',
                client_signed TEXT DEFAULT 'no',
                witness_name TEXT DEFAULT '',
                full_payment REAL DEFAULT 0,
                full_payment_mode TEXT DEFAULT '',
                full_payment_date TEXT DEFAULT '',
                flying_date TEXT DEFAULT '',
                flight_details TEXT DEFAULT '',
                ticket_status TEXT DEFAULT 'not_booked',
                remarks TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    conn.commit()
    
    # Check and fix admin
    if DB_TYPE == 'postgresql':
        cursor.execute("SELECT id, username, password FROM admin_users LIMIT 1")
    else:
        cursor.execute("SELECT id, username, password FROM admin_users LIMIT 1")
    
    admin = cursor.fetchone()
    
    if not admin:
        cursor.execute(
            "INSERT INTO admin_users (username, password) VALUES (%s, %s)" if DB_TYPE == 'postgresql' else "INSERT INTO admin_users (username, password) VALUES (?, ?)",
            ('admin', ADMIN123_HASH)
        )
        conn.commit()
        print("✅ Created default admin: admin / admin123")
    else:
        # Use index-based access for both SQLite and PostgreSQL
        admin_id = admin[0]
        admin_username = admin[1]
        stored_pass = admin[2]
        
        # Old wrong hash that was in previous version
        OLD_WRONG_HASH = '240be518fabd2724ddb6f04eeb9d5b76d76ad8f8e5d1a62bcf2caaec2b2b8b53'
        
        if len(stored_pass) != 64 or stored_pass == OLD_WRONG_HASH:
            cursor.execute(
                "UPDATE admin_users SET password = %s WHERE id = %s" if DB_TYPE == 'postgresql' else "UPDATE admin_users SET password = ? WHERE id = ?",
                (ADMIN123_HASH, admin_id)
            )
            conn.commit()
            print(f"✅ Fixed admin password for user: {admin_username}")
        else:
            print(f"✅ Admin OK: {admin_username}")
    cursor.close()
    conn.close()
    print("✅ Database ready!\n")

# Initialize on startup
init_db()

# ==================== Decorators ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Page Routes ====================

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ==================== Login API ====================

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required!'})
    
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_users WHERE username = ?", (username,))
    
    user = cursor.fetchone()
    if DB_TYPE == 'sqlite' and user:
        user = dict(user)
    
    cursor.close()
    conn.close()
    
    if user and verify_password(password, user['password']):
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login successful!'})
    
    return jsonify({'success': False, 'message': 'Invalid username or password!'})

# ==================== Admin Credentials API ====================

@app.route('/api/admin/credentials', methods=['GET'])
def get_admin_credentials():
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT username FROM admin_users LIMIT 1")
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM admin_users LIMIT 1")
    
    admin = cursor.fetchone()
    if DB_TYPE == 'sqlite' and admin:
        admin = dict(admin)
    
    cursor.close()
    conn.close()
    
    if admin:
        return jsonify({'success': True, 'username': admin['username'], 'passwordLength': 8})
    return jsonify({'success': False, 'message': 'No admin found'})

@app.route('/api/admin/change-credentials', methods=['POST'])
def change_admin_credentials():
    data = request.json
    current_password = data.get('currentPassword', '')
    new_username = data.get('newUsername', '').strip()
    new_password = data.get('newPassword', '')
    
    if not current_password:
        return jsonify({'success': False, 'message': 'Current password is required!'})
    if not new_username or len(new_username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters!'})
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters!'})
    
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM admin_users LIMIT 1")
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_users LIMIT 1")
    
    admin = cursor.fetchone()
    if DB_TYPE == 'sqlite' and admin:
        admin = dict(admin)
    
    if not admin:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'No admin account found!'})
    
    if not verify_password(current_password, admin['password']):
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect!'})
    
    new_hash = hash_password(new_password)
    
    if DB_TYPE == 'postgresql':
        cursor.execute(
            "UPDATE admin_users SET username = %s, password = %s, updated_at = %s WHERE id = %s",
            (new_username, new_hash, datetime.now().isoformat(), admin['id'])
        )
    else:
        cursor.execute(
            "UPDATE admin_users SET username = ?, password = ?, updated_at = ? WHERE id = ?",
            (new_username, new_hash, datetime.now().isoformat(), admin['id'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    session['username'] = new_username
    return jsonify({'success': True, 'message': 'Credentials updated successfully!'})

# ==================== Clients API ====================

@app.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM clients ORDER BY id DESC")
    clients = cursor.fetchall()
    
    if DB_TYPE == 'sqlite':
        clients = [dict(row) for row in clients]
    else:
        clients = [dict(row) for row in clients]
    
    cursor.close()
    conn.close()
    return jsonify(clients)

@app.route('/api/clients', methods=['POST'])
@login_required
def add_client():
    data = request.json
    
    columns = ['name', 'phone', 'district', 'job_role', 'country', 'passport_no', 
               'passport_submit_date', 'passport_submitted_by', 'passport_fee',
               'passport_payment_mode', 'passport_payment_status', 'passport_payment_date',
               'passport_payment_reference', 'interview_date', 'interview_time',
               'interview_location', 'interview_status', 'interview_reschedule_date',
               'interview_remarks', 'offer_letter_status', 'offer_letter_date',
               'offer_letter_reference', 'employer_company', 'offered_salary',
               'contract_duration', 'advance_payment', 'advance_payment_mode',
               'advance_payment_status', 'advance_payment_date', 'advance_payment_time',
               'advance_payment_reference', 'medical_status', 'medical_date',
               'medical_report_no', 'mofa_status', 'mofa_number', 'mofa_date',
               'vfs_status', 'vfs_appointment_date', 'vfs_reference_no',
               'takamual_status', 'takamual_date', 'takamual_certificate_no',
               'visa_status', 'visa_number', 'visa_expiry_date', 'agreement_process',
               'agreement_date', 'agreement_number', 'client_signed', 'witness_name',
               'full_payment', 'full_payment_mode', 'full_payment_date', 'flying_date',
               'flight_details', 'ticket_status', 'remarks']
    
    cols, vals, placeholders = [], [], []
    for col in columns:
        if col in data and data[col] is not None:
            cols.append(col)
            val = data[col]
            if col in ['advance_payment', 'full_payment', 'passport_fee']:
                vals.append(float(val) if val else 0)
            else:
                vals.append(str(val) if val else '')
            placeholders.append('%s' if DB_TYPE == 'postgresql' else '?')
    
    if not cols:
        return jsonify({'success': False, 'message': 'No data provided'})
    
    query = f"INSERT INTO clients ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
    
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor()
        query += " RETURNING id"
    else:
        cursor = conn.cursor()
    
    try:
        cursor.execute(query, vals)
        if DB_TYPE == 'postgresql':
            new_id = cursor.fetchone()[0]
        else:
            new_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'id': new_id, 'message': 'Client added successfully!'})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/clients/<int:client_id>', methods=['GET'])
@login_required
def get_client(client_id):
    conn = get_db()
    if DB_TYPE == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    
    client = cursor.fetchone()
    if DB_TYPE == 'sqlite' and client:
        client = dict(client)
    
    cursor.close()
    conn.close()
    
    if client:
        return jsonify(dict(client))
    return jsonify({'error': 'Client not found'}), 404

@app.route('/api/clients/<int:client_id>', methods=['PUT'])
@login_required
def update_client(client_id):
    data = request.json
    
    columns = ['name', 'phone', 'district', 'job_role', 'country', 'passport_no', 
               'passport_submit_date', 'passport_submitted_by', 'passport_fee',
               'passport_payment_mode', 'passport_payment_status', 'passport_payment_date',
               'passport_payment_reference', 'interview_date', 'interview_time',
               'interview_location', 'interview_status', 'interview_reschedule_date',
               'interview_remarks', 'offer_letter_status', 'offer_letter_date',
               'offer_letter_reference', 'employer_company', 'offered_salary',
               'contract_duration', 'advance_payment', 'advance_payment_mode',
               'advance_payment_status', 'advance_payment_date', 'advance_payment_time',
               'advance_payment_reference', 'medical_status', 'medical_date',
               'medical_report_no', 'mofa_status', 'mofa_number', 'mofa_date',
               'vfs_status', 'vfs_appointment_date', 'vfs_reference_no',
               'takamual_status', 'takamual_date', 'takamual_certificate_no',
               'visa_status', 'visa_number', 'visa_expiry_date', 'agreement_process',
               'agreement_date', 'agreement_number', 'client_signed', 'witness_name',
               'full_payment', 'full_payment_mode', 'full_payment_date', 'flying_date',
               'flight_details', 'ticket_status', 'remarks']
    
    updates, vals = [], []
    placeholder = '%s' if DB_TYPE == 'postgresql' else '?'
    
    for col in columns:
        if col in data:
            updates.append(f"{col} = {placeholder}")
            val = data[col]
            if col in ['advance_payment', 'full_payment', 'passport_fee']:
                vals.append(float(val) if val else 0)
            else:
                vals.append(val if val else '')
    
    updates.append(f"updated_at = {placeholder}")
    vals.append(datetime.now().isoformat())
    vals.append(client_id)
    
    query = f"UPDATE clients SET {', '.join(updates)} WHERE id = {placeholder}"
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, vals)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Client updated successfully!'})
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/clients/<int:client_id>', methods=['DELETE'])
@login_required
def delete_client(client_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if DB_TYPE == 'postgresql':
        cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
    else:
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'Client deleted successfully!'})

@app.route('/api/clients/clear', methods=['DELETE'])
@login_required
def clear_all_clients():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': 'All clients deleted!'})

# ==================== Stats API ====================

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM clients")
    stats['total_clients'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE interview_status IN ('pending', 'scheduled')")
    stats['interview_pending'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE interview_status IN ('selected', 'passed')")
    stats['interview_passed'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE visa_status = 'approved'")
    stats['visa_approved'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE visa_status NOT IN ('approved', 'rejected', 'not_applied', '')")
    stats['visa_processing'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(advance_payment), 0) FROM clients")
    stats['total_advance'] = float(cursor.fetchone()[0] or 0)
    
    cursor.execute("SELECT COALESCE(SUM(full_payment), 0) FROM clients")
    stats['total_full_payment'] = float(cursor.fetchone()[0] or 0)
    
    cursor.execute("SELECT COALESCE(SUM(passport_fee), 0) FROM clients WHERE passport_submitted_by = 'agency'")
    stats['total_passport_fee'] = float(cursor.fetchone()[0] or 0)
    
    stats['total_revenue'] = stats['total_advance'] + stats['total_full_payment'] + stats['total_passport_fee']
    
    cursor.execute("SELECT COUNT(*) FROM clients WHERE visa_status = 'approved' AND flying_date IS NOT NULL AND flying_date != ''")
    stats['ready_to_fly'] = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    return jsonify(stats)

# ==================== Health Check for Render ====================

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'database': DB_TYPE})

# ==================== Run Application ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("="*60)
    print("  🌍 Pavishna Global Service - Admin Panel")
    print("="*60)
    print(f"\n  🌐 Server: http://localhost:{port}")
    print(f"  📊 Database: {DB_TYPE.upper()}")
    print(f"\n  🔐 Default Login: admin / admin123")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
