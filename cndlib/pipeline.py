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
from spacy.tokens import Doc, Span, Token
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
from spacy.pipeline import merge_entities
import re
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex
from spacy.lang.char_classes import CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER

# custom modules
import cndlib.schemautils as mk
from cndlib import customchunks
from cndlib.customchunks import merge_custom_chunks
from cndlib.hpspacy import HearstPatterns
from cndlib.cndutils import find_file


class CND(object):
    # get dataset directory for supplementary datafiles
    ROOT = r"/Users/stephenanningcorp/Library/CloudStorage/OneDrive-UniversityofSouthampton/Hostile-Narrative-Analysis"
    dataset_dir = os.path.join(ROOT, 'dataset')
    entity_corrections = "named_entity_corrections.json"

    def __init__(self, model=None, merge=False, extended=True):

        ##########
        # load spacy model
        ##########
        SPACY_MODEL_NAMES = {"small": "en_core_web_sm",
                             "medium": "en_core_web_md",
                             "large": "en_core_web_lg"}

        if model is not None:
            if model == "small":
                print(f"{SPACY_MODEL_NAMES[model]} returns some incompatible results")
            self.nlp = spacy.load(SPACY_MODEL_NAMES[model])
        else:
            self.nlp = spacy.load(SPACY_MODEL_NAMES["medium"])  # set default to medium if no model size is passed

        #####
        # add pipeline components
        #####

        for component in self.nlp.pipe_names:
            if component not in ['tagger', "parser", "ner"]:
                self.nlp.remove_pipe(component)

        # add named entity matcher component to pipeline
        self.nlp.add_pipe(EntityMatcher(self.nlp), after="ner")  # top up on named entities

        # add merge entities
        self.nlp.add_pipe(merge_entities, after="Named Entity Matcher")

        # add concept matcher component to pipeline
        self.nlp.add_pipe(ConceptMatcher(self.nlp), after="merge_entities")  # add concepts

        if extended:
            # add merge custom chunks
            self.nlp.add_pipe(merge_custom_chunks, after="Concept Matcher")

            # add hearst pattern matcher
            self.nlp.add_pipe(HearstPatterns(self.nlp, extended=True), last=True)

            # add custom tokenizer
            self.nlp.tokenizer = custom_tokenizer(self.nlp)

            # TODO: add the merge compounds at somepoint

        # self.nlp.add_pipe(Group_ID(self.nlp), last = True) # add group id matcher

        # # add merge named concepts to pipeline
        # self.nlp.add_pipe(merge_named_concepts, last = True)

        #####
        # Doc extensions
        #####
        Doc.set_extension("concepts", default=[], force=True)
        Doc.set_extension("ideologies", getter=get_doc_ideologies, force=True)
        Doc.set_extension("custom_chunk_iterator", getter=customchunks.custom_chunk_iterator, force=True)
        Doc.set_extension("custom_chunks", getter=customchunks.custom_chunks, force=True)
        Token.set_extension("is_ADP_head", default=False, force=True)

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

        return doc  # this one


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

    def __init__(self, nlp=None):

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

        Token.set_extension("CONCEPT", default="", force=True)
        Token.set_extension("ATTRIBUTE", getter=self.get_attribute, force=True)
        Token.set_extension("IDEOLOGY", getter=self.get_ideology, force=True)

        Token.set_extension("span_type", default="", force=True)

        Span.set_extension("CONCEPT", default="", force=True)
        Span.set_extension("ATTRIBUTE", getter=self.get_attribute, force=True)
        Span.set_extension("IDEOLOGY", getter=self.get_ideology, force=True)

        Span.set_extension("span_type", default="", force=True)
        Span.set_extension("get_span_type", getter=self.get_span_type, force=True)
        Span.set_extension("get_span_CONCEPT", getter=self.get_span_concept, force=True)

        # create a json object structure for group ideologies
        with open(os.path.join(CND.dataset_dir, self.__class__.group_markup), 'r') as fp:
            self.__class__.ideologies = {key: 0 for key in json.load(fp).keys()}

        if nlp:
            self.nlp = nlp

            # Set up the Matcher using concepts as the rule name and terms in the pattern 
            self.matcher = Matcher(self.nlp.vocab)
            for concept, terms in mk.get_concept_lookup(self.__class__.group_schema):
                if concept == "SELF":
                    self.matcher.add(concept, None, [{"LOWER": {"IN": terms}}])
                else:
                    self.matcher.add(concept, None, [{"LEMMA": {"IN": terms}}])

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

                concept_id = self.nlp.vocab.strings[match_id]

                for token in span:
                    token._.CONCEPT = concept_id

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

        if isinstance(token, Span):
            token = token.root.lemma_

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

        if isinstance(token, (Span, Token)):
            token = token._.CONCEPT

        for attribute, concepts in mk.get_attribute_lookup(self.__class__.group_schema):
            if token.lower() in [concept.lower() for concept in concepts]:
                return attribute
        return ''

    def get_ideology(self, token):

        """
        getter function returning the ideology related to the token concept
        input: string Token, or Span
        output: related ideology
        """

        if isinstance(token, (Span, Token)):
            token = token._.CONCEPT

        for ideology, concepts in mk.get_ideology_lookup(self.__class__.group_schema):
            if token.lower() in [concept.lower() for concept in concepts]:
                return ideology
        return ''

    @staticmethod
    def is_modifier(token):

        """
        function to determine whether a token modifies a span
        """

        tag_modifiers = ["JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS"]
        dep_modifiers = ["amod", "poss", "pobj", "npadvmod", "appos", "compound"]

        if token.tag_ in tag_modifiers and token.dep_ in dep_modifiers:
            return True
        return False

    def get_span_modifier(self, span):

        """
        Getter function to for any modifying tokens of the root.
        """

        word = span.root

        for token in span:
            # when the root is not a conjunct head, can iterate over terms to the left and right
            if self.is_modifier(token) and token.i != word.i:
                return token
            # when the root is a conjunct head, need to isolate only terms to its left
            # return itself as a modifier if no modifiers to the left
            elif token.conjuncts and token.dep_ != "conj":
                return token
        # if no modifier is found return the span root.
        return word

    def get_span_concept(self, span):

        """
        get the concept which defines the span
        if the span has a modifier then the modifier concept is returned
        else the root concept is returned
        """

        concept = self.get_span_modifier(span)._.CONCEPT
        if concept:
            return concept
        return span.root._.CONCEPT

    def get_span_type(self, span):

        """
        getter function to define the span entity type for any named entities modifying the root token
        
        iterates through left facing tokens to the root to identify any modifier terms
        returns: ent_type_ of any modifier named entities
        else returns the span root ent_type_
        """

        # iterate through the span and return any named concepts other than those related to the root.

        ent_type = self.get_span_modifier(span).ent_type_
        if ent_type:
            return ent_type
        return span.root.ent_type_


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

        Doc.set_extension("outgroup_entities", default=[], force=True)
        Doc.set_extension("ingroup_entities", default=[], force=True)
        Token.set_extension("outgroup", default=False, force=True)
        Token.set_extension("ingroup", default=False, force=True)

        self.outgroups = Matcher(nlp.vocab)

        self.outgroups.add("OUTGROUP", None,
                           [{'ENT_TYPE': {"IN": Group_ID.GROUP}}, {"_": {"ATTRIBUTE": "outgroup"}}])

        self.ingroups = Matcher(nlp.vocab)

        self.ingroups.add("INGROUP", None,
                          [{'ENT_TYPE': {"IN": Group_ID.GROUP}}, {"_": {"ATTRIBUTE": "ingroup"}}])

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


def merge_compounds(doc):
    """
    pipeline component to merge compound linked terms in a doc
    
    """

    Token.set_extension("compound_merge", default=False, force=True)

    def get_compound(chunk):

        """
        function which returns compound words of a token
        input: list of a token's left children
        output: the left most compound term
        """

        for token in list(chunk.root.lefts):
            if token.dep_ == "compound":
                return token

    with doc.retokenize() as retokenizer:

        for chunk in doc.noun_chunks:
            if chunk.root.dep_ == "compound":
                continue

            left_token = get_compound(chunk)

            if left_token:
                #             print(doc[left_token.i : chunk.end])

                entity_type = ""
                if left_token.ent_type:
                    entity_type = left_token.ent_type
                else:
                    entity_type = chunk.root.ent_type_

                attrs = {"ENT_TYPE": entity_type,
                         "_": {"compound_merge": True}}
                retokenizer.merge(doc[left_token.i: chunk.end], attrs=attrs)

    return doc


def custom_tokenizer(nlp):
    inf = list(nlp.Defaults.infixes)
    inf = [x for x in inf if
           '-|–|—|--|---|——|~' not in x]  # remove the hyphen-between-letters pattern from infix patterns
    infix_re = compile_infix_regex(tuple(inf))

    infixes = (
            LIST_ELLIPSES
            + LIST_ICONS
            + [
                r'(?<=[0-9])[+\\-\\*^](?=[0-9-])',
                r'(?<=[{al}{q}])\\.(?=[{au}{q}])'.format(
                    al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
                ),
                # REMOVE: commented out regex that splits on hyphens between letters:
                # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
                # EDIT: remove split on slash between letters, and add comma
                # r'(?<=[{a}0-9])[:<>=/](?=[{a}])'.format(a=ALPHA),
                r'(?<=[{a}0-9])[:<>=,](?=[{a}])'.format(a=ALPHA),
                # ADD: ampersand as an infix character except for dual upper FOO&FOO variant
                r'(?<=[{a}0-9])[&](?=[{al}0-9])'.format(a=ALPHA, al=ALPHA_LOWER),
                r'(?<=[{al}0-9])[&](?=[{a}0-9])'.format(a=ALPHA, al=ALPHA_LOWER),
            ]
    )

    infix_re = spacy.util.compile_infix_regex(infixes)

    return Tokenizer(nlp.vocab, prefix_search=nlp.tokenizer.prefix_search,
                     suffix_search=nlp.tokenizer.suffix_search,
                     infix_finditer=infix_re.finditer,
                     token_match=nlp.tokenizer.token_match,
                     rules=nlp.Defaults.tokenizer_exceptions)


def add_hard_coded_entities(nlp, filename):
    with open(filename) as neaF:
        named_entity_additions = json.load(neaF)
    ner_additions = EntityRuler(nlp, overwrite_ents=True, phrase_matcher_attr="LOWER")
    for key, value in named_entity_additions.items():
        patterns = [{"label": key, "pattern": token} for token in value]  # create the pattern dictionary
        ner_additions.add_patterns(patterns)
    base = ['tagger', "parser", "ner"]
    for pipe in list(set(nlp.pipe_names) - set(base)):
        nlp.remove_pipe(pipe)
    nlp.add_pipe(ner_additions, after="ner")
    return nlp
