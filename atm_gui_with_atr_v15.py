# atm_by_zw_gui_cme.py
import tkinter as tk
from tkinter import ttk, messagebox

# ---- CME Group markets (tick specs) ----
# ticks_per_point = how many ticks in a 1.00 price move
# tick_value = USD per minimum tick
MARKETS = {
    # Equity index
    "MES (Micro ES)": {"ticks_per_point": 4,   "tick_value": 1.25},
    "ES  (E-mini ES)": {"ticks_per_point": 4,   "tick_value": 12.50},
    "MNQ (Micro NQ)": {"ticks_per_point": 4,   "tick_value": 0.50},
    "NQ  (E-mini NQ)": {"ticks_per_point": 4,   "tick_value": 5.00},
    "MYM (Micro YM)": {"ticks_per_point": 1,   "tick_value": 0.50},
    "YM  (E-mini YM)": {"ticks_per_point": 1,   "tick_value": 5.00},
    "M2K (Micro RTY)": {"ticks_per_point": 10,  "tick_value": 0.50},
    "RTY (E-mini RTY)": {"ticks_per_point": 10,  "tick_value": 5.00},

    # Energy (NYMEX)
    "MCL (Micro WTI Crude)": {"ticks_per_point": 100, "tick_value": 1.00},   # $0.01 tick
    "CL  (WTI Crude Oil)":   {"ticks_per_point": 100, "tick_value": 10.00},  # $0.01 tick

    # Metals (COMEX)
    "MGC (Micro Gold)": {"ticks_per_point": 10,  "tick_value": 1.00},  # $0.10 tick
    "GC  (Gold)":       {"ticks_per_point": 10,  "tick_value": 10.00}, # $0.10 tick
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

def trail_freqs(zw):
    f1 = max(1, round(0.25*zw))
    f2 = max(1, round(0.1875*zw))
    f3 = max(1, round(0.125*zw))
    return f1, f2, f3

def get_trail_settings(zw, trail_type):
    """Return trail stop levels, triggers, and frequencies based on trail type"""
    if trail_type == "Tight (Original)":
        # Original tight spacing
        stops = [1*zw, 2*zw, 3*zw]
        triggers = [2*zw, 3*zw, 4*zw]
    else:  # "Loose (More Space)"
        # Looser spacing for bigger moves
        stops = [1*zw, 2*zw, 3*zw]
        triggers = [3*zw, 5*zw, 7*zw]
    
    f1, f2, f3 = trail_freqs(zw)
    return stops, triggers, [f1, f2, f3]

def calc():
    try:
        spec = MARKETS[mkt_var.get()]
        zw   = int(zw_var.get())
        acct = float(acct_var.get())
        rpct = float(risk_var.get())/100.0
        split = float(split_var.get())/100.0
        atr_val = float(atr_var.get()) if atr_var.get().strip() else 0
        atr_mult = float(atr_mult_var.get())/100.0 if atr_mult_var.get().strip() else 0.02
        custom_t2 = int(custom_t2_var.get()) if custom_t2_var.get().strip() else 0
        trail_type = trail_var.get()
        if zw<=0 or acct<=0 or rpct<=0: raise ValueError
    except ValueError:
        messagebox.showerror("Input error","Enter valid numbers for ZW, account, and risk %."); return

    tpp = spec["ticks_per_point"]; tick = spec["tick_value"]

    sl_ticks = zw
    t1_ticks = 2*zw
    t2_ticks = 5*zw
    be_plus  = 1

    per_ct_risk = sl_ticks * tick
    max_risk = acct * rpct
    max_cts = int(max_risk // per_ct_risk) if per_ct_risk>0 else 0

    qty1 = int(max_cts * split); qty2 = max_cts - qty1
    t1_usd_1 = t1_ticks * tick; t2_usd_1 = t2_ticks * tick
    
    # Get trail settings based on selected type
    trail_stops, trail_triggers, trail_freqs = get_trail_settings(zw, trail_type)

    # ATR stop buffer calculation
    atr_buffer = 0
    atr_buffer_ticks = 0
    if atr_val > 0:
        atr_buffer = atr_val * atr_mult
        # Convert ATR buffer to ticks (approximate, depends on price level)
        # For most futures, 1 tick represents the minimum price movement
        # This is a rough conversion - actual implementation may need price context
        min_tick_size = 1.0 / tpp  # minimum price movement
        atr_buffer_ticks = int(round(atr_buffer / min_tick_size))

    # Adjust stop loss to include ATR buffer
    sl_ticks = zw + atr_buffer_ticks

    def pt(t): return t / tpp
    def fmt(x,n=2): return f"{x:,.{n}f}"

    lines = [
        f"Market: {mkt_var.get()}   Tick=${tick:.5g}   Ticks/pt={tpp}",
        f"Account=${fmt(acct,0)}   Risk/trade={rpct*100:.2f}% → Max risk=${fmt(max_risk)}",
        "",
    ]
    
    # Add ATR section if ATR value is provided
    if atr_val > 0:
        lines.extend([
            f"ATR STOP BUFFER:",
            f"  Daily ATR: {atr_val:.4f}",
            f"  ATR Multiplier: {atr_mult*100:.1f}%",
            f"  Stop Buffer: {fmt(atr_buffer, 4)} (≈{atr_buffer_ticks} ticks)",
            f"  Base ZW: {zw} ticks + Buffer: {atr_buffer_ticks} ticks = Final SL: {sl_ticks} ticks",
            "",
        ])
    
    lines.extend([
        f"Per-contract risk: {sl_ticks} ticks → ${fmt(per_ct_risk)}",
        f"Max contracts by risk: {max_cts}",
        f"Qty split: Safety {qty1} | Runner {qty2}",
        "",
        "ATM fields (enter ticks):",
        f"  Stop Loss (both): {sl_ticks}" + (f" (ZW:{zw} + ATR Buffer:{atr_buffer_ticks})" if atr_buffer_ticks > 0 else ""),
        f"  Target 1: {t1_ticks}  ({fmt(pt(t1_ticks))} pts)",
        f"  Target 2: {t2_ticks}  ({fmt(pt(t2_ticks))} pts)" + (" [CUSTOM]" if custom_t2 > 0 else " [AUTO: 5×ZW]"),
        f"  Breakeven: Trigger {sl_ticks}, Plus {be_plus}",
        f"  Runner Auto-Trail ({trail_type}):",
        f"    Step 1: Stop {trail_stops[0]}  |  Trigger {trail_triggers[0]}  |  Freq {trail_freqs[0]}",
        f"    Step 2: Stop {trail_stops[1]}  |  Trigger {trail_triggers[1]}  |  Freq {trail_freqs[1]}",
        f"    Step 3: Stop {trail_stops[2]}  |  Trigger {trail_triggers[2]}  |  Freq {trail_freqs[2]}",
        "",
        "Per-contract P&L if targets hit:",
        f"  T1: ${fmt(t1_usd_1)}   T2: ${fmt(t2_usd_1)}",
    ])

    out.configure(state="normal"); out.delete("1.0","end"); out.insert("1.0","\n".join(lines)); out.configure(state="disabled")

def copy_out():
    txt = out.get("1.0","end").strip()
    if not txt: return
    root.clipboard_clear(); root.clipboard_append(txt)

# ---- UI ----
root = tk.Tk(); root.title("ATM by Zone Width (ZW) — CME")
frm = ttk.Frame(root, padding=10); frm.grid(sticky="nsew")
root.columnconfigure(0, weight=1); root.rowconfigure(0, weight=1)

ttk.Label(frm,text="Market").grid(row=0,column=0,sticky="w")
mkt_var = tk.StringVar(value="MES (Micro ES)")
ttk.Combobox(frm,textvariable=mkt_var,values=list(MARKETS.keys()),state="readonly",width=28).grid(row=0,column=1,sticky="w")

ttk.Label(frm,text="Zone width ZW (ticks)").grid(row=1,column=0,sticky="w")
zw_var = tk.StringVar(value="18"); ttk.Entry(frm,textvariable=zw_var,width=12).grid(row=1,column=1,sticky="w")

ttk.Label(frm,text="Account size ($)").grid(row=2,column=0,sticky="w")
acct_var = tk.StringVar(value="50000"); ttk.Entry(frm,textvariable=acct_var,width=12).grid(row=2,column=1,sticky="w")

ttk.Label(frm,text="Risk % per trade").grid(row=3,column=0,sticky="w")
risk_var = tk.StringVar(value="2"); ttk.Entry(frm,textvariable=risk_var,width=12).grid(row=3,column=1,sticky="w")

ttk.Label(frm,text="Safety leg split (%)").grid(row=4,column=0,sticky="w")
split_var = tk.StringVar(value="50"); ttk.Entry(frm,textvariable=split_var,width=12).grid(row=4,column=1,sticky="w")

# ATR fields
ttk.Label(frm,text="Daily ATR (from FINVIZ)").grid(row=5,column=0,sticky="w")
atr_var = tk.StringVar(value=""); ttk.Entry(frm,textvariable=atr_var,width=12).grid(row=5,column=1,sticky="w")

ttk.Label(frm,text="ATR Multiplier (%)").grid(row=6,column=0,sticky="w")
atr_mult_var = tk.StringVar(value="2"); ttk.Entry(frm,textvariable=atr_mult_var,width=12).grid(row=6,column=1,sticky="w")

# Custom Target 2 field
ttk.Label(frm,text="Custom Target 2 (ticks, optional)").grid(row=7,column=0,sticky="w")
custom_t2_var = tk.StringVar(value=""); ttk.Entry(frm,textvariable=custom_t2_var,width=12).grid(row=7,column=1,sticky="w")

# Auto-trail spacing option
ttk.Label(frm,text="Auto-Trail Spacing").grid(row=8,column=0,sticky="w")
trail_var = tk.StringVar(value="Tight (Original)")
ttk.Combobox(frm,textvariable=trail_var,values=["Tight (Original)", "Loose (More Space)"],state="readonly",width=28).grid(row=8,column=1,sticky="w")

ttk.Button(frm,text="Calculate",command=calc).grid(row=9,column=0,sticky="ew",pady=6)
ttk.Button(frm,text="Copy Output",command=copy_out).grid(row=9,column=1,sticky="ew",pady=6)

out = tk.Text(frm,width=80,height=24,wrap="word",state="disabled")
out.grid(row=10,column=0,columnspan=2,sticky="nsew"); frm.rowconfigure(10, weight=1)

calc(); root.mainloop()
