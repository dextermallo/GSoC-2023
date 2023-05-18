<h1><p style="text-align: center;">
GSoC 2023 - CRS: WAF Performance Testing Framework
</p></h1>

> Contributor: [Dexter Chang]()
>
> Organisation: OWASP Foundation
>
> Mentor: 
>
> Link to PRs:
>
> Link to GSOC 2023 Project List: https://summerofcode.withgoogle.com/programs/2023/projects/jdv2MaJR

---

## Table of Contents

[Introduction](#introduction)
- [Project Details](#project-details)
- [Define the problem](#define-the-problem)
- [Why is it important to solve this problem?](#why-is-it-important-to-solve-this-problem)
- [Is there any prior work done on this?](#is-there-any-prior-work-done-on-this)
- [What is the expected outcome?](#what-is-the-expected-outcome?)
- [How will it benefit the community?](#how-will-it-benefit-the-community?)

[Implementation](#implementation)

[References](#references)

---

## Introduction

Performance evaluation is one of the concerns about using ModSecurity and Core Rule Sets. More specifically, people take different approaches to examine the performance, such as stability tests (e.g., the peak of I/O, speed of re-connection) and capacity tests (e.g., use of disks).
However, individuals often miss measuring before/after using the Firewall. Secondly, although there are many open-source utilities (e.g., Apache JMeter, httperf), no specific tool is designed to evaluate performance affected by a firewall. To address the issue, I suggest creating a CLI tool to benchmark the performance with CRS. 

A list of deliverables includes: 
1. Define a framework for testing performance for a generic WAF.
2. Research existing utilities for performance testing on WAF.
3. Create a CLI tool to achieve the framework and define different types of testing performed by the tool. 
4. Implement different types of performance testing. 
5. Integrate the CLI tool with pipelines (e.g., GitHub pipeline).
6. Based on the existing Docker images, perform different evaluations with different configurations/versions.
7. Documentation.

## Project Details

---

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

---

> WIP

## References

---