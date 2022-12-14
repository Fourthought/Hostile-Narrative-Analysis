import pandas as pd
from spacy.matcher import DependencyMatcher
from spacy.tokens import Span, Token


class CustomDependencyMatcher:

    def __init__(self, matcher, patterns):
        self.matcher = matcher
        self.pattern_labels = {}

        if patterns:
            self.add_patterns(patterns)
            
    def __call__(self, doclike):

        doc = doclike.doc

        df = []

        for clause in self.get_matches(doc):

            for key, value in clause.items():
                if isinstance(value, Token):
                    clause[key] = self.get_span(value).text
            df.append(clause)

        return df

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

    def get_span(self, token):
        return Span(token.doc, token._.get_left_edge(), token._.get_right_edge() + 1)


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
