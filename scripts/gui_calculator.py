import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import calculator as calc

# ---------------- data -----------------
df = pd.read_csv('data/prov_2025.csv')
provs = sorted(df['prov'].unique())

# ------------- helpers -----------------

def income_from_total_tax(paid: float, prov: str, tol: float = 0.01, max_income: float = 1e7) -> float:
    """Binary‑search the income that would generate *paid* tax in *prov*."""
    if paid < 0:
        raise ValueError("Tax paid can’t be negative")
    if paid > calc.calculate_tax(max_income, prov):
        raise ValueError("Amount is above the supported range – increase max_income")

    lo, hi = 0.0, max_income
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        if calc.calculate_tax(mid, prov) < paid:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2.0, 2)

# --------------  UI setup --------------
root = tk.Tk()
root.title("2025 Canada Tax Calculator")
root.geometry("650x320")
root.resizable(False, False)
root.configure(bg="#F7F9FC")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", foreground="#1F2937", background=root["bg"], font=("Arial", 11))
style.configure("TEntry", foreground="#1F2937", fieldbackground="#FFFFFF", font=("Arial", 11))
style.configure("TCombobox", foreground="#1F2937", fieldbackground="#FFFFFF", font=("Arial", 11))
style.configure(
    "TButton", foreground="#FFFFFF", background="#3B82F6", borderwidth=0,
    focusthickness=3, focuscolor="none", padding=(10, 6), font=("Arial", 11, "bold")
)
style.map("TButton", background=[("active", "#2563EB")])
root.option_add("*tearOff", False)

# -------------- shared state --------------
left_income = None       # latest numeric income entered on left pane
est_income = None        # latest numeric income estimated on right pane

def update_rrsp_label():
    """If both incomes are known, suggest an RRSP equal to their difference (min 0)."""
    if left_income is not None and est_income is not None:
        diff = max(0, left_income - est_income)
        rrsp_lbl.config(text=f"Suggested RRSP Contribution: ${diff:,.2f}")

# -------------- variables --------------
# left pane
income_var = tk.StringVar()
prov_var = tk.StringVar(value=provs[0])
# right pane
paid_var = tk.StringVar()
prov_rev_var = tk.StringVar(value=provs[0])

# -------------- layout -----------------
left = tk.Frame(root, bg=root["bg"])
right = tk.Frame(root, bg=root["bg"])
left.grid(row=0, column=0, padx=20, pady=10, sticky="n")
right.grid(row=0, column=1, padx=20, pady=10, sticky="n")

# ---- left: income -> tax ----
tk.Label(left, text="Income:").grid(row=0, column=0, sticky="e")
tk.Entry(left, textvariable=income_var, width=15).grid(row=0, column=1, pady=4)
tk.Label(left, text="Province:").grid(row=1, column=0, sticky="e")
ttk.Combobox(left, textvariable=prov_var, values=provs, state="readonly", width=12).grid(row=1, column=1, pady=4)

prov_tax_lbl = tk.Label(left, text="Provincial Tax: $0.00"); prov_tax_lbl.grid(row=2, column=0, columnspan=2, pady=2)
fed_tax_lbl = tk.Label(left, text="Federal Tax: $0.00"); fed_tax_lbl.grid(row=3, column=0, columnspan=2, pady=2)
total_tax_lbl = tk.Label(left, text="Total Tax: $0.00"); total_tax_lbl.grid(row=4, column=0, columnspan=2, pady=2)
net_income_lbl = tk.Label(left, text="Net Income: $0.00"); net_income_lbl.grid(row=5, column=0, columnspan=2, pady=2)
bracket_lbl = tk.Label(left, text="Provincial Bracket: 0.00%"); bracket_lbl.grid(row=6, column=0, columnspan=2, pady=2)

tk.Button(left, text="Calculate", command=lambda: calc_from_income()).grid(row=7, column=0, columnspan=2, pady=6)

# ---- right: tax -> income ----
tk.Label(right, text="Tax Paid:").grid(row=0, column=0, sticky="e")
tk.Entry(right, textvariable=paid_var, width=15).grid(row=0, column=1, pady=4)
tk.Label(right, text="Province:").grid(row=1, column=0, sticky="e")
ttk.Combobox(right, textvariable=prov_rev_var, values=provs, state="readonly", width=12).grid(row=1, column=1, pady=4)

inc_est_lbl = tk.Label(right, text="Estimated Income: $0.00")
inc_est_lbl.grid(row=2, column=0, columnspan=2, pady=2)
rrsp_lbl = tk.Label(right, text="Suggested RRSP Contribution: $0.00")
rrsp_lbl.grid(row=4, column=0, columnspan=2, pady=2)
tk.Label(right, text="(Maximize tax refund)").grid(row=5, column=0, columnspan=2, pady=2)

tk.Button(right, text="Reverse", command=lambda: calc_from_tax()).grid(row=3, column=0, columnspan=2, pady=6)

# -------------- callbacks --------------

def calc_from_income():
    global left_income
    try:
        inc = float(income_var.get().replace(',', '').replace('$', ''))
        prov = prov_var.get().upper()
        prov_tax = calc.calculate_provincial(inc, prov)
        fed_tax = calc.calculate_federal(inc)
        total_tax = calc.calculate_tax(inc, prov)
        net_inc = inc - total_tax
        bracket = calc.calculate_tax_bracket(inc, prov) * 100
        prov_tax_lbl.config(text=f"Provincial Tax: ${prov_tax:,.2f}")
        fed_tax_lbl.config(text=f"Federal Tax: ${fed_tax:,.2f}")
        total_tax_lbl.config(text=f"Total Tax: ${total_tax:,.2f}")
        net_income_lbl.config(text=f"Net Income: ${net_inc:,.2f}")
        bracket_lbl.config(text=f"Provincial Bracket: {bracket:.2f}%")
        left_income = inc
        update_rrsp_label()
    except ValueError:
        messagebox.showerror("Input Error", "Enter a numeric income amount.")


def calc_from_tax():
    global est_income
    try:
        paid = float(paid_var.get().replace(',', '').replace('$', ''))
        prov = prov_rev_var.get().upper()
        inc = income_from_total_tax(paid, prov)
        inc_est_lbl.config(text=f"Estimated Income: ${inc:,.2f}")
        est_income = inc
        update_rrsp_label()
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# ------------- start loop -------------
root.mainloop()