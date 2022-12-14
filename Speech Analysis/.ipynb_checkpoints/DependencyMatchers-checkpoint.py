import pandas as pd
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span, Token


class CustomDependencyMatcher:

    def __init__(self, nlp, patterns):
        self.matcher = DependencyMatcher(nlp.vocab, validate=True)
        self.pattern_labels = {}

        if patterns:
            self.add_patterns(patterns)

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

            for i in range(len(token_ids)):

                RIGHT_ID = pattern[i]["RIGHT_ID"]
                token = doc[token_ids[i]]

                clause[RIGHT_ID.upper()] = token

            yield clause
            
    def __call__(self, doclike):
        
        def is_clause_in_clauses(clause, clauses):
            match_key = "PREDICATE"
            for i, item in enumerate(clauses):
                if item[match_key].root.i == clause[match_key].root.i:
                    return i
            return None
        
        def is_item_a_span_object(item):
            return isinstance(item, Span)
            
        def is_key_in_clause_dict(key, clause):
            return clause.get(key, False)
        
        def does_the_clause_dict_contain_the_same_key_but_with_a_new_value(key, value, clause):
            return is_key_in_clause_dict(key, clause) and clause[key] != value
            
        doc = doclike.doc

        clauses = []

        for clause in self.get_matches(doc):
            
            clause = self.get_clause_spans(clause)
            
            clause_index = is_clause_in_clauses(clause, clauses)
            
            if clause_index is not None:
                clause_to_update = clauses[clause_index]
                
                additional_elements = {}
                
                for key, value in clause.items():
                    if not is_item_a_span_object(value):
                        continue
                    
                    if not is_key_in_clause_dict(key, clause_to_update):
                        additional_elements[key] = value
                    
                    if does_the_clause_dict_contain_the_same_key_but_with_a_new_value(key, value, clause_to_update):
                        key_list = [k for k in clause_to_update.keys() if key in k and len(k) == len(key) + 1]
                        additional_elements[key + str(len(key_list) + 1)] = value
                
                clause_to_update.update(additional_elements)
                # indicies = {(key): (span.root.i if isinstance(span, Span) else '') for key, span in clause_to_update.items()}
                # clauses.append(indicies)
            else:
                clauses.append(clause)

        return clauses

    def get_span(self, token):
        return Span(token.doc, token._.get_left_edge, token._.get_right_edge + 1)
    
    def get_clause_spans(self, clause):
        for key, value in clause.items():
            if isinstance(value, Token):
                clause[key] = self.get_span(value)
        return clause
        
        


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
