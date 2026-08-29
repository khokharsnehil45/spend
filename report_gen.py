"""
SPEND Report Generator - Beautiful Markdown and Styled PDF Financial Reports.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import db

def generate_markdown_report(month: str, include_ai: bool = False, ai_summary_text: Optional[str] = None) -> str:
    """Generates a comprehensive, cleanly styled Markdown report for the given month."""
    summary = db.get_summary(month=month)
    expenses = db.get_expenses(month=month)
    daily_data = db.get_daily_spending(month)
    
    total_spent = summary["total_amount"]
    budget = summary["budget"]
    count = summary["count"]
    
    md = []
    md.append(f"# 📊 SPEND Financial Statement — {month}")
    md.append(f"> *Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}*\n")
    md.append("---")
    
    # 1. Executive Summary
    md.append("## 📌 1. Executive Summary\n")
    md.append(f"- **Period**: `{month}`")
    md.append(f"- **Total Spending**: **₹{total_spent:,.2f}**")
    md.append(f"- **Total Transactions**: `{count}`")
    
    if budget:
        remaining = budget - total_spent
        pct = (total_spent / budget) * 100 if budget > 0 else 0
        md.append(f"- **Monthly Budget Limit**: ₹{budget:,.2f}")
        if remaining >= 0:
            md.append(f"- **Budget Status**: ✅ **₹{remaining:,.2f} Remaining** ({pct:.1f}% consumed)")
        else:
            md.append(f"- **Budget Status**: ⚠️ **OVER BUDGET by ₹{abs(remaining):,.2f}** ({pct:.1f}% consumed)")
    else:
        md.append("- **Monthly Budget Limit**: *Not set*")
        
    md.append("\n---\n")
    
    # 2. Category Breakdown
    md.append("## 🏷️ 2. Category Breakdown\n")
    if summary["by_category"]:
        md.append("| Category | Amount (₹) | Share (%) | Transactions |")
        md.append("| :--- | :---: | :---: | :---: |")
        for item in summary["by_category"]:
            share = (item["total"] / total_spent * 100) if total_spent > 0 else 0
            md.append(f"| {item['category']} | ₹{item['total']:,.2f} | {share:.1f}% | {item['count']} |")
    else:
        md.append("*No category expenses logged for this month.*")
        
    md.append("\n---\n")
    
    # 3. Payment Methods Distribution
    md.append("## 💳 3. Payment Method Distribution\n")
    if summary["by_payment_method"]:
        md.append("| Payment Method | Total Amount (₹) |")
        md.append("| :--- | :---: |")
        for pm in summary["by_payment_method"]:
            md.append(f"| {pm['method']} | ₹{pm['total']:,.2f} |")
    else:
        md.append("*No records available.*")
        
    md.append("\n---\n")
    
    # 4. Daily Spending Timeline
    if daily_data:
        md.append("## 📅 4. Daily Timeline Summary\n")
        peak = max(daily_data, key=lambda x: x["total"])
        avg = total_spent / len(daily_data)
        md.append(f"- **Peak Spending Date**: `{peak['date']}` (₹{peak['total']:,.2f})")
        md.append(f"- **Active Days Average**: `₹{avg:,.2f} / day` across {len(daily_data)} active days\n")
        md.append("| Date | Daily Total (₹) | Count |")
        md.append("| :--- | :---: | :---: |")
        for d in daily_data:
            md.append(f"| {d['date']} | ₹{d['total']:,.2f} | {d['count']} |")
        md.append("\n---\n")

    # 5. AI Advisor Section (Optional)
    if include_ai and ai_summary_text:
        md.append("## 🤖 5. SPEND AI Financial Insights & Advice\n")
        md.append(ai_summary_text)
        md.append("\n---\n")
        
    # 6. Itemized Transactions List
    md.append("## 📜 6. Itemized Transaction Log\n")
    if expenses:
        md.append("| ID | Date | Category | Description | Payment Method | Amount (₹) |")
        md.append("| :---: | :---: | :--- | :--- | :---: | :---: |")
        for e in expenses:
            desc = e["description"] if e["description"] else "-"
            md.append(f"| #{e['id']} | {e['date']} | {e['category']} | {desc} | {e['payment_method']} | ₹{e['amount']:,.2f} |")
    else:
        md.append("*No transactions found.*")
        
    md.append("\n\n---\n*Report generated with [SPEND](https://github.com) — Retro CLI Expense Tracker.*")
    return "\n".join(md)

def generate_styled_html_report(month: str, include_ai: bool = False, ai_summary_text: Optional[str] = None) -> str:
    """Generates a standalone, beautifully styled HTML document with modern typography and printable CSS."""
    summary = db.get_summary(month=month)
    expenses = db.get_expenses(month=month)
    daily_data = db.get_daily_spending(month)
    
    total_spent = summary["total_amount"]
    budget = summary["budget"]
    count = summary["count"]
    
    budget_status_html = ""
    if budget:
        remaining = budget - total_spent
        pct = (total_spent / budget) * 100 if budget > 0 else 0
        if remaining >= 0:
            budget_status_html = f"""
            <div class="stat-card">
                <div class="stat-title">Remaining Budget</div>
                <div class="stat-value text-green">₹{remaining:,.2f}</div>
                <div class="stat-sub">{pct:.1f}% of ₹{budget:,.2f} limit used</div>
            </div>
            """
        else:
            budget_status_html = f"""
            <div class="stat-card stat-alert">
                <div class="stat-title">Budget Overrun</div>
                <div class="stat-value text-red">₹{abs(remaining):,.2f} OVER</div>
                <div class="stat-sub">{pct:.1f}% of ₹{budget:,.2f} limit used</div>
            </div>
            """
    else:
        budget_status_html = """
        <div class="stat-card">
            <div class="stat-title">Budget Limit</div>
            <div class="stat-value text-muted">Not Set</div>
            <div class="stat-sub">Configure in SPEND</div>
        </div>
        """

    cat_rows = ""
    for item in summary.get("by_category", []):
        share = (item["total"] / total_spent * 100) if total_spent > 0 else 0
        cat_rows += f"""
        <tr>
            <td><strong>{item['category']}</strong></td>
            <td class="text-right">₹{item['total']:,.2f}</td>
            <td class="text-right">{share:.1f}%</td>
            <td class="text-center">{item['count']}</td>
        </tr>
        """

    pm_rows = ""
    for pm in summary.get("by_payment_method", []):
        pm_rows += f"""
        <tr>
            <td>{pm['method']}</td>
            <td class="text-right">₹{pm['total']:,.2f}</td>
        </tr>
        """

    tx_rows = ""
    for e in expenses:
        desc = e["description"] if e["description"] else "-"
        tx_rows += f"""
        <tr>
            <td class="text-center text-muted">#{e['id']}</td>
            <td>{e['date']}</td>
            <td><strong>{e['category']}</strong></td>
            <td>{desc}</td>
            <td>{e['payment_method']}</td>
            <td class="text-right font-semibold text-green">₹{e['amount']:,.2f}</td>
        </tr>
        """

    ai_section_html = ""
    if include_ai and ai_summary_text:
        formatted_ai = ai_summary_text.replace("\n", "<br>")
        ai_section_html = f"""
        <div class="section-card ai-box">
            <h2>🤖 SPEND AI Financial Insights</h2>
            <div class="ai-content">
                {formatted_ai}
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SPEND Financial Statement - {month}</title>
<style>
    @page {{
        size: A4;
        margin: 15mm 15mm;
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        line-height: 1.5;
        font-size: 13px;
        margin: 0;
        padding: 20px;
    }}
    .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #0284c7;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }}
    .logo {{
        font-size: 26px;
        font-weight: 900;
        color: #0284c7;
        letter-spacing: 1px;
    }}
    .subtitle {{
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }}
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-bottom: 25px;
    }}
    .stat-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
    }}
    .stat-alert {{
        background: #fff1f2;
        border-color: #fecdd3;
    }}
    .stat-title {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 4px;
    }}
    .stat-value {{
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
    }}
    .stat-sub {{
        font-size: 11px;
        color: #64748b;
        margin-top: 2px;
    }}
    .text-green {{ color: #16a34a !important; }}
    .text-red {{ color: #dc2626 !important; }}
    .text-muted {{ color: #94a3b8; }}
    .text-right {{ text-align: right; }}
    .text-center {{ text-align: center; }}
    .font-semibold {{ font-weight: 600; }}
    
    h2 {{
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 20px;
        margin-bottom: 10px;
        border-left: 4px solid #0284c7;
        padding-left: 8px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        font-size: 12px;
    }}
    th {{
        background-color: #f1f5f9;
        color: #475569;
        font-weight: 700;
        text-align: left;
        padding: 8px 12px;
        border-bottom: 1px solid #cbd5e1;
    }}
    td {{
        padding: 8px 12px;
        border-bottom: 1px solid #f1f5f9;
    }}
    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}
    .two-col {{
        display: grid;
        grid-template-columns: 3fr 2fr;
        gap: 20px;
    }}
    .ai-box {{
        background: #fdf4ff;
        border: 1px solid #f5d0fe;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 25px;
    }}
    .ai-content {{
        color: #701a75;
        font-size: 12px;
        line-height: 1.6;
    }}
    .footer {{
        text-align: center;
        margin-top: 30px;
        font-size: 11px;
        color: #94a3b8;
        border-top: 1px solid #e2e8f0;
        padding-top: 15px;
    }}
</style>
</head>
<body>
    <div class="header">
        <div>
            <div class="logo">⚡ SPEND FINANCIAL REPORT</div>
            <div class="subtitle">Personal Expense Tracking & Budget Statement</div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 700; font-size: 14px; color: #0f172a;">Month: {month}</div>
            <div class="subtitle">Generated on {datetime.now().strftime('%d %B %Y')}</div>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-title">Total Spending</div>
            <div class="stat-value text-green">₹{total_spent:,.2f}</div>
            <div class="stat-sub">{count} recorded transactions</div>
        </div>
        {budget_status_html}
        <div class="stat-card">
            <div class="stat-title">Active Categories</div>
            <div class="stat-value">{len(summary.get('by_category', []))}</div>
            <div class="stat-sub">Across {len(summary.get('by_payment_method', []))} payment channels</div>
        </div>
    </div>

    {ai_section_html}

    <div class="two-col">
        <div>
            <h2>Category Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th class="text-right">Spent</th>
                        <th class="text-right">Share</th>
                        <th class="text-center">Count</th>
                    </tr>
                </thead>
                <tbody>
                    {cat_rows if cat_rows else '<tr><td colspan="4" class="text-center text-muted">No category data</td></tr>'}
                </tbody>
            </table>
        </div>
        <div>
            <h2>Payment Channels</h2>
            <table>
                <thead>
                    <tr>
                        <th>Method</th>
                        <th class="text-right">Total Spent</th>
                    </tr>
                </thead>
                <tbody>
                    {pm_rows if pm_rows else '<tr><td colspan="2" class="text-center text-muted">No data</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>

    <h2>Itemized Transactions</h2>
    <table>
        <thead>
            <tr>
                <th class="text-center">ID</th>
                <th>Date</th>
                <th>Category</th>
                <th>Description</th>
                <th>Payment Method</th>
                <th class="text-right">Amount</th>
            </tr>
        </thead>
        <tbody>
            {tx_rows if tx_rows else '<tr><td colspan="6" class="text-center text-muted">No transactions</td></tr>'}
        </tbody>
    </table>

    <div class="footer">
        Generated automatically by SPEND CLI • Keep your finances on track.
    </div>
</body>
</html>
"""
    return html

def export_report_to_pdf(html_content: str, output_pdf_path: Path) -> bool:
    """Uses headless Chrome / Chromium to render clean pixel-perfect PDFs from styled HTML."""
    chrome_bin = "/usr/bin/google-chrome"
    if not os.path.exists(chrome_bin):
        import shutil
        chrome_bin = shutil.which("chromium-browser") or shutil.which("chromium") or shutil.which("google-chrome")
        
    if not chrome_bin:
        raise RuntimeError("No headless Chrome/Chromium browser found on system to compile PDF.")
        
    temp_html = output_pdf_path.with_suffix(".temp.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={output_pdf_path.resolve()}",
        str(temp_html.resolve())
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if temp_html.exists():
            temp_html.unlink()
        return True
    except Exception as e:
        if temp_html.exists():
            temp_html.unlink()
        raise RuntimeError(f"PDF compilation failed: {e}")
