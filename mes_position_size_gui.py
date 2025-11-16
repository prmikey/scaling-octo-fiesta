"""Unified CME futures zone risk calculator GUI."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Dict, List


@dataclass(frozen=True)
class ContractSpec:
    """Minimal contract information for sizing calculations."""

    symbol: str
    name: str
    exchange: str
    product_group: str
    tick_size: float
    tick_value: float
    contract_unit: str
    is_micro: bool = False
    notes: str = ""

    @property
    def display(self) -> str:
        """Formatted label used in the combobox."""

        return f"{self.symbol} – {self.name} ({self.exchange})"


def _build_specs() -> Dict[str, ContractSpec]:
    specs: List[ContractSpec] = [
        # Equity index futures
        ContractSpec(
            "ES",
            "E-mini S&P 500",
            "CME",
            "Equity Index",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="50 x S&P 500 Index",
        ),
        ContractSpec(
            "MES",
            "Micro E-mini S&P 500",
            "CME",
            "Equity Index",
            tick_size=0.25,
            tick_value=1.25,
            contract_unit="5 x S&P 500 Index",
            is_micro=True,
        ),
        ContractSpec(
            "NQ",
            "E-mini Nasdaq-100",
            "CME",
            "Equity Index",
            tick_size=0.25,
            tick_value=5.00,
            contract_unit="20 x Nasdaq-100 Index",
        ),
        ContractSpec(
            "MNQ",
            "Micro E-mini Nasdaq-100",
            "CME",
            "Equity Index",
            tick_size=0.25,
            tick_value=0.50,
            contract_unit="2 x Nasdaq-100 Index",
            is_micro=True,
        ),
        ContractSpec(
            "YM",
            "E-mini Dow ($5)",
            "CBOT",
            "Equity Index",
            tick_size=1.0,
            tick_value=5.00,
            contract_unit="$5 x Dow Jones Industrial Average",
        ),
        ContractSpec(
            "MYM",
            "Micro E-mini Dow",
            "CBOT",
            "Equity Index",
            tick_size=1.0,
            tick_value=0.50,
            contract_unit="$0.50 x Dow Jones Industrial Average",
            is_micro=True,
        ),
        ContractSpec(
            "RTY",
            "E-mini Russell 2000",
            "CME",
            "Equity Index",
            tick_size=0.1,
            tick_value=5.00,
            contract_unit="50 x Russell 2000 Index",
        ),
        ContractSpec(
            "M2K",
            "Micro E-mini Russell 2000",
            "CME",
            "Equity Index",
            tick_size=0.1,
            tick_value=0.50,
            contract_unit="5 x Russell 2000 Index",
            is_micro=True,
        ),
        ContractSpec(
            "EMD",
            "E-mini S&P MidCap 400",
            "CME",
            "Equity Index",
            tick_size=0.1,
            tick_value=10.00,
            contract_unit="100 x S&P MidCap 400 Index",
        ),
        ContractSpec(
            "NKD",
            "Nikkei 225 (USD)",
            "CME",
            "Equity Index",
            tick_size=5.0,
            tick_value=25.00,
            contract_unit="$5 x Nikkei 225 Index",
        ),
        ContractSpec(
            "NIY",
            "Nikkei 225 (JPY)",
            "CME",
            "Equity Index",
            tick_size=5.0,
            tick_value=12.50,
            contract_unit="¥500 x Nikkei 225 Index",
        ),
        # Cryptocurrency futures
        ContractSpec(
            "BTC",
            "Bitcoin",
            "CME",
            "Cryptocurrency",
            tick_size=5.0,
            tick_value=25.00,
            contract_unit="5 bitcoin",
        ),
        ContractSpec(
            "MBT",
            "Micro Bitcoin",
            "CME",
            "Cryptocurrency",
            tick_size=5.0,
            tick_value=1.25,
            contract_unit="0.5 bitcoin",
            is_micro=True,
        ),
        ContractSpec(
            "ETH",
            "Ether",
            "CME",
            "Cryptocurrency",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="50 ether",
        ),
        ContractSpec(
            "MET",
            "Micro Ether",
            "CME",
            "Cryptocurrency",
            tick_size=0.25,
            tick_value=0.50,
            contract_unit="5 ether",
            is_micro=True,
        ),
        # Interest rate futures
        ContractSpec(
            "ZN",
            "10-Year T-Note",
            "CBOT",
            "Interest Rates",
            tick_size=0.015625,
            tick_value=15.625,
            contract_unit="$100,000 face value",
        ),
        ContractSpec(
            "ZT",
            "2-Year T-Note",
            "CBOT",
            "Interest Rates",
            tick_size=0.0078125,
            tick_value=7.8125,
            contract_unit="$200,000 face value",
        ),
        ContractSpec(
            "ZF",
            "5-Year T-Note",
            "CBOT",
            "Interest Rates",
            tick_size=0.0078125,
            tick_value=7.8125,
            contract_unit="$100,000 face value",
        ),
        ContractSpec(
            "ZB",
            "U.S. Treasury Bond",
            "CBOT",
            "Interest Rates",
            tick_size=0.03125,
            tick_value=31.25,
            contract_unit="$100,000 face value",
        ),
        ContractSpec(
            "UB",
            "Ultra T-Bond",
            "CBOT",
            "Interest Rates",
            tick_size=0.03125,
            tick_value=31.25,
            contract_unit="$100,000 face value",
        ),
        ContractSpec(
            "SR3",
            "Three-Month SOFR",
            "CME",
            "Interest Rates",
            tick_size=0.0025,
            tick_value=6.25,
            contract_unit="$2,500 x contract price",
        ),
        ContractSpec(
            "SRS",
            "Micro SOFR",
            "CME",
            "Interest Rates",
            tick_size=0.005,
            tick_value=5.00,
            contract_unit="$1,000 x contract price",
            is_micro=True,
        ),
        # Energy futures
        ContractSpec(
            "CL",
            "Crude Oil",
            "NYMEX",
            "Energy",
            tick_size=0.01,
            tick_value=10.00,
            contract_unit="1,000 barrels",
        ),
        ContractSpec(
            "MCL",
            "Micro Crude Oil",
            "NYMEX",
            "Energy",
            tick_size=0.01,
            tick_value=1.00,
            contract_unit="100 barrels",
            is_micro=True,
        ),
        ContractSpec(
            "NG",
            "Natural Gas",
            "NYMEX",
            "Energy",
            tick_size=0.001,
            tick_value=10.00,
            contract_unit="10,000 mmBtu",
        ),
        ContractSpec(
            "QM",
            "E-mini Crude Oil",
            "NYMEX",
            "Energy",
            tick_size=0.025,
            tick_value=12.50,
            contract_unit="500 barrels",
        ),
        # Metals futures
        ContractSpec(
            "GC",
            "Gold",
            "COMEX",
            "Metals",
            tick_size=0.1,
            tick_value=10.00,
            contract_unit="100 troy ounces",
        ),
        ContractSpec(
            "MGC",
            "Micro Gold",
            "COMEX",
            "Metals",
            tick_size=0.1,
            tick_value=1.00,
            contract_unit="10 troy ounces",
            is_micro=True,
        ),
        ContractSpec(
            "SI",
            "Silver",
            "COMEX",
            "Metals",
            tick_size=0.005,
            tick_value=25.00,
            contract_unit="5,000 troy ounces",
        ),
        ContractSpec(
            "SIL",
            "Micro Silver",
            "COMEX",
            "Metals",
            tick_size=0.005,
            tick_value=5.00,
            contract_unit="1,000 troy ounces",
            is_micro=True,
        ),
        ContractSpec(
            "HG",
            "Copper",
            "COMEX",
            "Metals",
            tick_size=0.0005,
            tick_value=12.50,
            contract_unit="25,000 pounds",
        ),
        # Agricultural futures
        ContractSpec(
            "ZC",
            "Corn",
            "CBOT",
            "Agricultural",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZW",
            "Wheat",
            "CBOT",
            "Agricultural",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZS",
            "Soybeans",
            "CBOT",
            "Agricultural",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZL",
            "Soybean Oil",
            "CBOT",
            "Agricultural",
            tick_size=0.0001,
            tick_value=6.00,
            contract_unit="60,000 lbs",
        ),
        ContractSpec(
            "ZM",
            "Soybean Meal",
            "CBOT",
            "Agricultural",
            tick_size=0.1,
            tick_value=10.00,
            contract_unit="100 tons",
        ),
        ContractSpec(
            "HE",
            "Lean Hogs",
            "CME",
            "Livestock",
            tick_size=0.00025,
            tick_value=10.00,
            contract_unit="40,000 lbs",
        ),
        ContractSpec(
            "LE",
            "Live Cattle",
            "CME",
            "Livestock",
            tick_size=0.00025,
            tick_value=12.50,
            contract_unit="40,000 lbs",
        ),
        ContractSpec(
            "GF",
            "Feeder Cattle",
            "CME",
            "Livestock",
            tick_size=0.00025,
            tick_value=12.50,
            contract_unit="50,000 lbs",
        ),
    ]

    return {spec.symbol: spec for spec in specs}


CONTRACT_SPECS = _build_specs()
DEFAULT_CONTRACT = "MES"
DISPLAY_TO_SYMBOL = {spec.display: symbol for symbol, spec in CONTRACT_SPECS.items()}


def ordered_contract_displays() -> List[str]:
    """Return contract display labels sorted micro vs standard then alphabetically."""

    standard = sorted(
        [spec.display for spec in CONTRACT_SPECS.values() if not spec.is_micro]
    )
    micro = sorted([spec.display for spec in CONTRACT_SPECS.values() if spec.is_micro])
    return standard + micro


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
