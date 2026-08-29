import sqlite3
import hashlib
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path.home() / ".spend_tracker.db"

DEFAULT_CATEGORIES = [
    ("🍔 Food & Dining", "#ff79c6"),
    ("🚗 Transportation", "#8be9fd"),
    ("🏠 Housing & Rent", "#bd93f9"),
    ("💡 Utilities & Bills", "#f1fa8c"),
    ("🛍️ Shopping", "#ffb86c"),
    ("🎬 Entertainment", "#ff5555"),
    ("💊 Health & Fitness", "#50fa7b"),
    ("📚 Education & Learning", "#00e5ff"),
    ("💼 Work & Business", "#f8f8f2"),
    ("📦 Other / Misc", "#6272a4")
]

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    calc, _ = hash_password(password, salt)
    return calc == hashed

def init_db(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Users table (Multi-Account Authentication)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        name TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Check for existing default user, create if none
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        h, s = hash_password("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, name, created_at) VALUES (?, ?, ?, ?, ?)",
            ("admin", h, s, "Primary User", datetime.now().isoformat())
        )

    # Automatic column migration for legacy tables
    tables = ['categories', 'expenses', 'budgets', 'loans']
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [info[1] for info in cursor.fetchall()]
        if cols and 'user_id' not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER DEFAULT 1")

    # 2. Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#8be9fd',
        UNIQUE(user_id, name)
    )
    """)
    
    # 3. Expenses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        payment_method TEXT DEFAULT 'Card',
        created_at TEXT NOT NULL
    )
    """)

    # 4. Monthly Budget Goals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        user_id INTEGER DEFAULT 1,
        month TEXT NOT NULL,
        amount REAL NOT NULL,
        PRIMARY KEY(user_id, month)
    )
    """)

    # 5. Loans & Debts (Khata)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        type TEXT NOT NULL, -- 'lent' or 'borrowed'
        person TEXT NOT NULL,
        amount REAL NOT NULL,
        settled_amount REAL DEFAULT 0.0,
        due_date TEXT,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL
    )
    """)
    
    # Seed default categories for user_id = 1 if empty
    cursor.execute("SELECT COUNT(*) FROM categories WHERE user_id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT OR IGNORE INTO categories (user_id, name, color) VALUES (1, ?, ?)", DEFAULT_CATEGORIES)
        
    conn.commit()
    conn.close()

# ==========================================
# USER AUTHENTICATION & MULTI-ACCOUNT
# ==========================================

def create_user(username: str, password: str, name: Optional[str] = None, db_path: Path = DB_PATH) -> tuple[bool, str, Optional[int]]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    uname = username.strip().lower()
    
    # Explicitly check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (uname,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists", None
        
    h, s = hash_password(password)
    now = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, name, created_at) VALUES (?, ?, ?, ?, ?)",
            (uname, h, s, name or username, now)
        )
        user_id = cursor.lastrowid
        # Seed default categories for this new account
        cursor.executemany("INSERT OR IGNORE INTO categories (user_id, name, color) VALUES (?, ?, ?)", [(user_id, cat[0], cat[1]) for cat in DEFAULT_CATEGORIES])
        conn.commit()
        conn.close()
        return True, "Account created successfully", user_id
    except Exception as e:
        conn.close()
        return False, f"Error creating account: {e}", None

def authenticate_user(username: str, password: str, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return None
    if verify_password(password, user["password_hash"], user["salt"]):
        return {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"] or user["username"]
        }
    return None

def list_users(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, name, created_at FROM users ORDER BY id ASC")
    users = [dict(u) for u in cursor.fetchall()]
    conn.close()
    return users

# ==========================================
# EXPENSES (User-Isolated)
# ==========================================

def add_expense(amount: float, category: str, description: str, date: str, payment_method: str = "Card", user_id: int = 1, db_path: Path = DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO expenses (user_id, date, category, amount, description, payment_method, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, date, category, amount, description, payment_method, created_at)
    )
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def get_expenses(limit: Optional[int] = None, category: Optional[str] = None, month: Optional[str] = None, search: Optional[str] = None, user_id: int = 1, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM expenses WHERE user_id = ?"
    params = [user_id]
    
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
        
    if month:
        query += " AND date LIKE ?"
        params.append(f"{month}%")
        
    if search:
        query += " AND (description LIKE ? OR category LIKE ? OR payment_method LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    query += " ORDER BY date DESC, id DESC"
    
    if limit:
        query += f" LIMIT {int(limit)}"
        
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def delete_expense(expense_id: int, user_id: int = 1, db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_summary(month: Optional[str] = None, user_id: int = 1, db_path: Path = DB_PATH) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT SUM(amount), COUNT(*) FROM expenses WHERE user_id = ?"
    params = [user_id]
    if month:
        query += " AND date LIKE ?"
        params.append(f"{month}%")
        
    cursor.execute(query, params)
    total_amount, count = cursor.fetchone()
    total_amount = total_amount or 0.0
    count = count or 0
    
    # Group by category
    cat_query = "SELECT category, SUM(amount) as cat_total, COUNT(*) as cat_count FROM expenses WHERE user_id = ?"
    cat_params = [user_id]
    if month:
        cat_query += " AND date LIKE ?"
        cat_params.append(f"{month}%")
    cat_query += " GROUP BY category ORDER BY cat_total DESC"
    
    cursor.execute(cat_query, cat_params)
    by_category = [{"category": row[0], "total": row[1], "count": row[2]} for row in cursor.fetchall()]
    
    # Group by payment method
    pm_query = "SELECT payment_method, SUM(amount) as pm_total FROM expenses WHERE user_id = ?"
    pm_params = [user_id]
    if month:
        pm_query += " AND date LIKE ?"
        pm_params.append(f"{month}%")
    pm_query += " GROUP BY payment_method ORDER BY pm_total DESC"
    cursor.execute(pm_query, pm_params)
    by_pm = [{"method": row[0], "total": row[1]} for row in cursor.fetchall()]
    
    # Budget check
    budget_amount = None
    if month:
        cursor.execute("SELECT amount FROM budgets WHERE user_id = ? AND month = ?", (user_id, month))
        b_row = cursor.fetchone()
        if b_row:
            budget_amount = b_row[0]
            
    conn.close()
    return {
        "total_amount": total_amount,
        "count": count,
        "by_category": by_category,
        "by_payment_method": by_pm,
        "budget": budget_amount
    }

def get_daily_spending(month: str, user_id: int = 1, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Returns daily totals for a specific month (YYYY-MM)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, SUM(amount), COUNT(*) FROM expenses WHERE user_id = ? AND date LIKE ? GROUP BY date ORDER BY date ASC",
        (user_id, f"{month}%")
    )
    rows = [{"date": r[0], "total": r[1], "count": r[2]} for r in cursor.fetchall()]
    conn.close()
    return rows

def get_monthly_history(limit: int = 12, user_id: int = 1, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Returns total spending for recent months."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUBSTR(date, 1, 7) as month, SUM(amount), COUNT(*) FROM expenses WHERE user_id = ? GROUP BY month ORDER BY month DESC LIMIT ?",
        (user_id, limit)
    )
    rows = [{"month": r[0], "total": r[1], "count": r[2]} for r in cursor.fetchall()]
    conn.close()
    return list(reversed(rows))

def set_budget(month: str, amount: float, user_id: int = 1, db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO budgets (user_id, month, amount) VALUES (?, ?, ?)", (user_id, month, amount))
    conn.commit()
    conn.close()

def get_all_categories(user_id: int = 1, db_path: Path = DB_PATH) -> List[str]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE user_id = ? ORDER BY id ASC", (user_id,))
    cats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cats

def add_category(name: str, color: str = "#8be9fd", user_id: int = 1, db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (user_id, name, color) VALUES (?, ?, ?)", (user_id, name, color))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

# ==========================================
# LENDING & BORROWING (LOANS / DEBTS)
# ==========================================

def add_loan(loan_type: str, person: str, amount: float, due_date: Optional[str] = None, notes: Optional[str] = None, user_id: int = 1, db_path: Path = DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO loans (user_id, type, person, amount, settled_amount, due_date, notes, status, created_at) VALUES (?, ?, ?, ?, 0.0, ?, ?, 'pending', ?)",
        (user_id, loan_type, person, amount, due_date, notes, created_at)
    )
    loan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return loan_id

def get_loans(status_filter: Optional[str] = None, type_filter: Optional[str] = None, user_id: int = 1, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM loans WHERE user_id = ?"
    params = [user_id]
    
    if status_filter and status_filter != "all":
        query += " AND status = ?"
        params.append(status_filter)
        
    if type_filter and type_filter != "all":
        query += " AND type = ?"
        params.append(type_filter)
        
    query += " ORDER BY status ASC, id DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def settle_loan(loan_id: int, settle_amount: float, user_id: int = 1, db_path: Path = DB_PATH) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM loans WHERE id = ? AND user_id = ?", (loan_id, user_id))
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return {"success": False, "msg": "Record not found"}
        
    new_settled = (loan["settled_amount"] or 0.0) + settle_amount
    new_status = "settled" if new_settled >= loan["amount"] else "partial"
    
    cursor.execute(
        "UPDATE loans SET settled_amount = ?, status = ? WHERE id = ? AND user_id = ?",
        (new_settled, new_status, loan_id, user_id)
    )
    conn.commit()
    conn.close()
    return {"success": True, "new_settled": new_settled, "status": new_status, "remaining": max(0.0, loan["amount"] - new_settled)}

def delete_loan(loan_id: int, user_id: int = 1, db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM loans WHERE id = ? AND user_id = ?", (loan_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_loans_summary(user_id: int = 1, db_path: Path = DB_PATH) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount - settled_amount) FROM loans WHERE user_id = ? AND type = 'lent' AND status != 'settled'", (user_id,))
    total_lent_pending = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(amount - settled_amount) FROM loans WHERE user_id = ? AND type = 'borrowed' AND status != 'settled'", (user_id,))
    total_borrowed_pending = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT COUNT(*) FROM loans WHERE user_id = ? AND status != 'settled'", (user_id,))
    pending_count = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        "lent_pending": total_lent_pending,
        "borrowed_pending": total_borrowed_pending,
        "net_balance": total_lent_pending - total_borrowed_pending,
        "pending_count": pending_count
    }
