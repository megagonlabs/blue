# What is Blue?

Blue is an agent orchestration platform to coordinate data and work in an enterprise AI system, comprised of agents and other components to perform complex tasks with workflows, accessing data, models, and APIs in the enterprise.

We are building Blue to explore the design space of agent orchestration systems, to support a variety of use-cases: from data and domain-agnostic to data-aware design, from non-interactive use cases to conversational interaction, from fixed workflows to ad-hoc workflows with planners, from purely textual interaction to interactive agents with user interfaces, and beyond. Blue is designed such that it can be configured to support any of these use cases.

A key target use-case of Blue is enterprise, i.e. integrate an existing enterprise infrastructure with advanced AI, LLMs, and beyond for a wide-variety of enterprise use-cases. We aim to leverage what already exist in the enterprise infrastructure, i.e. existing APIs, models, and data in their original source, format, and systems and couple them with new capabilities.

Below is an overview of the Blue infrastructure, with the key touchpoints to an enterprise infrastructure:

![Stream](./docs/images/overview.png)

In Blue, key components of the AI system are:

- data lake(s) to store and query data from, consisting of a multitude of databases
- data registry, serving as a metadata store for data sources, with capabilities to discover and search data, and eventually query data from the sources
- data planner(s), modeled as an agent, utilizing metadata (performance and beyond) in the data registry, provide crucial functionality to generate query plans
- agent registry, serving as a metadata store for agents, with capabilities to search agent metadata (e.g. descriptions, inputs, outputs)
- agent(s) providing a wide range of functionality, from calling APIs, interfacing with LLMs, to running predictive models, etc.
- task planner(s), also modeled as an agent, taking initial user/agent input and creating execution plans, utilizing metadata in the agent registry, as well as basic operators to serve as glue between inputs and outputs.
- task coordinator(s), modeled as an agent,coordinate and monitor execution progress, once a plan is created.
- operators, supporting the need for basic common capabilities such as data transformation and beyond, as executable functions accessible to the coordinator to invoke
- orchestration, supporting infrastructure and streams to govern the flow of data and instructions among all agents within a user session
- a conversational user interface where users can create sessions, add agents to their conversation, interact with them, and accomplish tasks.
- a python API to allow other modalities where a multi-agent system can be utilized programatically, such as developing APIs.

</br>

# What can you build with Blue?

Here are a few examples to inspire you to build with blue:

* a fact-checker API to examine LLM generated text against propriery data (e.g. fact-check resume)
* a conversational agent that uses backend models and APIs (e.g. career support agent with predictive models and application data)
* a sophisticated search exploiting LLMs (e.g. search jobs interfacing to ranking models)
* an interactive graphical user experience for complex workflows, visualizations (e.g. profile builder)
* an API to convert user text into database queries (e.g. natural language to SQL)

# Want to try out blue demos?

You can try out a demos on our [blue-examples repository!](http://github.com/rit-git/blue-examples)

</br>

Sounds interesting? Want to learn more? Read documentation below.

# Outline of the Documentation:

* [Orchestration Concepts](ORCHESTRATION-CONCEPTS.md) to learn more about Blue concepts
* Install your own Blue environment
  * [Local Installation](LOCAL-INSTALLATION.md) more suited for trying out and development 
  * [SWARM Deployment](SWARM-DEPLOYMENT.md) more suited for staging and production deployment
* [Quickstart Guide](QUICK-START.md) to learn basics of using blue web application.
* [Demos](https://github.com/rit-git/blue-examples/tree/v0.9) to try out agentic demos with base and experimental agents
* [Build](BUILD.md) to learn how to build and deploy from repository
* [Development](DEVELOPMENT.md) to learn more about how to develop with Blue
* [Access Control](ACCESS-CONTROL.md) to learn more about access control with roles

</br>
</br>
