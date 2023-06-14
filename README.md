<h1><p style="text-align: center;">
GSoC 2023 - CRS: WAF Performance Testing Framework
</p></h1>

> Contributor: [Dexter Chang](https://github.com/dextermallo)
>
> Organisation: OWASP Foundation
>
> Mentor: fzipitria, Christian Folini
>
> Link to GSOC 2023 Project List: https://summerofcode.withgoogle.com/programs/2023/projects/jdv2MaJR

---

### Table of Contents

- [Introduction](#introduction)
    - [Define the problem](#define-the-problem)
    - [Is there any prior work done on this?](#is-there-any-prior-work-done-on-this)
- [Solution](#solution)
    - [Sidecar Pattern](#sidecar-pattern)
    - [Architecture](#architecture)
    - [Use case](#use-case)
    - [Matrices](#matrices)
        - [Sources of Matrices](#sources-of-matrices)
        - [Types of Matrices](#types-of-matrices)
    - [Limitations](#limitations)
- [Implementation](#implementation)
- [References](#references)

---

# Introduction

Performance evaluation is one of the concerns when using [OWASP Core Rule Sets](https://coreruleset.org/docs/). More specifically, people take different approaches to examine the performance, such as stability tests (e.g., the peak of I/O, speed of re-connection, RTT) and capacity tests (e.g., use of disks). However, individuals often miss measuring the performance when using 3rd-party library, namely before/after using the WAFs.

While performance evaluation is a challenge for the users, it is an obstacle for the community as well. Although there are automated tests in Core Rule Set when releasing the project (using another library called [go-ftw](https://github.com/coreruleset/go-ftw)), performance tests are yet to be integrated into the pipeline.

A list of deliverables in this GSoC project includes:
1. Define a framework for testing performance for a generic WAF using Core Rule Set (e.g., ModSecurity 2.9, 3.0+, and Coraza).
2. Research existing utilities for performance testing on WAF.
3. Integrate features into `go-ftw` to achieve the framework.
4. Implement different types of performance testing.
5. Integrate the CLI tool with pipelines (e.g., GitHub pipeline).
6. Based on the existing Docker images, perform different evaluations with different configurations/versions.
7. Documentation.

## Define the problem

Quoted from the [original proposal](https://owasp.org/www-community/initiatives/gsoc/gsoc2023ideas): 

"... Experience shows you do not really know the performance of a rule until you have tried it out. If you want to test it against a variety of payloads it’s quite a lot of manual work."

"...So the idea is to design a facility (typically a docker container) that is being configured with a rule and then used to test this rule with a variety of payloads and returns a standard report about the performance of the rule."

"Bonus points if multiple engines are covered (ModSecurity 2, libModSecurity 3, Coraza, …)"

Breaking down, we aim to fulfil the following:
- **Precision and accuracy**: One of the concerns about performance testing is that the test itself also affects the performance. Therefore, we need to reduce the performance impact of the testing framework as much as possible. Specifically, considering from client-server model, the server-side log is desired because the network latency and other friction (e.g., computational resource waste) are ignored.
- **Test with different payloads**: We need to test with different payloads to see if the rule works as expected.
- **Compatibility**: If feasible, the testing framework should be compatible with different engines.

## Is there any prior work done on this?

We have reviewed some works in [#3](https://github.com/dextermallo/GSoC-2023/issues/3).
Some literature to see what kinds of matrices can be utilised for testing in [#5](https://github.com/dextermallo/GSoC-2023/issues/5)

# Solution 

## Sidecar Pattern

[Sidecar pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sidecar), as the name suggests, is a pattern that adds a sidecar container to the main container. The sidecar container is responsible for a specific task, such as logging, monitoring, etc. 

Utilising sidecar patterns for performance tests has some advantages:
- **Isolation**: Sidecar pattern isolates performance-related tasks from the main application. This isolation helps ensure that the performance of the sidecar components does not impact the primary application's performance.
- **Observability**: We can easily integrate monitoring and logging functionalities without modifying the main application's code in a sidecar pattern. Therefore, we can collect performance metrics and analyze them separately from the primary application, providing valuable insights into its behaviour under various load conditions.
- **Modularity**: The sidecar pattern promotes modularity by decoupling functionalities into separate components, which is easier to update or replace specific functionalities without affecting the entire application.

In this case, we can utilise the sidecar pattern to test the performance of the WAF. The merits contributed by the sidecar pattern help to achieve the goals (precision and accuracy, testing with different payloads, compatibility) of this project.

## Architecture

![Architecture diagram](./assets/Overall%20System%20Diagram.png)

The figure depicts an overview of adapting sidecar patterns into performance testing. In this architecture, **the original service remains unchanged** (so it is safe for the original use, which is from the client to the server), but we can evaluate performance.

The easiest way to explain the architecture is that a collector collects the matrices, passes them through a parser, synthesis them, and builds a report.

Here are explanations of each component:

1. **Client**: The client is responsible for sending requests to the WAF. It can be a CLI tool or a web application.
2. **WAF + CRS**: The WAF is the main application, which is responsible for filtering requests.
3. **Request Decorator Proxy**: The decorator proxy, as the name suggests decorates the request or fulfils other purposes for testing. For instance
    - Fuzz: fuzzing payloads and sending them to the WAF. e.g., 
    ```sh
    # assume we are testing this rule
    SecRule REQUEST_METHOD "@rx ^(?:GET|HEAD)$"

    # fuzz proxy can help us to add random payloads for two purposes:
    # 1. Adding/Changing/Removing payloads will affect the result
    # For instance, in this case, if we use POST instead of GET, it will become a false positive

    # 2. Adding/Changing/Removing payloads which will not affect the result
    # In this case, if we add a header "Content-type"="xml"
    # It will not affect the result
    ``` 
    - Other Decorators: `WIP`
4. **Server-level Collector**: server-level collectors collect the matrices from the server. There are two types of server-level collectors:
    - without integration: the server-level collector collects the matrices from the server logs. Or relies on other 3rd utils like cAdvisor.
    - with integration: some server-level collectors require integration to the existing service. For instance, ElasticSearch and Prometheus require the service to be instrumented with their client library (e.g., HTTP endpoints).
5. **Host-level Collector**: The host-level collector collects the matrices mostly the same as server-level collectors. However, the host-level collector collects the matrices from the host machine (e.g., using ePBF).  
6. **Data Parser**, **Statistic Builder**, and **Comparison Report Builder**: These are the components that parse the data and build the report. The data parser parses the data into a unified format (e.g., JSON). The statistic builder builds the report based on the unified format. The comparison report builder compares the before/after report and generates a comparison report.

## Use case

As a contributor, I want to test code changes for a regex in the WAF. For example:

```sh
# original
SecRule REQUEST_METHOD "@rx ^(?:GET|HEAD)$" \

# after a code change
SecRule REQUEST_METHOD "@rx ^(?:GET|POST|HEAD)$" \
```

They can do a performance test with the following steps:

1. Run the WAF (e.g., docker-compose.yaml). Note that only the rules which are supposed to test should be imported.
2. Start the sidecar services. For instance:
    1. Host-level collector: `WIP`
    2. Server-Level Collector: `WIP`
    3. Client: `WIP`
3. Run your test. (e.g., using go-ftw and specifying a YAML file)
4. Run a script to generate a performance report. The data will be parsed into a unified format (e.g., JSON) and build the report (before_report).
5. doing code changes...
6. repeat 2, 3, and 4 to generate another performance report (after-report)
7. compare before_report and after_report to see the before/after performance differences. (e.g., via another script)

## Matrices

The matrices can be classified based on sources and types:

### Sources of Matrices

The sources of matrices can be classified into three categories:

|                              | Host-level                                   | Server-level                                                                 | Client-level                           |
|------------------------------|----------------------------------------------|------------------------------------------------------------------------------|----------------------------------------|
| Description                  | matrices are collected from the host machine | matrices are collected from the server                                       | matrices are collected from the client |
| Example of Matrices          | CPU, memory, network I/O, etc.               | CPU, memory, network I/O, the number of requests, the number of errors, etc. | RTT, top 10% response time             |
| Accuracy                     | High                                         | Mid                                                                          | Low                                    |
| Difficulty of Implementation | High                                         | Mid                                                                          | Low                                    |

### Types of Matrices

1. Server-side: Most of the server-side matrices relate to hardware, such as:
    - CPU
    - Memory
    - Network I/O
    - Disk I/O
2. Client-side: Related to the client's perspective. For example:
    - **Error rate**: We can compare before/after the test case pass percentage. Also, we can use `error.log` to compare the diff and see what happens
    - **Connection Time**: by [adding configuration in nginx](https://stackoverflow.com/questions/69534518/what-does-connection-time-mean-in-nginx)
    - **RTT**: currently in stdout
    - **Concurrency Maximum**: use utils such as [ab](https://httpd.apache.org/docs/2.4/programs/ab.html)
    - **average RTT, average top 10% RTT, average last 10% RTT**: ditto
    - etc.

> **Why do we need client-side matrices**: We need to know the performance from the client's perspective. For example, if the server-side matrices are good, but the client-side matrices are bad, it means that the server-side is not the bottleneck. Therefore, we need to collect both server-side and client-side matrices.

## Limitations

- **Log Formats**: Different WAFs have different log formats. Therefore, we need to write different parsers for different WAFs.
- **Evaluation of Accuracy and Precision**: Although the performance test is based on comparing before/after a code change, assuming one of them (before or after) is captured incorrectly, the result is not accurate as well. We should find a way to ensure the method we choose is reliable.
- **False Positive**: When performing fuzz testing, it is critical that we define a minimal scope for the random part. Otherwise, It is hard to evaluate whether the test is legit. For example:
    ```sh
    # assume we are testing this rule
    SecRule REQUEST_METHOD "@rx ^(?:GET|HEAD)$"

    # Therefore, the true positive is GET request and the false positive is POST request
    # In this case, we can perform fuzz testing with GET and POST request
    ```

# Implementation

## PRs

## References
