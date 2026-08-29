#!/usr/bin/env python3
"""
SPEND - Simple Retro-Styled Personal Expense Tracker CLI
Theme inspired by HANDY CLI with dual-tone gradient banners, interactive questionary prompts, and rich reporting.
"""

import os
import sys
import csv
from datetime import datetime
from pathlib import Path

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns

import db

console = Console()

# Theme styling matching handy-cli screenshot
CUSTOM_STYLE = Style([
    ('qmark', 'fg:#00e5ff bold'),
    ('question', 'bold fg:#00e5ff'),
    ('answer', 'fg:#50fa7b bold'),
    ('pointer', 'fg:#ff79c6 bold'),
    ('highlighted', 'fg:#ff79c6 bold'),
    ('selected', 'fg:#50fa7b bold'),
    ('separator', 'fg:#6272a4'),
    ('instruction', 'fg:#8be9fd italic'),
    ('text', 'fg:#f8f8f2'),
])

def render_banner(subtitle: str = "⚡ Fast, Lightweight & Intuitive Terminal Expense Tracker ⚡"):
    """Renders the retro 3D-styled SPEND banner with dual-tone gradient matching the theme."""
    banner_lines = [
        r"███████╗██████╗ ███████╗███╗   ██╗██████╗ ",
        r"██╔════╝██╔══██╗██╔════╝████╗  ██║██╔══██╗",
        r"███████╗██████╔╝█████╗  ██╔██╗ ██║██║  ██║",
        r"╚════██║██╔═══╝ ██╔══╝  ██║╚██╗██║██║  ██║",
        r"███████║██║     ███████╗██║ ╚████║██████╔╝",
        r"╚══════╝╚═╝     ╚══════╝╚═╝  ╚═══╝╚═════╝ "
    ]
    
    banner_text = Text()
    colors = ["#00e5ff", "#00c8ff", "#9d4edd", "#b5179e", "#3a86ff", "#4361ee"]
    
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        banner_text.append(line + "\n", style=f"bold {color}")
        
    banner_text.append(f"  {subtitle}", style="italic bright_white")
    
    console.print(Panel(
        banner_text,
        border_style="cyan",
        subtitle="[bold magenta]v1.0.0 • Personal Finance Suite[/bold magenta]",
        subtitle_align="right",
        padding=(1, 2)
    ))

def print_wizard_box(title: str, subtitle: str):
    content = Text()
    content.append(f"{title}\n", style="bold yellow")
    content.append(f"{subtitle}", style="dim bright_white")
    console.print(Panel(content, border_style="yellow", padding=(0, 1)))

def pause_prompt():
    questionary.press_any_key_to_continue("Press any key to return to the main menu...").ask()

# ==========================================
# EXPENSE ACTIONS
# ==========================================

def action_add_expense():
    console.clear()
    render_banner()
    print_wizard_box("➕ Record New Expense", "Enter details for your transaction.")
    
    # 1. Amount
    amount_str = questionary.text(
        "Enter amount (₹):",
        validate=lambda val: True if (val.replace('.', '', 1).isdigit() and float(val) > 0) else "Please enter a valid positive number",
        style=CUSTOM_STYLE
    ).ask()
    if amount_str is None:
        return
    amount = float(amount_str)
    
    # 2. Category
    categories = db.get_all_categories()
    categories.append("➕ Create new category...")
    category = questionary.select(
        "Select category:",
        choices=categories,
        style=CUSTOM_STYLE
    ).ask()
    if category is None:
        return
        
    if category == "➕ Create new category...":
        new_cat = questionary.text("Enter new category name (e.g. 🎮 Gaming):", style=CUSTOM_STYLE).ask()
        if not new_cat or not new_cat.strip():
            console.print("[red]Invalid category name. Cancelled.[/red]")
            time.sleep(1)
            return
        category = new_cat.strip()
        db.add_category(category)
        
    # 3. Description
    description = questionary.text(
        "Description / Note (optional):",
        style=CUSTOM_STYLE
    ).ask()
    if description is None:
        return
    description = description.strip() if description else "Expense"
    
    # 4. Date
    today_str = datetime.today().strftime('%Y-%m-%d')
    date_choice = questionary.select(
        "Date of expense:",
        choices=[
            f"Today ({today_str})",
            "Custom Date (YYYY-MM-DD)"
        ],
        style=CUSTOM_STYLE
    ).ask()
    if date_choice is None:
        return
        
    if "Today" in date_choice:
        date = today_str
    else:
        date = questionary.text(
            "Enter date (YYYY-MM-DD):",
            default=today_str,
            validate=lambda d: True if len(d) == 10 and d[4] == '-' and d[7] == '-' else "Format must be YYYY-MM-DD",
            style=CUSTOM_STYLE
        ).ask()
        if date is None:
            return

    # 5. Payment Method
    payment_method = questionary.select(
        "Payment Method:",
        choices=["📱 UPI / GPay / PhonePe", "💳 Credit/Debit Card", "💵 Cash", "🏦 Net Banking", "🪙 Other"],
        style=CUSTOM_STYLE
    ).ask()
    if payment_method is None:
        return
        
    exp_id = db.add_expense(amount, category, description, date, payment_method)
    console.print(f"\n[bold green]✓ Expense recorded successfully! (ID: #{exp_id})[/bold green]")
    pause_prompt()

def action_view_expenses():
    console.clear()
    render_banner()
    print_wizard_box("📜 Expense History & Transactions", "Browse, filter, and inspect your records.")
    
    filter_choice = questionary.select(
        "Filter records by:",
        choices=[
            "Recent 20 transactions",
            "All transactions",
            "By Month (e.g. 2026-08)",
            "By Category",
            "Search keyword"
        ],
        style=CUSTOM_STYLE
    ).ask()
    if filter_choice is None:
        return
        
    expenses = []
    if filter_choice == "Recent 20 transactions":
        expenses = db.get_expenses(limit=20)
    elif filter_choice == "All transactions":
        expenses = db.get_expenses()
    elif filter_choice == "By Month (e.g. 2026-08)":
        current_m = datetime.today().strftime('%Y-%m')
        month = questionary.text("Enter month (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
        if month:
            expenses = db.get_expenses(month=month.strip())
    elif filter_choice == "By Category":
        cats = db.get_all_categories()
        cat = questionary.select("Select category:", choices=cats, style=CUSTOM_STYLE).ask()
        if cat:
            expenses = db.get_expenses(category=cat)
    elif filter_choice == "Search keyword":
        kw = questionary.text("Enter search query (note, category, method):", style=CUSTOM_STYLE).ask()
        if kw:
            expenses = db.get_expenses(search=kw.strip())

    if not expenses:
        console.print("\n[yellow]No transactions found matching your criteria.[/yellow]\n")
        pause_prompt()
        return

    table = Table(title="[bold cyan]Transactions[/bold cyan]", border_style="cyan", show_lines=True)
    table.add_column("ID", justify="center", style="dim cyan", width=6)
    table.add_column("Date", justify="center", style="bold white", width=12)
    table.add_column("Category", justify="left", style="magenta", width=22)
    table.add_column("Description", justify="left", style="white")
    table.add_column("Payment Method", justify="center", style="yellow", width=22)
    table.add_column("Amount", justify="right", style="bold green", width=14)

    total = 0.0
    for exp in expenses:
        total += exp["amount"]
        table.add_row(
            f"#{exp['id']}",
            exp["date"],
            exp["category"],
            exp["description"] or "-",
            exp["payment_method"],
            f"₹{exp['amount']:,.2f}"
        )

    console.print(table)
    console.print(f"[bold cyan]Total for listed entries:[/bold cyan] [bold green]₹{total:,.2f}[/bold green] ([magenta]{len(expenses)} items[/magenta])\n")
    
    # Optional delete / manage item
    manage_choice = questionary.select(
        "Manage listed items?",
        choices=["No, return to menu", "🗑️ Delete a transaction"],
        style=CUSTOM_STYLE
    ).ask()
    
    if manage_choice == "🗑️ Delete a transaction":
        del_id = questionary.text("Enter transaction ID to delete (e.g. 5):", style=CUSTOM_STYLE).ask()
        if del_id and del_id.isdigit():
            if db.delete_expense(int(del_id)):
                console.print(f"[bold green]✓ Deleted transaction #{del_id}[/bold green]")
            else:
                console.print(f"[bold red]Transaction #{del_id} not found.[/bold red]")
            pause_prompt()

def render_ascii_bar_chart(title: str, items: list, value_key: str, label_key: str, color: str = "cyan", max_bar_width: int = 35):
    """Renders a beautiful ASCII vertical or horizontal trend chart."""
    if not items:
        console.print("[dim yellow]No data points to render graph.[/dim yellow]\n")
        return
        
    max_val = max([item[value_key] for item in items]) if items else 1
    if max_val == 0:
        max_val = 1
        
    table = Table(title=f"[bold {color}]{title}[/bold {color}]", border_style=color)
    table.add_column("Period / Date", style="bold white", width=14)
    table.add_column("Spending Trend Graph", style=f"{color}", width=max_bar_width + 4)
    table.add_column("Amount", justify="right", style="bold green", width=14)
    table.add_column("Txns", justify="center", style="magenta", width=6)
    
    for item in items:
        val = item[value_key]
        ratio = val / max_val
        bar_len = max(1, int(ratio * max_bar_width)) if val > 0 else 0
        bar = "█" * bar_len + ("▌" if (ratio * max_bar_width - bar_len) > 0.4 else "")
        bar_str = bar.ljust(max_bar_width)
        table.add_row(
            str(item[label_key]),
            f"[{color}]{bar}[/{color}]",
            f"₹{val:,.2f}",
            str(item.get("count", "-"))
        )
    console.print(table)

def render_ascii_line_chart(title: str, series: list, value_key: str, label_key: str, height: int = 10, width: int = 50):
    """Renders a 2D Braille/Unicode line chart with Y-axis currency ticks and timeline labels."""
    if not series or len(series) < 2:
        console.print("[dim yellow]Need at least 2 data points to plot a line chart.[/dim yellow]\n")
        return

    values = [float(s[value_key]) for s in series]
    labels = [str(s[label_key]) for s in series]
    
    min_val = min(values)
    max_val = max(values)
    if min_val == max_val:
        max_val += 1.0
        min_val = max(0.0, min_val - 1.0)
        
    val_range = max_val - min_val
    n_points = len(values)
    
    # Resample or interpolate values to fit graph width
    grid_w = min(width, max(20, n_points * 2))
    sampled_vals = []
    for x in range(grid_w):
        idx = int((x / (grid_w - 1)) * (n_points - 1))
        sampled_vals.append(values[idx])
        
    # Build 2D char canvas
    canvas = [[" " for _ in range(grid_w)] for _ in range(height)]
    
    prev_y = None
    for x, val in enumerate(sampled_vals):
        normalized = (val - min_val) / val_range
        y = int(normalized * (height - 1))
        y = max(0, min(height - 1, y))
        plot_y = (height - 1) - y
        
        # Connect dots
        if prev_y is not None:
            step = 1 if plot_y > prev_y else -1
            for mid_y in range(prev_y, plot_y, step):
                if canvas[mid_y][x] == " ":
                    canvas[mid_y][x] = "│" if abs(plot_y - prev_y) > 1 else ("╱" if step == -1 else "╲")
                    
        canvas[plot_y][x] = "●"
        prev_y = plot_y

    # Render Frame with Y-Axis Values
    lines = []
    lines.append(f"[bold cyan]📈 {title}[/bold cyan]\n")
    for r in range(height):
        frac = ((height - 1 - r) / (height - 1))
        y_val = min_val + frac * val_range
        axis_label = f"₹{y_val:>8,.0f} ┤"
        row_str = "".join(canvas[r])
        # Colorize graph curve in cyan/magenta gradient
        colored_row = ""
        for char in row_str:
            if char == "●":
                colored_row += "[bold magenta]●[/bold magenta]"
            elif char in "│╱╲":
                colored_row += "[cyan]" + char + "[/cyan]"
            else:
                colored_row += " "
        lines.append(f"[dim]{axis_label}[/dim] {colored_row}")
        
    # X-Axis base line
    lines.append(" " * 10 + "└" + "─" * grid_w)
    
    # X-Axis Start and End dates
    start_lbl = labels[0]
    end_lbl = labels[-1]
    space_gap = grid_w - len(start_lbl) - len(end_lbl)
    if space_gap > 0:
        lines.append(" " * 11 + f"[dim white]{start_lbl}[/dim white]" + " " * space_gap + f"[dim white]{end_lbl}[/dim white]\n")
    else:
        lines.append(" " * 11 + f"[dim white]{start_lbl} ... {end_lbl}[/dim white]\n")

    console.print(Panel("\n".join(lines), border_style="cyan", padding=(1, 2)))

def action_visual_charts():
    console.clear()
    render_banner()
    print_wizard_box("📈 Spend Graph & Visual Trends", "Interactive Line Charts, Timeline Bar Graphs & Multi-month History.")
    
    chart_type = questionary.select(
        "Select Chart to Visualize:",
        choices=[
            "📈 Daily Spending Line Chart (Continuous 2D Curve Timeline)",
            "📊 Daily Spending Bar Graph (Day-by-Day Bars with Peak Day)",
            "🗓️  Month-over-Month Trend (Past 6-12 Months Comparison)",
            "🍩 Category Spending Distribution Chart",
            "🔙 Back to Main Menu"
        ],
        style=CUSTOM_STYLE
    ).ask()
    
    if chart_type is None or "Back" in chart_type:
        return
        
    if "Line Chart" in chart_type:
        current_m = datetime.today().strftime('%Y-%m')
        month = questionary.text("Enter month for Line Chart (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
        if not month:
            return
        month = month.strip()
        daily_data = db.get_daily_spending(month)
        if not daily_data or len(daily_data) < 2:
            console.print(f"\n[yellow]Need at least 2 distinct days of spending in {month} to plot line chart.[/yellow]\n")
        else:
            console.print("\n")
            render_ascii_line_chart(f"Daily Spending Curve for {month}", daily_data, value_key="total", label_key="date", height=10, width=50)
            
            total = sum(d["total"] for d in daily_data)
            avg = total / len(daily_data)
            peak = max(daily_data, key=lambda x: x["total"])
            console.print(f"  🔥 [bold cyan]Peak Spending Day:[/bold cyan] [yellow]{peak['date']}[/yellow] ([bold green]₹{peak['total']:,.2f}[/bold green])")
            console.print(f"  📊 [bold cyan]Daily Average:[/bold cyan] [bold green]₹{avg:,.2f}/day[/bold green] across [magenta]{len(daily_data)} active days[/magenta]\n")
            
    elif "Bar Graph" in chart_type:
        current_m = datetime.today().strftime('%Y-%m')
        month = questionary.text("Enter month (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
        if not month:
            return
        month = month.strip()
        daily_data = db.get_daily_spending(month)
        if not daily_data:
            console.print(f"\n[yellow]No expenses logged in {month} to plot graph.[/yellow]\n")
        else:
            console.print("\n")
            render_ascii_bar_chart(f"📊 Daily Spending Graph for {month}", daily_data, value_key="total", label_key="date", color="cyan", max_bar_width=35)
            
            total = sum(d["total"] for d in daily_data)
            avg = total / len(daily_data) if daily_data else 0
            peak = max(daily_data, key=lambda x: x["total"])
            console.print(f"  🔥 [bold cyan]Peak Spending Day:[/bold cyan] [yellow]{peak['date']}[/yellow] ([bold green]₹{peak['total']:,.2f}[/bold green])")
            console.print(f"  📊 [bold cyan]Active Day Average:[/bold cyan] [bold green]₹{avg:,.2f}/day[/bold green] | [magenta]{len(daily_data)} active days[/magenta]\n")
            
    elif "Month-over-Month" in chart_type:
        history = db.get_monthly_history(limit=12)
        if not history:
            console.print("\n[yellow]No historical monthly data recorded yet.[/yellow]\n")
        else:
            console.print("\n")
            if len(history) >= 2:
                render_ascii_line_chart("Monthly Spending Trajectory (12 Months)", history, value_key="total", label_key="month", height=8, width=45)
            render_ascii_bar_chart("🗓️ Monthly Spending History", history, value_key="total", label_key="month", color="magenta", max_bar_width=35)
            total_all = sum(h["total"] for h in history)
            console.print(f"  💰 [bold magenta]Total Historical Spending:[/bold magenta] [bold green]₹{total_all:,.2f}[/bold green]\n")
            
    elif "Category Spending" in chart_type:
        current_m = datetime.today().strftime('%Y-%m')
        month = questionary.text("Enter month (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
        if not month:
            return
        summary = db.get_summary(month=month.strip())
        cats = summary.get("by_category", [])
        if not cats:
            console.print(f"\n[yellow]No categorized expenses in {month}.[/yellow]\n")
        else:
            console.print("\n")
            render_ascii_bar_chart(f"🍩 Category Spending Graph ({month})", cats, value_key="total", label_key="category", color="green", max_bar_width=30)
            
    pause_prompt()

def action_analytics_dashboard():
    console.clear()
    render_banner()
    print_wizard_box("📊 Analytics & Monthly Breakdown", "Review your spending distribution, categories, and budget.")
    
    current_m = datetime.today().strftime('%Y-%m')
    month = questionary.text("Enter month for analytics (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
    if month is None:
        return
    month = month.strip()
    
    summary = db.get_summary(month=month)
    total_spent = summary["total_amount"]
    budget = summary["budget"]
    
    # 1. Monthly Overview Panel
    overview_text = Text()
    overview_text.append(f"Month: ", style="bold")
    overview_text.append(f"{month}\n", style="cyan bold")
    overview_text.append(f"Total Transactions: ", style="bold")
    overview_text.append(f"{summary['count']}\n", style="magenta bold")
    overview_text.append(f"Total Spent: ", style="bold")
    overview_text.append(f"₹{total_spent:,.2f}\n", style="bold green")
    
    if budget:
        remaining = budget - total_spent
        pct = (total_spent / budget) * 100 if budget > 0 else 0
        overview_text.append(f"Monthly Budget: ", style="bold")
        overview_text.append(f"₹{budget:,.2f}\n", style="bold yellow")
        overview_text.append(f"Budget Status: ", style="bold")
        if remaining >= 0:
            overview_text.append(f"₹{remaining:,.2f} remaining ({pct:.1f}% used)", style="bold green")
        else:
            overview_text.append(f"₹{abs(remaining):,.2f} OVER BUDGET! ({pct:.1f}% used)", style="bold red")
    else:
        overview_text.append(f"Monthly Budget: ", style="bold")
        overview_text.append(f"Not set (Set via Budget Menu)", style="dim italic")

    console.print(Panel(overview_text, title=f"[bold cyan]📈 Overview for {month}[/bold cyan]", border_style="cyan", padding=(1, 2)))
    
    # 2. Category Breakdown Table with visual bar
    if summary["by_category"]:
        cat_table = Table(title=f"[bold magenta]Category Breakdown ({month})[/bold magenta]", border_style="magenta")
        cat_table.add_column("Category", style="cyan bold", width=25)
        cat_table.add_column("Spent", justify="right", style="green bold", width=14)
        cat_table.add_column("Share", justify="right", style="yellow", width=8)
        cat_table.add_column("Distribution Bar", style="magenta", width=25)
        
        for item in summary["by_category"]:
            share_pct = (item["total"] / total_spent * 100) if total_spent > 0 else 0
            bar_len = int(share_pct / 4) # up to 25 chars
            bar = "█" * bar_len + "░" * (25 - bar_len)
            cat_table.add_row(
                item["category"],
                f"₹{item['total']:,.2f}",
                f"{share_pct:.1f}%",
                bar
            )
        console.print(cat_table)
    else:
        console.print("[dim yellow]No category expenses recorded this month.[/dim yellow]\n")

    # 3. Payment Method Breakdown
    if summary["by_payment_method"]:
        pm_table = Table(title=f"[bold yellow]Payment Methods ({month})[/bold yellow]", border_style="yellow")
        pm_table.add_column("Method", style="bold white", width=25)
        pm_table.add_column("Total Spent", justify="right", style="bold green", width=16)
        for pm in summary["by_payment_method"]:
            pm_table.add_row(pm["method"], f"₹{pm['total']:,.2f}")
        console.print(pm_table)

    pause_prompt()

def action_set_budget():
    console.clear()
    render_banner()
    print_wizard_box("🎯 Monthly Budget Target", "Define spending limits to stay on top of your financial goals.")
    
    current_m = datetime.today().strftime('%Y-%m')
    month = questionary.text("Enter month (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
    if month is None:
        return
    month = month.strip()
    
    current_summary = db.get_summary(month=month)
    curr_b = current_summary["budget"]
    curr_b_str = f" (Current: ₹{curr_b:,.2f})" if curr_b else " (Currently not set)"
    
    b_val_str = questionary.text(
        f"Enter monthly budget goal (₹){curr_b_str}:",
        validate=lambda val: True if (val.replace('.', '', 1).isdigit() and float(val) > 0) else "Please enter a valid positive number",
        style=CUSTOM_STYLE
    ).ask()
    if b_val_str is None:
        return
        
    db.set_budget(month, float(b_val_str))
    console.print(f"\n[bold green]✓ Budget for {month} updated to ₹{float(b_val_str):,.2f}[/bold green]\n")
    pause_prompt()

import report_gen

def action_export_reports():
    console.clear()
    render_banner()
    print_wizard_box("📄 Export Financial Reports & Data", "Generate styled PDF statements, Markdown reports, or raw CSV spreadsheets.")
    
    export_format = questionary.select(
        "Choose Export Format:",
        choices=[
            "📕 Styled PDF Financial Statement (Printable A4 with Summary & Charts)",
            "📝 Markdown Report (.md - Ideal for Obsidian, Notion, GitHub)",
            "📊 Raw CSV Spreadsheet (.csv - Excel & Sheets compatible)",
            "🔙 Back to Main Menu"
        ],
        style=CUSTOM_STYLE
    ).ask()
    
    if export_format is None or "Back" in export_format:
        return
        
    current_m = datetime.today().strftime('%Y-%m')
    
    # 1. PDF Export
    if "PDF" in export_format:
        month = questionary.text("Enter month for PDF report (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
        if not month:
            return
        month = month.strip()
        
        include_ai_choice = questionary.confirm("Include SPEND AI Insights in this report?", default=False, style=CUSTOM_STYLE).ask()
        ai_text = None
        if include_ai_choice:
            with console.status("[bold cyan]Generating AI analysis for PDF report...[/bold cyan]", spinner="dots"):
                try:
                    ai_text = ai_advisor.run_ai_financial_analysis(db.get_expenses(month=month), db.get_summary(month=month), month)
                except Exception as e:
                    console.print(f"[yellow]Could not generate AI section ({e}), generating report without AI.[/yellow]")
                    
        default_pdf_name = f"spend_report_{month}.pdf"
        out_path_str = questionary.text("Output PDF path:", default=default_pdf_name, style=CUSTOM_STYLE).ask()
        if not out_path_str:
            return
        pdf_path = Path(out_path_str.strip()).expanduser()
        
        with console.status(f"[bold cyan]Compiling styled PDF for {month}...[/bold cyan]", spinner="dots"):
            try:
                html_code = report_gen.generate_styled_html_report(month, include_ai=include_ai_choice, ai_summary_text=ai_text)
                report_gen.export_report_to_pdf(html_code, pdf_path)
                console.print(f"\n[bold green]✓ Successfully exported PDF report to:[/bold green] [bold cyan]{pdf_path.resolve()}[/bold cyan]\n")
            except Exception as err:
                console.print(f"\n[bold red]❌ PDF Export Error:[/bold red] {err}\n")
        pause_prompt()

    # 2. Markdown Export
    elif "Markdown" in export_format:
        month = questionary.text("Enter month for Markdown report (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
        if not month:
            return
        month = month.strip()
        
        include_ai_choice = questionary.confirm("Include SPEND AI Insights in this Markdown report?", default=False, style=CUSTOM_STYLE).ask()
        ai_text = None
        if include_ai_choice:
            with console.status("[bold cyan]Generating AI analysis for Markdown report...[/bold cyan]", spinner="dots"):
                try:
                    ai_text = ai_advisor.run_ai_financial_analysis(db.get_expenses(month=month), db.get_summary(month=month), month)
                except Exception as e:
                    console.print(f"[yellow]Could not generate AI section ({e}).[/yellow]")
                    
        default_md_name = f"spend_report_{month}.md"
        out_path_str = questionary.text("Output Markdown path:", default=default_md_name, style=CUSTOM_STYLE).ask()
        if not out_path_str:
            return
        md_path = Path(out_path_str.strip()).expanduser()
        
        try:
            md_content = report_gen.generate_markdown_report(month, include_ai=include_ai_choice, ai_summary_text=ai_text)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            console.print(f"\n[bold green]✓ Successfully exported Markdown report to:[/bold green] [bold cyan]{md_path.resolve()}[/bold cyan]\n")
        except Exception as err:
            console.print(f"\n[bold red]❌ Markdown Export Error:[/bold red] {err}\n")
        pause_prompt()

    # 3. CSV Export
    elif "CSV" in export_format:
        expenses = db.get_expenses()
        if not expenses:
            console.print("[yellow]No expenses found to export.[/yellow]")
            pause_prompt()
            return
            
        default_filename = f"spend_export_{datetime.today().strftime('%Y%m%d_%H%M%S')}.csv"
        filename = questionary.text(
            "Enter output CSV path/filename:",
            default=default_filename,
            style=CUSTOM_STYLE
        ).ask()
        if filename is None:
            return
            
        filepath = Path(filename.strip()).expanduser()
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Category", "Amount", "Description", "Payment Method", "Created At"])
                for e in expenses:
                    writer.writerow([e["id"], e["date"], e["category"], e["amount"], e["description"], e["payment_method"], e["created_at"]])
            console.print(f"\n[bold green]✓ Successfully exported {len(expenses)} expenses to:[/bold green] [bold cyan]{filepath.resolve()}[/bold cyan]\n")
        except Exception as err:
            console.print(f"[bold red]Error saving CSV: {err}[/bold red]")
            
        pause_prompt()

def action_manage_loans():
    console.clear()
    render_banner()
    summary = db.get_loans_summary()
    print_wizard_box(
        "🤝 Lending & Borrowing (Khata / Debts)",
        f"Lent to Others: ₹{summary['lent_pending']:,.2f}  |  You Borrowed: ₹{summary['borrowed_pending']:,.2f}  |  Net: ₹{summary['net_balance']:,.2f}"
    )
    
    action = questionary.select(
        "Select Lending/Debt Action:",
        choices=[
            "➕ Record New Loan (Lent Money to Someone)",
            "📥 Record Borrowed Money (Money You Owe)",
            "📋 View Active / Pending Debts & Loans",
            "💰 Settle / Record Repayment on a Loan",
            "📜 Full Loan History & Archive",
            "🔙 Back to Main Menu"
        ],
        style=CUSTOM_STYLE
    ).ask()
    
    if action is None or "Back" in action:
        return
        
    if "Record New Loan" in action or "Record Borrowed" in action:
        loan_type = "lent" if "Record New Loan" in action else "borrowed"
        role_label = "Person who borrowed from you:" if loan_type == "lent" else "Person you borrowed from:"
        
        person = questionary.text(role_label, style=CUSTOM_STYLE).ask()
        if not person or not person.strip():
            return
            
        amount_str = questionary.text(
            "Amount (₹):",
            validate=lambda v: True if (v.replace('.', '', 1).isdigit() and float(v) > 0) else "Enter a valid positive number",
            style=CUSTOM_STYLE
        ).ask()
        if not amount_str:
            return
        amount = float(amount_str)
        
        due_date = questionary.text("Expected Repayment Date (YYYY-MM-DD, optional):", style=CUSTOM_STYLE).ask()
        due_date = due_date.strip() if due_date and due_date.strip() else None
        
        notes = questionary.text("Notes / Reason (e.g. Lunch split, emergency loan):", style=CUSTOM_STYLE).ask()
        notes = notes.strip() if notes and notes.strip() else None
        
        loan_id = db.add_loan(loan_type, person.strip(), amount, due_date, notes)
        type_str = "Lent to" if loan_type == "lent" else "Borrowed from"
        console.print(f"\n[bold green]✓ Recorded: {type_str} {person.strip()} (₹{amount:,.2f}) — ID: #{loan_id}[/bold green]\n")
        pause_prompt()
        
    elif "View Active" in action or "Full Loan History" in action:
        status_filter = "all" if "Full Loan History" in action else "pending"
        loans = db.get_loans(status_filter=None if status_filter == "all" else "pending")
        
        if not loans:
            console.print("\n[yellow]No records found matching criteria.[/yellow]\n")
            pause_prompt()
            return
            
        table = Table(title="[bold cyan]Lending & Borrowing Ledger[/bold cyan]", border_style="cyan", show_lines=True)
        table.add_column("ID", justify="center", style="dim cyan", width=5)
        table.add_column("Type", justify="center", width=12)
        table.add_column("Person", style="bold white", width=18)
        table.add_column("Principal", justify="right", style="bold yellow", width=12)
        table.add_column("Settled", justify="right", style="green", width=12)
        table.add_column("Remaining", justify="right", style="bold red", width=12)
        table.add_column("Due Date", justify="center", style="dim white", width=12)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Notes", style="dim cyan")
        
        for l in loans:
            rem = max(0.0, l["amount"] - (l["settled_amount"] or 0.0))
            if l["type"] == "lent":
                type_tag = "[green]LENT (Owed)[/green]"
                rem_color = "green"
            else:
                type_tag = "[red]BORROWED[/red]"
                rem_color = "red"
                
            status_style = "green" if l["status"] == "settled" else ("yellow" if l["status"] == "partial" else "red")
            table.add_row(
                f"#{l['id']}",
                type_tag,
                l["person"],
                f"₹{l['amount']:,.2f}",
                f"₹{l['settled_amount'] or 0.0:,.2f}",
                f"[{rem_color}]₹{rem:,.2f}[/{rem_color}]",
                l["due_date"] or "-",
                f"[{status_style}]{l['status'].upper()}[/{status_style}]",
                l["notes"] or "-"
            )
        console.print(table)
        pause_prompt()
        
    elif "Settle / Record Repayment" in action:
        active_loans = [l for l in db.get_loans() if l["status"] != "settled"]
        if not active_loans:
            console.print("\n[green]No outstanding loans or debts to settle! All caught up.[/green]\n")
            pause_prompt()
            return
            
        choices = []
        for l in active_loans:
            rem = max(0.0, l["amount"] - (l["settled_amount"] or 0.0))
            prefix = "🟢 Lent to" if l["type"] == "lent" else "🔴 Borrowed from"
            choices.append(questionary.Choice(
                f"#{l['id']} - {prefix} {l['person']} | Remaining: ₹{rem:,.2f}",
                value=l["id"]
            ))
        choices.append(questionary.Choice("🔙 Cancel", value=None))
        
        selected_id = questionary.select("Select record to settle/repay:", choices=choices, style=CUSTOM_STYLE).ask()
        if not selected_id:
            return
            
        target = next((l for l in active_loans if l["id"] == selected_id), None)
        rem = max(0.0, target["amount"] - (target["settled_amount"] or 0.0))
        
        settle_amt_str = questionary.text(
            f"Enter repayment amount (Remaining: ₹{rem:,.2f}):",
            default=str(rem),
            validate=lambda v: True if (v.replace('.', '', 1).isdigit() and float(v) > 0) else "Enter a valid positive number",
            style=CUSTOM_STYLE
        ).ask()
        if not settle_amt_str:
            return
            
        settle_amt = float(settle_amt_str)
        res = db.settle_loan(selected_id, settle_amt)
        if res["success"]:
            console.print(f"\n[bold green]✓ Recorded repayment of ₹{settle_amt:,.2f}![/bold green]")
            if res["status"] == "settled":
                console.print(f"[bold cyan]🎉 This debt is now fully SETTLED![/bold cyan]\n")
            else:
                console.print(f"[yellow]Status: PARTIAL. Remaining balance: ₹{res['remaining']:,.2f}[/yellow]\n")
        else:
            console.print(f"[red]{res['msg']}[/red]")
        pause_prompt()

def action_manage_categories():
    console.clear()
    render_banner()
    print_wizard_box("🏷️  Category Manager", "View and register customized spending categories.")
    
    cats = db.get_all_categories()
    table = Table(title="[bold cyan]Available Categories[/bold cyan]", border_style="cyan")
    table.add_column("#", justify="center", style="dim cyan", width=4)
    table.add_column("Category Name", style="magenta bold")
    for i, cat in enumerate(cats, 1):
        table.add_row(str(i), cat)
    console.print(table)
    
    action = questionary.select(
        "Action:",
        choices=["➕ Add New Category", "🔙 Return to Main Menu"],
        style=CUSTOM_STYLE
    ).ask()
    
    if action == "➕ Add New Category":
        new_name = questionary.text("Enter category name (e.g. ✈️ Travel):", style=CUSTOM_STYLE).ask()
        if new_name and new_name.strip():
            if db.add_category(new_name.strip()):
                console.print(f"[bold green]✓ Category '{new_name.strip()}' created![/bold green]")
            else:
                console.print("[bold red]Category already exists.[/bold red]")
            pause_prompt()

from rich.markdown import Markdown
from rich.status import Status
import ai_advisor

def action_ai_analysis():
    console.clear()
    render_banner()
    cfg = ai_advisor.load_ai_config()
    provider_name = "🔷 Google Gemini API" if cfg.get("provider") == "gemini" else f"🦙 Local Ollama ({cfg.get('ollama_model', 'llama3.2:3b')})"
    print_wizard_box("🤖 SPEND AI Financial Advisor", f"Intelligent Spending Health Check & Budget Optimization via {provider_name}")
    
    current_m = datetime.today().strftime('%Y-%m')
    month = questionary.text("Enter month to analyze (YYYY-MM):", default=current_m, style=CUSTOM_STYLE).ask()
    if month is None:
        return
    month = month.strip()
    
    expenses = db.get_expenses(month=month)
    summary = db.get_summary(month=month)
    
    if not expenses:
        console.print(f"\n[yellow]No transactions found for {month} to analyze. Try logging some expenses first![/yellow]\n")
        pause_prompt()
        return

    query_type = questionary.select(
        "Analysis Mode:",
        choices=[
            "💡 Full Financial Health Audit & Cost Reduction Plan",
            "💬 Ask a Custom Question about your spending"
        ],
        style=CUSTOM_STYLE
    ).ask()
    if query_type is None:
        return
        
    user_q = None
    if "Custom Question" in query_type:
        user_q = questionary.text("Enter your question for SPEND AI:", style=CUSTOM_STYLE).ask()
        if not user_q:
            return
            
    with console.status(f"[bold cyan]🧠 SPEND AI is evaluating your {month} finances with {provider_name}...[/bold cyan]", spinner="dots"):
        try:
            report = ai_advisor.run_ai_financial_analysis(expenses, summary, month, user_q)
        except Exception as e:
            console.print(f"\n[bold red]❌ AI Analysis Failed:[/bold red] {e}\n")
            if cfg.get("provider") == "gemini" and not cfg.get("gemini_api_key"):
                console.print("[dim yellow]Hint: Configure your Gemini API key in 'AI Advisor Settings'.[/dim yellow]")
            elif cfg.get("provider") == "ollama":
                console.print("[dim yellow]Hint: Ensure Ollama is running (`ollama serve`) and the model is pulled.[/dim yellow]")
            pause_prompt()
            return
            
    console.print("\n")
    console.print(Panel(
        Markdown(report),
        title=f"[bold magenta]✨ SPEND AI Advisory Report ({month})[/bold magenta]",
        border_style="magenta",
        padding=(1, 2)
    ))
    console.print("\n")
    pause_prompt()

def action_ai_settings():
    console.clear()
    render_banner()
    print_wizard_box("⚙️  AI Advisor Settings", "Switch between Local Offline Ollama and Cloud Gemini API.")
    
    cfg = ai_advisor.load_ai_config()
    current_p = cfg.get("provider", "ollama")
    
    provider_choice = questionary.select(
        f"Active AI Engine (Current: {current_p.upper()}):",
        choices=[
            questionary.Choice("🦙 Local Offline (Ollama - Private & Free)", value="ollama"),
            questionary.Choice("🔷 Google Gemini API (High-speed Cloud intelligence)", value="gemini"),
            questionary.Choice("🔙 Back to Main Menu", value="back")
        ],
        style=CUSTOM_STYLE
    ).ask()
    
    if provider_choice is None or provider_choice == "back":
        return
        
    if provider_choice == "ollama":
        cfg["provider"] = "ollama"
        host = questionary.text("Ollama Host URL:", default=cfg.get("ollama_host", "http://localhost:11434"), style=CUSTOM_STYLE).ask()
        if host:
            cfg["ollama_host"] = host.strip()
            
        models = ai_advisor.get_ollama_models(cfg["ollama_host"])
        if models:
            m_choice = questionary.select("Select installed Ollama Model:", choices=models, default=cfg.get("ollama_model", models[0]), style=CUSTOM_STYLE).ask()
            if m_choice:
                cfg["ollama_model"] = m_choice
        else:
            m_manual = questionary.text("Enter Ollama model name:", default=cfg.get("ollama_model", "llama3.2:3b"), style=CUSTOM_STYLE).ask()
            if m_manual:
                cfg["ollama_model"] = m_manual.strip()
                
    elif provider_choice == "gemini":
        cfg["provider"] = "gemini"
        current_k = cfg.get("gemini_api_key", "")
        masked_k = f"***...{current_k[-4:]}" if len(current_k) > 4 else "(Not set)"
        k = questionary.text(f"Google Gemini API Key [Current: {masked_k}]:", default=current_k, style=CUSTOM_STYLE).ask()
        if k:
            cfg["gemini_api_key"] = k.strip()
            
        model = questionary.select(
            "Select Gemini Model:",
            choices=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
            default=cfg.get("gemini_model", "gemini-2.5-flash"),
            style=CUSTOM_STYLE
        ).ask()
        if model:
            cfg["gemini_model"] = model
            
    ai_advisor.save_ai_config(cfg)
    console.print(f"\n[bold green]✓ AI configuration saved successfully![/bold green]\n")
    pause_prompt()

# ==========================================
# MAIN INTERACTIVE LOOP
# ==========================================
def main():
    db.init_db()
    
    while True:
        console.clear()
        render_banner()
        print_wizard_box(
            "💰 SPEND Interactive Financial Manager",
            "Track daily expenses, monitor budget targets, analyze categories, and get AI insights."
        )
        
        choice = questionary.select(
            "Select an action to launch: (Use arrow keys)",
            choices=[
                questionary.Choice("➕  Add New Expense        — Record a purchase, bill, or daily transaction", value="add"),
                questionary.Choice("📜  View & Search Expenses — Filter transaction history, inspect and delete", value="view"),
                questionary.Choice("📈  Spend Graph & Trends   — Daily timelines, month-over-month visual charts", value="graphs"),
                questionary.Choice("📊  Analytics & Dashboard  — Monthly spending summaries, category breakdown", value="analytics"),
                questionary.Choice("🤖  AI Financial Advisor   — Smart spending audits & cost reduction (Ollama/Gemini)", value="ai"),
                questionary.Choice("🤝  Lending & Borrowing    — Track money lent to friends & debts owed", value="loans"),
                questionary.Choice("🎯  Set Monthly Budget     — Configure spending limits and track savings goals", value="budget"),
                questionary.Choice("🏷️   Manage Categories      — Browse and create custom spending tags", value="categories"),
                questionary.Choice("⚙️   AI Advisor Settings    — Configure Ollama host / Gemini API key", value="ai_settings"),
                questionary.Choice("📄  Export Reports & Data  — Generate PDF statements, Markdown & CSVs", value="export"),
                questionary.Separator(),
                questionary.Choice("🚪  Exit SPEND", value="exit")
            ],
            style=CUSTOM_STYLE
        ).ask()
        
        if choice is None or choice == "exit":
            console.print("\n[bold magenta]Thank you for using SPEND! Have a great day! 👋[/bold magenta]\n")
            sys.exit(0)
        elif choice == "add":
            action_add_expense()
        elif choice == "view":
            action_view_expenses()
        elif choice == "graphs":
            action_visual_charts()
        elif choice == "analytics":
            action_analytics_dashboard()
        elif choice == "ai":
            action_ai_analysis()
        elif choice == "loans":
            action_manage_loans()
        elif choice == "budget":
            action_set_budget()
        elif choice == "categories":
            action_manage_categories()
        elif choice == "ai_settings":
            action_ai_settings()
        elif choice == "export":
            action_export_reports()

if __name__ == "__main__":
    main()
