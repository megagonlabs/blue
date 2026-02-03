# Searchable Custom Logger

A **structured, searchable logging framework** for Blue that turns agent execution events into **queryable data**, not just text logs.

This module extends `CustomLogger` with:
- Structured JSON event emission
- Pluggable storage backends
- Full-text and faceted search via Redis + RediSearch
- First-class support for agent, plan, operator, and session context

---

## Why This Exists

Traditional logs are:
- Free-text
- Grep-based
- Host-centric
- Hard to aggregate or analyze

**Agentic systems need more.**

The Searchable Custom Logger makes logs:
- **Structured**
- **Searchable**
- **Context-aware**
- **Evaluation-ready**

This enables:
- Debugging agent behavior
- Tracing plans and operators
- Analyzing failures and fallbacks
- Offline evaluation and observability

---
