# Portfolio Rebalancing — CRD Technical Assessment

## The question

> Account ABC holds IBM, MSFT, ORCL, AAPL and HD, with $100,000 in total assets (100% vested).
> **What do you have to do to get to zero target variance?**

## The answer

| Security | target % | current % | variance | unit price | **shares to buy/sell** | ends at |
|---|---|---|---|---|---|---|
| IBM | 20 | 10 | −10 | $150 | **buy 66.6667** | 20.00% |
| MSFT | 20 | 20 | 0 | $90 | no trade | 20.00% |
| ORCL | 20 | 30 | +10 | $220 | **sell 45.4545** | 20.00% |
| AAPL | 20 | 20 | 0 | $450 | no trade | 20.00% |
| HD | 20 | 20 | 0 | $70 | no trade | 20.00% |


## Where things are

| | |
|---|---|
| `docs/ASSUMPTIONS.md` | what was assumed, and why |
| `docs/MANUAL_TEST_CASES.md` | the full test design — manual and automated |
| `tests/test_rebalance.py` | the automated test cases |
| `src/rebalance.py` | the calculator |
| `src/models.py` | `Security` — one row of the account table |

## Running it

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt

make test     # run the suite
make lint     # check formatting and style
```

The suite reports **14 passed** and **8 xfailed**. The `xfail` cases are not failures —
they assert behaviour the calculator does not yet have, so the gaps are visible on every
run. `pytest -rx` lists each one with the behaviour it expects.
