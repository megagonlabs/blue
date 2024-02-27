# RAG Agent

RAG Agent is a thin-wrapper around Llama-index that interfaces with blue. The core functionalities of the agent are:
1. Reading a query (or text) from the (blue) stream initiated by USER agent
2. Running the query over the llama-index pipeline
3. Writing the output to the (blue) stream

## Setup
1. Pull the dependencies

```
cd agents/rag/
mkdir -p lib
sh ./docker_build_agent.sh
```

## Index creation (optional)

If you already have access to the index, skip this step. 

The file `indexing.py` demonstrates a way to create a llama index with input in jsonl format. Please write your custom indexing scripts for different file formats


## Running RAG agent

RAG agent currently relies on the USER agent (`simple_user`) to initiate the query. To start the agent, follow these steps  

### 1. Start the platform (check main README.md for latest commands)

```
cd platform
docker compose up
```

### 2. Run the user agent 

In a new terminal (2)

```
cd agents/simple_user/
python src/simple_user_agent.py --interactive

```

### 3. Run the RAG agent

In a new terminal (3)

```
cd agents/rag/

python src/rag_agent.py \
    --session SESSION:<get_session_id_from_user_agent> \
    --loglevel ERROR \
    --properties '{"llm_model_str":"gpt-3.5-turbo-0125","openai_api_key":"<OPENAI_API_KEY>", "llm_temperature":0.1, "embed_model_str":"facebook/contriever-msmarco", "embed_model_pool":"mean", "persist_dir":"./index/", "top_k":1}'
```

### 4. Enter your queries through USER agent (terminal 2)
