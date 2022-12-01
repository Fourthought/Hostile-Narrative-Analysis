"""
module to capture dependency patterns

Taken from and organised by ClearNLP schema
https://github.com/clir/clearnlp-guidelines/blob/master/md/specifications/dependency_labels.md
"""

# import srsly
# from pathlib import Path

# pattern_data_dir = Path(__file__).parent / "pattern_data"
# patterns_path = pattern_data_dir / "syntacticpatterns_v2.jsonl"
# # print(patterns_path)

# dependency_patterns = list(srsly.read_jsonl(patterns_path))

verb_list = ["VBN", "VBD", "VBP", "VBG", "VBZ"]
subject_list = ["NOUN", "PROPN", "PRON"]
object_list = ["NOUN", "PROPN"]


subject_deps_list = ["nsubj", "csubj", "agent", "expl"]
passive_subject_deps_list = ["nsubjpass", "csubjpass"]
object_deps_list = ["dobj", "dative", "attr", "oprd", "prt"]

complements_list = ["ccomp", "xcomp", "acomp"]
nominal_deps_list = ["appos", "acl", "relcl", "det", "predet", "nummod", "amod", "poss", "nmod"]
adverbial_deps_list = ["advmod", "advcl", "neg", "npmod"]
preposition_deps_list = ["pobj", "pcomp"]
coordination_deps_list = ["conj", "cc", "preconj", "prep"]
auxiliary_deps_list = ["aux", "auxpass"]
compound_deps_list = ["compound", "prt", "case", "mark"]
ROOT_list = ["ROOT"]

naming_predicate_list = {"LEMMA": {"IN": ["know", "name", "namely", "baptize", "call", "christen", "dub", "entitle", "nickname", "rename"]}}
verb_tag_list = {"TAG": {"IN": verb_list}}
object_pos = {"POS": {"IN": subject_list}}
subject_pos = {"POS": {"IN": subject_list}}
subject_deps = {"DEP": {"IN": subject_deps_list}}
subject_passive_deps = {"DEP": {"IN": passive_subject_deps_list}}
object_deps = {"DEP": {"IN": object_deps_list}}
complements_deps = {"DEP": {"IN": complements_list}}
nominal_deps = {"DEP": {"IN": nominal_deps_list}}
adverbial_deps = {"DEP": {"IN": adverbial_deps_list}}
preposition_deps = {"DEP": {"IN": preposition_deps_list}}
coordination_deps = {"DEP": {"IN": coordination_deps_list}}
auxiliary_deps = {"DEP": {"IN": auxiliary_deps_list}}
compound_deps = {"DEP": {"IN": compound_deps_list}}
ROOT = {"DEP": {"IN": ROOT_list}}
agent_dep = {"DEP": {"IN": ["agent"]}}

_object = {**object_pos, **object_deps}
_subject = {**subject_pos, **subject_deps}
_subject_passive = {**subject_pos, **subject_passive_deps}
_adjective = {"POS": "ADJ"}


def join_objs(d1, lst):
    DEPS = []
    for entry in lst:
        DEPS += entry["DEP"]["IN"]

    return dict([("POS", d1["POS"]), ("DEP", {"IN": d1["DEP"]["IN"] + DEPS})])
