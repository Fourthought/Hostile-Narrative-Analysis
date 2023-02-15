import pandas as pd
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span, Token
from spacy.symbols import NOUN, PROPN, PRON, ADJ, ADV, ADP, VERB, AUX, CCONJ
from customchunks import chunker
from copy import copy, deepcopy

def get_span(token):
    
    def is_verb(word):
        verb_labels = [VERB, AUX]
        return word.pos in verb_labels
    
    def is_negated_verb(word, neighbour):
        
        neg_deps = ["neg"]

        if neighbour.dep_ in neg_deps:
            return neighbour.i
        return word.i
    
    def is_noun_or_adjective(word):
        
        pos_labels = [NOUN, PROPN, PRON, ADJ, ADV]

        return word.pos in pos_labels


    def get_left_edge(word):
        
        if is_verb(word):
            if word.i > 0:
                return is_negated_verb(word, word.nbor(-1))
            return word.i

        return word.left_edge.i

    def get_right_edge(word):
        
        def is_not_last_token_in_doc(word):
            return word.i + 1 < len(word.doc)
            
        if is_verb(word):
            if is_not_last_token_in_doc(word):
                return is_negated_verb(word, word.nbor())
            return word.i
        
        if not is_noun_or_adjective(word):
            return word.i
        
        return word.right_edge.i
    
    return Span(token.doc, get_left_edge(token), get_right_edge(token) + 1)


class Clause(dict):
    
    def is_linked(self, item):
        # print(f'is_linked: {item.get("predicate", False) == self.get("predicate", False)}')
        return self.is_base() and item.get("PREDICATE", None) == self.get("PREDICATE", False)
    
    def is_base(self):
        return "SUBJECT" in self
    
    def is_extension(self):
        return not self.is_base()

class CustomDependencyMatcher:

    def __init__(self, matcher, patterns):
        
        self.matcher = matcher
        self.get_span = get_span
        
        self.pattern_labels = {}

        if patterns:
            self.add_patterns(patterns)
            
    def __call__(self, doclike):

        doc = doclike.doc
        
        base_matches = []
        extensions = []
        
        for match in self.get_matches(doc):
            if match.is_base():
                base_matches.append(copy(match))
            if match.is_extension():
                extensions.append(copy(match))
        
        for base in base_matches:
            
            link = False
            
            for extension in extensions:
                
                if base.is_linked(extension):
                    clause = copy(base)
                    clause.update(extension)
                    link = True
                    yield clause
            
            if not link:
                yield match
    
    def get_matches(self, doclike):

        doc = doclike.doc

        matches = []

        for match in self.matcher(doc):

            # get the pattern name (match_id) and list of matched tokens (token_ids)
            match_id, token_ids = match
            match_id = doc.vocab.strings[match_id]
            pattern = self.matcher.get(match_id)[1][0]
            
            pairs = []
                        
            for i in range(len(token_ids)):

                RIGHT_ID = pattern[i]["RIGHT_ID"]
                token = doc[token_ids[i]]
                
                span = self.get_span(token)
                
                for conjunction in self.get_conjunctions(span):
                    pairs.append({RIGHT_ID.upper() : conjunction})             
            
            
            for clause in self.get_clauses_from_pairs(pairs, match_id):
                
                yield clause
    
    def get_clauses_from_pairs(self, pairs, match_id):
        
        extras = []
        clauses = []
        clause = Clause(RULE = match_id)
        for pair in pairs:
            if set(list(pair)).isdisjoint(set(list(clause))):
                clause.update(pair)
            else:
                extras.append(pair)
        clauses.append(clause)
        
        for extra in extras:
            new_clause = copy(clause)
            new_clause.update(pair)
            clauses.append(new_clause)

        return clauses
            
    
    def get_conjunctions(self, span):
        
        def get_right_edge(word):
            for i in range(word.i, word.right_edge.i):
                if word.doc[i].pos == CCONJ:
                    if word.doc[i].is_punct:
                        return i - 1
                    return i     
            return word.right_edge.i
            
            
        conjuncts = list(span.root.conjuncts)
        spans = []
        if conjuncts:
            spans.append(Span(span.doc, span.root.left_edge.i, get_right_edge(span.root)))
            for conjunct in conjuncts:
                spans.append(Span(span.doc, conjunct.left_edge.i, conjunct.right_edge.i + 1))
            return spans
            
        return [span]

    def add_patterns(self, patterns):

        """
        function to add patterns to the dependency pattern matcher
        - if the pattern name is not in the pattern list, the pattern is added
        - if the pattern name is in the list, the pattern is replaced
        """

        for pattern in patterns:

            label = pattern["pattern_name"]
            dep_pattern = pattern["pattern"]

            if label in self.matcher:
                print("Replacing: ", label)
                self.matcher.remove(label)

            self.matcher.add(label, [dep_pattern])
            self.pattern_labels[label] = {
                "category": pattern["category"],
                "inverse": pattern["inverse"],
            }

            # print("Added: ", label)

    def get_pattern_category(self, key):
        return self.pattern_labels[key]["category"]
        


class ExtractJourneys(CustomDependencyMatcher):

    def __call__(self, doclike):

        doc = doclike.doc

        df = []

        for clause in self.get_matches(doc):

            for key, value in clause.items():
                if isinstance(value, Token):
                    clause[key] = self.get_span(value).text
            df.append(clause)

        return df
