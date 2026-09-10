# Test Strategy & Scope Assumptions

This document outlines the core assumptions, rationale, and scope boundaries applied during test case design for the rebalancer MVP.

---

## 1. Assumptions & Design Scope

* **Test Generation Scope:** The goal is strictly to validate the current MVP rebalancer implementation, not to add or propose extra product requiremnets but to still test imlpiciet requiremtns
* **Fractional Shares & Precision:** Since rounding rules and whole-share constraints were not specified, calculations retain precision up to the maximum decimal length without arbitrary rounding.
* **Minimal Data Model:** The `Security` object includes only attributes explicitly defined in the provided examples.
* **100% Vesting:** The test suite assumes a fully vested account balance of $100,000. Partial vesting logic is excluded.
* **Domain Knowledge:** Unspecified domain rules or external financial logic were intentionally omitted rather than assumed.
* Test also contain x failed scenarios scenarios that I believe would cause issue if released in prodcution so the are highlighted as soon as possible.
* **Test Types & Coverage:**
  * **Automated Tests:** Assume direct execution without a user interface.
  * **Manual Tests:** Include basic end-user flows assuming a UI context.
  * **Non-Functional Tests:** Load, stress, and concurrency testing are out of scope.
  * Negative test cases are in cluded to run for behaviour qa would expect to work but does not example inputitng negative values


---

## 2. Baseline Rules

All test cases trace directly back to these eight fundamental requirements:

1. An account holds a list of securities.
2. The account total asset value is $100,000 (100% vested).
3. Each security has a target allocation percentage.
4. Each security has a current allocation percentage.
5. Each security has a unit price.
6. Target variance measures deviation: negative (`-`) indicates a **Buy**, positive (`+`) indicates a **Sell**.
7. Output specifies the exact number of shares to buy or sell for each security.
8. The target state is zero target variance across all holdings.