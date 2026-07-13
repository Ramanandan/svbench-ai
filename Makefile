PY := .venv/bin/python
PIP := .venv/bin/pip

# Homebrew binaries (macOS). On Linux use apt/bioconda equivalents.
BREW_PKGS := python@3.12 samtools bcftools bedtools htslib
PY312 := /usr/local/opt/python@3.12/bin/python3.12

.PHONY: setup tools venv install check clean

setup: tools venv install ## full environment setup

tools: ## install C bioinformatics binaries via Homebrew
	brew install $(BREW_PKGS)

venv: ## create the Python 3.12 virtualenv
	$(PY312) -m venv .venv
	$(PIP) install --upgrade pip

install: ## install python deps (real samplot from source, not the PyPI squatter)
	$(PIP) install -e .
	$(PIP) install "git+https://github.com/ryanlayer/samplot.git"

check: ## import + tool sanity check
	$(PY) -c "import svbench, svbench.review, svbench.annotate, svbench.visualize, svbench.report, svbench.benchmark, svbench.data; print('svbench imports OK')"
	$(PY) -m svbench.cli --help >/dev/null && echo "cli OK"
	@for t in samtools bcftools bedtools tabix; do command -v $$t >/dev/null && echo "$$t OK" || echo "$$t MISSING"; done
	.venv/bin/truvari version
	.venv/bin/samplot plot --help >/dev/null && echo "samplot OK"

clean:
	rm -rf outputs/*/images outputs/*/*.vcf.gz
