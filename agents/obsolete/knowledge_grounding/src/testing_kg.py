from neo4j import GraphDatabase


def main():
    graph = GraphDatabase("http://18.216.233.236:7474", auth=("neo4j", "444@Castro"))
    person = "Eser Kandogan"
    next_title = "Software Engineer - 2"

    name_query = '''
        MATCH (p:PERSON{{name: '{}'}})-[h1:HAS]->(b)-[h2:HAS]->(c)
        RETURN c.label, h2.duration
        ORDER BY h2.duration DESC
        LIMIT 2
    '''.format(
        person
    )

    title_query = '''
        MATCH (j:TITLE{{label: '{}'}})-[r:REQUIRES]->(b)
        RETURN b.label, r.avg_duration
        ORDER BY r.avg_duration DESC
        LIMIT 2
    '''.format(
        next_title
    )

    s1 = graph.run(name_query)  # .to_ndarray(dtype='str')
    s2 = graph.run(title_query)  # .to_ndarray(dtype='str')


if __name__ == '__main__':
    main()
