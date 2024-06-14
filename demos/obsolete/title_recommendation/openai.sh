export SESSION_ID=$(cat .sid)
# Triple Extractor
export TRIPLE_EXTRACTOR_PROPERTIES='{"openai.service":"ws://blue_service_openai:8002","listens": {"includes": ["USER"],"excludes": []},"tags": ["TRIPLE"]}'
blue session --session-id ${SESSION_ID} join --REGISTRY default --AGENT OpenAITripleExtractor --AGENT_PROPERTIES "${TRIPLE_EXTRACTOR_PROPERTIES}"
#  Cypher Translator
export CYPHER_TRANSLATOR_PROPERTIES='{"openai.service":"ws://blue_service_openai:8002","listens":{"includes":["TRIPLE"],"excludes":[]},"tags": ["CYPHER"]}'
blue session --session-id ${SESSION_ID} join --REGISTRY default --AGENT OpenAINeo4JQuery --AGENT_PROPERTIES "${CYPHER_TRANSLATOR_PROPERTIES}"
