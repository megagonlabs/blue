# data registry

Data registry is a repository of metadata about data elements that blue agents can connect to, search, and browse. Each data element is described with metadata such as name, type, description, properties, and contents. 

Data elements in the registry are nested. At the top is a data lake. A data lake consists of a number of data sources (e.g. postgress dbms, mongo server, etc.). Data sources contain databases (e.g. postgres db, mongo db). Databases contain collections (e.g. postgress table, mongo collection, etc.). 

Data registry defines the set of data that can be put to utilized on specific deployments by the agents in that deployment. When deployed each deployment (platform) is paired with a specific data registry. Each data registry has a `name` that is used in configuring a platform.


Data registry can be utilized by a various agents (including planner) to find suitable data. To facilitate that data registry supports parameteric (embeddings) search as well as keyword based search. 

## contents
Below is an example content of a data registry. At the top level a data element `indeed_mongodb` of type `source` is defined. It's scope is `/` meaning that it is a top level data element. It's properties contains a `connection` object that is used to sync its metadata and contents (e.g. databases) by connecting to a running instance. Databases under `indeed_mongodb` such as `indeed_dev` are listed in `contents`, and as such their scope is set as `/indeed_mongodb`.  Collections under `indeed_dev` such as `resume` collection are listed similarly in a nested manner, and their scope is set to `/indeed_mongodb/indeed_dev`. Each of these data elements can have other metadata and schema and their are listed in `properties`. Schema is a list of `entities` and `relations` as below, and it automatically fetched from the source connection. 

```json
{
    "indeed_mongodb": {
        "name": "indeed_mongodb",
        "type": "source",
        "scope": "/",
        "description": "Source for all indeed original data",
        "properties": {
            "connection": {
                "host": "localhost",
                "port": 27017,
                "protocol": "mongodb"
            }
        },
        "contents": {
            "indeed_dev": {
                "name": "indeed_dev",
                "type": "database",
                "scope": "/indeed_mongodb",
                "description": "Database for indeed data, development level",
                "properties": {
                    "metadata": {},
                    "schema": {}
                },
                "contents": {
                    "resume": {
                        "name": "resume",
                        "type": "collection",
                        "scope": "/indeed_mongodb/indeed_dev",
                        "description": "",
                        "properties": {
                            "metadata": {},
                            "schema": {
                                "entities": {
                                    "awards": {
                                        "name": "awards",
                                        "index": 0,
                                        "properties": {}
                                    },
                                    "certifications": {
                                        "name": "certifications",
                                        "index": 0,
                                        "properties": {}
                                    },
                                    ...
                                },
                                "relations": {
                                    "(experiences)-experiences:jobLocation->(jobLocation)": {
                                        "name": "experiences:jobLocation",
                                        "index": 0,
                                        "source": "experiences",
                                        "target": "jobLocation",
                                        "properties": {}
                                    },
                                    "(experiences)-experiences:timeRange->(timeRange)": {
                                        "name": "experiences:timeRange",
                                        "index": 0,
                                        "source": "experiences",
                                        "target": "timeRange",
                                        "properties": {}
                                    },
                                    ...
                                }
                            },
                            ...
                         }
                                  
        }
    },
    }
}

```
## build

To build data registry:
```
$ cd platform/data_registry
$  ./docker_build_dataregistry.sh 
```

### run

To run data registry, as a prerequisite you need to have the platform up and running.

Then, you can run data registry either as a python function:
```
$ cd platform/data_registry
$ python src/data_registry.py --list
```

Note in the above case the properties of the agent registry may have to be additionally set (for example `db.host`) to allow connections to database to store registry entiries. Note above `id` of the agent registry is not provided as such default is used.

Data registry is also available on the web interface.


### properties

Data registry has a number of properties that can be configured when a registry is created:

* `db.host`: host of the Redis database backend, default 'localhost'
* `db.port`: port address of the Redis database backend, default 6379
* embeddings_model: name of the embeddings model from huggingface, sentence transformer library, default `paraphrase-MiniLM-L6-v2`

### command line parameters

```
--name', type=str, default='DATA_REGISTRY', help='name of the registry'
--id', type=str, default='default', help='id of the registry'
--sid', type=str, help='short id (sid) of the registry'
--cid', type=str, help='canonical id (cid) of the registry'
--prefix', type=str, help='prefix for the canonical id of the registry'
--suffix', type=str, help='suffix for the canonical id of the registry'
--properties: type=str, help='properties in json format'
--loglevel: default="INFO", type=str, help='log level'
--add: type=str, default=None, help='json array of data elements to be add to the registry'
--update: type=str, default=None, help='json array of data elements to be updated in the registry'
--remove: type=str, default=None, help='json array of data elements names to be removed'
--search: type=str, default=None, help='search registry with keywords'
--type: type=str, default=None, help='search registry limited to data metadata type [source, database, collection]'
--scope: type=str, default=None, help='limit to scope'
--page: type=int, default=0, help='search result page, default 0'
--page_size: type=int, default=5, help='search result page size, default 5'
--list: type=bool, default=False, help='list data elements in the registry'
--approximate: type=bool, default=False, help='use approximate (embeddings) search'
--hybrid: type=bool, default=False, help='use hybrid (keyword and approximate) search'
--sync: type=bool, default=False, help='sync registry contents'
--recursive: type=bool, default=False, help='sync recursively'
--source: type=str, default=None, help='data source'
--database: type=str, default=None, help='database'
--collection: type=str, default=None, help='collection'
```

    
#### add data elements
Data elements is an json array of data elements that can be in any scope and of type. See `data/sample_data.json`.

```
$ python src/data_registry.py --add "`cat data/sample_data.json`"
```

#### search data elements
Approximate data search using only source type:
```
$ python src/data_registry.py --search resume --approximate --type source
```

Approximate data search using only collection type:
```
$ python src/data_registry.py --search resume --approximate --type collection
```

#### sync data elements
```
$ python src/data_registry.py --sync --source indeed_mongodb --recursive
$ python src/data_registry.py --sync --source indeed_mongodb --database indeed_dev --collection resume
```
