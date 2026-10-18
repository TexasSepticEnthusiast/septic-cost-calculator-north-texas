# Septic estimate review and arithmetic reference

This worksheet totals supplied inputs; it does not publish North Texas price averages. It was prepared as an AI-assisted contribution for Jake's [Out West Septic](https://outwestseptic.com) project.

## Build a reviewable estimate

For each line, record the scope, quantity unit, expected quantity, and source/date of the low and high unit rates in your own project records. The public examples are synthetic arithmetic, not prices or business activity.

Useful scope questions include whether a written amount includes site evaluation, planning, permit-related work, installation, restoration, and any identified site work. These are review prompts, not a claim that every item applies or a complete bid specification. Add only applicable quoted amounts and avoid charging for an included item twice.

The [TCEQ owner's guide](https://www.tceq.texas.gov/permitting/ossf/ossfadvice.html) explains that system selection depends on site conditions and discusses approved plans, permitting, and choosing an installer. Its advice supports obtaining project-specific information; it does not substantiate the old repository's price ranges.

The [TCEQ system-selection guide](https://www.tceq.texas.gov/permitting/ossf/ossfsystems.html) distinguishes treatment and disposal methods and their constraints. A cost worksheet does not determine which method is suitable or authorize construction.

## Calculation contract

All amounts are USD. Rates are user-entered values with at most two decimal places. Quantities support six decimal places. Each low/high line amount is quantity × corresponding unit rate, rounded half-up to cents. Rounded lines are summed. An explicit contingency percentage is then applied to each subtotal and rounded half-up to cents. Totals are subtotal plus contingency.

Example only: 2.5 units at $10.00–$12.00/unit gives $25.00–$30.00. Adding a $3.00–$4.00 line produces $28.00–$34.00; a chosen 10% reserve produces $30.80–$37.40 overall.

Tax, permit fees, financing, discounts, omitted work, and site-specific uncertainties are not inferred. The low/high totals are arithmetic bounds from supplied ranges, not a statistical confidence interval or verified market estimate.

## Exports

JSON preserves decimal strings and the supplied labels. CSV includes line items and subtotal/contingency/total rows. Formula-like user labels are prefixed with an apostrophe in CSV so opening the export does not turn them into spreadsheet formulas. Control characters in project and item labels are rejected.

Existing export files require explicit overwrite. Input errors are detected before a file is opened.

## Sources and review status

Primary guidance reviewed 2026-10-18:

- [TCEQ: Advice for an Owner of an On-Site Sewage Facility](https://www.tceq.texas.gov/permitting/ossf/ossfadvice.html).
- [TCEQ: Choosing a Septic System](https://www.tceq.texas.gov/permitting/ossf/ossfsystems.html).

No verified market-rate dataset, contractor quote, or owner-approved price book was provided. That is why prices are explicit inputs. The software remains useful without such a dataset; adding automatic prices later requires a maintained, attributable source and an owner decision about how rates should be updated.
