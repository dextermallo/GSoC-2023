# Implementation

This is a documentation of the implementation of the project. It takes five steps to collect the data and analyze the performance:

1. install all the prerequisites
2. start a runnable CRS-supported WAF
3. create .env files and install dependencies
4. run a data collector and parser if necessary
5. run the visualizer to compare the results of changes

# 1. Prerequisites

Before starting the project, you need to install the following prerequisites:

- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/) (>= 3.9.0)
- [Poetry](https://python-poetry.org/)
- A runnable CRS-supported WAF (See Section: [2. Start with a WAF](#2-start-with-a-waf))
- Some data collectors may require additional prerequisites. Related information can be found in each sub-section.

# 2. Start with a WAF

You can follow the [quick start guide](https://coreruleset.org/docs/deployment/quick_start/) from the core rule set to start a CRS-supported WAF. Or you can use `docker compose` and clone the project to start rapidly:

```sh
git clone git@github.com:coreruleset/coreruleset.git

# specify a service name (modsec2-apache or modsec3-nginx)
docker compose -f './coreruleset/tests/docker-compose.yml' up -d  <service-name>
```

Noted that if you are only interested in the performance of the CRS **on one specific rule**, you should load as minimal rules as possible. For example, you can load the `REQUEST-920-PROTOCOL-ENFORCEMENT.conf` rule by adding the following line to the `tests/docker-compose.yml` file and removing the `../rules` volume:

```yaml
    volumes:
      - ./logs/modsec2-apache:/var/log:rw
      - ../rules/REQUEST-920-PROTOCOL-ENFORCEMENT.conf:/opt/owasp-crs/rules/REQUEST-920-PROTOCOL-ENFORCEMENT.conf:ro
      # - ../rules:/opt/owasp-crs/rules:ro
```

# 3. Create ENV and Install Dependencies

To create the `.env` file, you can copy the `.env.example` file and rename it to `.env`. Then, you can change the values of the variables in the `.env` file.

To install dependencies with poetry and use the virtual environment, follow the commands below:
```sh
# use the virtual environment
poetry env use 3.9.6

# install dependencies
poetry install
```

# 4. Data Collector

Next, once the WAF service is up and running, you can decide which data collector you want to use. Currently, there are several data collectors available:

## 4.1. cAdvisor

> *WIP: the data collector is planned to modify on the usage to make it more comprehensive to collect the data.*

To use cAdvisor as a data collector, you can follow the steps below:

```sh
# Start cAdvisor service using Docker before collecting data
# Ref: https://github.com/google/cadvisor/tree/master#readme
sudo docker run \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --publish=8080:8080 \
  --detach=true \
  --name=cadvisor \
  --privileged \
  --device=/dev/kmsg \
  gcr.io/cadvisor/cadvisor:v0.45.0

# Next, use poetry to run the collector, noted that you will need to specific a group name
# As an identifier when analyzing the data. For example, `ca-before-rule-920170-change`
# if the group name is not specified, it will create a random group name directly.
GROUP_NAME=ca-before-rule-920170-change
poetry run collect-cAdvisor $GROUP_NAME

# Once it is up and running, it will be executed in the foreground,
# you can start to test your rule changes. For instance, using go-ftw:
# Ref: https://github.com/coreruleset/go-ftw
go-ftw run -d $TEST_FILE_LOCATION -i 920170 --show-failures-only

# Once the test is finished, you can stop the collector by pressing `Ctrl + C`
# Then, apply your rule changes and start the collector again with another group name:
# `ca-after-rule-920170-change`
```

## 4.2. go-ftw

> Prerequisite: Before using go-ftw data collector, you will need to install go-ftw and create its configuration. Please refer to the [Install](https://github.com/coreruleset/go-ftw) in go-ftw.
> 
> For the configuration, you can copy the `.example.ftw.yaml` file and rename it to `.ftw.yaml`. and change the values of the variables in it.

```sh
# Start go-ftw service using Docker before collecting data with variables:
# $GROUP_NAME (Optional): a group name as an identifier when analyzing the data. If not specified, it will create a random group name directly.
# $RULE_ID (Optional): a rule id to test. If not specified, it will test all the rules.
poetry run collect-ftw $GROUP_NAME $RULE_ID
```

## 4.3 eBPF `(WIP)`

## 4.4 locust

To run locust data collector, you can use the following command:

```sh
# Start locust service using Docker before collecting data with variables:
# $GROUP_NAME (Optional): a group name as an identifier when analyzing the data. If not specified, it will create a random group name directly.
# $RULE_ID (Required): a rule id to test. If not specified, it will test all the rules.
poetry run collect-locust -g $GROUP_NAME -id $RULE_ID
```

# 5. Visualizer

> *WIP: There is a planned refactor on the visualizer. As the project is currently under the rapid development, we suggest not using this feature*

Visualizer is a tool to compare the performance of the CRS before and after the rule changes. To use the visualizer, you can follow the steps below:

```sh
# enter interaction mode
poetry run visualize

# Once it is up and running, you can use the following commands to add data sources:
add-group $GROUP_NAME_A # e.g., add-group ca-before-rule-920170-change
add-group $GROUP_NAME_A # e.g., add-group ca-after-rule-920170-change
```

# Pipeline Integration `(WIP)`

# Write your Own Data Collector and Parser `(WIP)`

# Tests

To run the unit tests and yield a test coverage report of the framework, you can follow the commands below:

```sh
#run unit tests
poetry run coverage run -m pytest

# create a coverage report
poetry run coverage report -m
```