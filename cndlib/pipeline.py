###
# useful code reference for detecting ingroup, outgroup based on modifier terms
# https://medacy.readthedocs.io/en/latest/_modules/medacy/pipeline_components/units/unit_component.html
# contains the following:
# - cna_pipe
# - hearst patterns

# python system modules
import os
import json
from datetime import date, datetime
from collections import Counter
import numpy as np

# spacy modules
import spacy
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
from spacy.pipeline import merge_entities
from spacy.tokens import Doc, Span, Token

#custom modules
import schemautils as mk

class CND(object):

    # get dataset directory for supplementary datafiles
    ROOT = r"C:\Users\Steve\OneDrive - University of Southampton\CNDPipeline"
    dataset_dir = os.path.join(ROOT, 'dataset')
    entity_corrections = "named_entity_corrections.json"

    def __init__(self, model = None):

        ##########
        #load spacy model
        ##########
        SPACY_MODEL_NAMES = {"small" : "en_core_web_sm", "medium" : "en_core_web_md", "large" : "en_core_web_md"}
        
        if model is not None and model in list(SPACY_MODEL_NAMES.keys()):
            if model == "small":
                print(f"{SPACY_MODEL_NAMES} returns some imcompatible results")
            self.nlp = spacy.load(SPACY_MODEL_NAMES[model])
        else:
            self.nlp = spacy.load(SPACY_MODEL_NAMES["medium"]) # set default to medium if no model size is passed
        
        #####
        # add pipeline components
        #####

        for component in self.nlp.pipe_names:
            if component not in ['tagger', "parser", "ner"]:
                self.nlp.remove_pipe(component)
        
        # add named entity matcher component to pipeline
        self.nlp.add_pipe(EntityMatcher(self.nlp), after = "ner") # top up on named entities

        # add merge entities
        self.nlp.add_pipe(merge_entities, after = "Named Entity Matcher")

        # add concept matcher component to pipeline
        self.nlp.add_pipe(ConceptMatcher(self.nlp), after = "merge_entities") # add concepts

        #self.nlp.add_pipe(Group_ID(self.nlp), last = True) # add group id matcher

        # # add merge named concepts to pipeline
        # self.nlp.add_pipe(merge_named_concepts, last = True)

        #####
        # Doc extensions
        #####
        #Doc.set_extension("custom_chunks", getter=custom_chunks, force = True)
        Doc.set_extension("concepts", default = [], force = True)
        Doc.set_extension("ideologies", getter=get_doc_ideologies, force=True)
        
    def __call__(self, text):

        if isinstance(text, str):
            return self.nlp(text)
        else:
            return 'not of type text'

#####
# pipeline components
#####

class EntityMatcher(object):
    
    """
    EntityMatcher is a pipeline component for supplementing named entities in a text.
    
    The supplementary named entities are found in the file /dataset/named_entity_corrections.json

    ideally placed after ner in the spaCy pipeline

    merge named entities after this component.
    """

    name = "Named Entity Matcher"  # component name, will show up in the pipeline

    def __init__(self, nlp):
        
        """
        Initialise the pipeline component. The shared nlp instance is used to initialise the matcher 
        with the shared vocab, get the label ID and generate Doc objects as phrase match patterns.
        """
        
        self.nlp = nlp

        # load entity corrections dataset
        with open(os.path.join(CND.dataset_dir, CND.entity_corrections), 'r') as fp:
            self.named_entities = json.load(fp)

        # initialise PhraseMatcher: matches made on lower case verion of token/span
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # add entity corrections to PhraseMatcher
        for label, terms in self.named_entities.items():
            if len(terms) > 0:
                patterns = [nlp.make_doc(text) for text in terms] 
                self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        
        """
        Apply the pipeline component on a Doc object and modify it if matches are found. 
        Return the Doc, so it can be processed by the next component in the pipeline, if available.
        """

        with doc.retokenize() as retokenizer:

            matches = self.matcher(doc)
            for match_id, start, end in matches:
                span = Span(doc, start, end, label=self.nlp.vocab.strings[match_id])

                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = spacy.util.filter_spans(list(doc.ents) + [span])

        return doc # this one

class ConceptMatcher(object):
    
    """
    This class is a for a pipelines component for detecting concepts in a text.
    
    The group schema is used to mark up tokens with the following custom attributes:
    - token._.CONCEPT
    - token._.ATTRIBUTE
    - token._.IDEOLOGY
    """

    name = "Concept Matcher"  # component name, will show up in the pipeline

    group_markup = "group_schema.json"

    ideologies = None
    group_schema = None
    
    def __init__(self, nlp = None):
        
        """
        Initialise the pipeline component. The shared nlp instance is used to initialise the matcher
        with the shared vocab, get the label ID and generate Doc objects as phrase match patterns.
        """
                
        #####
        # initiate group schema attributes to ConceptMatcher()
        #####

        # load group schema from disc
        with open(os.path.join(CND.dataset_dir, self.__class__.group_markup), 'r') as fp:
            self.__class__.group_schema = json.load(fp)

        Token.set_extension("CONCEPT", default = '', force = True)

        Token.set_extension("ATTRIBUTE", default = '', force = True)

        Token.set_extension("IDEOLOGY", default = '', force = True)

        # create a json object structure for group ideologies
        with open(os.path.join(CND.dataset_dir, self.__class__.group_markup), 'r') as fp:
            self.__class__.ideologies = {key : 0 for key in json.load(fp).keys()}
        
        if nlp:
            self.nlp = nlp

            # Set up the Matcher using concepts as the rule name and terms in the pattern 
            self.matcher = Matcher(self.nlp.vocab)
            for concept, terms in mk.get_concept_lookup(self.__class__.group_schema):
                self.matcher.add(concept, None, [{"LEMMA" : {"IN" : terms}}])     

    def __call__(self, doc):
        
        """Apply the pipeline component on a Doc object and modify it if matches are found. 
        Return the Doc, so it can be processed by the next component in the pipeline, if available.
        
        merge entities code: https://github.com/explosion/spaCy/issues/4107
        filter code: https://github.com/explosion/spaCy/issues/4056
        """

        with doc.retokenize() as retokenizer:

            matches = self.matcher(doc)
            for match_id, start, end in matches:
                span = Span(doc, start, end)
                if self.nlp:
                    concept_id = self.nlp.vocab.strings[match_id]
                
                    for token in span:
                        token._.CONCEPT = concept_id
                        token._.ATTRIBUTE = self.get_attribute(token)
                        token._.IDEOLOGY = self.get_ideology(token)

                    # try:
                    if len(span) > 1:
                        retokenizer.merge(span)

        return doc

    def get_concept(self, token):
    
        """
        getter function returning the concept related to token text
        input: string or Token
        output: related concept
        """
        
        if isinstance(token, Token):
            token = token.lemma_

        for concept, terms in mk.get_concept_lookup(self.__class__.group_schema):
            if token.lower() in [term.lower() for term in terms]:
                return concept
        
        return ''

    def get_attribute(self, token):

        """
        getter function returning group attribute related to the token concept
        input: string Token, or Span
        output attribute
        """

        if isinstance(token, (Token, Span)):
            token = token._.CONCEPT

        for attribute, concepts in mk.get_attribute_lookup(self.__class__.group_schema):
            if token.lower() in [concept.lower() for concept in concepts]:
                return attribute
        return ''

    def get_ideology(self, token):

        """
        getter function returning the ideology related to the token concpet
        input: string Token, or Span
        output: related ideology
        """
        
        if isinstance(token, (Token, Span)):
            token = token._.CONCEPT

        for ideology, concepts in mk.get_ideology_lookup(self.__class__.group_schema):
            if token.lower() in [concept.lower() for concept in concepts]:
                return ideology
        return ''

def get_doc_ideologies(doc):
    
    """
    returns a dictionary containing a count of ideologies mentioned within the document
    count is a percentage of ideology instances / total number of ideology instances
    """
    
    ## create a list for counting the number of ideologies featuring as custom attributes of each named concept
    ideology_list = [concept._.IDEOLOGY for concept in doc._.custom_chunks if concept._.IDEOLOGY]
    doc._.custom_chunks
    
    ## get the data structure of ideologies as a json object
    doc_ideologies = ConceptMatcher.ideologies.copy()
        
    ## create a counter for the ideologies featuring in the doc
    for k, v in dict(Counter(ideology_list)).items():
        doc_ideologies[k] = v / len(ideology_list)
        
    return doc_ideologies


class Group_ID(object):

    """
    pipeline extension for identifying ingroup and outgroup at the noun phrase level.

    uses Matcher to identify each whereby ingroup and outgroup terms identified by the
    named concept matcher are modified by a named entity.
    """
    
    name = "group id"
    
    GROUP = ["NORP", "GPE", "ORG", "PERSON"]
    
    def __init__(self, nlp):
        
        self.nlp = nlp
        
        Doc.set_extension("outgroup_entities", default = [], force = True)
        Doc.set_extension("ingroup_entities", default = [], force = True)
        Token.set_extension("outgroup", default = False, force = True)
        Token.set_extension("ingroup", default = False, force = True)
        
        self.outgroups = Matcher(nlp.vocab)
        
        self.outgroups.add("OUTGROUP", None,
                            [{'ENT_TYPE': {"IN" : Group_ID.GROUP}}, {"_" : {"ATTRIBUTE" : "outgroup"}}])

        self.ingroups = Matcher(nlp.vocab)
        
        self.ingroups.add("INGROUP", None,
                            [{'ENT_TYPE': {"IN" : Group_ID.GROUP}}, {"_" : {"ATTRIBUTE" : "ingroup"}}])
        
    def __call__(self, doc):

        ## process outgroup entities
        with doc.retokenize() as retokenizer:

            matches = self.outgroups(doc)
            for _, start, end in matches:
                span = Span(doc, start, end)
                for token in span:
                    token._.outgroup = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc._.outgroup_entities = list(doc._.outgroup_entities) + [span]

        ## process ingroup entities        
        with doc.retokenize() as retokenizer:

            matches = self.ingroups(doc)
            for _, start, end in matches:
                span = Span(doc, start, end)
                for token in span:
                    token._.ingroup = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc._.ingroup_entities = list(doc._.ingroup_entities) + [span]
                
        return doc