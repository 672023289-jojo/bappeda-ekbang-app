import sqlite3
import os

DB_NAME = "bappeda.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabel Pengguna (Login & Hak Akses)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            opd_name TEXT
        )
    ''')
    
    # Tabel Metadata Dokumen (CRUD)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            uploaded_by TEXT,
            opd_name TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Buat akun bawaan (default) jika belum ada
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role, opd_name) VALUES ('admin_ekbang', 'admin123', 'ekbang', 'Bidang Ekbang')")
        cursor.execute("INSERT INTO users (username, password, role, opd_name) VALUES ('staf_dinkes', 'dinkes123', 'opd', 'Dinas Kesehatan')")
        cursor.execute("INSERT INTO users (username, password, role, opd_name) VALUES ('staf_disdik', 'disdik123', 'opd', 'Dinas Pendidikan')")
    
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, opd_name FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def save_document_meta(filename, filepath, uploaded_by, opd_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (filename, filepath, uploaded_by, opd_name) VALUES (?, ?, ?, ?)",
                   (filename, filepath, uploaded_by, opd_name))
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_all_documents(user_role, user_opd):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Ekbang bisa lihat semua dokumen, OPD hanya bisa lihat dokumen milik OPD-nya sendiri
    if user_role == 'ekbang':
        cursor.execute("SELECT id, filename, uploaded_by, opd_name, upload_date FROM documents")
    else:
        cursor.execute("SELECT id, filename, uploaded_by, opd_name, upload_date FROM documents WHERE opd_name = ?", (user_opd,))
    docs = cursor.fetchall()
    conn.close()
    return docs

def delete_document_meta(doc_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT filepath FROM documents WHERE id = ?", (doc_id,))
    res = cursor.fetchone()
    if res:
        filepath = res[0]
        if os.path.exists(filepath):
            os.remove(filepath)
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
    conn.close()