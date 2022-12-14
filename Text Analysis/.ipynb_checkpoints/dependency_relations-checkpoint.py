from typing import Iterable, Union, Type

import spacy
from spacy import Language
from spacy.language import Doc
from spacy.matcher import DependencyMatcher
import networkx as nx

from striad.nlp.ner2.components.named_pipe import NamedPipe
from striad.nlp.ner2.patterns.dependency import (
    AnyConnectedEntities,
    BaseDependencyPattern,
)
from striad.nlp.spacy_registry_factory import SpacyRegistryFactory


def _ensure_iterable(items):
    if isinstance(items, Iterable):
        return items
    else:
        return [items]


_default_dependency_patterns = [AnyConnectedEntities()]


def dependency_graph(doc):
    """Creates a networkx graph from a document's dependency tree"""
    graph = nx.Graph()
    for token in doc:
        graph.add_node(token.i, text=token.lower_, pos=token.pos_)
    for token in doc:
        for child in token.children:
            graph.add_edge(
                token.i,
                child.i,
                source_text=token.lower_,
                target_text=child.lower_,
                dep=token.dep_,
            )
    # print(json.dumps(nx.node_link_data(graph), indent=4))
    return graph


def clause_path(dep_graph, source_i, target_i):
    """Finds the shortest path between to entities in a dependency graph"""
    try:
        return sorted(nx.shortest_path(dep_graph, source_i, target_i))
    except:
        return None


def edge_indexes(a, b):
    """Orders the matched dependency path (of length 2)"""
    if a < b:
        return a, b
    else:
        return b, a


class DependencyRelationsExtractor(NamedPipe):
    def __init__(self, vocab, dependency_patterns=None):
        if dependency_patterns is None:
            dependency_patterns = _default_dependency_patterns
        dependency_patterns = _ensure_iterable(dependency_patterns)
        self.dependency_patterns = dependency_patterns
        self._init_matcher(vocab, dependency_patterns)
        Doc.set_extension("relationships", default=[], force=True)

    @classmethod
    def pipe_name(self):
        return "DependencyRelationsExtractor"

    def __call__(self, doc):
        if len(self.dependency_patterns) == 0:
            return doc
        dep_graph = dependency_graph(doc)
        for match_id, token_indexes in self.matcher(doc):
            source_i, target_i = edge_indexes(*token_indexes)
            clause_i = clause_path(dep_graph, source_i, target_i)
            doc._.relationships.append(
                {
                    "source_i": source_i,
                    "target_i": target_i,
                    "source_text": doc[source_i].text,
                    "target_text": doc[target_i].text,
                    "clause": [doc[i].text for i in clause_i],
                    "label": doc.vocab.strings[match_id],
                }
            )
            # print("MATCHED", [doc[i] for i in token_indexes], [doc[i] for i in clause_i])
        return doc

    def _init_matcher(self, vocab, dependency_patterns):
        self.matcher = DependencyMatcher(vocab, validate=True)
        for dependency in dependency_patterns:
            self.matcher.add(dependency.label, dependency.patterns)


@Language.factory(
    DependencyRelationsExtractor.pipe_name(),
    assigns=["doc._.relationships"],
    default_config={"dependency_patterns": _default_dependency_patterns},
)
def create_entity_pattern_recognizer(
    nlp, name, dependency_patterns: Iterable[Union[str, Type[BaseDependencyPattern]]]
):
    factory = SpacyRegistryFactory(BaseDependencyPattern)
    return DependencyRelationsExtractor(
        nlp.vocab, dependency_patterns=factory.create_objects(dependency_patterns)
    )
