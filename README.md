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
    - [Project Details](#project-details)
    - [Define the problem](#define-the-problem)
    - [Why is it important to solve this problem?](#why-is-it-important-to-solve-this-problem)
    - [Is there any prior work done on this?](#is-there-any-prior-work-done-on-this)
    - [What is the expected outcome?](#what-is-the-expected-outcome)
    - [How will it benefit the community?](#how-will-it-benefit-the-community)
- [Implementation](#implementation)
- [References](#references)

---

## Introduction

Performance evaluation is one of the concerns when using [OWASP Core Rule Sets](https://coreruleset.org/docs/). More specifically, people take different approaches to examine the performance, such as stability tests (e.g., the peak of I/O, speed of re-connection, RTT) and capacity tests (e.g., use of disks). However, individuals often miss measuring the performance when using 3rd-party library, namely before/after using the WAFs.

While performance evaluation as a challange for the users, it as a obstacle for the project cumminity as well. Although there are automated tests in Core Rule Set when releasing the project (using another library called [go-ftw](https://github.com/coreruleset/go-ftw)), performance tests are yet to be integrated into the pipeline.

A list of deliverables in this GSoC project includes:
1. Define a framework for testing performance for a generic WAF using Core Rule Set (e.g., ModSecurity 2.9, 3.0+, and coraza).
2. Research existing utilities for performance testing on WAF.
3. Integrate features into `go-ftw` to achieve the framework.
4. Implement different types of performance testing.
5. Integrate the CLI tool with pipelines (e.g., GitHub pipeline).
6. Based on the existing Docker images, perform different evaluations with different configurations/versions.
7. Documentation.

## Project Details

> WIP

### Define the problem

> WIP

### Why is it important to solve this problem?

> WIP

### Is there any prior work done on this?

> WIP

### What is the expected outcome?

> WIP

### How will it benefit the community?

> WIP

## Implementation

### PRs

## References
