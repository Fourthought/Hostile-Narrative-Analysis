"""
module to capture dependency patterns
"""

import srsly
from pathlib import Path

pattern_data_dir = Path(__file__).parent / "pattern_data"
patterns_path = pattern_data_dir / "syntacticpatterns_v2.jsonl"
# print(patterns_path)

dependency_patterns = list(srsly.read_jsonl(patterns_path))

verb_tag_list = ["VBN", "VBD", "VBP", "VBG", "VBZ"]
subject_list = ["NOUN", "PROPN", "PRON"]
object_list = ["NOUN", "PROPN"]
subject_deps_list = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
object_deps_list = ["dobj", "dative", "attr", "oprd"]
complements_list = ["ccomp", "xcomp", "acomp"]
nominal_deps_list = [
    "appos",
    "acl",
    "relcl",
    "det",
    "predet",
    "nummod",
    "amod",
    "poss",
    "nmod",
]
adverbial_deps_list = ["advmod", "advcl", "neg", "npmod"]
preposition_deps_list = ["pobj", "pcomp"]
coordination_deps_list = ["conj", "cc", "preconj", "prep"]
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
_object = {"POS": {"IN": ["NOUN", "PROPN"]}}
_subject = {"POS": {"IN": ["NOUN", "PROPN", "PRON"]}}
subject_deps = {
    "DEP": {"IN": ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]}
}
object_deps = {"DEP": {"IN": ["dobj", "dative", "attr", "oprd"]}}
complements_deps = {"DEP": {"IN": ["ccomp", "xcomp", "acomp"]}}
nominal_deps = {
    "DEP": {
        "IN": [
            "appos",
            "acl",
            "relcl",
            "det",
            "predet",
            "nummod",
            "amod",
            "poss",
            "nmod",
        ]
    }
}
adverbial_deps = {"DEP": {"IN": ["advmod", "advcl", "neg", "npmod"]}}
preposition_deps = {"DEP": {"IN": ["pobj", "pcomp"]}}
coordination_deps = {"DEP": {"IN": ["conj", "cc", "preconj", "prep"]}}
auxiliary_deps = {"DEP": {"IN": ["aux", "auxpass"]}}
compound_deps = {"DEP": {"IN": ["compound", "prt", "case", "mark"]}}
ROOT = {"DEP": {"IN": ["ROOT"]}}
_object = {**_object, **object_deps}
_subject = {**_subject, **subject_deps}


def join_objs(d1, lst):
    DEPS = []
    for entry in lst:
        DEPS += entry["DEP"]["IN"]

    return dict([("POS", d1["POS"]), ("DEP", {"IN": d1["DEP"]["IN"] + DEPS})])


if __name__ == "__main__":

    for pattern in dependency_patterns:
        print(pattern)
