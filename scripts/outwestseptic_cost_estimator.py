"""Itemized USD estimates from supplied quantities and rates.

AI-assisted contribution for Jake's Out West Septic project.
See the repository documentation for source and scope limitations.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import tempfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path

Number = str | int | float | Decimal
CENT = Decimal("0.01")


def _number(value: Number, label: str, *, maximum: str, places: int) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(f"{label} must be a finite decimal number.")
    try:
        result = Decimal(str(value))
        if not result.is_finite() or not 0 <= result <= Decimal(maximum):
            raise ValueError(f"{label} must be between 0 and {maximum}.")
        with localcontext() as context:
            context.prec = 50
            normalized = result.quantize(Decimal(1).scaleb(-places))
        if normalized != result:
            raise ValueError(f"{label} supports at most {places} decimal places.")
        return normalized
    except (InvalidOperation, OverflowError):
        raise ValueError(f"{label} must be a finite decimal number.") from None


def _label(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f"{name} must contain 1 to 200 characters.")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{name} cannot contain control characters.")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError(f"{name} must contain valid Unicode text encodable as UTF-8.") from None
    return value.strip()


def _display_number(value: Decimal) -> str:
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class OutWestSepticCostLineItem:
    label: str
    quantity: Number
    unit_low_usd: Number
    unit_high_usd: Number

    def __post_init__(self):
        object.__setattr__(self, "label", _label(self.label, "Item label"))
        quantity = _number(self.quantity, "Quantity", maximum="1000000000", places=6)
        low = _number(self.unit_low_usd, "Low unit price", maximum="1000000000000", places=2)
        high = _number(self.unit_high_usd, "High unit price", maximum="1000000000000", places=2)
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if low > high:
            raise ValueError("Low unit price must not exceed high unit price.")
        object.__setattr__(self, "quantity", quantity)
        object.__setattr__(self, "unit_low_usd", low)
        object.__setattr__(self, "unit_high_usd", high)

    @property
    def low_usd(self) -> Decimal:
        with localcontext() as context:
            context.prec = 50
            return _money(self.quantity * self.unit_low_usd)

    @property
    def high_usd(self) -> Decimal:
        with localcontext() as context:
            context.prec = 50
            return _money(self.quantity * self.unit_high_usd)

    def to_dict(self) -> dict:
        return {
            "label": self.label, "quantity": str(self.quantity),
            "unit_low_usd": str(self.unit_low_usd),
            "unit_high_usd": str(self.unit_high_usd),
            "low_usd": str(self.low_usd), "high_usd": str(self.high_usd),
        }


class OutWestSepticCostEstimator:
    """Total supplied line items; no market prices or site multipliers."""

    @staticmethod
    def estimate(
        *, project: str, items: list[OutWestSepticCostLineItem] | tuple[OutWestSepticCostLineItem, ...],
        contingency_percent: Number = "0",
    ) -> "OutWestSepticCostEstimate":
        project = _label(project, "Project")
        if not isinstance(items, (list, tuple)) or not 1 <= len(items) <= 1000:
            raise ValueError("Supply 1 to 1000 line items.")
        if not all(isinstance(item, OutWestSepticCostLineItem) for item in items):
            raise ValueError("Each item must be an OutWestSepticCostLineItem.")
        percentage = _number(contingency_percent, "Contingency percent", maximum="1000", places=4)
        with localcontext() as context:
            context.prec = 50
            subtotal_low = sum((item.low_usd for item in items), Decimal("0.00"))
            subtotal_high = sum((item.high_usd for item in items), Decimal("0.00"))
            reserve_low = _money(subtotal_low * percentage / 100)
            reserve_high = _money(subtotal_high * percentage / 100)
            return OutWestSepticCostEstimate(
                project, tuple(items), percentage, subtotal_low, subtotal_high,
                reserve_low, reserve_high,
                subtotal_low + reserve_low, subtotal_high + reserve_high,
            )


@dataclass(frozen=True)
class OutWestSepticCostEstimate:
    project: str
    items: tuple[OutWestSepticCostLineItem, ...]
    contingency_percent: Decimal
    subtotal_low_usd: Decimal
    subtotal_high_usd: Decimal
    contingency_low_usd: Decimal
    contingency_high_usd: Decimal
    low_usd: Decimal
    high_usd: Decimal

    def render(self) -> str:
        lines = [
            "Out West Septic project - Itemized planning estimate",
            f"Project: {self.project}",
            "Currency: USD; all quantities and rates supplied by the user.",
        ]
        for item in self.items:
            lines.append(
                f"- {item.label}: {_display_number(item.quantity)} x "
                f"${item.unit_low_usd:,.2f} to ${item.unit_high_usd:,.2f}"
                f" = ${item.low_usd:,.2f} to ${item.high_usd:,.2f}"
            )
        lines.extend([
            f"Subtotal: ${self.subtotal_low_usd:,.2f} to ${self.subtotal_high_usd:,.2f}",
            f"Contingency ({_display_number(self.contingency_percent)}%): "
            f"${self.contingency_low_usd:,.2f} to ${self.contingency_high_usd:,.2f}",
            f"Total: ${self.low_usd:,.2f} to ${self.high_usd:,.2f}",
            "No tax, fee, discount, or omitted work is added automatically.",
            "This arithmetic is not a quote or a verified market-price range.",
        ])
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "schema_version": 1, "project": self.project, "currency": "USD",
            "basis": "user-supplied quantities and rates",
            "items": [item.to_dict() for item in self.items],
            "contingency_percent": str(self.contingency_percent),
            **{field: str(getattr(self, field)) for field in (
                "subtotal_low_usd", "subtotal_high_usd", "contingency_low_usd",
                "contingency_high_usd", "low_usd", "high_usd",
            )},
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n"

    def to_csv(self) -> str:
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\r\n")
        writer.writerow(["row_type", "label", "quantity", "unit_low_usd", "unit_high_usd",
                         "low_usd", "high_usd"])
        # Prefix spreadsheet formula markers in user text; JSON preserves raw text.
        def safe(text: str) -> str:
            return "'" + text if text.startswith(("=", "+", "-", "@")) else text
        writer.writerow(["project", safe(self.project), "", "", "", "", ""])
        for item in self.items:
            writer.writerow(["item", safe(item.label), item.quantity, item.unit_low_usd,
                             item.unit_high_usd, item.low_usd, item.high_usd])
        writer.writerow(["subtotal", "", "", "", "", self.subtotal_low_usd, self.subtotal_high_usd])
        writer.writerow(["contingency", f"{_display_number(self.contingency_percent)}%", "", "", "",
                         self.contingency_low_usd, self.contingency_high_usd])
        writer.writerow(["total", "", "", "", "", self.low_usd, self.high_usd])
        return stream.getvalue()


CostEstimate = OutWestSepticCostEstimate


def _write_export(target: Path, content: str, *, overwrite: bool) -> None:
    """Encode before opening files; stage replacements beside the destination."""
    payload = content.encode("utf-8")
    if not overwrite:
        with target.open("xb") as output:
            output.write(payload)
        return
    staged = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=".outwestseptic-export-",
            suffix=".tmp", delete=False,
        ) as output:
            staged = Path(output.name)
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(staged, target)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Itemized USD estimate using your quantities and unit-price ranges.",
        allow_abbrev=False,
    )
    parser.add_argument("--project", required=True, help="A project label, not a predefined price category.")
    parser.add_argument("--item", action="append", nargs=4, required=True,
                        metavar=("LABEL", "QUANTITY", "LOW_USD", "HIGH_USD"),
                        help="Repeat for each item; include its quantity unit in the label.")
    parser.add_argument("--contingency-percent", default="0", help="Explicit reserve percentage; default 0.")
    exports = parser.add_mutually_exclusive_group()
    exports.add_argument("--json", type=Path, metavar="PATH")
    exports.add_argument("--csv", type=Path, metavar="PATH")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing the selected export file.")
    args = parser.parse_args(argv)
    try:
        estimate = OutWestSepticCostEstimator.estimate(
            project=args.project,
            items=[OutWestSepticCostLineItem(*item) for item in args.item],
            contingency_percent=args.contingency_percent,
        )
        target = args.json if args.json is not None else args.csv
        if args.overwrite and target is None:
            raise ValueError("--overwrite requires --json or --csv.")
        if target is not None:
            content = estimate.to_json() if args.json is not None else estimate.to_csv()
            _write_export(target, content, overwrite=args.overwrite)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(estimate.render())
    if target is not None:
        print(f"Export written: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
