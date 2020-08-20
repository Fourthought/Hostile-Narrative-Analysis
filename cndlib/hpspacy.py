import spacy
from spacy.tokens import Doc, Span, Token

class HearstPatterns(object):

    name = "hearst pattern matcher"
    
    """ Hearst Patterns is a class object used to detects hypernym relations to hyponyms in a text
    
    input: raw text
    returns: list of dict object with each entry all the hypernym-hyponym pairs of a text
    entry format: ["predicate" : [(hyponym, hypernym), (hyponym, hypernym), ..]]
    
    """
    
    def __init__(self, nlp, extended=False):
        
#     Included in each entry is the original regex pattern now adapted as a spaCy matcher pattern.
#     Many of these patterns are in the same format, next iteration of code should include an
#     automatic pattern generator for patterns.
            
#     These patterns need checking and cleaning up for testing.
            
#     Format for the dict entry of each pattern
#     {
#      "label" : predicate, 
#      "pattern" : spaCy pattern, 
#      "posn" : first/last depending on whether the hypernym appears before its hyponym
#     }
      
        # make the patterns easier to read
        # as lexical understanding develops, consider adding attributes to dstinguish between hypernyms and hyponyms
        
        self.nlp = nlp
        
        hypernym = {"POS" : {"IN": ["NOUN", "PROPN", "PRON"]}}
        hyponym = {"POS" : {"IN": ["NOUN", "PROPN", "PRON"]}}
        punct = {"IS_PUNCT": True, "OP": "?"}
        det = {"ORTH" : "*", "OP" : "*"}
        wildcard = {}

        self.patterns = [

        {"label" : "such_as", "pattern" : [
#                 '(NP_\\w+ (, )?such as (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             hypernym, punct, {"LEMMA": "such"}, {"LEMMA": "as"}, det, hyponym
        ], "posn" : "first"},

        {"label" : "know_as", "pattern" : [
#                 '(NP_\\w+ (, )?know as (NP_\\w+ ?(, )?(and |or )?)+)', # added for this experiment
#                 'first'
             hypernym, punct, {"LEMMA": "know"}, {"LEMMA": "as"}, det, hyponym
        ], "posn" : "first"},

        {"label" : "include", "pattern" : [
#                 '(NP_\\w+ (, )?include (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             hypernym, punct, wildcard, {"LEMMA" : "include"}, det, hyponym
        ], "posn" : "first"},

        {"label" : "especially", "pattern" : [ ## problem - especially is merged as a modifier in to a noun phrase
#                 '(NP_\\w+ (, )?especially (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             hypernym, punct, {"LEMMA" : "especially"}, det, hyponym
        ], "posn" : "first"},

        {"label" : "other", "pattern" : [
#             problem: the noun_chunk, 'others' clashes with this rule to create a zero length chunk when predicate removed
#                 '((NP_\\w+ ?(, )?)+(and |or )?other NP_\\w+)',
#                 'last'
             det, hyponym, punct, {"LEMMA" : {"IN" : ["and", "or"]}}, {"LEMMA" : "other"}, hypernym
#             There were bruises, lacerations, or other injuries were not prevalent."
        ], "posn" : "last"},

        ]

        if extended:
            self.patterns.extend([

            {"label" : "which_may_include", "pattern" : [
#                     '(NP_\\w+ (, )?which may include (NP_\\w+ '
#                     '?(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "which"}, {"LEMMA" : "may"}, {"LEMMA" : "include"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "which_be_similar_to", "pattern" : [
#                     '(NP_\\w+ (, )?which be similar to (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "which"}, {"LEMMA" : "be"}, {"LEMMA" : "similar"}, {"LEMMA" : "to"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "example_of_this_be", "pattern" : [
#                     '(NP_\\w+ (, )?example of this be (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "example"}, {"LEMMA" : "of"}, {"LEMMA" : "this"}, {"LEMMA" : "be"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "type", "pattern" : [
#                     '(NP_\\w+ (, )?type (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "type"}, punct, det, hyponym
            ], "posn" : "first"},

            {"label" : "mainly", "pattern" : [
#                     '(NP_\\w+ (, )?mainly (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "mainly"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "mostly", "pattern" : [
#                     '(NP_\\w+ (, )?mostly (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "mostly"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "notably", "pattern" : [
#                     '(NP_\\w+ (, )?notably (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "notably"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "particularly", "pattern" : [
#                     '(NP_\\w+ (, )?particularly (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "particularly"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "principally", "pattern" : [
#                     '(NP_\\w+ (, )?principally (NP_\\w+ ? (, )?(and |or )?)+)', - fuses in a noun phrase
#                     'first'
                hypernym, punct, {"LEMMA" : "principally"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "in_particular", "pattern" : [
#                     '(NP_\\w+ (, )?in particular (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "in"}, {"LEMMA" : "particular"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "except", "pattern" : [
#                     '(NP_\\w+ (, )?except (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "except"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "other_than", "pattern" : [
#                     '(NP_\\w+ (, )?other than (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "other"}, {"LEMMA" : "than"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "eg", "pattern" : [
#                     '(NP_\\w+ (, )?e.g. (, )?(NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : {"IN" : ["e.g.", "eg"]}}, det, hyponym 
            ], "posn" : "first"},

#                 {"label" : "eg-ie", "pattern" : [ 
# #                     '(NP_\\w+ \\( (e.g.|i.e.) (, )?(NP_\\w+ ? (, )?(and |or )?)+' - need to understand this pattern better
# #                     '(\\. )?\\))',
# #                     'first'
#                     hypernym, punct, {"LEMMA" : {IN : ["e.g.", "i.e.", "eg", "ie"]}}, {"LEMMA" : "than"}, hyponym
#                 ]},

            {"label" : "ie", "pattern" : [
#                     '(NP_\\w+ (, )?i.e. (, )?(NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : {"IN" : ["i.e.", "ie"]}}, det, hyponym 
            ], "posn" : "first"},

            {"label" : "for_example", "pattern" : [
#                     '(NP_\\w+ (, )?for example (, )?'
#                     '(NP_\\w+ ?(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "for"}, {"LEMMA" : "example"}, punct, det, hyponym
            ], "posn" : "first"},

            {"label" : "example_of_be", "pattern" : [
#                     'example of (NP_\\w+ (, )?be (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                {"LEMMA" : "example"}, {"LEMMA" : "of"}, hypernym, punct, {"LEMMA" : "be"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "like", "pattern" : [
#                     '(NP_\\w+ (, )?like (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "like"}, det, hyponym,
            ], "posn" : "first"},

            {"label" : "such_NOUN_as", "pattern" : [
#                     'such (NP_\\w+ (, )?as (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                {"LEMMA" : "such"}, hypernym, punct, {"LEMMA": "as"}, det, hyponym
            ], "posn" : "first"},

                {"label" : "whether", "pattern" : [
#                     '(NP_\\w+ (, )?whether (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "whether"}, det, hyponym
            ], "posn" : "first"},

            {"label" : "compare_to", "pattern" : [
#                     '(NP_\\w+ (, )?compare to (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "compare"}, {"LEMMA" : "to"}, det, hyponym 
            ], "posn" : "first"},

            {"label" : "among_-PRON-", "pattern" : [
#                     '(NP_\\w+ (, )?among -PRON- (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "among"}, {"LEMMA" : "-PRON-"}, det, det, hyponym
            ], "posn" : "first"},

            {"label" : "for_instance", "pattern" : [
#                     '(NP_\\w+ (, )? (NP_\\w+ ? (, )?(and |or )?)+ '
#                     'for instance)',
#                     'first'
                hypernym, punct, det, hyponym, {"LEMMA" : "for"}, {"LEMMA" : "instance"}
            ], "posn" : "first"},

            {"label" : "and-or_any_other", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?any other NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"DEP": "cc"}, {"LEMMA" : "any"}, {"LEMMA" : "other"}, hypernym,
            ], "posn" : "last"},

            {"label" : "some_other", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?some other NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"DEP": "cc", "OP" : "?"}, {"LEMMA" : "some"}, {"LEMMA" : "other"}, hypernym,
            ], "posn" : "last"},

            {"label" : "be_a", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?be a NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "be"}, {"LEMMA" : "a"}, hypernym,
            ], "posn" : "last"},

            {"label" : "like_other", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?like other NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "like"}, {"LEMMA" : "other"}, hypernym,
            ], "posn" : "last"},

             {"label" : "one_of_the", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?one of the NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "one"}, {"LEMMA" : "of"}, {"LEMMA" : "the"}, hypernym,
            ], "posn" : "last"},

            {"label" : "one_of_these", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?one of these NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "one"}, {"LEMMA" : "of"}, {"LEMMA" : "these"}, hypernym,
            ], "posn" : "last"},

            {"label" : "one_of_those", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?one of those NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"DEP": "cc", "OP" : "?"}, {"LEMMA" : "one"}, {"LEMMA" : "of"}, {"LEMMA" : "those"}, hypernym,
            ], "posn" : "last"},

            {"label" : "be_example_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?be example of NP_\\w+)', added optional "an" to spaCy pattern for singular vs. plural
#                     'last'
                det, hyponym, punct, {"LEMMA" : "be"}, {"LEMMA" : "an", "OP" : "?"}, {"LEMMA" : "example"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

            {"label" : "which_be_call", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which be call NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "be"}, {"LEMMA" : "call"}, hypernym
            ], "posn" : "last"},
#               
            {"label" : "which_be_name", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which be name NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "be"}, {"LEMMA" : "name"}, hypernym
            ], "posn" : "last"},

            {"label" : "a_kind_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and|or)? a kind of NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "a"}, {"LEMMA" : "kind"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

#                     '((NP_\\w+ ?(, )?)+(and|or)? kind of NP_\\w+)', - combined with above
#                     'last'

            {"label" : "form_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and|or)? form of NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "a", "OP" : "?"}, {"LEMMA" : "form"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

            {"label" : "which_look_like", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which look like NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "look"}, {"LEMMA" : "like"}, hyponym
            ], "posn" : "last"},

            {"label" : "which_sound_like", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which sound like NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "sound"}, {"LEMMA" : "like"}, hypernym
            ], "posn" : "last"},

            {"label" : "type", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )? NP_\\w+ type)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "type"}, hypernym
            ], "posn" : "last"},

            {"label" : "compare_with", "pattern" : [
#                     '(compare (NP_\\w+ ?(, )?)+(and |or )?with NP_\\w+)',
#                     'last'
                {"LEMMA" : "compare"}, det, hyponym, punct, {"LEMMA" : "with"}, hypernym
            ], "posn" : "last"},

#             {"label" : "as", "pattern" : [
# #                     '((NP_\\w+ ?(, )?)+(and |or )?as NP_\\w+)',
# #                     'last'
#                 hyponym, punct, {"LEMMA" : "as"}, hypernym
#             ], "posn" : "last"},

            {"label" : "sort_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and|or)? sort of NP_\\w+)',
#                     'last'
                det, hyponym, punct, {"LEMMA" : "sort"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

        ]),        

        ## initiate matcher
        from spacy.matcher import Matcher
        self.matcher = Matcher(self.nlp.vocab, validate = True)

        Doc.set_extension("pairs", default = [], force = True) # set up dictionary containing pairs
        Token.set_extension("is_hypernym", default = False, force = True)
        Token.set_extension("has_hyponyms", default = [], force = True)
        Token.set_extension("is_hyponym", default = False, force = True)
        Token.set_extension("has_hypernym", default = "", force = True)
        Token.set_extension("predicate", default = "", force = True)

        self.predicates = []
        self.first = []
        self.last = []

        # add patterns to matcher
        for pattern in self.patterns:
            self.matcher.add(pattern["label"], None, pattern["pattern"])

            # gather list of predicates where the hypernym appears first
            if pattern["posn"] == "first":
                self.first.append(pattern["label"])

            # gather list of predicates where the hypernym appears last
            if pattern["posn"] == "last":
                self.last.append(pattern["label"]) 
    
    def __call__(self, text):
        
        """
        this is the main function of the class object
        
        follows logic of:
        1. checks whether text has been parsed
        2. pre-processing for noun_chunks
        3. generate matches
        4. create list of dict object containing match results
        """
        
        if isinstance(text, spacy.tokens.doc.Doc):
            doc = text
        else:
            doc = self.nlp(text) # initiate doc 
            
        
        ## Pre-processing
        # there are some predicate terms, such as "particularly", "especially" and "some other" which are
        # merged with the noun phrase. Such terms are part of the pattern and become part of the
        # merged noun-chunk, consequently, they are not detected in by the matcher.
        # This pre-processing, therefore, walks through the noun_chunks of a doc object to remove those
        # predicate terms from each noun_chunk and merges the result.
    
        ## Main Body
        #Find matches in doc
        matches = self.matcher(doc)
        
        # If none are found then return None
        if not matches:
            return doc

        for match_id, start, end in matches:
            predicate = self.nlp.vocab.strings[match_id]
            
            # if the predicate is in the list where the hypernym is last, else hypernym is first
            if predicate in self.last: 
                hypernym = doc[end - 1]
                hyponym = doc[start]
            else:
                # an inelegent way to deal with the "such_NOUN_as pattern" since the first token is not the hypernym
                if doc[start].lemma_ == "such":
                    start += 1
                hypernym = doc[start]
                hyponym = doc[end - 1]

            # hypernym recorded as True and list of hyponyms created 
            hypernym._.is_hypernym = True
            hypernym._.predicate = predicate
            hypernym._.has_hyponyms.append(hyponym)
           
            # hyponym recorded as True and its hypernym is recorded
            hyponym._.is_hyponym = True
            hyponym._.has_hypernym = hypernym
            hyponym._.predicate = predicate

            # iterate over conjunct list attached to hyponym
            for token in hyponym.conjuncts:   
                if token != hypernym and token != None:
                    hypernym._.has_hyponyms.append(token)
                    token._.is_hyponym = True
                    token._.has_hypernym = hypernym
                    hyponym._.predicate = predicate

            hypernym_extended = doc[hypernym.left_edge.i : hypernym.i + 1]
            hyponym_extended = doc[hyponym.left_edge.i : hyponym.i + 1]

            doc._.pairs.append((predicate, hypernym_extended, hyponym_extended)) 
            for token in hyponym.conjuncts:   
                if token != hypernym and token != None:
                    doc._.pairs.append((predicate, hypernym_extended,  doc[token.left_edge.i : token.i + 1]))

        return doc