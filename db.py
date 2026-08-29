import sqlite3
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

def init_db(db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table for Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        color TEXT DEFAULT '#8be9fd'
    )
    """)
    
    # Table for Expenses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        payment_method TEXT DEFAULT 'Card',
        created_at TEXT NOT NULL
    )
    """)

    # Table for Monthly Budget Goals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        month TEXT PRIMARY KEY, -- format YYYY-MM
        amount REAL NOT NULL
    )
    """)

    # Table for Loans & Debts (Lending / Borrowing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL, -- 'lent' (you gave to someone) or 'borrowed' (you owe someone)
        person TEXT NOT NULL,
        amount REAL NOT NULL,
        settled_amount REAL DEFAULT 0.0,
        due_date TEXT,
        notes TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'settled', 'partial'
        created_at TEXT NOT NULL
    )
    """)
    
    # Seed default categories if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categories (name, color) VALUES (?, ?)", DEFAULT_CATEGORIES)
        
    conn.commit()
    conn.close()

def add_expense(amount: float, category: str, description: str, date: str, payment_method: str = "Card", db_path: Path = DB_PATH) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description, payment_method, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (date, category, amount, description, payment_method, created_at)
    )
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def get_expenses(limit: Optional[int] = None, category: Optional[str] = None, month: Optional[str] = None, search: Optional[str] = None, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    
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

def delete_expense(expense_id: int, db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_summary(month: Optional[str] = None, db_path: Path = DB_PATH) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT SUM(amount), COUNT(*) FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND date LIKE ?"
        params.append(f"{month}%")
        
    cursor.execute(query, params)
    total_amount, count = cursor.fetchone()
    total_amount = total_amount or 0.0
    count = count or 0
    
    # Group by category
    cat_query = "SELECT category, SUM(amount) as cat_total, COUNT(*) as cat_count FROM expenses WHERE 1=1"
    if month:
        cat_query += " AND date LIKE ?"
    cat_query += " GROUP BY category ORDER BY cat_total DESC"
    
    cursor.execute(cat_query, params)
    by_category = [{"category": row[0], "total": row[1], "count": row[2]} for row in cursor.fetchall()]
    
    # Group by payment method
    pm_query = "SELECT payment_method, SUM(amount) as pm_total FROM expenses WHERE 1=1"
    if month:
        pm_query += " AND date LIKE ?"
    pm_query += " GROUP BY payment_method ORDER BY pm_total DESC"
    cursor.execute(pm_query, params)
    by_pm = [{"method": row[0], "total": row[1]} for row in cursor.fetchall()]
    
    # Budget check
    budget_amount = None
    if month:
        cursor.execute("SELECT amount FROM budgets WHERE month = ?", (month,))
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

def get_daily_spending(month: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Returns daily totals for a specific month (YYYY-MM)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, SUM(amount), COUNT(*) FROM expenses WHERE date LIKE ? GROUP BY date ORDER BY date ASC",
        (f"{month}%",)
    )
    rows = [{"date": r[0], "total": r[1], "count": r[2]} for r in cursor.fetchall()]
    conn.close()
    return rows

def get_monthly_history(limit: int = 12, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Returns total spending for recent months."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUBSTR(date, 1, 7) as month, SUM(amount), COUNT(*) FROM expenses GROUP BY month ORDER BY month DESC LIMIT ?",
        (limit,)
    )
    rows = [{"month": r[0], "total": r[1], "count": r[2]} for r in cursor.fetchall()]
    conn.close()
    return list(reversed(rows))

def set_budget(month: str, amount: float, db_path: Path = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO budgets (month, amount) VALUES (?, ?)", (month, amount))
    conn.commit()
    conn.close()

def get_all_categories(db_path: Path = DB_PATH) -> List[str]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM categories ORDER BY id ASC")
    cats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cats

def add_category(name: str, color: str = "#8be9fd", db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name, color) VALUES (?, ?)", (name, color))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

# ==========================================
# LENDING & BORROWING (LOANS / DEBTS)
# ==========================================

def add_loan(loan_type: str, person: str, amount: float, due_date: Optional[str] = None, notes: Optional[str] = None, db_path: Path = DB_PATH) -> int:
    """Adds a lending or borrowing record. loan_type: 'lent' or 'borrowed'."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO loans (type, person, amount, settled_amount, due_date, notes, status, created_at) VALUES (?, ?, ?, 0.0, ?, ?, 'pending', ?)",
        (loan_type, person, amount, due_date, notes, created_at)
    )
    loan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return loan_id

def get_loans(status_filter: Optional[str] = None, type_filter: Optional[str] = None, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM loans WHERE 1=1"
    params = []
    
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

def settle_loan(loan_id: int, settle_amount: float, db_path: Path = DB_PATH) -> Dict[str, Any]:
    """Records a repayment or partial settlement on a loan."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return {"success": False, "msg": "Record not found"}
        
    new_settled = (loan["settled_amount"] or 0.0) + settle_amount
    new_status = "settled" if new_settled >= loan["amount"] else "partial"
    
    cursor.execute(
        "UPDATE loans SET settled_amount = ?, status = ? WHERE id = ?",
        (new_settled, new_status, loan_id)
    )
    conn.commit()
    conn.close()
    return {"success": True, "new_settled": new_settled, "status": new_status, "remaining": max(0.0, loan["amount"] - new_settled)}

def delete_loan(loan_id: int, db_path: Path = DB_PATH) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_loans_summary(db_path: Path = DB_PATH) -> Dict[str, Any]:
    """Summary of all pending money lent to others and money borrowed."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total lent (others owe you)
    cursor.execute("SELECT SUM(amount - settled_amount) FROM loans WHERE type = 'lent' AND status != 'settled'")
    total_lent_pending = cursor.fetchone()[0] or 0.0
    
    # Total borrowed (you owe others)
    cursor.execute("SELECT SUM(amount - settled_amount) FROM loans WHERE type = 'borrowed' AND status != 'settled'")
    total_borrowed_pending = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT COUNT(*) FROM loans WHERE status != 'settled'")
    pending_count = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        "lent_pending": total_lent_pending,
        "borrowed_pending": total_borrowed_pending,
        "net_balance": total_lent_pending - total_borrowed_pending,
        "pending_count": pending_count
    }
