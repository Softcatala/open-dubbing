.PHONY: dev run-tests run-e2e-tests publish-release

PATHS = open_dubbing/ tests/ e2e-tests/

dev:
	python -m black $(PATHS)
	python -m flake8 $(PATHS)
	python -m isort $(PATHS)

run-tests:
	python -m pytest tests/

run-e2e-tests:
	CT2_USE_MKL="False" CT2_FORCE_CPU_ISA='GENERIC' KMP_DUPLICATE_LIB_OK="TRUE" python -m pytest e2e-tests/

publish-release:
	rm dist/ -r -f
	python setup.py sdist bdist_wheel
	python -m  twine upload -u "__token__" -p "${PYPI_API_TOKEN}" --repository-url https://upload.pypi.org/legacy/ dist/*

