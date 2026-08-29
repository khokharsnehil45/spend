# SPEND - Retro CLI & Cyberpunk GUI Expense Manager

A fast, lightweight personal expense tracker with interactive Terminal CLI and Cyberpunk Web/Desktop Dashboard built with **FastAPI**, **Tailwind CSS**, **Chart.js**, **Rich**, and **Questionary**, matching the aesthetic theme of [HANDY](file:///home/kevin/handy-cli/handy.py).

## ✨ Features

- 💻 **Modern Cyberpunk Web/Desktop Dashboard**:
  - 📈 **Interactive Smooth Charts**: Daily continuous line spending curves and month-over-month bar charts with live hover tooltips.
  - 🍩 **Category Donut Chart**: Dynamic proportional expense distribution ring.
  - ⚡ **Instant Real-Time SQLite Sync**: Add an expense in CLI or GUI and see it reflect immediately across both.
  - 🤝 **Interactive Khata & Loans Ledger**: Log loans lent and debts with partial repayment modals.
  - 🤖 **AI Drawer**: Conversational chat and audits with Ollama or Google Gemini.
  - 📄 **1-Click Downloads**: Direct PDF, Markdown, and CSV statement exports from the browser.
- 🎨 **Retro Gradient Theme**: Dual-tone gradient block typography banner with clean cyan borders and purple/pink highlights.
- 🇮🇳 **Rupee (₹) First**: Formatted in Indian Rupees with UPI/GPay/PhonePe, Net Banking, Card, and Cash payment options.
- 🤝 **Lending & Borrowing (Khata / Debts Manager)**:
  - 🟢 **Money Lent**: Keep track of friends/colleagues who borrowed money from you, principal amount, expected repayment date, and notes.
  - 🔴 **Money Borrowed**: Track debts you owe to others.
  - 💰 **Partial & Full Settlements**: Record repayments with dynamic balance updates.
  - 📋 **Live Ledger**: Summary showing pending money lent, debts owed, and your net balance.
- 📈 **Visual Line Charts & Trend Graphs (CLI & GUI)**:
  - 📈 **2D Continuous Line Chart**: Beautiful Braille/Unicode continuous 2D spending curve with formatted Y-axis Rupee ticks and timeline baseline.
  - 📊 **Daily Timeline Bar Chart**: Displays day-by-day spikes, peak spending days, and daily velocity (`₹/day`).
  - 🗓️ **Month-over-Month Trajectory**: Visual multi-month line & bar trends across the past 12 months.
  - 🍩 **Category Distribution Graph**: Visual ASCII breakdown of budget allocation per category.
- 📄 **Styled PDF & Markdown Financial Reports**:
  - 📕 **Printable A4 PDF**: Generates professional financial statements with statistics cards, category tables, payment distribution, and transaction logs.
  - 📝 **Clean Markdown (`.md`)**: Formatted for Obsidian, Notion, GitHub notes, or archiving.
  - 🤖 **Optional AI Insights Section**: Embeds automated SPEND AI spending audits directly into your exported PDF or Markdown report.
  - 📊 **Raw CSV Export**: For spreadsheets in Excel and Google Sheets.
- 🤖 **AI Financial Advisor (Offline + Cloud)**:
  - 🦙 **Local Offline**: Free & 100% private analysis using **Ollama** (e.g., `llama3.2:3b`).
  - 🔷 **Cloud API**: Ultra-fast high intelligence analysis using **Google Gemini** (`gemini-2.5-flash` / `gemini-1.5-pro`).
  - 💡 Generates **Spending Health Scores**, flags **spending anomalies**, suggests **frugal cost-cutting steps**, or answers custom financial questions.
- 💾 **SQLite Storage**: Persistent zero-configuration local database (`~/.spend_tracker.db`).

## 🚀 How to Launch

### Option 1: Launch GUI Dashboard
Run directly from terminal to open the web dashboard in your browser:

```bash
spend gui
```
Or run with Python:
```bash
python3 /home/kevin/spend/server.py
```
Dashboard opens automatically at `http://localhost:8321`.

---

### Option 2: Launch Terminal CLI
Run standard interactive terminal wizard:

```bash
spend
```
*(Select `💻 Launch SPEND GUI` from the menu or use arrow keys for CLI tools)*
