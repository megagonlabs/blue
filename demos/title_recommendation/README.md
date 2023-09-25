# Title Recommendation

This demo illustrates a number of agents working together to make a title recommendation. Starting with a user input such as "Using the information from the resume of Kushan Mitra, recommend a title for him", agents fetch the resume of the person, extract pieces from the resume, such as title, run a title recommender, and eventually ground the rationale of the recommendation using an external knowledge making a case with the skills of the recommendation.

Overall the demo illustrates:
* Ability to orchestrate/coordinate multiple agents/services (e.g. listeners, planner, session stream and memory) [SYSTEMS, NLP/PLANNING]
* Ability to detect explicit information need (e.g. detect triples) [NL/SQL]
* Ability to fetch structured data (e.g. query neo4j, postgres) [API/STRUCTURED DATA]
* Ability to run models (e.g. run title recommender model) [API/CUSTOM MODELS]
* Ability to pull implicit knowledge to ground outcome [HAI/GROUNDING]
* Ability to compose good, rational response leveraging multitude of information [HAI/EXPL]

## Running the Demo

### flush.sh
To flush the contents of the Redis backend run:
```
$ ./flush.sh
```

### user.sh
Invoke user agent to input text:
```
$ /user.sh 'Using the information from the resume of Kushan Mitra recommend a title for him'
```

### observer.sh
To observe the outputs from each agent run observer agent using the session is from the output of user.sh script:
```
$ ./observer.sh <SESSION>
```
