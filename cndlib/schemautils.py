from collections import Counter

def get_concept_lookup(schema):

    """
    getter function for creating a concept lookup table
    input: group schema
    output: dict() object in the format {"CONCEPT" : ["terms"]}

    (TODO: will require a check for correct format of group schema)
    """
    
    concept_lookup = dict()

    for attribute in schema.values():
        for concept in attribute.values():
            concept_lookup.update(concept)

    return concept_lookup

def get_attribute_lookup(schema):

    """
    getter function for creating a attribute lookup table
    input: group schema
    output: dict() object in the format {"attribute" : ["CONCEPTS"]}

    (TODO: will require a check for correct format of group schema)
    """

    attribute_lookup = dict()
    for attribute_dict in schema.values():
        attribute_lookup = {key : [] for key in list(attribute_dict.keys())}

    for attribute_dict in schema.values():
        for attribute, concept in attribute_dict.items():
            attribute_lookup[attribute] += (list(concept.keys()))

    return attribute_lookup

def get_ideology_lookup(schema):

    """
    getter function for creating a ideology lookup table
    input: group schema
    output: dict() object in the format {"ideology" : ["CONCEPTS"]}

    (TODO: will require a check for correct format of group schema)
    """

    ideology_lookup = dict()     
    for ideology, attribute in schema.items():
        labels = []
        for concepts in attribute.values():
            labels += list(concepts.keys())
        ideology_lookup[ideology] = labels

    return ideology_lookup

def get_concept(token):
    
    """
    getter function returning the concept related to token text
    """
    
    for concept, terms in concept_lookup.items():
        if token.lemma_.lower() in [pattern.lower() for pattern in terms]:
            return concept
    return ''

def get_ideology(token):

        """
        getter function returning the ideology related to the token concpet
        input: token._.CONCEPT
        output: related ideology
        
        """

        for ideology, concepts in ideology_lookup.items():
            if token._.CONCEPT.lower() in [pattern.lower() for pattern in concepts]:
                return ideology
        return ''

def get_attribute(token):

    """
    getter function returning group attribute related to the token concept
    input: token._.concept
    output attribute
    """

    for attribute, concepts in attribute_lookup.items():
        if token._.CONCEPT.lower() in [pattern.lower() for pattern in concepts]:
            return attribute
    return ''

def get_doc_ingroup(doc):
    
    """
    returns a dictionary containing a count of the ingroup terms mentioned within the document
    format = {"ingroup term" : number of occurances}
    
    """
    
    group = [feature.lower_.title() for feature in doc._.concepts if feature._.ATTRIBUTE in ["ingroup"]]

    return {k: v for k, v in sorted(dict(Counter(group)).items(), key=lambda item: item[1], reverse = True)} #ingroup terms

def get_doc_outgroup(doc):

    """
    returns a dictionary containing a count of the outgroup terms mentioned within the document
    format = {"outgroup term" : number of occurances}
    """

    group = [feature.lower_.title() for feature in doc._.concepts if feature._.ATTRIBUTE in ["outgroup"]]
    
    return {k: v for k, v in sorted(dict(Counter(group)).items(), key=lambda item: item[1], reverse = True)} # outgroup terms