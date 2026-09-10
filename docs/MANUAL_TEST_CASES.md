# Manual Test Cases

Every case below is derived from the exercise text alone. Nothing here assumes knowledge of
trading, settlement or compliance that the brief does not itself introduce.

## The facts the exercise gives us

1. An account holds a list of securities.
2. The account has a total asset value ($100,000), of which 100% is vested.
3. Each security has a target percentage.
4. Each security has a current percentage.
5. Each security has a unit price.
6. Target variance is "how much deviation you have"; (−ve) means buy, (+ve) means sell.
7. The output is the "number of shares to buy/sell" for each security.
8. The goal is to get to zero target variance.

Every case traces back to one of those eight facts.



## UI Step Execution

Group F assumes a user interface. This implementation is a calculation engine with no
front end, so these steps describe the layer above it.

1. Open the account screen for Account ABC.
2. Read the displayed table: security, target %, current %, target variance, unit price and
   the output quantity.
3. Perform the interaction the case describes.
4. Record what is displayed, and whether it matches what the calculator returns.

---

## The Automated column

| Value | Meaning |
|---|---|
| **True** | Automated and passing |
| **True (xfail)** | Automated, expected behaviour asserted, application does not meet it. The defect number is given. Marked `xfail(strict=True)`, so the build fails the moment one starts passing |
| **False** | Designed but not automated — the reason is given under the coverage summary |


---

## A. Functional — the rules the exercise states

| Test case name | Expected behaviour | Automated |
|---|---|---|
| A1 — The stated scenario produces the correct quantities | IBM +66.6667, MSFT 0, ORCL −45.4545, AAPL 0, HD 0 | True |
| A2 — Negative variance produces a buy | An underweight security returns a positive quantity | True |
| A3 — Positive variance produces a sell | An overweight security returns a negative quantity | True |
| A4 — Zero variance produces no trade | MSFT, AAPL and HD return exactly 0 | True |
| A5 — An account already at target generates no trades | Every security returns 0 | True |
| A6 — Applying the orders reaches zero variance | Every security lands on exactly its target % | True |
| A7 — The money bought equals the money sold | $10,000 each way, agreeing to the cent. No cash required, none left over | True |

## B. Boundary — extreme values

| Test case name | Expected behaviour | Automated |
|---|---|---|
| B1 — A target of 0% | The security's entire value is moved, and never more | True |
| B2 — A variance far smaller than the unit price | A $5,000 variance in a $600,000 share is 0.0083 shares, and is still corrected | True |
| B3 — A very small unit price | $0.29 at $0.01 a share is exactly 29, with no loss of precision | True |
| B4 — A target of 100% in one security | Every other security sold in full, all value moved into that one | True |
| B5 — Whole-share quantities, if a platform required them | Truncated toward zero, never rounded up: IBM 66 costs $9,900 against a $10,000 variance; 67 costs $10,050. The mode itself is not implemented — the rule is asserted against the exact quantities | True |
| B6 — A large number of securities (100 at 1% each) | All 100 correctly calculated | False |

## C. Negative — invalid or inconsistent input

| Test case name | Expected behaviour | Automated |
|---|---|---|
| C1 — Target % total something other than 100 | Rejected with an error naming the total. No orders produced | True (xfail) |
| C2 — Current % total something other than 100 | Rejected with an error naming the total. Same rule as C1 on the other column | True (xfail) |
| C3 — A negative target % or current % | Rejected — a security cannot be a negative share of the account | True (xfail) |
| C4 — Total assets of zero or below | Rejected — every target is a percentage of it | True (xfail) |
| C5 — The same security listed twice | Rejected, naming the symbol. Combining the rows would mean deciding what a duplicate means | True (xfail) |
| C6 — A unit price of zero or below | Rejected; zero divides by zero, negative reverses the trade direction | True (xfail) |
| C7 — A security with a required field missing | Rejected, naming the security and the field | True (xfail) |
| C8 — An empty list of securities | No orders, and no error — there is nothing to rebalance | True |
| C9 — Weights totalling exactly 100 across uneven values | 33.33 + 33.33 + 33.34 is a legitimate model and rebalances normally | True |
| C10 — A security named in the targets but absent from the table | Treated as 0% current, or rejected — but not silently dropped | False |
| C11 — An account less than 100% vested | Undefined — targets could apply to the vested portion only, to total assets with only vested holdings tradable, or unvested holdings could be excluded entirely. These give different orders, so the requirement is a question for the business | False |
| C12 — An empty, whitespace-only or missing symbol | Rejected — an order keyed by `''` cannot be acted on | True (xfail) |


## E. Non-functional

| Test case name | Expected behaviour | Automated |
|---|---|---|
| E1 — The same input produces the same output | Identical results across repeated runs | True |
| E2 — A large account completes in acceptable time | Within the agreed SLA. Measured manually; a timing assertion makes a flaky test | False |


## F. User interface — assumes a front end exists

The exercise calls the rebalancer an "application", which implies an interface, but supplies
no detail about one. **This implementation has none** — it is a calculation engine, so every
case below is designed rather than executed. Each is still derived from the exercise's own
table: the six columns it shows, the figures it states, and the output it defines.

| Test case name | Expected behaviour | Automated |
|---|---|---|
| F1 — Every column the exercise defines is displayed | Security, target %, current %, target variance, unit price and output quantity, for all five securities | False |
| F2 — Displayed variance matches current % − target % | IBM shows −10, ORCL +10, the rest 0. The figure is derived, not separately entered | False |
| F3 — Editing a target % updates the variance immediately | Changing IBM's target from 20 to 25 changes its variance from −10 to −15 without a reload | False |
| F4 — Each weight column shows a running total | The user can see whether the column reaches 100% before running anything, rather than discovering it in an error | False |
| F5 — An output quantity is shown for every security | Five rows in, five quantities out. A security at target shows `0`, not a blank cell | False |
| F6 — A buy is distinguishable from a sell at a glance | Not by a minus sign alone — direction is stated in words or colour, and legible without colour | False |
| F7 — Quantities are displayed at a readable precision | IBM shows `66.6667`, not the 28 significant digits the calculator returns | False |
| F8 — The displayed quantity matches what the calculator returned | Rounding for display never changes the value acted on | False |
| F9 — Invalid input is rejected at the field | Typing `2` where `20` was meant is flagged on the row, before the rebalance runs, naming the problem | False |
| F10 — The rebalance control is unavailable while the model is invalid | A user cannot generate orders from a model whose weights do not total 100% | False |
| F11 — Errors are shown to the user, not only logged | A rejected rebalance explains what was wrong and what to change, on screen | False |
| F12 — Total assets and vested percentage are displayed | $100,000 and 100% are shown, since every other figure is a percentage of them | False |
| F13 — The output can be exported for someone to act on | Copy or download producing a record of the security, direction and quantity | False |

---

## Coverage summary

| Group | Cases | Automated |
|---|---|---|
| A — Functional | 7 | 7 |
| B — Boundary | 6 | 5 |
| C — Negative | 12 | 10 |
| E — Non-functional | 2 | 1 |
| F — User interface | 13 | 0 |
| **Total** | **40** | **23** |

