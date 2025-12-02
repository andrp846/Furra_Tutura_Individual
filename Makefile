check_and_test: FORCE
	mypy terra_futura --strict
	mypy test --strict
	python3 -m unittest 
	pytest test/ -q --no-header

lint: FORCE
	pylint terra_futura/
	pylint test/

format: FORCE
	autopep8 -i terra_futura/*.py
	autopep8 -i test/*.py
	autopep8 -i test/test_integration/*.py
FORCE: ;
