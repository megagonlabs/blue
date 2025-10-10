###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer, default_attributes_validator
from blue.operators.registry import OperatorRegistry
from blue.operators.operator_discover import operator_discover_operator_function, operator_discover_operator_validator
from blue.data.pipeline import DataPipeline, Status

###############
### Multipart Query Operator


def multipart_query_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """
    Orchestrate the execution of multi-part query, starting with data discovery, leading to execution.

    !!! note
        MultipartQueryOperator only does plan refinement. This function simply returns empty output.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), each array represents a part of the multipart query plan.
        attributes: Dictionary containing operator attributes including serialize.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        Empty list.
    """
    # TODO:
    return [[]]


def multipart_query_operator_refiner(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Refine the multipart query plan by constructing a data pipeline for each subquery comprising data discovery, query routing, data insertion.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), each array represents a part of the multipart query plan.
        attributes: Dictionary containing operator attributes including serialize
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List of data pipelines (as dictionaries) representing the refined multipart query plans.
    """
    # Extract attributes
    serialize = attributes.get('serialize', True)

    plans = input_data
    pipelines = []

    for plan in plans:
        # create pipeline for each alternative set
        pipeline = DataPipeline(properties=properties)

        ctes = plan
        # discover, query, create table, and insert for each cte
        failed = False

        #### build plan

        # input
        input_node = pipeline.define_input(value=None)
        # output
        output_node = pipeline.define_output(properties={})
        # set plan input / output
        pipeline.set_plan_input(input_node)
        pipeline.set_plan_output(output_node)

        # cte start/end nodes
        cte_start_nodes = {}
        cte_end_nodes = {}
        # dependents
        dependents = set()

        # create database
        db_name = "db_" + pipeline.get_id()
        create_database_attributes = {"source": "internal", "database": db_name}
        create_database_node = pipeline.define_operator("/server/blue_ray/operator/create_database", attributes=create_database_attributes, properties={})

        # connect to input
        pipeline.connect_nodes(input_node, create_database_node)
        # connection point for cte paths
        cte_root_node = create_database_node

        # create path of operators for each cte
        for cte in ctes:
            description = cte['description'] if 'description' in cte else None
            sql = cte['sql'] if 'sql' in cte else None
            table = cte['table'] if 'table' in cte else None
            columns = cte['columns'] if 'columns' in cte else None
            dependency = cte['dependency'] if 'dependency' in cte else None
            generality = cte['generality'] if 'generality' in cte else 0

            # fail
            if description is None or sql is None or table is None or columns is None or dependency is None:
                failed = True
                break

            ## build pipeline
            # start
            start_node = None
            end_node = None

            if len(dependency) > 0:
                # create table
                create_table_attributes = {"source": "internal", "database": db_name, "table": table, "columns": columns}
                create_table_node = pipeline.define_operator("/server/blue_ray/operator/create_table", attributes=create_table_attributes, properties={})

                # nl2sql, use internal db
                attr_names = [column['name'] for column in columns]
                nl2sql_attributes = {
                    "question": description,
                    "protocol": "sqlite",
                    "source": "internal",
                    "database": db_name,
                    "collection": "public",
                    "attr_names": attr_names,
                    "execute_query": True,
                }
                nl2sql_node = pipeline.define_operator("/server/blue_ray/operator/nl2sql", attributes=nl2sql_attributes, properties={})

                # insert table
                insert_table_attributes = {"source": "internal", "database": db_name, "table": table}
                insert_table_node = pipeline.define_operator("/server/blue_ray/operator/insert_table", attributes=insert_table_attributes, properties={})

                start_node = create_table_node
                end_node = insert_table_node

                ## intra-cte connections
                pipeline.connect_nodes(create_table_node, nl2sql_node)
                pipeline.connect_nodes(nl2sql_node, insert_table_node)

            else:
                # data discover, first at source level

                data_discovery_attributes = {
                    "search_query": description,
                    "approximate": True,
                    "concept_type": 'source',
                    "limit": 1,
                    "filter_names": ["internal"],
                    "use_hierarchical_search": False,
                }

                if generality >= 5:
                    data_discovery_attributes['search_query'] = "general knowledge"
                data_discovery_node = pipeline.define_operator("/server/blue_ray/operator/data_discover", attributes=data_discovery_attributes, properties={})

                # create table
                create_table_attributes = {"source": "internal", "database": db_name, "table": table, "columns": columns}
                create_table_node = pipeline.define_operator("/server/blue_ray/operator/create_table", attributes=create_table_attributes, properties={})

                # nl2q
                nl2query_router_attributes = {"search_query": description, "execute_query": True, "columns": columns}
                nl2query_router_node = pipeline.define_operator("/server/blue_ray/operator/nl2query_router", attributes=nl2query_router_attributes, properties={})

                # # insert table
                insert_table_attributes = {"source": "internal", "database": db_name, "table": table}
                insert_table_node = pipeline.define_operator("/server/blue_ray/operator/insert_table", attributes=insert_table_attributes, properties={})

                start_node = data_discovery_node
                end_node = insert_table_node

                ## intra-cte connections
                pipeline.connect_nodes(data_discovery_node, create_table_node)
                pipeline.connect_nodes(create_table_node, nl2query_router_node)
                pipeline.connect_nodes(nl2query_router_node, insert_table_node)

            ## set cte start / end nodes
            dependents.add(table)
            cte_start_nodes[table] = start_node
            cte_end_nodes[table] = end_node

            # remove any dependency
            for d in dependency:
                dependents.remove(d)

        if failed:
            continue

        if serialize:
            last_end_node = cte_root_node

            # add ctes to queue
            cte_queue = []
            cte_dict = {}
            for cte in ctes:
                table = cte['table'] if 'table' in cte else None
                cte_queue.append(table)
                cte_dict[table] = cte

            # process queue by dependencu
            processed_ctes = []
            while len(cte_queue) > 0:
                table = cte_queue.pop(0)
                cte = cte_dict[table]
                dependency = cte['dependency'] if 'dependency' in cte else []

                # check if cte's depencencies are processed
                dependent = False
                for d in dependency:
                    if d not in processed_ctes:
                        dependent = True
                # still dependent, back to the queue
                if dependent:
                    cte_queue.append(table)

                # connect last_end node to cte
                start_node = cte_start_nodes[table]
                end_node = cte_end_nodes[table]
                pipeline.connect_nodes(last_end_node, start_node)
                last_end_node = end_node

                # add to processed
                processed_ctes.append(table)

            # connect last end node to output
            pipeline.connect_nodes(last_end_node, output_node)

        else:
            for cte in ctes:
                description = cte['description'] if 'description' in cte else None
                sql = cte['sql'] if 'sql' in cte else None
                table = cte['table'] if 'table' in cte else None
                columns = cte['columns'] if 'columns' in cte else None
                dependency = cte['dependency'] if 'dependency' in cte else []

                ## inter-cte connections
                start_node = cte_start_nodes[table]
                end_node = cte_end_nodes[table]

                # if no dependency, connect from cte_root_node to start
                if len(dependency) == 0:
                    pipeline.connect_nodes(cte_root_node, start_node)
                else:
                    # connect from sink node of dependency if exists
                    for d in dependency:
                        if d in cte_end_nodes:
                            cte_end_node = cte_end_nodes[d]
                            pipeline.connect_nodes(cte_end_node, start_node)
                        else:
                            # dependency not found!
                            failed = True
                            break

                # if nobody depends on this connect end node to output node
                for d in dependents:
                    cte_end_node = cte_end_nodes[d]
                    pipeline.connect_nodes(cte_end_node, output_node)

        # add to pipelines
        pipelines.append(pipeline.to_dict())

    return pipelines


def multipart_query_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain multipart query operator output.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    multipart_query_explanation = {
        'output': output,
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"multipart query orchestrated the execution of...",
    }
    return multipart_query_explanation


###############
### MultipartQueryOperator
#
class MultipartQueryOperator(Operator):
    """
    Multipart query operator orchestrates the execution of multi-part query, starting with data discovery, and exectution.

    Attributes:
    -------------
    | Name      | Type  | Required | Default | Description                                         |
    |-----------|-------|----------|---------|-----------------------------------------------------|
    | `serialize` | bool  |     | True    | Whether to serialize each part of the query        |


    """

    PROPERTIES = {}

    name = "multipart_query"
    description = "Orchestrates the execution of multi-part query, starting with data discovery, leading to execution"
    default_attributes = {
        "serialize": {"type": "bool", "description": "Whether to use serialize each part of the query", "required": False, "default": True},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=multipart_query_operator_function,
            description=description or self.description,
            properties=properties,
            validator=default_attributes_validator,
            explainer=multipart_query_operator_explainer,
            refiner=multipart_query_operator_refiner,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # refine
        self.properties["refine"] = True


###########
### Helper functions
