"""Unified CME futures zone risk calculator GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from cme_contract_specs import (
    CONTRACT_SPECS,
    DEFAULT_CONTRACT,
    DISPLAY_TO_SYMBOL,
    ContractSpec,
    ordered_contract_displays,
)


def validate_positive_float(value: str, field_name: str) -> float:
    """Convert *value* to a positive float or raise ``ValueError``."""

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
    """Tkinter GUI that sizes CME futures via zone width + dollar risk."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("CME Futures Zone Risk Calculator")
        self.root.geometry("560x420")
        self.root.resizable(False, False)

        self.contract_var = tk.StringVar(value="")

        self._build_widgets()
        self._populate_contracts()
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        # Contract selection
        ttk.Label(main, text="Contract").grid(row=0, column=0, sticky="w")
        self.contract_combo = ttk.Combobox(
            main, textvariable=self.contract_var, state="readonly", width=45
        )
        self.contract_combo.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 8))
        self.contract_combo.bind("<<ComboboxSelected>>", self._on_contract_change)

        self.contract_info = ttk.Label(main, text="Select a contract to load specs.")
        self.contract_info.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # Risk input
        ttk.Label(main, text="Account risk per trade ($)").grid(row=2, column=0, sticky="w")
        self.risk_entry = ttk.Entry(main)
        self.risk_entry.insert(0, "500")
        self.risk_entry.grid(row=2, column=1, columnspan=2, sticky="ew")

        ttk.Label(main, text="Zone width (price)").grid(row=3, column=0, sticky="w")
        self.zone_entry = ttk.Entry(main)
        self.zone_entry.insert(0, "1.00")
        self.zone_entry.grid(row=3, column=1, columnspan=2, sticky="ew")

        detail_frame = ttk.LabelFrame(main, text="Contract details")
        detail_frame.grid(row=4, column=0, columnspan=3, pady=(12, 0), sticky="ew")

        ttk.Label(detail_frame, text="Tick size").grid(row=0, column=0, sticky="w")
        self.tick_size_var = tk.StringVar(value="-")
        ttk.Label(detail_frame, textvariable=self.tick_size_var).grid(
            row=0, column=1, sticky="w"
        )

        ttk.Label(detail_frame, text="Tick value").grid(row=1, column=0, sticky="w")
        self.tick_value_var = tk.StringVar(value="-")
        ttk.Label(detail_frame, textvariable=self.tick_value_var).grid(
            row=1, column=1, sticky="w"
        )

        ttk.Label(detail_frame, text="Contract unit").grid(row=2, column=0, sticky="w")
        self.contract_unit_var = tk.StringVar(value="-")
        ttk.Label(detail_frame, textvariable=self.contract_unit_var).grid(
            row=2, column=1, sticky="w"
        )

        calc_button = ttk.Button(main, text="Calculate", command=self.calculate)
        calc_button.grid(row=5, column=0, columnspan=3, pady=(12, 0), sticky="ew")

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
    def _on_contract_change(self, *_args) -> None:
        spec = self._get_selected_spec()
        if not spec:
            return

        tick_info = f"{spec.symbol}: {spec.name}\nGroup: {spec.product_group}"
        self.contract_info.configure(text=tick_info)
        self.tick_size_var.set(f"{spec.tick_size:g}")
        self.tick_value_var.set(format_currency(spec.tick_value))
        self.contract_unit_var.set(spec.contract_unit)

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
            zone_width = validate_positive_float(self.zone_entry.get(), "Zone width")

            ticks = zone_width / spec.tick_size
            per_contract_risk = ticks * spec.tick_value

            contracts = int(account_risk // per_contract_risk) if per_contract_risk else 0
            used_risk = contracts * per_contract_risk
            unused_risk = account_risk - used_risk

            if contracts <= 0:
                raise ValueError(
                    "Account risk is too small for one contract with the chosen zone width."
                )
        except ValueError as exc:
            messagebox.showerror("Input error", str(exc))
            return

        result_lines = [
            f"Contract: {spec.symbol} – {spec.name}",
            f"Zone width: {zone_width:.4f} ({ticks:.2f} ticks)",
            f"Per-contract risk: {format_currency(per_contract_risk)}",
            f"Contracts: {contracts}",
            f"Total risk: {format_currency(used_risk)}",
            f"Unused risk: {format_currency(unused_risk)}",
        ]

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(result_lines))
        self.result_text.configure(state="disabled")

    # ------------------------------------------------------------------
    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    PositionSizeApp().run()
