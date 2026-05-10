# PrivateBox GRC OS — build pipeline targets

PYTHON ?= python3
FRAMEWORKS := frameworks/iso-27001/iso-27001.yaml frameworks/iso-27701/iso-27701.yaml frameworks/eu-ai-act/eu-ai-act.yaml frameworks/iso-42001/iso-42001.yaml frameworks/popia/popia.yaml

.PHONY: help validate crosswalks data dev build all clean

help:
	@echo "PrivateBox GRC OS — build targets"
	@echo ""
	@echo "  make validate     Run schema v2 validator on every framework YAML"
	@echo "  make crosswalks   Regenerate crosswalk candidates report"
	@echo "  make data         Rebuild os/src/data.json from YAMLs"
	@echo "  make dev          Start vite dev server (localhost:5173)"
	@echo "  make build        Production build of the OS"
	@echo "  make all          validate + data + babel-parse OS"
	@echo "  make clean        Remove generated data.json and OS build output"

validate:
	@echo "── Validating $(words $(FRAMEWORKS)) framework(s) ──"
	@for fw in $(FRAMEWORKS); do \
		echo ""; \
		echo "── $$fw ──"; \
		$(PYTHON) build/validate_framework.py $$fw || exit 1; \
	done
	@echo ""
	@echo "All frameworks validate clean."

crosswalks:
	@echo "── Regenerating crosswalk candidates ──"
	$(PYTHON) build/crosswalk_candidates.py $(FRAMEWORKS) > docs/crosswalk-candidates-report.md
	@echo "Report written to docs/crosswalk-candidates-report.md"

data:
	@echo "── Building os/src/data.json from YAMLs ──"
	$(PYTHON) build/build_os_data.py $(FRAMEWORKS) os/src/data.json
	@echo "Built os/src/data.json"
	@ls -lh os/src/data.json | awk '{print "  " $$5 "  " $$NF}'

dev:
	cd os && npm run dev

build:
	cd os && npm run build

all: validate data
	@echo ""
	@echo "── Babel-parsing assembled OS (optional; requires npm install) ──"
	@if [ -d os/node_modules/@babel/parser ]; then \
		cd os && node -e "const p=require('@babel/parser'); const fs=require('fs'); p.parse(fs.readFileSync('src/App.jsx','utf8'),{sourceType:'module',plugins:['jsx']}); console.log('OS Babel parse: OK');"; \
	else \
		echo "  (skipped — run \`cd os && npm install\` first to enable JSX parse check)"; \
	fi
	@echo ""
	@echo "── All checks passed ──"

clean:
	rm -f os/src/data.json
	rm -rf os/dist os/node_modules/.vite
