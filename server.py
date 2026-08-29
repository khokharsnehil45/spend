"""
SPEND Web/Desktop GUI Backend API Server (FastAPI).
Serves multi-account auth, real-time financial data, transactions, charts, AI analytics, and loan ledgers.
"""

import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

import db
import ai_advisor
import report_gen

app = FastAPI(title="SPEND GUI", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "web"
STATIC_DIR.mkdir(exist_ok=True)

# Models
class UserRegister(BaseModel):
    username: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = ""
    date: str
    payment_method: str = "📱 UPI / GPay / PhonePe"
    user_id: Optional[int] = 1

class BudgetSet(BaseModel):
    month: str
    amount: float
    user_id: Optional[int] = 1

class CategoryCreate(BaseModel):
    name: str
    user_id: Optional[int] = 1

class LoanCreate(BaseModel):
    type: str # 'lent' or 'borrowed'
    person: str
    amount: float
    due_date: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[int] = 1

class LoanSettle(BaseModel):
    amount: float
    user_id: Optional[int] = 1

class AIQuery(BaseModel):
    month: str
    question: Optional[str] = None
    user_id: Optional[int] = 1

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.post("/api/auth/register")
def register(data: UserRegister):
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    success, msg, user_id = db.create_user(data.username, data.password, data.name)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "user_id": user_id, "username": data.username.lower(), "name": data.name or data.username}

@app.post("/api/auth/login")
def login(data: UserLogin):
    user = db.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"success": True, "user": user}

@app.get("/api/auth/users")
def get_accounts():
    return db.list_users()

# ==========================================
# DATA ROUTES (User-Scoped)
# ==========================================

@app.get("/api/summary")
def get_summary(month: Optional[str] = None, user_id: int = 1):
    if not month:
        month = datetime.today().strftime('%Y-%m')
    summary = db.get_summary(month=month, user_id=user_id)
    loans_summary = db.get_loans_summary(user_id=user_id)
    return {
        "month": month,
        "summary": summary,
        "loans_summary": loans_summary
    }

@app.get("/api/expenses")
def get_expenses(month: Optional[str] = None, category: Optional[str] = None, search: Optional[str] = None, limit: Optional[int] = None, user_id: int = 1):
    return db.get_expenses(month=month, category=category, search=search, limit=limit, user_id=user_id)

@app.post("/api/expenses")
def create_expense(data: ExpenseCreate):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    uid = data.user_id or 1
    exp_id = db.add_expense(data.amount, data.category, data.description or "", data.date, data.payment_method, user_id=uid)
    return {"success": True, "id": exp_id}

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, user_id: int = 1):
    success = db.delete_expense(expense_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"success": True}

@app.get("/api/charts/daily")
def get_daily_charts(month: Optional[str] = None, user_id: int = 1):
    if not month:
        month = datetime.today().strftime('%Y-%m')
    return db.get_daily_spending(month, user_id=user_id)

@app.get("/api/charts/monthly")
def get_monthly_charts(user_id: int = 1):
    return db.get_monthly_history(limit=12, user_id=user_id)

@app.get("/api/categories")
def get_categories(user_id: int = 1):
    return db.get_all_categories(user_id=user_id)

@app.post("/api/categories")
def add_category(data: CategoryCreate):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Invalid name")
    uid = data.user_id or 1
    success = db.add_category(data.name.strip(), user_id=uid)
    if not success:
        raise HTTPException(status_code=400, detail="Category already exists")
    return {"success": True}

@app.post("/api/budget")
def set_budget(data: BudgetSet):
    uid = data.user_id or 1
    db.set_budget(data.month, data.amount, user_id=uid)
    return {"success": True}

@app.get("/api/loans")
def get_loans(status: Optional[str] = None, type: Optional[str] = None, user_id: int = 1):
    return db.get_loans(status_filter=status, type_filter=type, user_id=user_id)

@app.post("/api/loans")
def create_loan(data: LoanCreate):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    uid = data.user_id or 1
    loan_id = db.add_loan(data.type, data.person, data.amount, data.due_date, data.notes, user_id=uid)
    return {"success": True, "id": loan_id}

@app.post("/api/loans/{loan_id}/settle")
def settle_loan(loan_id: int, data: LoanSettle):
    uid = data.user_id or 1
    res = db.settle_loan(loan_id, data.amount, user_id=uid)
    if not res["success"]:
        raise HTTPException(status_code=404, detail=res["msg"])
    return res

@app.delete("/api/loans/{loan_id}")
def delete_loan(loan_id: int, user_id: int = 1):
    success = db.delete_loan(loan_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"success": True}

@app.get("/api/ai/config")
def get_ai_config():
    return ai_advisor.load_ai_config()

@app.post("/api/ai/config")
def save_ai_config(cfg: Dict[str, Any]):
    ai_advisor.save_ai_config(cfg)
    return {"success": True}

@app.post("/api/ai/analyze")
def run_ai_analysis(data: AIQuery):
    uid = data.user_id or 1
    expenses = db.get_expenses(month=data.month, user_id=uid)
    summary = db.get_summary(month=data.month, user_id=uid)
    try:
        report = ai_advisor.run_ai_financial_analysis(expenses, summary, data.month, data.question)
        return {"success": True, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/pdf")
def download_pdf_report(month: str, include_ai: bool = False, user_id: int = 1):
    ai_text = None
    if include_ai:
        try:
            ai_text = ai_advisor.run_ai_financial_analysis(db.get_expenses(month=month, user_id=user_id), db.get_summary(month=month, user_id=user_id), month)
        except Exception:
            pass
    html = report_gen.generate_styled_html_report(month, include_ai=include_ai, ai_summary_text=ai_text)
    out_pdf = STATIC_DIR / f"spend_report_{month}.pdf"
    report_gen.export_report_to_pdf(html, out_pdf)
    return FileResponse(out_pdf, media_type="application/pdf", filename=f"spend_report_{month}.pdf")

@app.get("/api/reports/markdown")
def download_md_report(month: str, include_ai: bool = False, user_id: int = 1):
    ai_text = None
    if include_ai:
        try:
            ai_text = ai_advisor.run_ai_financial_analysis(db.get_expenses(month=month, user_id=user_id), db.get_summary(month=month, user_id=user_id), month)
        except Exception:
            pass
    md = report_gen.generate_markdown_report(month, include_ai=include_ai, ai_summary_text=ai_text)
    out_md = STATIC_DIR / f"spend_report_{month}.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    return FileResponse(out_md, media_type="text/markdown", filename=f"spend_report_{month}.md")

# Serve Frontend SPA
@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    return FileResponse(index_file)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def launch_server(port: int = 8321, open_browser: bool = True):
    db.init_db()
    url = f"http://localhost:{port}"
    print(f"\n🚀 SPEND GUI launched at: {url}\n")
    if open_browser:
        webbrowser.open(url)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    launch_server()
