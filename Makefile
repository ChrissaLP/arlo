deps:
	sudo apt install python3.7 python3-pip nodejs libpython3.7-dev libpq-dev
	python3.7 -m pip install pipenv
	sudo npm install -g yarn
	sudo apt install postgresql

# this should only be used for development
initdevdb:
	sudo -u postgres psql -c "create user arlo superuser password 'arlo';"
	sudo -u postgres psql -c "create database arlo with owner arlo;"

install:
	pipenv install
	yarn install
	yarn --cwd arlo-client install
	yarn --cwd arlo-client build

install-development:
	pipenv install --dev
	yarn install
	yarn --cwd arlo-client install

resettestdb:
	FLASK_ENV=test make resetdb

resetdb:
	FLASK_ENV=$${FLASK_ENV:-development} pipenv run python resetdb.py

dev-environment: deps initdevdb install-development resetdb

typecheck-server:
	pipenv run mypy .

format-server:
	pipenv run black .

lint-server:
	find . -name '*.py' | xargs pipenv run pylint --load-plugins pylint_flask_sqlalchemy

test-client:
	yarn --cwd arlo-client lint
	yarn --cwd arlo-client test

# To run tests matching a search string: TEST=<search string> make test-server
# To run specific test files: FILE=<file path> make test-server
# To pass in additional flags to pytest: FLAGS=<extra flags> make test-server
test-server:
	FLASK_ENV=test pipenv run pytest ${FILE} \
		-k '${TEST}' --ignore=arlo-client -vv ${FLAGS}

test-server-coverage:
	FLAGS='--cov=. ${FLAGS}' make test-server

test-math:
	FILE=tests/audit_math_tests make test-server

test-utils:
	FILE=tests/util_tests make test-server

test-routes:
	FILE=tests/routes_tests make test-server