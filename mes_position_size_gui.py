"""General CME futures position sizing GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from cme_contract_specs import (
    CONTRACT_SPECS,
    DEFAULT_CONTRACT,
    DISPLAY_TO_SYMBOL,
    ContractSpec,
    ordered_contract_displays,
)


def validate_positive_float(value: str, field_name: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:  # pragma: no cover - tkinter runtime guard
        raise ValueError(f"Enter a number for {field_name}.") from exc
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return number


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


class PositionSizeApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("CME Futures Position Size Calculator")
        self.root.geometry("520x420")
        self.root.resizable(False, False)

        self.contract_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="ticks")

        self._build_widgets()
        self._populate_contracts()
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        # Contract selection
        contract_label = ttk.Label(main, text="Contract")
        contract_label.grid(row=0, column=0, sticky="w")
        self.contract_combo = ttk.Combobox(
            main, textvariable=self.contract_var, state="readonly", width=42
        )
        self.contract_combo.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 8))
        self.contract_combo.bind("<<ComboboxSelected>>", self._on_contract_change)

        self.contract_info = ttk.Label(main, text="Select a contract to load specs.")
        self.contract_info.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # Risk input
        risk_label = ttk.Label(main, text="Account risk per trade ($)")
        risk_label.grid(row=2, column=0, sticky="w")
        self.risk_entry = ttk.Entry(main)
        self.risk_entry.insert(0, "500")
        self.risk_entry.grid(row=2, column=1, columnspan=2, sticky="ew")

        # Tick value input
        tick_value_label = ttk.Label(main, text="Tick value ($)")
        tick_value_label.grid(row=3, column=0, sticky="w")
        self.tick_value_entry = ttk.Entry(main)
        self.tick_value_entry.grid(row=3, column=1, columnspan=2, sticky="ew")

        # Stop mode frame
        mode_frame = ttk.LabelFrame(main, text="Stop input mode")
        mode_frame.grid(row=4, column=0, columnspan=3, pady=(12, 0), sticky="ew")

        rb_ticks = ttk.Radiobutton(
            mode_frame, text="Ticks", value="ticks", variable=self.mode_var
        )
        rb_ticks.grid(row=0, column=0, padx=4, pady=4, sticky="w")
        rb_dollars = ttk.Radiobutton(
            mode_frame, text="Dollars", value="dollars", variable=self.mode_var
        )
        rb_dollars.grid(row=0, column=1, padx=4, pady=4, sticky="w")

        stop_ticks_label = ttk.Label(mode_frame, text="Stop size (ticks)")
        stop_ticks_label.grid(row=1, column=0, sticky="w", padx=4)
        self.stop_ticks_entry = ttk.Entry(mode_frame)
        self.stop_ticks_entry.insert(0, "10")
        self.stop_ticks_entry.grid(row=1, column=1, sticky="ew", padx=4)

        stop_dollars_label = ttk.Label(mode_frame, text="Stop size ($)")
        stop_dollars_label.grid(row=2, column=0, sticky="w", padx=4)
        self.stop_dollars_entry = ttk.Entry(mode_frame, state="disabled")
        self.stop_dollars_entry.insert(0, "50")
        self.stop_dollars_entry.grid(row=2, column=1, sticky="ew", padx=4)

        self.mode_var.trace_add("write", self._switch_mode)

        # Calculate button
        calc_button = ttk.Button(main, text="Calculate", command=self.calculate)
        calc_button.grid(row=5, column=0, columnspan=3, pady=(12, 0), sticky="ew")

        # Result display
        self.result_text = tk.Text(main, height=8, width=50, state="disabled")
        self.result_text.grid(row=6, column=0, columnspan=3, pady=(12, 0), sticky="nsew")

        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(6, weight=1)

    # ------------------------------------------------------------------
    def _populate_contracts(self) -> None:
        choices = ordered_contract_displays()
        self.contract_combo.configure(values=choices)

        default_display = CONTRACT_SPECS[DEFAULT_CONTRACT].display
        self.contract_var.set(default_display)
        self._on_contract_change()

    # ------------------------------------------------------------------
    def _switch_mode(self, *_args) -> None:
        ticks_selected = self.mode_var.get() == "ticks"
        self.stop_ticks_entry.configure(state="normal" if ticks_selected else "disabled")
        self.stop_dollars_entry.configure(state="disabled" if ticks_selected else "normal")

    # ------------------------------------------------------------------
    def _on_contract_change(self, *_args) -> None:
        spec = self._get_selected_spec()
        if not spec:
            return
        self._prefill_tick_value(spec)
        tick_info = (
            f"{spec.symbol}: {spec.name}\n"
            f"Group: {spec.product_group} • Tick size: {spec.tick_size:g} • "
            f"Tick value: {format_currency(spec.tick_value)}\n"
            f"Contract unit: {spec.contract_unit}"
        )
        self.contract_info.configure(text=tick_info)

    # ------------------------------------------------------------------
    def _prefill_tick_value(self, spec: ContractSpec) -> None:
        self.tick_value_entry.delete(0, tk.END)
        self.tick_value_entry.insert(0, f"{spec.tick_value}")

    # ------------------------------------------------------------------
    def _get_selected_spec(self) -> ContractSpec | None:
        display_value = self.contract_var.get()
        symbol = DISPLAY_TO_SYMBOL.get(display_value)
        if not symbol:
            return None
        return CONTRACT_SPECS[symbol]

    # ------------------------------------------------------------------
    def calculate(self) -> None:
        spec = self._get_selected_spec()
        if not spec:
            messagebox.showerror("Contract", "Select a valid contract.")
            return

        try:
            account_risk = validate_positive_float(
                self.risk_entry.get(), "Account risk"
            )
            tick_value = validate_positive_float(
                self.tick_value_entry.get(), "Tick value"
            )

            if self.mode_var.get() == "ticks":
                stop_ticks = validate_positive_float(
                    self.stop_ticks_entry.get(), "Stop size (ticks)"
                )
                per_contract_risk = stop_ticks * tick_value
                extra_info = f"Stop size: {stop_ticks:.2f} ticks"
            else:
                stop_dollars = validate_positive_float(
                    self.stop_dollars_entry.get(), "Stop size ($)"
                )
                per_contract_risk = stop_dollars
                approx_ticks = stop_dollars / tick_value
                extra_info = (
                    f"Stop size: {format_currency(stop_dollars)} (≈ {approx_ticks:.2f} ticks)"
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
            f"Contract: {spec.symbol} – {spec.name}",
            f"Contracts: {contracts}",
            f"Per-contract risk: {format_currency(per_contract_risk)}",
            f"Total risk: {format_currency(used_risk)}",
            f"Unused risk: {format_currency(unused_risk)}",
            extra_info,
        ]

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(result_lines))
        self.result_text.configure(state="disabled")

    # ------------------------------------------------------------------
    def run(self) -> None:
        self._switch_mode()
        self.root.mainloop()


if __name__ == "__main__":
    PositionSizeApp().run()

