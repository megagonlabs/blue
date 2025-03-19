# What is Blue?

Blue is an agent orchestration platform for building and deploying applications with agentic workflows for the enterprise. 

A key target use-case of Blue is enterprise, i.e. integrate an existing enterprise infrastructure with advanced AI, LLMs, and beyond for a wide-variety of enterprise use-cases. We aim to leverage what already exist in the enterprise infrastructure, i.e. existing APIs, models, and data in their original source, format, and systems and couple them with new capabilities.

Blue is currently a research project to explore the design space of agent orchestration systems, to support a variety of use-cases: from data and domain-agnostic to data-aware design, from non-interactive use cases to conversational interaction, from fixed workflows to ad-hoc workflows with planners, from purely textual interaction to interactive agents with user interfaces, and beyond. 

# How does Blue work?

To help facilitate ‘Agentic for Enterprise’ we are introducing several concepts in the design of our framework, including:
- **Streams** to facilitate data, control, and communication among agents
- **Messages** in streams to standardize of data and instructions for agents
- **Registries** to capture metadata about data, agents and beyond
- **Session** to provide context (and shared memory) for computation
- **Plans** to represent workflows and execution of agents

![Stream](./docs/images/concepts.png)

To get a glimpse of where we are heading with agentic architectures, read our papers:

* [A Blueprint Architecture of Compound AI Systems for Enterprise](https://arxiv.org/abs/2406.00584) [Compound AI Systems Workshop](https://sites.google.com/view/compound-ai-systems-workshop/home)
* [Orchestrating Agents and Data for Enterprise: A Blueprint Architecture for Compound AI]() [Data-AI Systems Workshop at ICDE'25](https://dais-workshop-icde.github.io/)

</br>

# What can you build with Blue?

Here are a few examples to inspire you to build with blue:

* a set of agents that convert natural language to SQL, executes, and summarizes results in natural language 
* agents that produces interactive graphical user interfaces and visualizations with your data (e.g. self-service business intelligence) 
* a conversational agent that interfaces to existing predictive models and APIs (e.g. job search agent with predictive models and data)
* agents that execute workflows processing text data, extracting and populating databases.


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
