import pandas as pd
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span, Token
from spacy.symbols import NOUN, PROPN, PRON, ADJ, ADV, ADP, VERB, AUX

def get_span(token):
    
    def is_negated_verb(word, neighbour):
        
        verb_labels = [VERB, AUX]
        neg_deps = ["neg"]

        if word.pos in verb_labels and neighbour.dep_ in neg_deps:
            return True
        return False
    
    def is_noun_or_adjective(word):
        
        pos_labels = [NOUN, PROPN, PRON, ADJ, ADV]

        if word.pos in pos_labels:
            return True
        return False

    def get_left_edge(word):
        
        if word.i > 0 and is_negated_verb(word, word.nbor(-1)):
            return word.nbor(-1).i
        
        # print(word.left_edge, ':', word, '=>', word.doc[word.left_edge.i : word.i + 1])
        if not is_noun_or_adjective(word):
            return word.i
            
        # if word.left_edge.pos == PRON:
        #     return word.i

        return word.left_edge.i

    def get_right_edge(word):
        
        def is_not_last_token_in_doc(word):
            return word.i + 1 < len(word.doc)
        
        def is_adverbial_clause_modifier(word):
            dep_list = ['advcl']
            return word.dep_ in dep_list
        
        def is_word_an_adjective_or_adverb(word):
            return next_word.pos in (ADJ, ADV)
        
        def is_word_a_preposition_head(word):
            return next_word.pos == ADP
        
        if is_adverbial_clause_modifier(word):
            return list(word.subtree)[-1].i
            
        next_word = None
              
        if is_not_last_token_in_doc(word):
            next_word = word.nbor()
            
        if next_word and is_negated_verb(word, next_word):
            return next_word.i
        
        if not is_noun_or_adjective(word):
            return word.i
        
        if next_word and is_word_an_adjective_or_adverb(word):
            return next_word.i
        
        if next_word and is_word_a_preposition_head(word):
            return get_prepositional_object(word)
        
        return word.right_edge.i
    
    def get_prepositional_object(word):
            
        return list(word.subtree)[-1].i

        # while True:
        #     token = next(word.rights, False)
        #     if token and token.head.i == word.i:
        #         return token.i
    

    
    return Span(token.doc, get_left_edge(token), get_right_edge(token) + 1)


class ClauseList(list):
    
    def get_repr(self):
        clauses = []
        for clause in self:
            clauses.append({key: str(value) for key, value in clause.items()})
        return clauses

class CustomDependencyMatcher:

    def __init__(self, matcher, patterns):
        
        self.matcher = matcher
        self.get_span = get_span
        
        self.pattern_labels = {}

        if patterns:
            self.add_patterns(patterns)
            
    def __call__(self, doclike):

        doc = doclike.doc

        clauses = ClauseList([match for match in self.get_matches(doc) if match["CATEGORY"].upper() == "BASE"])
        
        for match in clauses:

            for match2 in self.get_matches(doc):
                if match["PREDICATE"] == match2["PREDICATE"] and match["RULE"] != match2["RULE"]:
                    match.update(match2)
                    
        return clauses
    
    def get_matches(self, doclike):

        doc = doclike.doc

        matches = []

        for match in self.matcher(doc):

            # get the pattern name (match_id) and list of matched tokens (token_ids)
            match_id, token_ids = match
            match_id = doc.vocab.strings[match_id]
            pattern = self.matcher.get(match_id)[1][0]

            clause = {'RULE': match_id}
            if self.pattern_labels:
                clause["CATEGORY"] = self.get_pattern_category(match_id)

            ID = None
            
            for i in range(len(token_ids)):

                RIGHT_ID = pattern[i]["RIGHT_ID"]
                span = doc[token_ids[i]]
                
                if isinstance(span, Token):
                    span = self.get_span(span)

                clause[RIGHT_ID.upper()] = span

            yield clause

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

            print("Added: ", label)

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
