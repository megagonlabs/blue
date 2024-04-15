export SESSION_ID=$(cat .sid)
# Triple Extractor
export TRIPLE_EXTRACTOR_PROPERTIES='{"openai.service":"ws://blue_service_neo4j:8002","listens": {"includes": ["USER"],"excludes": []},"tags": ["TRIPLE"]}'
blue session --session-id ${SESSION_ID} --REGISTRY default --AGENT OpenAITripleExtractor --AGENT_PROPERTIES "${TRIPLE_EXTRACTOR_PROPERTIES}" join
#  Cypher Translator
export CYPHER_TRANSLATOR_PROPERTIES='{"openai.service":"ws://blue_service_neo4j:8002","listens":{"includes":["TRIPLE"],"excludes":[]},"tags": ["CYPHER"]}'
blue session --session-id ${SESSION_ID} --REGISTRY default --AGENT OpenAINeo4JQuery --AGENT_PROPERTIES "${CYPHER_TRANSLATOR_PROPERTIES}" join
