import csv
import json
import os
from pathlib import Path

import spacy
from spacy import displacy
from spacy.matcher import DependencyMatcher
from spacy.pipeline import merge_entities
from spacy.tokens import Token


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


def load_jsonl(input_path) -> list:
    """
    Read list of objects from a JSON lines file.
    """
    data = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.rstrip('\n|\r')))
    print('Loaded {} records from {}'.format(len(data), input_path))
    return data


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe(merge_entities)
nlp.add_pipe(merge_compounds, after="ner")


def doc_dep_graph(doc):
    """
    Put the graph with entity labels present (see 'tag' and 'label')
    """

    words = []  # the words of a dependency graph
    arcs = []  # the arcs of a dependency graph

    # iterate through each token in a doc
    for tok in doc:

        # if the token is not a named entity, use the named entity tag
        if tok.ent_type == 0:
            tag = f"{tok.pos_}, ({tok.tag_}), ({tok.head})"
        else:
            # else use the named entity label with its pos tag
            tag = "_::" + tok.ent_type_ + " (" + tok.tag_ + ")::_"

        # create a dictionary of the words with their tags
        words.append({
            "text": tok.text,
            "tag": tag
        })

        # ignore punctuation
        if tok.dep_ in {'punct'}:
            continue

        # if the token index is less than its head, the token is the head
        if tok.i < tok.head.i:
            arcs.append({
                "start": tok.i,
                "end": tok.head.i,
                "label": tok.dep_,
                "dir": "left"
            })

        # if the token index is greater than its head, the token head is the head
        elif tok.i > tok.head.i:
            arcs.append({
                "start": tok.head.i,
                "end": tok.i,
                "label": tok.dep_,
                "dir": "right"
            })
    return {"words": words, "arcs": arcs}


def output_to_svg(filename, dep):
    """Save the dependency graph to SVG """
    svg = spacy.displacy.render(dep, style="dep",
                                jupyter=False, manual=True)
    Path(filename + ".svg").open("w", encoding="utf-8").write(svg)


def get_dep_matcher(nlp, patterns, pattern_names=None) -> object:
    """ Add patterns with pattern_names to the dependency matcher """
    if pattern_names is None:
        pattern_names = ["pattern" + str(pi) for pi in range(len(patterns))]
    else:
        pattern_names = [x for x in pattern_names]
    matcher = DependencyMatcher(nlp.vocab)
    for pi, pattern in enumerate(patterns):
        #         print("pattern names: ", pattern_names[pi], pattern)
        matcher.add(pattern_names[pi], None, pattern)
    return matcher


def predicate_matching(doc, matcher, patterns):
    """
    Match the patterns to a doc, returns dep graph with edges that match 
    """

    matches = []
    # iterate through the matches
    for match in matcher(doc):

        # capture the match label
        match_id = nlp.vocab.strings[match[0]]

        for subtree in match[1]:
            for i, idx in zip(range(len(subtree)), subtree):
                pattern = patterns[match_id][i]["SPEC"]["NODE_NAME"]
                if pattern == "SUBJECT":
                    clause_subject = doc[idx]
                if pattern == "OBJECT":
                    clause_object = doc[idx]
            clause_subject._.isKnownAs = (match_id, clause_object)
            print(f"{clause_subject} {str(clause_subject._.isKnownAs[0])} {str(clause_subject._.isKnownAs[1])}")

        # isolate the matches from the output
        for subtrees in match[1]:
            # print("pattern: ", [doc[idx] for idx in subtrees])

            # capture the words of the dependency match
            words = [{"text": t.text, "tag": t.pos_} for t in doc]

            # check of for subtrees that are not lists
            if not isinstance(subtrees[0], list):
                subtrees = [subtrees]

            # iterate through each of the matches
            for subtree in subtrees:
                # print("subtree: ", subtree)
                arcs = []

                tree_indices = set(subtree)

                # capture the hypernyms and hyponyms
                # this is the point at which hyponymns and hypernyms are captured
                hyps = []
                for token in subtree:
                    left_token = token
                    for mod in doc[token].children:
                        if mod.dep_ in ["amod", "nmod"] and doc[token].pos_ in ["NOUN", "PROPN", "PRON"]:
                            left_token = mod.i
                    hyps.append(doc[left_token: token + 1])

                # hyps = [doc[t] for t in subtree]

                # iterate through the subtree to capture the words and arcs for displaying dependency graph
                for index in subtree:

                    # capture the token and token head
                    token = doc[index]
                    head = token.head

                    # if the token head is the token or is outside the range of matched words, then continue
                    if token.head.i == token.i or token.head.i not in tree_indices:
                        continue

                    else:
                        if token.i < head.i:
                            arcs.append(
                                {
                                    "start": token.i,
                                    "end": head.i,
                                    "label": token.dep_,
                                    "dir": "left",
                                }
                            )
                        else:
                            arcs.append(
                                {
                                    "start": head.i,
                                    "end": token.i,
                                    "label": token.dep_,
                                    "dir": "right",
                                }
                            )

                matches.append({"words": words, "arcs": arcs, "match_id": match_id, "hyps": hyps})

    return matches


patterns = {}

naming_predicate_list = ["know", "name", "namely", "baptize", "call", "christen",
                         "dub", "entitle", "nickname", "rename"]
verb_tag_list = ["VBN", "VBD", "VBP", "VBG", "VBZ"]
_object = {"POS": {"IN": ["NOUN", "PROPN"]}}
_subject = {"POS": {"IN": ["NOUN", "PROPN", "PRON"]}}
subject_deps = {"DEP": {"IN": ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]}}
object_deps = {"DEP": {"IN": ["dobj", "dative", "attr", "oprd"]}}
complements_deps = {"DEP": {"IN": ["ccomp", "xcomp", "acomp"]}}
nominal_deps = {"DEP": {"IN": ["appos", "acl", "relcl", "det", "predet", "nummod", "amod", "poss", "nmod"]}}
adverbial_deps = {"DEP": {"IN": ["advmod", "advcl", "neg", "npmod"]}}
preposition_deps = {"DEP": {"IN": ["pobj", "pcomp"]}}
coordination_deps = {"DEP": {"IN": ["conj", "cc", "preconj", "prep"]}}
auxiliary_deps = {"DEP": {"IN": ["aux", "auxpass"]}}
compound_deps = {"DEP": {"IN": ["compound", "prt", "case", "mark"]}}
_object = {**_object, **object_deps}
_subject = {**_subject, **subject_deps}


def join_objs(d1, lst):
    DEPS = []
    for entry in lst:
        DEPS += entry["DEP"]["IN"]

    return dict([("POS", d1["POS"]), ("DEP", {"IN": d1["DEP"]["IN"] + DEPS})])


# # In reference to UD framework categories one of six subject dependency labels generally refer to a clause's
# subject, # and one of four object labels refer to the object, while one of two prepositional or one of three
# complement labels can refer to either. # Therefore, these different labels are joined together


patterns.update({"isKnownAs": [  # object naming object

    # organisation known as / named

    {"PATTERN": join_objs(_object, [preposition_deps]),
     "SPEC": {"NODE_NAME": "OBJECT"}},

    {"PATTERN": {
        "LEMMA": {"IN": naming_predicate_list}},
        "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "PREDICATE"}},

    {"PATTERN": join_objs(_object, [_subject, preposition_deps]),
     "SPEC": {"NBOR_NAME": "PREDICATE", "NBOR_RELOP": ">>", "NODE_NAME": "SUBJECT"}}
]})

patterns.update({"isNamely": [  # object naming object

    # organisation known as / named

    {"PATTERN": join_objs(_object, [preposition_deps]),
     "SPEC": {"NODE_NAME": "OBJECT"}},

    {"PATTERN": join_objs(_object, [nominal_deps]),
     "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "SUBJECT"}},

    {"PATTERN": {
        "LEMMA": {"IN": naming_predicate_list}},
        "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": ">", "NODE_NAME": "MODIFIER"}},
]})

# # patterns.update({"PredicateVerb": [  # Hyponym verb (prep) Hypernym (reverse)
# #     {"PATTERN": hypernym,
# #      "SPEC": {"NODE_NAME": "OBJECT"}},
# #
# #     {"PATTERN": {
# #         "POS": {"IN": ["AUX"]}},
# #         "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": "<", "NODE_NAME": "VERB_PREDICATE"}},
# #
# #     {"PATTERN": hyponym,
# #      "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "SUBJECT"}}
# # ]})
#
# patterns.update({"preposition": [  # Hyponym verb prep  Hypernym (reverse)
#
#     # enemy of America
#
#     {"PATTERN": join_objs(hypernym, [preposition_deps]),
#      "SPEC": {"NODE_NAME": "NOUN_HYPERNYM"}},
#
#     {"PATTERN": {
#         "DEP": {"IN": ["prep"]},
#         "POS": {"NOT_IN": ["VERB"]}},  # TODO: this needs to be fixed to be an adjacent token
#         "SPEC": {"NBOR_NAME": "NOUN_HYPERNYM", "NBOR_RELOP": ">", "NODE_NAME": "PREP_PREDICATE"}},
#
#     # {"PATTERN": {
#     #     "POS": "VERB"},
#     #     "SPEC": {"NBOR_NAME": "PREP_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "VERB_PREDICATE"}},
#
#     {"PATTERN": join_objs(hypernym, [preposition_deps]),
#      "SPEC": {"NBOR_NAME": "PREP_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "HYPONYM"}}
# ]})
#
patterns.update({"verbPredicate": [  # Hypernym verb Hyponym

    # who attacked our country
    {"PATTERN": _subject,
     "SPEC": {"NODE_NAME": "SUBJECT"}},

    {"PATTERN": {
        "TAG": {"IN": verb_tag_list}},
        "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": "<", "NODE_NAME": "VERB_PREDICATE"}},

    # {"PATTERN": {
    #     "DEP": {"IN": ["neg"]}},
    #     "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "NEGATION"}},

    {"PATTERN": join_objs(_object, [complements_deps]),
     "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">>", "NODE_NAME": "OBJECT"}}
]})
#
# patterns.update({"verbcompPredicate": [
#
#     # mafia is to crime
#
#     {"PATTERN": hyponym,
#      "SPEC": {"NODE_NAME": "SUBJECT"}},
#
#     {"PATTERN": {
#         "TAG": {"IN": verb_tag_list}},
#         "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": "<", "NODE_NAME": "VERB_PREDICATE"}},
#
#     {"PATTERN": complements_deps,
#      "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "2_VERB_PREDICATE"}},
#
#     {"PATTERN": join_objs(hypernym, [complements_deps]),
#      "SPEC": {"NBOR_NAME": "2_VERB_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "OBJECT"}}
# ]})
#
# patterns.update({"verbprepPredicate": [  # Hypernym verb (prep) Hyponym
#
#     # war begins with al Qaeda
#
#     {"PATTERN": hyponym,
#      "SPEC": {"NODE_NAME": "SUBJECT"}},
#
#     {"PATTERN": {
#         "TAG": {"IN": verb_tag_list}},
#         "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": "<", "NODE_NAME": "VERB_PREDICATE"}},
#
#     {"PATTERN": {
#         "DEP": {"IN": ["prep"]}}, # TODO: this needs to be fixed to be an adjacent token
#         "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "PREP"}},
#
#     {"PATTERN": join_objs(hypernym, [complements_deps, preposition_deps]),
#      "SPEC": {"NBOR_NAME": "PREP", "NBOR_RELOP": ">", "NODE_NAME": "OBJECT"}}
# ]})
#
# prepPredicate_list = ["like", "include", "except", "whether", "as"]
# patterns.update({"prepHyponym": [  # Hyponym prep Hypernym
#     {"PATTERN": join_objs(hyponym, [preposition_deps]),
#      "SPEC": {"NODE_NAME": "OBJECT"}},
#
#     {"PATTERN": {
#         "LEMMA": {"IN": prepPredicate_list}},
#         "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "PREP_PREDICATE"}},
#
#     {"PATTERN": join_objs(hyponym, [preposition_deps]),
#      "SPEC": {"NBOR_NAME": "PREP_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "SUBJECT"}}
# ]})
#
# patterns.update({"modifierSubject": [  # Hypernym, modifer Hyponym
#     {"PATTERN": hypernym,
#      "SPEC": {"NODE_NAME": "OBJECT"}},
#
#     {"PATTERN": {"DEP": {"IN": ["appos", "conj"]}},
#      "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "SUBJECT"}},
#
#     {"PATTERN": {
#         "DEP": {"IN": ["amod", "advmod"]}},
#         "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": ">", "NODE_NAME": "MODIFIER"}}
# ]})
#
# patterns.update({"subjectPrep": [  # Hypernym, modifer Hyponym
#     {"PATTERN": hypernym,
#      "SPEC": {"NODE_NAME": "OBJECT"}},
#
#     {"PATTERN": {"DEP": {"IN": ["appos", "conj"]}},
#      "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "SUBJECT"}},
#
#     {"PATTERN": {
#         "LOWER": "instance"},
#         "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": ">>", "NODE_NAME": "INSTANCE"}}
# ]})
#
# patterns.update({"modifierPredicate": [  # Hyponym modifer (prep) Hypernym
#     {"PATTERN": hypernym,
#      "SPEC": {"NODE_NAME": "OBJECT"}},
#
#     {"PATTERN": {
#         "DEP": {"IN": ["amod", "advmod"]}},
#         "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "MODIFIER"}},
#
#     # {"PATTERN": {
#     #     "DEP": {"IN": ["prep"]}},
#     #     "SPEC": {"NBOR_NAME": "MODIFIER", "NBOR_RELOP": ">", "NODE_NAME": "PREP"}},
#
#     {"PATTERN": {
#         "DEP": {"IN": ["pobj", "appos", "conj"]}},
#         "SPEC": {"NBOR_NAME": "MODIFIER", "NBOR_RELOP": ">>", "NODE_NAME": "SUBJECT"}}
# ]})
#
# patterns.update({"otherPredicate": [  # hyponym other hypernym
#     {"PATTERN": hyponym,
#      "SPEC": {"NODE_NAME": "SUBJECT"}},
#
#     {"PATTERN": {
#         "LOWER": "other"},
#         "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": ">", "NODE_NAME": "other"}},
#
#     {"PATTERN": hypernym,
#      # "DEP": {"IN": ["conj", "attr", "pobj"]}},
#      "SPEC": {"NBOR_NAME": "SUBJECT", "NBOR_RELOP": "<", "NODE_NAME": "OBJECT"}},
# ]})
#
# patterns.update({"hasRelationship": [
#     {"PATTERN": hyponym,
#      "SPEC": {"NODE_NAME": "OBJECT"}},
#
#     {"PATTERN": {
#         "POS": {"IN": ["AUX"]}},
#         "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": "<", "NODE_NAME": "VERB_PREDICATE"}},
#
#     {"PATTERN": join_objs(hypernym, [complements_deps]),
#      "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">", "NODE_NAME": "NOUN_PHRASE"}},
#
#     {"PATTERN": {
#         "DEP": {"IN": ["prep"]}},
#         "SPEC": {"NBOR_NAME": "NOUN_PHRASE", "NBOR_RELOP": ">", "NODE_NAME": "PREP"}},
#
#     {"PATTERN": preposition_deps,
#      "SPEC": {"NBOR_NAME": "PREP", "NBOR_RELOP": ">", "NODE_NAME": "SUBJECT"}}
# ]})
#
# #
# # patterns.update({"whichverbPredicate": [  # Hypernym verb Hyponym
# #     {"PATTERN": hypernym,
# #         "SPEC": {"NODE_NAME": "OBJECT"}},
# #
# #     {"PATTERN": {
# #         "TAG": {"IN": verb_tag_list}},
# #         "SPEC": {"NBOR_NAME": "OBJECT", "NBOR_RELOP": ">", "NODE_NAME": "VERB_PREDICATE"}},
# #
# #     {"PATTERN": hyponym,
# #         "SPEC": {"NBOR_NAME": "VERB_PREDICATE", "NBOR_RELOP": ">>", "NODE_NAME": "SUBJECT"}}
# # ]})

filepath = "C:\\Users\\spa1e17\\OneDrive - University of Southampton\\Hostile-Narrative-Analysis\\Obj 1 - detect " \
           "ingroup and outgroup of a text"
filename = "hyp_test.jsonl"
texts = load_jsonl(os.path.join(filepath, filename))

filename = "entity_list_gold.txt"
filename = os.path.join(filepath, filename)

test_data = []

with open(filename, newline="") as fp:
    data = csv.DictReader(fp, delimiter='\t')

    for entry in data:
        test_data.append(entry)

# test_data = [
#     "They want to overthrow existing governments in many Muslim countries, such as Egypt, Saudi Arabia, and Jordan."
# #     "Al Qaeda is to terror what the mafia is to crime."
# # #     "They want to overthrow existing governments in many Muslim countries, such as Egypt, Saudi Arabia, and Jordan."
# # #     "Al Qaeda is to terror what the mafia is to crime.",
# # #     "The Aryan himself was probably at first a nomad and became a settler in the course of ages",
# # #     "The Jew has never been a nomad, but always a parasite, battening on the substance of others",
# ]

test_data = [
    "passengers like an exceptional man named Todd Beamer",
    "a collection of loosely affiliated terrorist organizations known as al Qaeda.",
    "leaving the main enemy in the region, namely the Jewish-American alliance",
    "The Aryan himself was probably at first a nomad and became a settler in the course of ages",
    "The Jew has never been a nomad, but always a parasite, battening on the substance of others",
]

Token.set_extension("isKnownAs", default="", force=True)

seen_sents = set()
for text in test_data:
    matcher = get_dep_matcher(nlp, patterns.values(), patterns.keys())
    if not isinstance(text, str):
        text = text["Sentence"]
    if text not in seen_sents:
        doc = nlp(text)
        matched_edges = predicate_matching(doc, matcher, patterns)
        print(doc)
        for match in matched_edges:
            print(match['match_id'], '=>', match['hyps'])
        print('-----')
    seen_sents.add(text)
    # dep_graph = doc_dep_graph(doc)
    # displacy.render(dep_graph, style="dep", jupyter=True, manual=True)
    #
    # if matched_edges:
    #     tree = dict(words=matched_edges[0]['words'], arcs=matched_edges[0]['arcs'])
    #     displacy.render(tree, style="dep", jupyter=True, manual=True)
    # else:
    #     print('nothing found')
