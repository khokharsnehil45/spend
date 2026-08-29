```text
███████╗██████╗ ███████╗███╗   ██╗██████╗ 
██╔════╝██╔══██╗██╔════╝████╗  ██║██╔══██╗
███████╗██████╔╝█████╗  ██╔██╗ ██║██║  ██║
╚════██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║  ██║
███████║██║     ███████╗██║ ╚████║██████╔╝
╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ 
  ⚡ Fast, Lightweight & Intuitive Terminal Expense Tracker ⚡
```

<div align="center">

# SPEND — Minimalist Personal Finance & Khata Manager

**Fast, Multi-Account Expense Tracker with an Interactive Retro CLI & Sleek Web GUI**  
*Track daily expenses, monitor budget targets, manage lending/debts (Khata), analyze visual trends, and get AI spending audits.*

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fkhokharsnehil45%2Fspend)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 Overview

**SPEND** is a privacy-first personal expense tracker and lending ledger designed for developers, professionals, and students. It combines a high-speed **Interactive Terminal CLI** (with 2D Unicode ASCII trendlines) and a **Minimalist Dark Web App** (optimized for desktop & mobile viewports).

With **Multi-Account Authentication**, **Lending & Borrowing (Khata)**, **Budget Velocity Tracking**, **Local/Cloud AI Financial Auditing**, and **1-Click PDF/Markdown Statement Exports**, SPEND gives you full control over your finances with zero subscriptions and zero bloat.

---

## 🌐 1-Click Free Cloud Deployment (Vercel)

You can deploy the SPEND Web App online for free in under 60 seconds:

1. Click the **[Deploy with Vercel](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fkhokharsnehil45%2Fspend)** button or import the repository `khokharsnehil45/spend` on your [Vercel Dashboard](https://vercel.com).
2. Click **Deploy**. Vercel will automatically detect `vercel.json` and deploy the serverless Python FastAPI app.
3. Access your live web app from any device at your custom Vercel domain (`https://spend-xxx.vercel.app`)!

---

## ✨ Key Features

### 1. 🔐 Multi-Account & Profile Security
- **Salted SHA-256 Authentication**: Securely switch between multiple accounts (e.g. `Personal`, `Business`, `Travel`).
- **Complete Data Isolation**: Transactions, budgets, debts, and custom categories are strictly partitioned per user ID.
- **Interactive Login Wizard**: Beautiful startup authentication screen in both CLI and Web GUI.

### 2. 🤝 Lending & Borrowing Manager (Khata / Debts)
- 🟢 **Money Lent**: Track money lent to friends, colleagues, or roommates with repayment due dates.
- 🔴 **Money Borrowed**: Monitor debts you owe with outstanding balances.
- 💰 **Partial & Full Repayments**: Record settlements with real-time balance calculations.
- 📋 **Net Position Card**: Live summary cards showing total lent, total borrowed, and net financial standing.

### 3. 📈 Visual Graphs & 2D Trend Curves (CLI & GUI)
- 📈 **2D Continuous Line Chart**: Unicode Braille/ASCII trajectory curves with formatted currency ticks.
- 📊 **Daily Velocity Bar Chart**: Day-by-day spending spikes and velocity (`₹/day`).
- 🗓️ **Month-over-Month History**: Multi-month comparative bar graphs.
- 🍩 **Category Donut Allocation**: Dynamic visual breakdown of budget utilization.

### 4. 🤖 AI Financial Advisor (Local Ollama + Google Gemini)
- 🦙 **100% Offline Local Mode**: Free & private financial audits powered by **Ollama** (e.g. `llama3.2:3b`).
- 🔷 **High-Speed Cloud Mode**: Fast intelligence via **Google Gemini** (`gemini-2.5-flash` / `gemini-1.5-pro`).
- 💡 **Automated Spending Health Audits**: Flags recurring anomalies, recommends cost-cutting strategies, and answers custom questions about your finances.

### 5. 📄 Styled PDF, Markdown & CSV Report Exports
- 📕 **Printable A4 PDF Statement**: Professional financial statements with summary metrics, category tables, payment distribution, and transaction logs.
- 📝 **Markdown Statements (`.md`)**: Formatted for Obsidian, Notion, or GitHub.
- 📊 **Raw CSV Spreadsheet**: Universal compatibility with Excel, Numbers, and Google Sheets.

### 6. 📱 Responsive Minimalist Mobile Viewport
- Symmetrical dashboard cards with fixed mobile bottom navigation bar (`Overview`, `Txns`, `+ Add`, `Khata`, `AI`).
- Touch-friendly controls and smooth Chart.js animations.

---

## 🛠️ Quick Installation & Setup

### 1. Clone and Install Dependencies
```bash
git clone https://github.com/khokharsnehil45/spend.git
cd spend

# Install required Python packages
pip install -r requirements.txt

# Make spend launcher executable and link to PATH
chmod +x spend.py
ln -sf $(pwd)/spend.py ~/.local/bin/spend
```

---

## 💻 Usage Guide

### 1. Launch Terminal CLI
Launch the interactive terminal interface:
```bash
spend
```

**CLI Menu Capabilities:**
- `➕ Add New Expense`: Log purchases with custom categories, dates, and payment methods (UPI, Card, Cash).
- `📜 View & Search Expenses`: Filter by month, category, or keyword, and manage records.
- `📈 Spend Graph & Trends`: Generate 2D continuous line charts and daily bar timelines.
- `📊 Analytics & Dashboard`: Monthly spending breakdown, category tables, and budget gauges.
- `🤖 AI Financial Advisor`: Run local/cloud spending audits.
- `🤝 Lending & Borrowing`: Manage money lent, debts, and settlements.
- `🎯 Set Monthly Budget`: Configure spending limits and track savings goals.
- `📄 Export Reports & Data`: Compile styled PDF statements, Markdown, and CSVs.
- `🔄 Switch User Account`: Log into a different profile.
- `💻 Launch SPEND GUI`: Starts the local web app.

---

### 2. Launch Web GUI Dashboard
Launch the browser dashboard directly:
```bash
spend gui
```
Opens automatically in your browser at: **`http://localhost:8321`**

---

## ⚙️ Configuration & Architecture

- **Local Database**: Stored in `~/.spend_tracker.db` (auto-created on first run).
- **Serverless Database**: Dynamic fallback to `/tmp/spend_tracker.db` when deployed on Vercel.
- **AI Settings**: Configurable inside the CLI (`AI Advisor Settings`) or stored in `~/.spend_ai_config.json`.

---

## 📄 License
Released under the [MIT License](LICENSE). Built for fast, distraction-free personal finance.
