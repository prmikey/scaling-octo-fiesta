"""TopstepX-tailored ATM helper GUI.

This version of the ATM sizing tool mirrors the base CME calculator but
layers in TopstepX-specific risk guardrails:

* Pre-loaded account configurations with published daily loss limits and
  trailing drawdown values.
* Scaling plan enforcement based on current realized profits so traders
  can keep their position sizing inside the TopstepX limits.
* Risk checks that compare the proposed stop size against TopstepX rules.

The tool still supports ATR-based stop buffers, custom target two values,
and two different auto-trail spacing templates.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple

# ---- CME Group markets (tick specs) ----
# ticks_per_point = how many ticks in a 1.00 price move
# tick_value = USD per minimum tick
MARKETS: Dict[str, Dict[str, float]] = {
    # Equity index
    "MES (Micro ES)": {"ticks_per_point": 4, "tick_value": 1.25},
    "ES  (E-mini ES)": {"ticks_per_point": 4, "tick_value": 12.50},
    "MNQ (Micro NQ)": {"ticks_per_point": 4, "tick_value": 0.50},
    "NQ  (E-mini NQ)": {"ticks_per_point": 4, "tick_value": 5.00},
    "MYM (Micro YM)": {"ticks_per_point": 1, "tick_value": 0.50},
    "YM  (E-mini YM)": {"ticks_per_point": 1, "tick_value": 5.00},
    "M2K (Micro RTY)": {"ticks_per_point": 10, "tick_value": 0.50},
    "RTY (E-mini RTY)": {"ticks_per_point": 10, "tick_value": 5.00},

    # Energy (NYMEX)
    "MCL (Micro WTI Crude)": {"ticks_per_point": 100, "tick_value": 1.00},   # $0.01 tick
    "CL  (WTI Crude Oil)":   {"ticks_per_point": 100, "tick_value": 10.00},  # $0.01 tick

    # Metals (COMEX)
    "MGC (Micro Gold)": {"ticks_per_point": 10,  "tick_value": 1.00},   # $0.10 tick
    "GC  (Gold)":       {"ticks_per_point": 10,  "tick_value": 10.00},  # $0.10 tick
    "SIL (Micro Silver)": {"ticks_per_point": 200, "tick_value": 5.00}, # $0.005 tick
    "SI  (Silver)":       {"ticks_per_point": 200, "tick_value": 25.00},# $0.005 tick
    "HG  (Copper)":       {"ticks_per_point": 2000,"tick_value": 12.50},# $0.0005 tick

    # Treasuries (CBOT)
    "ZT (2Y Note)": {"ticks_per_point": 128, "tick_value": 7.8125},  # 1/128
    "ZF (5Y Note)": {"ticks_per_point": 128, "tick_value": 7.8125},  # 1/128
    "ZN (10Y Note)": {"ticks_per_point": 64,  "tick_value": 15.625},  # 1/64
    "ZB (30Y Bond)": {"ticks_per_point": 32,  "tick_value": 31.25},   # 1/32

    # FX (CME)
    "M6E (Micro EUR/USD)": {"ticks_per_point": 20000, "tick_value": 1.25},  # 0.00005
    "6E  (Euro FX)":       {"ticks_per_point": 20000, "tick_value": 6.25},  # 0.00005
}

# ---- TopstepX account guardrails ----
# The scaling plan entries are sorted by profit threshold. The highest entry
# whose threshold is <= current realized profit determines the maximum
# contracts permitted under the plan.
TOPSTEPX_ACCOUNTS: Dict[str, Dict[str, object]] = {
    "50K Express": {
        "starting_balance": 50_000,
        "daily_loss_limit": 2_500,
        "trailing_drawdown": 2_500,
        # threshold → max contracts (TopstepX published plan as of late 2023)
        "scaling_plan": [
            {"threshold": 0,     "contracts": 4},
            {"threshold": 1_000, "contracts": 6},
            {"threshold": 2_000, "contracts": 8},
            {"threshold": 3_000, "contracts": 10},
        ],
    },
    "100K Express": {
        "starting_balance": 100_000,
        "daily_loss_limit": 3_000,
        "trailing_drawdown": 3_000,
        "scaling_plan": [
            {"threshold": 0,     "contracts": 8},
            {"threshold": 2_000, "contracts": 12},
            {"threshold": 4_000, "contracts": 14},
            {"threshold": 6_000, "contracts": 16},
        ],
    },
    "150K Express": {
        "starting_balance": 150_000,
        "daily_loss_limit": 3_500,
        "trailing_drawdown": 4_500,
        "scaling_plan": [
            {"threshold": 0,     "contracts": 10},
            {"threshold": 3_000, "contracts": 14},
            {"threshold": 6_000, "contracts": 18},
            {"threshold": 9_000, "contracts": 22},
        ],
    },
}


def trail_freqs(zw: int) -> Tuple[int, int, int]:
    f1 = max(1, round(0.25 * zw))
    f2 = max(1, round(0.1875 * zw))
    f3 = max(1, round(0.125 * zw))
    return f1, f2, f3


def get_trail_settings(zw: int, trail_type: str) -> Tuple[List[int], List[int], List[int]]:
    """Return trail stop levels, triggers, and frequencies based on trail type."""
    if trail_type == "Tight (Original)":
        stops = [1 * zw, 2 * zw, 3 * zw]
        triggers = [2 * zw, 3 * zw, 4 * zw]
    else:  # "Loose (More Space)"
        stops = [1 * zw, 2 * zw, 3 * zw]
        triggers = [3 * zw, 5 * zw, 7 * zw]

    f1, f2, f3 = trail_freqs(zw)
    return stops, triggers, [f1, f2, f3]


def contracts_allowed_by_scaling(plan: List[Dict[str, int]], realized_profit: float) -> int:
    """Return the max contracts allowed by the TopstepX scaling plan."""
    eligible = plan[0]["contracts"] if plan else 0
    for rung in plan:
        if realized_profit >= rung["threshold"]:
            eligible = rung["contracts"]
        else:
            break
    return eligible


def fmt_dollar(value: float, decimals: int = 2) -> str:
    return f"${value:,.{decimals}f}"


def calc() -> None:
    try:
        spec = MARKETS[mkt_var.get()]
        zw = int(zw_var.get())
        account_cfg = TOPSTEPX_ACCOUNTS[acct_plan_var.get()]
        acct = float(acct_var.get())
        rpct = float(risk_var.get()) / 100.0
        split = float(split_var.get()) / 100.0
        atr_val = float(atr_var.get()) if atr_var.get().strip() else 0.0
        atr_mult = float(atr_mult_var.get()) / 100.0 if atr_mult_var.get().strip() else 0.02
        custom_t2 = int(custom_t2_var.get()) if custom_t2_var.get().strip() else 0
        trail_type = trail_var.get()
        realized_profit = float(realized_profit_var.get()) if realized_profit_var.get().strip() else 0.0
        if zw <= 0 or acct <= 0 or rpct <= 0:
            raise ValueError
    except (ValueError, KeyError):
        messagebox.showerror("Input error", "Enter valid numbers for ZW, account, and risk %.\n"
                             "Ensure a TopstepX account is selected.")
        return

    tpp = spec["ticks_per_point"]
    tick = spec["tick_value"]

    # Base stop/targets
    sl_ticks = zw
    t1_ticks = 2 * zw
    t2_ticks = custom_t2 if custom_t2 > 0 else 5 * zw
    be_plus = 1

    # ATR buffer calculation (converted to ticks)
    atr_buffer = 0.0
    atr_buffer_ticks = 0
    if atr_val > 0:
        atr_buffer = atr_val * atr_mult
        min_tick_size = 1.0 / tpp
        atr_buffer_ticks = int(round(atr_buffer / min_tick_size))

    # Adjust stop loss to include ATR buffer
    final_sl_ticks = sl_ticks + atr_buffer_ticks

    # Per-contract risk needs to reflect the buffered stop size
    per_ct_risk = final_sl_ticks * tick
    max_risk = acct * rpct
    max_cts_by_risk = int(max_risk // per_ct_risk) if per_ct_risk > 0 else 0

    qty1 = int(max_cts_by_risk * split)
    qty2 = max_cts_by_risk - qty1
    t1_usd_1 = t1_ticks * tick
    t2_usd_1 = t2_ticks * tick

    trail_stops, trail_triggers, trail_freq_vals = get_trail_settings(zw, trail_type)

    # TopstepX guardrails
    daily_loss_limit = account_cfg["daily_loss_limit"]
    trailing_drawdown = account_cfg["trailing_drawdown"]
    scaling_plan = account_cfg["scaling_plan"]
    starting_balance = account_cfg["starting_balance"]

    max_cts_daily = int(daily_loss_limit // per_ct_risk) if per_ct_risk else 0
    max_cts_trailing = int(trailing_drawdown // per_ct_risk) if per_ct_risk else 0
    max_cts_scaling = contracts_allowed_by_scaling(scaling_plan, realized_profit)

    enforced_max_cts = min(max_cts_by_risk, max_cts_daily, max_cts_trailing, max_cts_scaling)

    warnings: List[str] = []
    if per_ct_risk > daily_loss_limit:
        warnings.append("Per-contract risk exceeds the daily loss limit.")
    if per_ct_risk > trailing_drawdown:
        warnings.append("Per-contract risk exceeds the trailing drawdown cushion.")
    if max_cts_by_risk > max_cts_scaling:
        warnings.append("Risk sizing wants more contracts than the scaling plan permits.")
    if max_cts_by_risk > max_cts_daily:
        warnings.append("Risk sizing violates the daily loss cap if all contracts stop out.")
    if max_cts_by_risk > max_cts_trailing:
        warnings.append("Risk sizing would blow the trailing drawdown if fully stopped.")

    def pt(t: int) -> float:
        return t / tpp

    def fmt(val: float, digits: int = 2) -> str:
        return f"{val:,.{digits}f}"

    lines: List[str] = [
        f"TopstepX Account: {acct_plan_var.get()}  (Start {fmt_dollar(starting_balance, 0)})",
        f"Market: {mkt_var.get()}   Tick=${tick:.5g}   Ticks/pt={tpp}",
        f"Account balance used=${fmt(acct, 0)}   Risk/trade={rpct * 100:.2f}% → Max risk={fmt_dollar(max_risk)}",
        "",
    ]

    if atr_val > 0:
        lines.extend([
            "ATR STOP BUFFER:",
            f"  Daily ATR: {atr_val:.4f}",
            f"  ATR Multiplier: {atr_mult * 100:.1f}%",
            f"  Stop Buffer: {fmt(atr_buffer, 4)} (≈{atr_buffer_ticks} ticks)",
            f"  Base ZW: {zw} ticks + Buffer: {atr_buffer_ticks} ticks = Final SL: {final_sl_ticks} ticks",
            "",
        ])

    lines.extend([
        f"Per-contract risk: {final_sl_ticks} ticks → {fmt_dollar(per_ct_risk)}",
        f"Max contracts by account risk: {max_cts_by_risk}",
        f"Qty split: Safety {qty1} | Runner {qty2}",
        "",
        "TopstepX guardrails:",
        f"  Daily loss limit: {fmt_dollar(daily_loss_limit)} → Max contracts {max_cts_daily}",
        f"  Trailing drawdown cushion: {fmt_dollar(trailing_drawdown)} → Max contracts {max_cts_trailing}",
        f"  Scaling plan (profit {fmt_dollar(realized_profit)}): allows up to {max_cts_scaling} contracts",
        f"  Enforced max contracts: {enforced_max_cts}",
        "",
        "ATM fields (enter ticks):",
        f"  Stop Loss (both): {final_sl_ticks}" + (f" (ZW:{zw} + ATR Buffer:{atr_buffer_ticks})" if atr_buffer_ticks > 0 else ""),
        f"  Target 1: {t1_ticks}  ({fmt(pt(t1_ticks))} pts)",
        f"  Target 2: {t2_ticks}  ({fmt(pt(t2_ticks))} pts)" + (" [CUSTOM]" if custom_t2 > 0 else " [AUTO]") ,
        f"  Breakeven: Trigger {final_sl_ticks}, Plus {be_plus}",
        f"  Runner Auto-Trail ({trail_type}):",
        f"    Step 1: Stop {trail_stops[0]}  |  Trigger {trail_triggers[0]}  |  Freq {trail_freq_vals[0]}",
        f"    Step 2: Stop {trail_stops[1]}  |  Trigger {trail_triggers[1]}  |  Freq {trail_freq_vals[1]}",
        f"    Step 3: Stop {trail_stops[2]}  |  Trigger {trail_triggers[2]}  |  Freq {trail_freq_vals[2]}",
        "",
        "Per-contract P&L if targets hit:",
        f"  T1: {fmt_dollar(t1_usd_1)}   T2: {fmt_dollar(t2_usd_1)}",
    ])

    if warnings:
        lines.extend(["", "⚠️  WARNINGS:"] + [f"  • {msg}" for msg in warnings])

    out.configure(state="normal")
    out.delete("1.0", "end")
    out.insert("1.0", "\n".join(lines))
    out.configure(state="disabled")


def copy_out() -> None:
    txt = out.get("1.0", "end").strip()
    if not txt:
        return
    root.clipboard_clear()
    root.clipboard_append(txt)


def update_account_fields(event=None) -> None:
    """Update editable account size field when plan selection changes."""
    cfg = TOPSTEPX_ACCOUNTS.get(acct_plan_var.get())
    if not cfg:
        return
    acct_var.set(str(cfg["starting_balance"]))
    daily_loss_value.configure(text=fmt_dollar(cfg["daily_loss_limit"]))
    trailing_value.configure(text=fmt_dollar(cfg["trailing_drawdown"]))


# ---- UI ----
root = tk.Tk()
root.title("TopstepX ATM by Zone Width (ZW)")
frm = ttk.Frame(root, padding=10)
frm.grid(sticky="nsew")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Market selection
row = 0

(ttk.Label(frm, text="Market")) .grid(row=row, column=0, sticky="w")
mkt_var = tk.StringVar(value="MES (Micro ES)")
ttk.Combobox(frm, textvariable=mkt_var, values=list(MARKETS.keys()), state="readonly", width=28).grid(row=row, column=1, sticky="w")

# TopstepX account selection
row += 1
(ttk.Label(frm, text="TopstepX Account")) .grid(row=row, column=0, sticky="w")
acct_plan_var = tk.StringVar(value="50K Express")
acct_combo = ttk.Combobox(frm, textvariable=acct_plan_var, values=list(TOPSTEPX_ACCOUNTS.keys()), state="readonly", width=28)
acct_combo.grid(row=row, column=1, sticky="w")
acct_combo.bind("<<ComboboxSelected>>", update_account_fields)

# ZW input
row += 1
(ttk.Label(frm, text="Zone width ZW (ticks)")) .grid(row=row, column=0, sticky="w")
zw_var = tk.StringVar(value="18")
ttk.Entry(frm, textvariable=zw_var, width=12).grid(row=row, column=1, sticky="w")

# Account size (auto-populated but editable)
row += 1
(ttk.Label(frm, text="Account balance used ($)")) .grid(row=row, column=0, sticky="w")
acct_var = tk.StringVar(value=str(TOPSTEPX_ACCOUNTS[acct_plan_var.get()]["starting_balance"]))
ttk.Entry(frm, textvariable=acct_var, width=12).grid(row=row, column=1, sticky="w")

# Risk percent
row += 1
(ttk.Label(frm, text="Risk % per trade")) .grid(row=row, column=0, sticky="w")
risk_var = tk.StringVar(value="1.0")
ttk.Entry(frm, textvariable=risk_var, width=12).grid(row=row, column=1, sticky="w")

# Safety split
row += 1
(ttk.Label(frm, text="Safety leg split (%)")) .grid(row=row, column=0, sticky="w")
split_var = tk.StringVar(value="50")
ttk.Entry(frm, textvariable=split_var, width=12).grid(row=row, column=1, sticky="w")

# ATR fields
row += 1
(ttk.Label(frm, text="Daily ATR")) .grid(row=row, column=0, sticky="w")
atr_var = tk.StringVar(value="")
ttk.Entry(frm, textvariable=atr_var, width=12).grid(row=row, column=1, sticky="w")

row += 1
(ttk.Label(frm, text="ATR Multiplier (%)")) .grid(row=row, column=0, sticky="w")
atr_mult_var = tk.StringVar(value="2")
ttk.Entry(frm, textvariable=atr_mult_var, width=12).grid(row=row, column=1, sticky="w")

# Custom Target 2
row += 1
(ttk.Label(frm, text="Custom Target 2 (ticks, optional)")) .grid(row=row, column=0, sticky="w")
custom_t2_var = tk.StringVar(value="")
ttk.Entry(frm, textvariable=custom_t2_var, width=12).grid(row=row, column=1, sticky="w")

# Realized profit for scaling
row += 1
(ttk.Label(frm, text="Realized profit (for scaling)")).grid(row=row, column=0, sticky="w")
realized_profit_var = tk.StringVar(value="0")
ttk.Entry(frm, textvariable=realized_profit_var, width=12).grid(row=row, column=1, sticky="w")

# Auto-trail spacing option
row += 1
(ttk.Label(frm, text="Auto-Trail Spacing")) .grid(row=row, column=0, sticky="w")
trail_var = tk.StringVar(value="Tight (Original)")
ttk.Combobox(frm, textvariable=trail_var, values=["Tight (Original)", "Loose (More Space)"], state="readonly", width=28).grid(row=row, column=1, sticky="w")

# Guardrail summary labels
row += 1
summary_frame = ttk.Frame(frm)
summary_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(6, 2))
summary_frame.columnconfigure((0, 1), weight=1)

(ttk.Label(summary_frame, text="Daily loss limit:")) .grid(row=0, column=0, sticky="w")
daily_loss_value = ttk.Label(summary_frame, text=fmt_dollar(TOPSTEPX_ACCOUNTS[acct_plan_var.get()]["daily_loss_limit"]))
daily_loss_value.grid(row=0, column=1, sticky="w")

(ttk.Label(summary_frame, text="Trailing drawdown:")) .grid(row=1, column=0, sticky="w")
trailing_value = ttk.Label(summary_frame, text=fmt_dollar(TOPSTEPX_ACCOUNTS[acct_plan_var.get()]["trailing_drawdown"]))
trailing_value.grid(row=1, column=1, sticky="w")

# Buttons
row += 1
button_frame = ttk.Frame(frm)
button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)
button_frame.columnconfigure((0, 1), weight=1)

ttk.Button(button_frame, text="Calculate", command=calc).grid(row=0, column=0, sticky="ew")
ttk.Button(button_frame, text="Copy Output", command=copy_out).grid(row=0, column=1, sticky="ew")

# Output area
row += 1
out = tk.Text(frm, width=90, height=28, wrap="word", state="disabled")
out.grid(row=row, column=0, columnspan=2, sticky="nsew")
frm.rowconfigure(row, weight=1)

update_account_fields()
calc()
root.mainloop()
