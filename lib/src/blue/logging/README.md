# Searchable Custom Logger

A **structured, searchable logging framework** for Blue that turns agent execution events into **queryable data**, not just text logs.

This module extends `CustomLogger` with:
- Structured JSON event emission
- Pluggable storage backends
- Full-text and faceted search via Redis + RediSearch
- First-class support for agent, plan, operator, and session context



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

## Core Components

### LogStore (Abstract Interface)

```python
class LogStore(ABC):
    @abstractmethod
    def write(self, record: Dict[str, Any]):
        pass


Defines a pluggable backend contract

Decouples logging from storage

Enables future backends (Postgres, S3, OpenTelemetry)

RedisLogStore

A Redis-backed implementation using:

RedisJSON for structured storage

RediSearch for indexing and search

Key Features

Automatic index creation on startup

Namespaced Redis keys by platform, context, and date

Catch-all _blob field for semantic full-text search

Redis Key Format

PLATFORM:{platform_id}:LOGS:DATA:
  SESSION:{session_id}:
  AGENT:{agent}:
  OPERATOR:{operator}:
  YYYYMMDD:{uuid}

This supports both:

Prefix-based key lookup

Full-text and faceted search

RediSearch Index Schema

Indexed fields:

| Field      | Type | Purpose                   |
| ---------- | ---- | ------------------------- |
| `action`   | Text | Logical event name        |
| `message`  | Text | Human-readable summary    |
| `detail`   | Text | Extended description      |
| `question` | Text | User or NL query          |
| `session`  | Tag  | Session filtering         |
| `agent`    | Tag  | Agent filtering           |
| `worker`   | Tag  | Worker filtering          |
| `plan`     | Tag  | Plan filtering            |
| `operator` | Tag  | Operator filtering        |
| `_blob`    | Text | Catch-all semantic search |

Example query:
@agent:{NL2SQLAgent} @operator:{infer_value_axis}

LogSearchClient

A lightweight wrapper around FT.SEARCH for querying logs.

search = LogSearchClient()

search.by_session("sess_123")
search.by_agent("NL2SQL")
search.by_action("fallback")
search.text("mass casualty")
search.recent(limit=50)

SearchableCustomLogger

Extends CustomLogger with structured event emission.

Context Management

logger.set_context(
    session="sess_123",
    agent="NL2SQLAgent",
    operator="infer_value_axis"
)

Context persists across log records and is automatically stored and indexed.

Recording Structured Events

## Example: NL2SQL Query Execution Logging

Below is a realistic example of how the `SearchableCustomLogger` is used to record a structured NL2SQL execution event.

### Code Example

```python
logger.record(
    action="nl2sql_query_execution",
    inputs={
        "question": question,
        "sql_query": query,
        "source_key": key
    },
    outputs={
        "result_count": count,
        "result_preview": (
            result[:3] if isinstance(result, list) else result
        )
    },
    error=error,
    result="success" if error is None else "failed"
)

What This Records

This single call produces a fully structured log event that captures:

Action

action: Logical name of the event (nl2sql_query_execution)

Inputs

Natural language question

Generated SQL query

Data source identifier

Outputs

Number of rows returned

A small preview of the result (safe for inspection)

Outcome

result: success / failed

error: captured error object or message (if any)

All fields are stored verbatim as structured JSON, not flattened strings.

Stored Log Record (Simplified)

{
  "timestamp": "2026-02-02T21:41:18Z",
  "action": "nl2sql_query_execution",
  "inputs": {
    "question": "Show me severe collisions",
    "sql_query": "SELECT * FROM collisions WHERE number_of_persons_injured >= 10",
    "source_key": "nyc_collisions"
  },
  "outputs": {
    "result_count": 12,
    "result_preview": [
      { "...": "..." }
    ]
  },
  "result": "success",
  "error": null,
  "context": {
    "session": "sess_123",
    "agent": "NL2SQLAgent",
    "operator": "execute_query"
  }
}

Why This Matters

Because the event is structured and indexed, you can later ask questions like:

“Show all failed NL2SQL executions”

“Which questions produced empty results?”

“Which SQL queries frequently error?”

“How often does this operator succeed?”

All without parsing logs or reproducing runs.

Search Examples

search.by_action("nl2sql_query_execution")
search.by_agent("NL2SQLAgent")
search.text("number_of_persons_injured")


