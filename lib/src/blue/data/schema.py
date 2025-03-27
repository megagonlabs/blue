###############
### DataSchema
#
class DataSchema():
    def __init__(self):

        self.entities = {}
        self.relations = {}

    def has_entity(self, key):
        return key in self.entities

    def add_entity(self, key):
        index = 0
        if key in self.entities:
            entity_obj = self.entities[key]
            index = entity_obj["index"] + 1
            entity_obj["index"] = index
      
        unique_key = key
        if index > 0:
            unique_key = key + "__" + str(index) 

        entity_obj = {}
        entity_obj['name'] = key 
        entity_obj['index'] = index
        entity_obj['properties'] = {}

        self.entities[unique_key] = entity_obj

        return key

    def add_entity_property(self, key, property, type):
        if key in self.entities:
            entity_obj = self.entities[key]
            properties_obj = entity_obj['properties']
            properties_obj[property] = type
    
    def _relation_encoding(self, source, relation, target):
        s = source + " " + relation + " " + target 
        return s.replace(" ", "__")
        # return "(" + source + ")" + "-" + relation + "->" + "(" + target + ")" 

    def has_relation(self, source, relation, target):
        relation_encoding = self._relation_encoding(source, relation, target)
        return relation_encoding in self.relations 

    def add_relation(self, source, relation, target):  
        key = self._relation_encoding(source, relation, target)
        index = 0
        if key in self.relations:
            relation_obj = self.relations[key]
            index = relation_obj["index"] + 1
            relation_obj["index"] = index
      
        unique_key = key
        if index > 0:
            unique_key = key + "__" + str(index) 

        relation_obj = {}
        relation_obj['name'] = relation
        relation_obj['index'] = index
        relation_obj['source'] = source
        relation_obj['target'] = target
        relation_obj['properties'] = {}

        self.relations[unique_key] = relation_obj

        return unique_key

    def add_relation_property(self, key, property, type):
        if key in self.relations:
            relation_obj = self.relations[key]
            properties_obj = relation_obj['properties']
            properties_obj[property] = type

    def to_json(self):
        s = {}
        s['entities'] = self.entities.copy()
        s['relations'] = self.relations.copy()
        return s

    def __repr__(self):
        return "DataSchema()"

    def __str__(self):
        s = 'Schema:' + '\n'
        s += 'Entities: ' + '\n'
        for key in self.entities:
            entity_obj = self.entities[key]
            name = entity_obj['name']
            index = entity_obj['index']
            properties = entity_obj['properties']
            s += "key: " + key + '\n'
            s += "  name: " + name + '\n'
            s += "  index: " + str(index) + '\n'
            s += "  properties: " +  '\n'
            for property in properties:
                s += "    " + property + ": " + properties[property] + '\n'

        s += 'Relations: ' + '\n'
        for key in self.relations:
            relation_obj = self.relations[key]
            name = relation_obj['name']
            index = relation_obj['index']
            source = relation_obj['source']
            target = relation_obj['target']
            properties = relation_obj['properties']
            s += "key: " + key + '\n'
            s += "  name: " + name + '\n'
            s += "  index: " + str(index) + '\n'
            s += "  source: " + source + '\n'
            s += "  target: " + target + '\n'
            s += "  properties: " +  '\n'
            for property in properties:
                s += "    " + property + ": " + properties[property] + '\n'

        return s
