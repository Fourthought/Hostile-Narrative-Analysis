# resources:
# https://qqeng.net/Learning/basic-sentence-patterns-in-english/
# https://blog.collinsdictionary.com/language-lovers/what-are-grammar-patterns/#:~:text=There%20are%205%20main%20types%20of%20verb%20patterns.&text=The%20types%20of%20clauses%20identified,infinitive%20clauses%20and%20infinitive%20clauses.&text=prepositional%20phrase%20or%20adverb.
# https://grammar.collinsdictionary.com/grammar-pattern
# https://webapps.towson.edu/ows/sentpatt.htm

from dependency_objects import _subject, _subject_passive, _object, _direct_object
from dependency_objects import _prepositional_object, coordination_deps, _adposition, preposition_deps, prepositional_object_deps, adverbial_deps
from dependency_objects import _adjective_complement, _verb_complement, _dative
NOUN = {"POS": {"IN": ["NOUN", "PROPN", "PRON"]}}
VERB = {"POS": "VERB", "DEP": {"NOT_IN": ["relcl", "pcomp"]}}
ROOT = {"POS": "VERB", "DEP": "ROOT"}
ADJ = {"POS": "ADJ"}
ADV = {"POS": "ADV"}
AUX = {"POS": "AUX"}
it = {"LEMMA": "it"}

base_patterns = [
    {
        "pattern_name": "BaseActive",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
            ],
        "category": "Base", "inverse": "isBaseOf"
    },
    {
        "pattern_name": "BasePassive",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject_passive},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "OBJECT", "RIGHT_ATTRS": _object},
            ],
        "category": "Base", "inverse": "isBaseOf"
    },
    {
        "pattern_name": "BaseAttribute",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": AUX},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "OBJECT", "RIGHT_ATTRS": _object},
            ],
        "category": "Base", "inverse": "isBaseOf"
    },
    {
        "pattern_name": "BasePassiveAttribute",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": AUX},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject_passive},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "OBJECT", "RIGHT_ATTRS": _object},
            ],
        "category": "Base", "inverse": "isBaseOf"
    }
]

patterns = [

    {
        "pattern_name": "SimpleDirectObject",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "DIRECTOBJECT", "RIGHT_ATTRS": _direct_object},
            ],
        "category": "hasAction", "inverse": "isActionOf"
    },

    {
        "pattern_name": "SimpleAdjective",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": AUX},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "ATTRIBUTE", "RIGHT_ATTRS": ADJ},
            ],
        "category": "hasAttribute", "inverse": "isAttributeOf"
    },
    {
        "pattern_name": "SimpleAttribute",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": AUX},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "ATTRIBUTE", "RIGHT_ATTRS": _object},
            ],
        "category": "hasAttribute", "inverse": "isAttributeOf"
    },
    {
        "pattern_name": "SimpleAdverb",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": AUX},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "MODIFIER", "RIGHT_ATTRS": ADV},
            ],
        "category": "hasAttribute", "inverse": "isAttributeOf"
    },
    {
        "pattern_name": "SimpleVerbComplement",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "VERBCOMPLEMENT", "RIGHT_ATTRS": _verb_complement},
            ],
        "category": "hasEvent", "inverse": "isEventOf"
    },
    {
        "pattern_name": "SimpleAdjectiveComplement",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "ADJECTIVECOMPLEMENT", "RIGHT_ATTRS": _adjective_complement},
            ],
        "category": "hasEvent", "inverse": "isEventOf"
    },
    {
        "pattern_name": "SimpleNounPreposition",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "PREPOSITION", "RIGHT_ATTRS": preposition_deps},
                {"LEFT_ID": "PREPOSITION", "REL_OP": ">", "RIGHT_ID": "PREPOSITIONALOBJECT", "RIGHT_ATTRS": _prepositional_object},
            ],
        "category": "hasLinkTo", "inverse": "isLinkedTo"
    },
    {
        "pattern_name": "SimpleAdverbialModifier",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "MODIFIER", "RIGHT_ATTRS": adverbial_deps},
            ],
        "category": "hasLinkTo", "inverse": "isLinkedTo"
    },
    {
        "pattern_name": "SimpleAdverbPreposition",
        "pattern":
            [
                {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
                # {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
                {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "PREPOSITION", "RIGHT_ATTRS": adverbial_deps},
                {"LEFT_ID": "PREPOSITION", "REL_OP": ">", "RIGHT_ID": "MODIFIER", "RIGHT_ATTRS": {"DEP": {"IN": ["pobj", "pcomp"]}, "POS": {"NOT_IN": ["NOUN", "PRON"]}}},
            ],
        "category": "hasLinkTo", "inverse": "isLinkedTo"
    },
    # {
    #     "pattern_name": "Ditransitive",
    #     "pattern":
    #         [
    #             {"RIGHT_ID": "PREDICATE", "RIGHT_ATTRS": VERB},
    #             {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "SUBJECT", "RIGHT_ATTRS": _subject},
    #             {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "INDIRECTOBJECT", "RIGHT_ATTRS": _dative},
    #             {"LEFT_ID": "PREDICATE", "REL_OP": ">", "RIGHT_ID": "DIRECTOBJECT", "RIGHT_ATTRS": _object},
    #         ],
    #     "category": "hasEvent", "inverse": "isEventOf"
    # },
]