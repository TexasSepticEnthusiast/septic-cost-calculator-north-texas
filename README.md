# North Texas septic cost worksheet

Build an itemized USD estimate using quantities and unit-price ranges you supply. The worksheet keeps cents, shows each calculation, and exports JSON or spreadsheet-ready CSV. It contains no default contractor prices, county fees, or rock/access multipliers.

An AI-assisted automated contribution for the [Out West Septic](https://outwestseptic.com) project. This is affiliated planning software, not an independent endorsement or a contractor quote.

## Start an estimate

Python 3.10 or newer; no runtime dependencies.

```bash
git clone https://github.com/TexasSepticEnthusiast/septic-cost-calculator-north-texas.git
cd septic-cost-calculator-north-texas
python scripts/outwestseptic_cost_estimator.py --project "Arithmetic example" --item "Example labor (hours)" 2.5 10 12 --item "Example fee (each)" 1 3 4 --contingency-percent 10 --json estimate.json
```

**These are invented arithmetic inputs, not septic market prices.** This example gives a $28.00–$34.00 subtotal, a $2.80–$3.40 contingency, and a **$30.80–$37.40 total**.

Repeat `--item LABEL QUANTITY LOW_USD HIGH_USD` for each part of the work. Put the quantity unit in the label, such as hours, feet, acres, or each. A fixed amount uses quantity 1 with equal low and high unit prices. Obtain actual rates and allowances from current written project information. Use separate lines for separately priced rock work or access work instead of an unexplained multiplier.

## How money is calculated

1. Multiply each quantity by its low and high unit prices.
2. Round each resulting line amount to cents using decimal half-up rounding.
3. Sum the rounded line amounts.
4. Calculate the explicitly chosen contingency percentage on each subtotal, round it to cents, and add it.

A quantity of 0.5 at $0.01/unit becomes $0.01 for that line. Two such lines total $0.02. Decimal arithmetic avoids binary floating-point rounding surprises.

No tax, permit fee, discount, or omitted work is added automatically. Contingency defaults to 0%; it is a user-selected reserve, not a risk prediction. Costs must be nonnegative; negative credits are not supported in this version. Record exclusions or credits separately when comparing the worksheet with a quote.

Input limits are software limits, not business assumptions:

| Input | Supported values |
| --- | --- |
| Line items | 1–1000 |
| Quantity | Greater than 0 through 1,000,000,000; up to 6 decimal places |
| Unit price | $0 through $1,000,000,000,000; at most 2 decimal places |
| Contingency | 0–1000 percent; up to 4 decimal places |
| Project and item labels | 1–200 characters; valid UTF-8 Unicode text without control characters |

NaN, infinity, booleans, reversed price ranges, and unsupported precision are rejected.

## Exports and review

Use `--json PATH` or `--csv PATH`. JSON records the supplied values, each rounded line, subtotals, contingency, and totals as decimal strings. CSV uses separate item and total rows; labels beginning with spreadsheet formula markers receive an apostrophe prefix. JSON retains the original label.

Existing files require explicit `--overwrite`. The complete export is encoded before any file is opened. Overwrites are written and flushed to a temporary file in the destination directory, then atomically replace the old file; encoding, staging-write or replacement failures preserve the old bytes. Export errors exit with status 2 without printing a successful estimate or export message. Parent directories must exist.

```python
from scripts.outwestseptic_cost_estimator import (
    OutWestSepticCostEstimator,
    OutWestSepticCostLineItem,
)

estimate = OutWestSepticCostEstimator.estimate(
    project="Arithmetic example",
    items=[OutWestSepticCostLineItem("Example hours", "2.5", "10", "12")],
    contingency_percent="10",
)
print(estimate.low_usd)  # Decimal('27.50')
```

## Scope and migration

The earlier project-type price ranges and site multipliers were unsupported. They have been removed, along with fictitious field-experience claims and seed issue/PR histories. The old positional project category, `--modifier`, `--acres`, and `--list` interface is replaced by explicit `--project` and `--item` inputs.

`OutWestSepticCostEstimator` remains the main class. `CostEstimate` is an import alias for `OutWestSepticCostEstimate`; the report schema and constructor have changed.

See the [source and estimate-review guide](wiki/Cost-Estimator-Reference.md) for what to verify before treating a cost worksheet as a project budget.

## Test and license

```bash
python -m unittest discover -s tests -v
```

Tests cover cent rounding, exact large values, invalid quantities and rates, CSV safety, real exports, invalid Unicode, and preservation of existing exports during simulated partial-write, flush and replacement failures. CI runs Python 3.10 and 3.13.

See the existing [license reference](LICENSE).
