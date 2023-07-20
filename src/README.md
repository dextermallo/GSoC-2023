# 0. Initialization

```sh
# To run the performance test, you can initialize the environment by running the following command:
source ./init.sh

# and initialize the python environment
poetry install
```

# 1. Start a test

```sh
# One-liner to start your performance test, where --test-name represents the name of the test, and --utils represents the util for testing.
# by default, the command will compare HEAD (the latest commit) and . (which is the current directory) to get the changes
poetry run collect --test-name test --utils ftw

# or multiple utils at a time
poetry run collect --test-name test --utils ftw,locust,cAdvisor

# specify your commit
poetry run collect --test-name test --before $GITHUB_COMMIT_A --after $GITHUB_COMMIT_B --utils ftw

# If you want to test on the latest cahanges, you can use the following command:
poetry run collect --test-name "latest-command-changes" --utils "ftw" --before HEAD^ --after HEAD

# The test will generate these files, directories, and corresponding services automatically:
# -- Project directory
#     |-- report (report data created by command `poetry run report`)
#          |-- $TEST_NAME
#               |-- _before_<util>_report
#     |-- data (raw data collected from the util)
#          |-- $TEST_NAME
#               |-- <state>_<util>.data (e.g., before_ftw.json, after_locust_stats_history.json)
#     |-- tmp (stores the temprary files during the test)
#          |-- $TEST_NAME
#               |-- after-rules (the rules after the changes)
#               |-- before-rules (the rules before the changes)
#               |-- test-cases (the test cases related to the changed rules)
#               |-- exec.py (the script created by locust to run the test)

# Specifically, the command has the following options:
# --test-name       (required): the name of the test
# --utils           (required): util for testing, if there is multiple utils, use comma to separate them
# --before          (optional): git commit hash, default=HEAD
# --after           (optional): git commit hash, or a path to a directory (default=.), Noted that only --after supports the local path.
# --raw-output      (optional): default is ./data
# --output          (optional): default is ./report
# --waf-endpoint    (optional): default is http://localhost:80

# @TODO
# --clean-history   (optional): default is false, clean the tmp
```

# 2. Get reports

```sh
# --test-name       (required)
# --threshold-conf  (optional): default is none
# --raw-output      (optional): default is ./data
# --output          (optional): default is ./report
# --format          (optional): default is text
# --utils           (optional): default is all

# without threshold
poetry run report --test-name test

# using threshold
poetry run report --test-name test --utils ftw --threshold "./config" -format text
```

# 3. Other commands

```sh
# other command
poetry run check-threshold --file $THRESHOLD_CONF
poetry run check-threshold --file $THRESHOLD_CONF
```

# 4. Pipeline Integration `(WIP)`

# 5. Write your Own Data Collector `(WIP)`

# 6. Tests

To run the unit tests and yield a test coverage report of the framework, you can follow the commands below:

```sh
#run unit tests
poetry run coverage run -m pytest

# create a coverage report
poetry run coverage report -m
```