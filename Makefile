PROJECT = lisco

MANIFEST_DIR = manifest
REQUIREMENT_FILE = $(MANIFEST_DIR)/requirements.txt

PIP_MIRROR_SOURCE = https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
PYTHON_VERSION = $(shell python --version)


.PHONY: install-requirements
install-requirements:
	pip install -r $(REQUIREMENT_FILE)  -i $(PIP_MIRROR_SOURCE)

.PHONY: release-requirements
release-requirements:
	echo "# $(PYTHON_VERSION)" > $(REQUIREMENT_FILE)
	pip list --format=freeze >> $(REQUIREMENT_FILE)

.PHONY: test
test:
	coverage run --rcfile=./.coveragerc -m pytest -s -v
	coverage report --rcfile=./.coveragerc


.PHONY: test-all
test-all:
	coverage run --rcfile=./.coveragerc -m pytest -s
	coverage report --rcfile=./.coveragerc


TARGET_DIR = pkg/

.PHONY: reformat
reformat:
	black $(TARGET_DIR)
	flake8 $(TARGET_DIR) --max-line-length=120
	isort $(TARGET_DIR)

