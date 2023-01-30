"""
module to capture dependency objects
source: https://universaldependencies.org/u/dep/
https://github.com/explosion/spaCy/blob/b69d249a223fa4e633e11babc0830f3b68df57e2/spacy/glossary.py
"""

import srsly
from pathlib import Path

# Set parts of speech labels
verb_tag_list = ["VBN", "VBD", "VBP", "VBG", "VBZ"]
noun_list = ["NOUN", "PROPN", "PRON"]
verb_list = ["VERB"]
adjective_list = ["ADJ"]


# Set dependency labels
subject_deps_list = ["nsubj", "csubj", "agent", "expl"]
subject_passive_deps_list = ["nsubjpass", "csubjpass"]

object_deps_list = ["attr", "oprd"]
direct_object_deps_list = ["dobj"]
dative_deps_list = ["dative"]
prepositional_object_deps_list = ["pobj", "pcomp"]

complements_list = ["ccomp", "xcomp", "acomp"]
nominal_deps_list = ["appos", "acl", "relcl", "det", "predet", "nummod", "amod", "poss", "nmod"]
adverbial_deps_list = ["advmod", "advcl", "neg", "npmod", "npadvmod"]

coordination_deps_list = ["conj", "cc", "preconj"]
preposition_deps_list = ["prep", "agent"]
auxiliary_deps_list = ["aux", "auxpass"]
compound_deps_list = ["compound", "prt", "case", "mark"]
ROOT_list = ["ROOT"]

naming_predicate_list = {
    "LEMMA": {
        "IN": [
            "know",
            "name",
            "namely",
            "baptize",
            "call",
            "christen",
            "dub",
            "entitle",
            "nickname",
            "rename",
        ]
    }
}
verb_tag_list = {"TAG": {"IN": ["VBN", "VBD", "VBP", "VBG", "VBZ"]}}

# create dependency dictionaries dictionaries
_object = {"POS": {"IN": noun_list}}
_subject = {"POS": {"IN": noun_list}}
_verb = {"POS": {"IN": verb_list}}
_adjective = {"POS": {"IN": adjective_list}}

subject_deps = {"DEP": {"IN": subject_deps_list}}
subject_passive_deps = {"DEP": {"IN": subject_passive_deps_list}}
dative_deps = {"DEP": {"IN": dative_deps_list}}
prepositional_object_deps = {"DEP": {"IN": prepositional_object_deps_list}}
adverbial_deps = {"DEP": {"IN": adverbial_deps_list}}

object_deps = {"DEP": {"IN": object_deps_list}}
direct_objects_deps = {"DEP": {"IN": direct_object_deps_list}}

complements_deps = {"DEP": {"IN": complements_list}}

nominal_deps = {"DEP": {"IN": nominal_deps_list}}
adverbial_deps = {"DEP": {"IN": adverbial_deps_list}}

coordination_deps = {"DEP": {"IN": coordination_deps_list}}
preposition_deps = {"DEP": {"IN": preposition_deps_list}}
auxiliary_deps = {"DEP": {"IN": auxiliary_deps_list}}
compound_deps = {"DEP": {"IN": compound_deps_list}}
ROOT = {"DEP": {"IN": ROOT_list}}

               
#combine pos and dependency dictionaries
_subject = {**_subject, **subject_deps}
_subject_passive = {**_subject, **subject_passive_deps}

_object = {**_object, **object_deps}
_direct_object = {**_object, **direct_objects_deps}
_prepositional_object = {**_object, **prepositional_object_deps}
_adposition = {"POS": "ADP"}
_dative = {**_object, **dative_deps}

_verb_complement = {**_verb, **complements_deps}
_adjective_complement = {**_adjective, **complements_deps}



def join_objs(d1, lst):
    DEPS = []
    for entry in lst:
        DEPS += entry["DEP"]["IN"]

    return dict([("POS", d1["POS"]), ("DEP", {"IN": d1["DEP"]["IN"] + DEPS})])
