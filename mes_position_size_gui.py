import tkinter as tk
from tkinter import ttk, messagebox

MES_TICK_VALUE = 1.25  # USD per tick for MES
MES_TICKS_PER_POINT = 4  # 4 ticks per index point (0.25)

def validate_positive_float(value: str, field_name: str) -> float:
    try:
        number = float(value)
    except ValueError:
        raise ValueError(f"Enter a number for {field_name}.")
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return number


def calculate():
    try:
        account_risk = validate_positive_float(risk_entry.get(), "Account risk")
        tick_value = validate_positive_float(tick_value_entry.get(), "Tick value")

        if mode_var.get() == "ticks":
            stop_ticks = validate_positive_float(stop_ticks_entry.get(), "Stop size (ticks)")
            per_contract_risk = stop_ticks * tick_value
            extra_info = f"Stop size: {stop_ticks:.2f} ticks"
        else:
            stop_dollars = validate_positive_float(stop_dollars_entry.get(), "Stop size ($)")
            per_contract_risk = stop_dollars
            stop_ticks_equiv = stop_dollars / tick_value
            extra_info = (
                f"Stop size: ${stop_dollars:.2f} (≈ {stop_ticks_equiv:.2f} ticks)"
            )

        contracts = int(account_risk // per_contract_risk) if per_contract_risk else 0
        used_risk = contracts * per_contract_risk
        unused_risk = account_risk - used_risk

        if contracts <= 0:
            raise ValueError(
                "Account risk is too small for one contract with the chosen stop size."
            )
    except ValueError as exc:
        messagebox.showerror("Input error", str(exc))
        return

    result_lines = [
        f"MES contracts: {contracts}",
        f"Per-contract risk: ${per_contract_risk:,.2f}",
        f"Total risk: ${used_risk:,.2f}",
        f"Unused risk: ${unused_risk:,.2f}",
        extra_info,
        f"Ticks per point: {ticks_per_point_entry.get()}"
    ]

    result_text.configure(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert("1.0", "\n".join(result_lines))
    result_text.configure(state="disabled")


def switch_mode(*_args):
    if mode_var.get() == "ticks":
        stop_ticks_entry.configure(state="normal")
        stop_dollars_entry.configure(state="disabled")
    else:
        stop_ticks_entry.configure(state="disabled")
        stop_dollars_entry.configure(state="normal")


root = tk.Tk()
root.title("MES Position Size Calculator")
root.geometry("420x320")
root.resizable(False, False)

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

# Risk input
risk_label = ttk.Label(main, text="Account risk per trade ($)")
risk_label.grid(row=0, column=0, sticky="w")
risk_entry = ttk.Entry(main)
risk_entry.insert(0, "500")
risk_entry.grid(row=0, column=1, sticky="ew")

# Tick value input (editable just in case)
tick_value_label = ttk.Label(main, text="Tick value ($)")
tick_value_label.grid(row=1, column=0, sticky="w")
tick_value_entry = ttk.Entry(main)
tick_value_entry.insert(0, f"{MES_TICK_VALUE}")
tick_value_entry.grid(row=1, column=1, sticky="ew")

# Ticks per point (informational)
ticks_per_point_label = ttk.Label(main, text="Ticks per point")
ticks_per_point_label.grid(row=2, column=0, sticky="w")
ticks_per_point_entry = ttk.Entry(main, state="readonly")
ticks_per_point_entry.grid(row=2, column=1, sticky="ew")
ticks_per_point_entry.configure(state="normal")
ticks_per_point_entry.insert(0, str(MES_TICKS_PER_POINT))
ticks_per_point_entry.configure(state="readonly")

# Mode selection
mode_var = tk.StringVar(value="ticks")
mode_frame = ttk.LabelFrame(main, text="Stop input mode")
mode_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")

rb_ticks = ttk.Radiobutton(mode_frame, text="Ticks", value="ticks", variable=mode_var)
rb_ticks.grid(row=0, column=0, padx=4, pady=4, sticky="w")
rb_dollars = ttk.Radiobutton(mode_frame, text="Dollars", value="dollars", variable=mode_var)
rb_dollars.grid(row=0, column=1, padx=4, pady=4, sticky="w")

stop_ticks_label = ttk.Label(mode_frame, text="Stop size (ticks)")
stop_ticks_label.grid(row=1, column=0, sticky="w", padx=4)
stop_ticks_entry = ttk.Entry(mode_frame)
stop_ticks_entry.insert(0, "10")
stop_ticks_entry.grid(row=1, column=1, sticky="ew", padx=4)

stop_dollars_label = ttk.Label(mode_frame, text="Stop size ($)")
stop_dollars_label.grid(row=2, column=0, sticky="w", padx=4)
stop_dollars_entry = ttk.Entry(mode_frame, state="disabled")
stop_dollars_entry.insert(0, "50")
stop_dollars_entry.grid(row=2, column=1, sticky="ew", padx=4)

mode_var.trace_add("write", switch_mode)

# Calculate button
calc_button = ttk.Button(main, text="Calculate", command=calculate)
calc_button.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="ew")

# Result display
result_text = tk.Text(main, height=6, width=40, state="disabled")
result_text.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="nsew")

main.columnconfigure(1, weight=1)
main.rowconfigure(5, weight=1)

switch_mode()
root.mainloop()
