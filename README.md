# SPEND - Retro CLI Expense Tracker, Line Charts & Khata Debt Manager

A lightweight, retro-styled interactive expense tracker for your terminal built with **Rich** and **Questionary**, matching the aesthetic theme of [HANDY](file:///home/kevin/handy-cli/handy.py).

## ✨ Features

- 🎨 **Retro Gradient Theme**: Dual-tone gradient block typography banner with clean cyan borders and purple/pink highlights.
- 🇮🇳 **Rupee (₹) First**: Formatted in Indian Rupees with UPI/GPay/PhonePe, Net Banking, Card, and Cash payment options.
- 📈 **Visual Line Charts & Trend Graphs**:
  - 📈 **2D Continuous Line Chart**: Beautiful Braille/Unicode continuous 2D spending curve with formatted Y-axis Rupee ticks and timeline baseline.
  - 📊 **Daily Timeline Bar Chart**: Displays day-by-day spikes, peak spending days, and daily velocity (`₹/day`).
  - 🗓️ **Month-over-Month Trajectory**: Visual multi-month line & bar trends across the past 12 months.
  - 🍩 **Category Distribution Graph**: Visual ASCII breakdown of budget allocation per category.
- 🤝 **Lending & Borrowing (Khata / Debts Manager)**:
  - 🟢 **Money Lent**: Keep track of friends/colleagues who borrowed money from you, principal amount, expected repayment date, and notes.
  - 🔴 **Money Borrowed**: Track debts you owe to others.
  - 💰 **Partial & Full Settlements**: Record repayments with dynamic balance updates.
  - 📋 **Live Ledger**: Summary showing pending money lent, debts owed, and your net balance.
- 📄 **Styled PDF & Markdown Financial Reports**:
  - 📕 **Printable A4 PDF**: Generates professional financial statements with statistics cards, category tables, payment distribution, and transaction logs.
  - 📝 **Clean Markdown (`.md`)**: Formatted for Obsidian, Notion, GitHub notes, or archiving.
  - 🤖 **Optional AI Insights Section**: Embeds automated SPEND AI spending audits directly into your exported PDF or Markdown report.
  - 📊 **Raw CSV Export**: For spreadsheets in Excel and Google Sheets.
- 🤖 **AI Financial Advisor (Offline + Cloud)**:
  - 🦙 **Local Offline**: Free & 100% private analysis using **Ollama** (e.g., `llama3.2:3b`).
  - 🔷 **Cloud API**: Ultra-fast high intelligence analysis using **Google Gemini** (`gemini-2.5-flash` / `gemini-1.5-pro`).
  - 💡 Generates **Spending Health Scores**, flags **spending anomalies**, suggests **frugal cost-cutting steps**, or answers custom financial questions.
- ➕ **Fast Expense Entry**: Interactive wizard to quickly log amount, category, note, custom/today's date, and payment method.
- 📜 **Transaction History & Search**: View transactions with search, month filter, category filter, and deletion.
- 🎯 **Monthly Budget Tracking**: Configure spending limit goals per month and monitor budget progress/overages.
- 🏷️ **Custom Categories**: Browse and define personalized expense categories.
- 💾 **SQLite Storage**: Persistent zero-configuration local database (`~/.spend_tracker.db`).

## 🚀 Quick Start

Run anytime from your terminal:

```bash
spend
```

Or run directly with Python:
```bash
python3 /home/kevin/spend/spend.py
```
