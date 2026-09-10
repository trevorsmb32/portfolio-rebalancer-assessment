PY := ./.venv/bin/python3
RUFF := ./.venv/bin/ruff

fix:                       ## auto-fix lint + formatting
	$(RUFF) check --fix src/ tests/
	$(RUFF) format src/ tests/

lint:                      ## check without fixing
	$(RUFF) check src/ tests/
	$(RUFF) format --check src/ tests/

test:                      ## run the test suite
	$(PY) -m pytest -v

debug:                     ## run tests with print output shown (make debug K=fat_finger)
	$(PY) -m pytest -s -vv $(if $(K),-k "$(K)")

pdb:                       ## drop into the debugger at the first failure
	$(PY) -m pytest --pdb $(if $(K),-k "$(K)")

check: fix test            ## fix, then test
