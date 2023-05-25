# Week 1

> May 11, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1683814881754659 

1. Highlights
    - Weekly meeting if possible (Thu)
    - Changes on the schedule/work items (To be discussed)
    - The proposal aims to work on an overall performance framework, whereas the original initiative is to identify performance changes when a single SecRule is updated (e.g., regex changes). We will focus on a single SecRule first, which can be extended to an overall performance test.
    - The initiative of the framework is to be flexible enough to adapt to other WAFs (e.g., Coraza). In the first stage, We will start with ModSecurity 2.9.
    - As a public-facing application, testing the functionality is essential. (Adds into the schedule)

2. Ideas
    - Performance tests cannot rely on a single payload. Fuzzing might be a good way to yield multiple payloads to support the test
    - Before the development, defining the matrix we want is necessary. Meanwhile, we also need to consider what matrix/data we can get.

3. To-dos
    - Review/update the proposals.
    - Establish a work environment. (ModSecurity 2.9)
    - Research on existing performance testing framework.
    - Reading documentations.

# Week 2

> May 25, 2023
>
> Thread: https://owasp.slack.com/archives/C03EXFGM4FJ/p1685040293587099

1. Progress
    - [x] [#1](https://github.com/dextermallo/GSoC-2023/issues/1) Review and update the proposals
    - [x] [#2](https://github.com/dextermallo/GSoC-2023/issues/2) Establish a work environment
    - [ ] [#3](https://github.com/dextermallo/GSoC-2023/issues/3) Research on existing performance testing framework (`WIP`: collect some sources but yet to read)
    - [ ] Reading documentation (CRS/go-ftw) (`WIP`: learning some args and workflow)
    - [x] Reading some suggestions for GSoC and other community topics 
    - [x] A draft of the framework (under discussion)

2. Findings & Ideas
    - N/A

3. Impediments
    - The complexity of implementing CRS with services. (e.g., different ways to configure. When I attempted to remove a SecRule from ModSecurity v3 using nginx, I found multiple ways from the Internet but none of them worked, such as modifying nginx.conf or crs-setup.conf. Keep working on it.)

4. Others
    - review/add contexts for attempts to remove a SecRule from ModSecurity v3 using nginx. (since issues happened on nginx recently as well)
    - Focus on one feature at a time.
    - Applying integration into the existing utility (go-ftw) might not be a good idea. Although less wheel-rebuild, the complexity and purity (functionality) will be affected.
    - The framework is way more important than tech details.

5. Next Actions
    - Continue researching other approaches (benchmarking in the same container; using another container to test the WAF container; server-side testing)
    - Update the proposal
    - Clarify/refine the draft of the framework
    - Research more about different matrix/matrix collection