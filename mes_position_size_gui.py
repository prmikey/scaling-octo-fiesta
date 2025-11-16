"""Unified CME futures zone risk calculator GUI with embedded CME specs."""

from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
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
    """Return an in-memory dataset of CME futures specs."""

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
            tick_value=0.50,
            contract_unit="0.1 bitcoin",
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
            tick_value=0.025,
            contract_unit="0.1 ether",
            is_micro=True,
        ),
        # Energy (NYMEX)
        ContractSpec(
            "CL",
            "WTI Crude Oil",
            "NYMEX",
            "Energy",
            tick_size=0.01,
            tick_value=10.00,
            contract_unit="1,000 barrels",
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
        ContractSpec(
            "MCL",
            "Micro WTI Crude Oil",
            "NYMEX",
            "Energy",
            tick_size=0.01,
            tick_value=1.00,
            contract_unit="100 barrels",
            is_micro=True,
        ),
        ContractSpec(
            "NG",
            "Henry Hub Natural Gas",
            "NYMEX",
            "Energy",
            tick_size=0.001,
            tick_value=10.00,
            contract_unit="10,000 mmBtu",
        ),
        ContractSpec(
            "QG",
            "E-mini Natural Gas",
            "NYMEX",
            "Energy",
            tick_size=0.005,
            tick_value=12.50,
            contract_unit="2,500 mmBtu",
        ),
        ContractSpec(
            "MNG",
            "Micro Henry Hub Natural Gas",
            "NYMEX",
            "Energy",
            tick_size=0.001,
            tick_value=1.00,
            contract_unit="1,000 mmBtu",
            is_micro=True,
        ),
        ContractSpec(
            "RB",
            "RBOB Gasoline",
            "NYMEX",
            "Energy",
            tick_size=0.0001,
            tick_value=4.20,
            contract_unit="42,000 gallons",
        ),
        ContractSpec(
            "HO",
            "NY Harbor ULSD (Heating Oil)",
            "NYMEX",
            "Energy",
            tick_size=0.0001,
            tick_value=4.20,
            contract_unit="42,000 gallons",
        ),
        ContractSpec(
            "BZ",
            "Brent Crude Oil",
            "NYMEX",
            "Energy",
            tick_size=0.01,
            tick_value=10.00,
            contract_unit="1,000 barrels",
        ),
        # Metals (COMEX)
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
            "QO",
            "E-mini Gold",
            "COMEX",
            "Metals",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="50 troy ounces",
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
        ContractSpec(
            "QC",
            "E-mini Copper",
            "COMEX",
            "Metals",
            tick_size=0.0005,
            tick_value=6.25,
            contract_unit="12,500 pounds",
        ),
        ContractSpec(
            "PL",
            "Platinum",
            "NYMEX",
            "Metals",
            tick_size=0.1,
            tick_value=5.00,
            contract_unit="50 troy ounces",
        ),
        ContractSpec(
            "PA",
            "Palladium",
            "NYMEX",
            "Metals",
            tick_size=0.1,
            tick_value=10.00,
            contract_unit="100 troy ounces",
        ),
        # Agricultural (CBOT/CME)
        ContractSpec(
            "ZC",
            "Corn",
            "CBOT",
            "Agriculture",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZS",
            "Soybeans",
            "CBOT",
            "Agriculture",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZW",
            "Chicago Wheat",
            "CBOT",
            "Agriculture",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "KE",
            "KC Hard Red Winter Wheat",
            "KC Board of Trade",
            "Agriculture",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZO",
            "Oats",
            "CBOT",
            "Agriculture",
            tick_size=0.25,
            tick_value=12.50,
            contract_unit="5,000 bushels",
        ),
        ContractSpec(
            "ZR",
            "Rough Rice",
            "CBOT",
            "Agriculture",
            tick_size=0.005,
            tick_value=10.00,
            contract_unit="2,000 cwt",
        ),
        ContractSpec(
            "ZM",
            "Soybean Meal",
            "CBOT",
            "Agriculture",
            tick_size=0.1,
            tick_value=10.00,
            contract_unit="100 short tons",
        ),
        ContractSpec(
            "ZL",
            "Soybean Oil",
            "CBOT",
            "Agriculture",
            tick_size=0.0001,
            tick_value=6.00,
            contract_unit="60,000 pounds",
        ),
        ContractSpec(
            "GF",
            "Feeder Cattle",
            "CME",
            "Livestock",
            tick_size=0.00025,
            tick_value=12.50,
            contract_unit="50,000 pounds",
        ),
        ContractSpec(
            "LE",
            "Live Cattle",
            "CME",
            "Livestock",
            tick_size=0.00025,
            tick_value=10.00,
            contract_unit="40,000 pounds",
        ),
        ContractSpec(
            "HE",
            "Lean Hogs",
            "CME",
            "Livestock",
            tick_size=0.00025,
            tick_value=10.00,
            contract_unit="40,000 pounds",
        ),
        ContractSpec(
            "LBS",
            "Random Length Lumber",
            "CME",
            "Lumber",
            tick_size=0.1,
            tick_value=11.00,
            contract_unit="27,500 board feet",
        ),
        ContractSpec(
            "DC",
            "Class III Milk",
            "CME",
            "Dairy",
            tick_size=0.01,
            tick_value=20.00,
            contract_unit="200,000 pounds",
        ),
        ContractSpec(
            "DA",
            "Class IV Milk",
            "CME",
            "Dairy",
            tick_size=0.01,
            tick_value=20.00,
            contract_unit="200,000 pounds",
        ),
        # Interest rates
        ContractSpec(
            "SR3",
            "3-Month SOFR",
            "CME",
            "Interest Rates",
            tick_size=0.0025,
            tick_value=6.25,
            contract_unit="$2,500 x (100 - rate)",
        ),
        ContractSpec(
            "GE",
            "Eurodollar",
            "CME",
            "Interest Rates",
            tick_size=0.0025,
            tick_value=6.25,
            contract_unit="$2,500 x (100 - rate)",
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
            "Ultra U.S. Treasury Bond",
            "CBOT",
            "Interest Rates",
            tick_size=0.03125,
            tick_value=31.25,
            contract_unit="$100,000 face value",
        ),
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
            "TN",
            "Ultra 10-Year T-Note",
            "CBOT",
            "Interest Rates",
            tick_size=0.015625,
            tick_value=15.625,
            contract_unit="$100,000 face value",
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
            "ZT",
            "2-Year T-Note",
            "CBOT",
            "Interest Rates",
            tick_size=0.0078125,
            tick_value=7.8125,
            contract_unit="$200,000 face value",
        ),
        ContractSpec(
            "ZQ",
            "30-Day Fed Funds",
            "CME",
            "Interest Rates",
            tick_size=0.0025,
            tick_value=10.42,
            contract_unit="$4,167 x (100 - rate)",
        ),
        # FX majors
        ContractSpec(
            "6A",
            "Australian Dollar",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=10.00,
            contract_unit="100,000 AUD",
        ),
        ContractSpec(
            "M6A",
            "Micro Australian Dollar",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=1.00,
            contract_unit="10,000 AUD",
            is_micro=True,
        ),
        ContractSpec(
            "6B",
            "British Pound",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=6.25,
            contract_unit="62,500 GBP",
        ),
        ContractSpec(
            "M6B",
            "Micro British Pound",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=0.625,
            contract_unit="6,250 GBP",
            is_micro=True,
        ),
        ContractSpec(
            "6C",
            "Canadian Dollar",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=10.00,
            contract_unit="100,000 CAD",
        ),
        ContractSpec(
            "M6C",
            "Micro Canadian Dollar",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=1.00,
            contract_unit="10,000 CAD",
            is_micro=True,
        ),
        ContractSpec(
            "6E",
            "Euro FX",
            "CME",
            "FX",
            tick_size=0.00005,
            tick_value=6.25,
            contract_unit="125,000 EUR",
        ),
        ContractSpec(
            "M6E",
            "Micro Euro FX",
            "CME",
            "FX",
            tick_size=0.00005,
            tick_value=0.625,
            contract_unit="12,500 EUR",
            is_micro=True,
        ),
        ContractSpec(
            "6J",
            "Japanese Yen",
            "CME",
            "FX",
            tick_size=0.0000005,
            tick_value=6.25,
            contract_unit="12,500,000 JPY",
        ),
        ContractSpec(
            "M6J",
            "Micro Japanese Yen",
            "CME",
            "FX",
            tick_size=0.0000005,
            tick_value=0.625,
            contract_unit="1,250,000 JPY",
            is_micro=True,
        ),
        ContractSpec(
            "6M",
            "Mexican Peso",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=5.00,
            contract_unit="500,000 MXN",
        ),
        ContractSpec(
            "M6M",
            "Micro Mexican Peso",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=0.50,
            contract_unit="50,000 MXN",
            is_micro=True,
        ),
        ContractSpec(
            "6N",
            "New Zealand Dollar",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=10.00,
            contract_unit="100,000 NZD",
        ),
        ContractSpec(
            "M6N",
            "Micro New Zealand Dollar",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=1.00,
            contract_unit="10,000 NZD",
            is_micro=True,
        ),
        ContractSpec(
            "6S",
            "Swiss Franc",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=12.50,
            contract_unit="125,000 CHF",
        ),
        ContractSpec(
            "M6S",
            "Micro Swiss Franc",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=1.25,
            contract_unit="12,500 CHF",
            is_micro=True,
        ),
        ContractSpec(
            "6R",
            "Brazilian Real",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=10.00,
            contract_unit="100,000 BRL",
        ),
        ContractSpec(
            "6Z",
            "South African Rand",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=5.00,
            contract_unit="500,000 ZAR",
        ),
        ContractSpec(
            "6L",
            "Israeli Shekel",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=10.00,
            contract_unit="100,000 ILS",
        ),
        ContractSpec(
            "6U",
            "Russian Ruble",
            "CME",
            "FX",
            tick_size=0.0001,
            tick_value=10.00,
            contract_unit="2,500,000 RUB",
        ),
    ]
    return {spec.symbol: spec for spec in specs}


CONTRACT_SPECS: Dict[str, ContractSpec] = _build_specs()

DEFAULT_CONTRACT = "MES"


def ordered_contract_displays() -> List[str]:
    """Return the drop-down values grouped by product type then symbol."""

    return [
        spec.display
        for spec in sorted(
            CONTRACT_SPECS.values(),
            key=lambda spec: (spec.product_group, spec.is_micro, spec.symbol),
        )
    ]


DISPLAY_TO_SYMBOL = {spec.display: spec.symbol for spec in CONTRACT_SPECS.values()}


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
