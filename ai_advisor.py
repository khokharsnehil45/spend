"""
SPEND AI Financial Advisor & Analysis Engine.
Supports local offline models via Ollama and cloud API intelligence via Google Gemini.
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console

console = Console()
CONFIG_FILE = Path.home() / ".spend_ai_config.json"

def load_ai_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {
        "provider": "ollama",
        "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
        "gemini_model": "gemini-2.5-flash",
        "ollama_host": "http://localhost:11434",
        "ollama_model": "llama3.2:3b"
    }

def save_ai_config(cfg: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

def get_ollama_models(host: str = "http://localhost:11434") -> List[str]:
    """Fetch installed local models from Ollama."""
    url = f"{host.rstrip('/')}/api/tags"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []

def query_gemini(prompt: str, system_prompt: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
    """Generate financial advice using Google Gemini API."""
    if not api_key:
        raise ValueError("Google Gemini API Key is not configured. Please set your API key in AI Settings.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = json.dumps({
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3}
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        raise RuntimeError(f"Gemini API Error ({e.code}): {err_body}")

def query_ollama(prompt: str, system_prompt: str, host: str = "http://localhost:11434", model: str = "llama3.2:3b") -> str:
    """Generate financial advice locally & offline via Ollama."""
    url = f"{host.rstrip('/')}/api/generate"
    payload = json.dumps({
        "model": model,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Could not connect to Ollama at {host}. Is 'ollama serve' running? Error: {e}")

def run_ai_financial_analysis(transactions: List[Dict[str, Any]], summary: Dict[str, Any], month: str, user_question: Optional[str] = None) -> str:
    """Coordinates analysis prompt generation and model execution."""
    cfg = load_ai_config()
    provider = cfg.get("provider", "ollama")
    
    # Build financial context
    system_prompt = (
        "You are 'SPEND AI', a certified expert personal financial advisor and frugal budget coach. "
        "Your task is to analyze user spending transactions (in Indian Rupees ₹), pinpoint wasteful habits, "
        "provide actionable cost-cutting tips, highlight budget status, and answer questions concisely in clean markdown format. "
        "Keep recommendations practical, empathetic, and structured with bold highlights and bullet points."
    )
    
    # Format transactions snippet
    tx_lines = []
    for t in transactions[:35]: # top 35 records
        desc = f" ({t['description']})" if t['description'] else ""
        tx_lines.append(f"- {t['date']}: ₹{t['amount']:,.2f} | {t['category']} | {t['payment_method']}{desc}")
        
    tx_text = "\n".join(tx_lines) if tx_lines else "No recent transactions logged."
    
    cat_summary = "\n".join([f"- {c['category']}: ₹{c['total']:,.2f} ({c['count']} txns)" for c in summary.get("by_category", [])])
    pm_summary = "\n".join([f"- {p['method']}: ₹{p['total']:,.2f}" for p in summary.get("by_payment_method", [])])
    
    budget_info = f"₹{summary['budget']:,.2f}" if summary.get("budget") else "Not set"
    
    prompt = f"""
### FINANCIAL DATA SUMMARY FOR MONTH: {month}
- Total Spent: ₹{summary['total_amount']:,.2f}
- Transaction Count: {summary['count']}
- Monthly Budget Goal: {budget_info}

### SPENDING BY CATEGORY:
{cat_summary}

### PAYMENT METHODS USED:
{pm_summary}

### RECENT TRANSACTIONS:
{tx_text}

### INSTRUCTIONS:
"""
    if user_question:
        prompt += f"User's Specific Query: '{user_question}'\nPlease answer their question thoroughly using the financial data above."
    else:
        prompt += """Please provide:
1. 💡 **Executive Summary & Spending Health Score** (1-10)
2. ⚠️ **Top Spending Leaks & Anomalies** (Which categories or frequent expenses need attention)
3. 🎯 **Budget & Savings Optimization** (3 concrete steps to cut costs next month)
4. 🔮 **Smart Prediction & Recommendations**
"""

    if provider == "gemini":
        api_key = cfg.get("gemini_api_key") or os.getenv("GEMINI_API_KEY", "")
        model = cfg.get("gemini_model", "gemini-2.5-flash")
        return query_gemini(prompt, system_prompt, api_key, model)
    else:
        host = cfg.get("ollama_host", "http://localhost:11434")
        model = cfg.get("ollama_model", "llama3.2:3b")
        return query_ollama(prompt, system_prompt, host, model)
