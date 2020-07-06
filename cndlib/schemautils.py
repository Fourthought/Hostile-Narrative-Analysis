from collections import Counter

def get_concept_lookup(schema):

    """
    getter function to enable concept lookup for a term
    input: group schema
    output: generator object of concept-list(terms) pairs

    (TODO: will require a check for correct format of group schema)
    """
    
    for attributes_dict in schema.values():
        for concepts in attributes_dict.values():
            for concept, terms in concepts.items():
                yield concept, terms

def get_attribute_lookup(schema):

    """
    getter function to enable attribute lookup for a concept
    input: group schema
    output: generator object of attribute-list(concept) pairs

    (TODO: will require a check for correct format of group schema)
    """

    for attribute_dict in schema.values():
        for attribute, concept in attribute_dict.items():
            yield attribute, list(concept.keys())

def get_ideology_lookup(schema):

    """
    getter function to enable ideology lookup for a concept
    input: group schema
    output: generator object of ideology-list(concept) pairs

    (TODO: will require a check for correct format of group schema)
    """

    for ideology, attribute in schema.items():
        for concepts in attribute.values():
            yield ideology, list(concepts.keys())

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