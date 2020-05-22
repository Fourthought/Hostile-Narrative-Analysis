###
# useful code reference for detecting ingroup, outgroup based on modifier terms
# https://medacy.readthedocs.io/en/latest/_modules/medacy/pipeline_components/units/unit_component.html


class cna_pipe(object):

    import spacy

    def __init__(self):
        
        self.nlp = spacy.load("en_core_web_md")
        
        for component in self.nlp.pipe_names:
            if component not in ['tagger', "parser", "ner"]:
                self.nlp.remove_pipe(component)
        
        merge_ents = self.nlp.create_pipe("merge_entities")
        self.nlp.add_pipe(merge_ents)
        
    def __call__(self, text):
        
        doc = self.nlp(text)
        
        return doc


class hearst_patterns(object):
    
    """ 
    hearst_patterns() is a class object used to detects hypernym relations to hyponyms in a text
    
    input: raw text
    returns: list of dict object with each entry all the hypernym-hyponym pairs of a text
    entry format: ["predicate" : [(hyponym, hypernym), (hyponym, hypernym), ..]]
    
    """
    
    import spacy
    
    def __init__(self, extended=False):
        
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
        hypernym = {"POS" : {"IN": ["NOUN", "PROPN"]}} 
        hyponym = {"POS" : {"IN": ["NOUN", "PROPN"]}}
        punct = {"IS_PUNCT": True, "OP": "?"}

        self.patterns = [

        {"label" : "such_as", "pattern" : [
#                 '(NP_\\w+ (, )?such as (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             hypernym, punct, {"LEMMA": "such"}, {"LEMMA": "as"}, hyponym
        ], "posn" : "first"},

        {"label" : "know_as", "pattern" : [
#                 '(NP_\\w+ (, )?know as (NP_\\w+ ?(, )?(and |or )?)+)', # added for this experiment
#                 'first'
             hypernym, punct, {"LEMMA": "know"}, {"LEMMA": "as"}, hyponym
        ], "posn" : "first"},

        {"label" : "such_NOUN_as", "pattern" : [
#                 '(such NP_\\w+ (, )?as (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             {"LEMMA": "such"}, hypernym, punct, {"LEMMA": "as"}, hyponym
        ], "posn" : "first"},

        {"label" : "include", "pattern" : [
#                 '(NP_\\w+ (, )?include (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             hypernym, punct, {"LEMMA" : "include"}, hyponym
        ], "posn" : "first"},

        {"label" : "especially", "pattern" : [ ## problem - especially is merged as a modifier in to a noun phrase
#                 '(NP_\\w+ (, )?especially (NP_\\w+ ?(, )?(and |or )?)+)',
#                 'first'
             hypernym, punct, {"LEMMA" : "especially"}, hyponym
        ], "posn" : "first"},

        {"label" : "and-or_other", "pattern" : [ ## problem - other is merged as a modifier in to a noun phrase
#                 '((NP_\\w+ ?(, )?)+(and |or )?other NP_\\w+)',
#                 'last'
             hyponym, punct, {"DEP": "cc"}, {"LEMMA" : "other"}, hypernym
        ], "posn" : "last"},

        ]

        if extended:
            self.patterns.extend([

            {"label" : "which_may_include", "pattern" : [
#                     '(NP_\\w+ (, )?which may include (NP_\\w+ '
#                     '?(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "which"}, {"LEMMA" : "may"}, {"LEMMA" : "include"}, hyponym
            ], "posn" : "first"},

            {"label" : "which_be_similar_to", "pattern" : [
#                     '(NP_\\w+ (, )?which be similar to (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "which"}, {"LEMMA" : "be"}, {"LEMMA" : "similar"}, {"LEMMA" : "to"}, hyponym
            ], "posn" : "first"},

            {"label" : "example_of_this_be", "pattern" : [
#                     '(NP_\\w+ (, )?example of this be (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "example"}, {"LEMMA" : "of"}, {"LEMMA" : "this"}, {"LEMMA" : "be"}, hyponym
            ], "posn" : "first"},

            {"label" : ",type", "pattern" : [
#                     '(NP_\\w+ (, )?type (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "type"}, punct, hyponym
            ], "posn" : "first"},

            {"label" : "mainly", "pattern" : [
#                     '(NP_\\w+ (, )?mainly (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "mainly"}, hyponym
            ], "posn" : "first"},

            {"label" : "mostly", "pattern" : [
#                     '(NP_\\w+ (, )?mostly (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "mostly"}, hyponym
            ], "posn" : "first"},

            {"label" : "notably", "pattern" : [
#                     '(NP_\\w+ (, )?notably (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "notably"}, hyponym
            ], "posn" : "first"},

            {"label" : "particularly", "pattern" : [
#                     '(NP_\\w+ (, )?particularly (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "particularly"}, hyponym
            ], "posn" : "first"},

            {"label" : "principally", "pattern" : [
#                     '(NP_\\w+ (, )?principally (NP_\\w+ ? (, )?(and |or )?)+)', - fuses in a noun phrase
#                     'first'
                hypernym, punct, {"LEMMA" : "principally"}, hyponym
            ], "posn" : "first"},

            {"label" : "in_particular", "pattern" : [
#                     '(NP_\\w+ (, )?in particular (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "in"}, {"LEMMA" : "particular"}, hyponym
            ], "posn" : "first"},

            {"label" : "except", "pattern" : [
#                     '(NP_\\w+ (, )?except (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "except"}, hyponym
            ], "posn" : "first"},

            {"label" : "other_than", "pattern" : [
#                     '(NP_\\w+ (, )?other than (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "other"}, {"LEMMA" : "than"}, hyponym
            ], "posn" : "first"},

            {"label" : "eg", "pattern" : [
#                     '(NP_\\w+ (, )?e.g. (, )?(NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : {"IN" : ["e.g.", "eg"]}}, hyponym 
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
                hypernym, punct, {"LEMMA" : {"IN" : ["i.e.", "ie"]}}, hyponym 
            ], "posn" : "first"},

            {"label" : "for_example", "pattern" : [
#                     '(NP_\\w+ (, )?for example (, )?'
#                     '(NP_\\w+ ?(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "for"}, {"LEMMA" : "example"}, punct, hyponym
            ], "posn" : "first"},

            {"label" : "example_of_be", "pattern" : [
#                     'example of (NP_\\w+ (, )?be (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                {"LEMMA" : "example"}, {"LEMMA" : "of"}, hypernym, punct, {"LEMMA" : "be"}, hyponym
            ], "posn" : "first"},

            {"label" : "like", "pattern" : [
#                     '(NP_\\w+ (, )?like (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "like"}, hyponym,
            ], "posn" : "first"},

            # repeat of such_as pattern in primary patterns???
#                     'such (NP_\\w+ (, )?as (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'

                {"label" : "whether", "pattern" : [
#                     '(NP_\\w+ (, )?whether (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "whether"}, hyponym
            ], "posn" : "first"},

            {"label" : "compare_to", "pattern" : [
#                     '(NP_\\w+ (, )?compare to (NP_\\w+ ? (, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "compare"}, {"LEMMA" : "to"}, hyponym 
            ], "posn" : "first"},

            {"label" : "among_-PRON-", "pattern" : [
#                     '(NP_\\w+ (, )?among -PRON- (NP_\\w+ ? '
#                     '(, )?(and |or )?)+)',
#                     'first'
                hypernym, punct, {"LEMMA" : "among"}, {"LEMMA" : "-PRON-"}, hyponym
            ], "posn" : "first"},

            {"label" : "for_instance", "pattern" : [
#                     '(NP_\\w+ (, )? (NP_\\w+ ? (, )?(and |or )?)+ '
#                     'for instance)',
#                     'first'
                hypernym, punct, hyponym, {"LEMMA" : "for"}, {"LEMMA" : "instance"}
            ], "posn" : "first"},

            {"label" : "and-or_any_other", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?any other NP_\\w+)',
#                     'last'
                hyponym, punct, {"DEP": "cc"}, {"LEMMA" : "any"}, {"LEMMA" : "other"}, hypernym,
            ], "posn" : "last"},

            {"label" : "some_other", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?some other NP_\\w+)',
#                     'last'
                hyponym, punct, {"DEP": "cc", "OP" : "?"}, {"LEMMA" : "some"}, {"LEMMA" : "other"}, hypernym,
            ], "posn" : "last"},

            {"label" : "be_a", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?be a NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "be"}, {"LEMMA" : "a"}, hypernym,
            ], "posn" : "last"},

            {"label" : "like_other", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?like other NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "like"}, {"LEMMA" : "other"}, hypernym,
            ], "posn" : "last"},

             {"label" : "one_of_the", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?one of the NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "one"}, {"LEMMA" : "of"}, {"LEMMA" : "the"}, hypernym,
            ], "posn" : "last"},

            {"label" : "one_of_these", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?one of these NP_\\w+)',
#                     'last'
            hyponym, punct, {"LEMMA" : "one"}, {"LEMMA" : "of"}, {"LEMMA" : "these"}, hypernym,
            ], "posn" : "last"},

            {"label" : "one_of_those", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?one of those NP_\\w+)',
#                     'last'
            hyponym, punct, {"DEP": "cc", "OP" : "?"}, {"LEMMA" : "one"}, {"LEMMA" : "of"}, {"LEMMA" : "those"}, hypernym,
            ], "posn" : "last"},

            {"label" : "be_example_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?be example of NP_\\w+)', added optional "an" to spaCy pattern for singular vs. plural
#                     'last'
                hyponym, punct, {"LEMMA" : "be"}, {"LEMMA" : "an", "OP" : "?"}, {"LEMMA" : "example"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

            {"label" : "which_be_call", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which be call NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "be"}, {"LEMMA" : "call"}, hypernym
            ], "posn" : "last"},
#               
            {"label" : "which_be_name", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which be name NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "be"}, {"LEMMA" : "name"}, hypernym
            ], "posn" : "last"},

            {"label" : "a_kind_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and|or)? a kind of NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "a"}, {"LEMMA" : "kind"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

#                     '((NP_\\w+ ?(, )?)+(and|or)? kind of NP_\\w+)', - combined with above
#                     'last'

            {"label" : "form_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and|or)? form of NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "a", "OP" : "?"}, {"LEMMA" : "form"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

            {"label" : "which_look_like", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which look like NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "look"}, {"LEMMA" : "like"}, hyponym
            ], "posn" : "last"},

            {"label" : "which_sound_like", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?which sound like NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "which"}, {"LEMMA" : "sound"}, {"LEMMA" : "like"}, hypernym
            ], "posn" : "last"},

            {"label" : "type", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )? NP_\\w+ type)',
#                     'last'
                hyponym, punct, {"LEMMA" : "type"}, hypernym
            ], "posn" : "last"},

            {"label" : "compare_with", "pattern" : [
#                     '(compare (NP_\\w+ ?(, )?)+(and |or )?with NP_\\w+)',
#                     'last'
                {"LEMMA" : "compare"}, hyponym, punct, {"LEMMA" : "with"}, hypernym
            ], "posn" : "last"},

            {"label" : "as", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and |or )?as NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "as"}, hypernym
            ], "posn" : "last"},

            {"label" : "sort_of", "pattern" : [
#                     '((NP_\\w+ ?(, )?)+(and|or)? sort of NP_\\w+)',
#                     'last'
                hyponym, punct, {"LEMMA" : "sort"}, {"LEMMA" : "of"}, hypernym
            ], "posn" : "last"},

        ]),        

    ## initiate matcher
        from spacy.matcher import Matcher
        self.matcher = Matcher(nlp.vocab, validate = True)

        self.predicates = []
        self.first = []
        self.last = []

        # add patterns to matcher
        for pattern in self.patterns:
            self.matcher.add(pattern["label"], None, pattern["pattern"])

            # gather list of predicate terms for the noun_chunk deconfliction
            self.predicates.append(pattern["label"].split('_'))

            # gather list of predicates where the hypernym appears first
            if pattern["posn"] == "first":
                self.first.append(pattern["label"])

            # gather list of predicates where the hypernym appears last
            if pattern["posn"] == "last":
                self.last.append(pattern["label"])

    def isPredicateMatch(self, chunk, predicates):

        """
        Function to remove predicate phrases from noun_chunks

        input: the chunk to be checked, list of predicate phrases
        returns: the chnunk with predicate phrases removed.

        """

        def match(empty, count, chunk, predicates):#
            # empty: check whether predicates list is empty
            # chunk[count].lemma_ != predicates[0][-count]: checks convergence between chunk and predicate string, removes empty spans
            # chunk[count].lemma_ == predicates[0][count]: check whether chunk term is equal to the predicates term
            
            while not empty and chunk[count].lemma_ != predicates[0][-count] and chunk[count].lemma_ == predicates[0][count]:
                count += 1

            return empty, count
    
        def isMatch(chunk, predicates):

            empty, counter = match(predicates == [], 0, chunk, predicates)
            if empty or counter == len(predicates[0]):
                return chunk[counter:]
            else:
                return isMatch(chunk, predicates[1:])

        return isMatch(chunk, predicates)
    
    
    def find_hyponyms(self, text):
        
        """
        this is the main function of the class object
        
        follows logic of:
        1. checks whether text has been parsed
        2. pre-processing for noun_chunks
        3. generate matches
        4. create list of dict object containing match results
        """
        
        if type(text) is spacy.tokens.doc.Doc:
            doc = text
        else:
            doc = nlp(text) # initiate doc 
            
        
        ## Pre-processing
        # there are some predicate terms, such as "particularly", "especially" and "some other" which are
        # merged with the noun phrase. Such terms are part of the pattern and become part of the
        # merged noun-chunk, consequently, they are not detected in by the matcher.
        # This pre-processing, therefore, walks through the noun_chunks of a doc object to remove those
        # predicate terms from each noun_chunk and merges the result.
        
        with doc.retokenize() as retokenizer:

            for chunk in doc.noun_chunks:

                attrs = {"tag": chunk.root.tag, "dep": chunk.root.dep}

                retokenizer.merge(self.isPredicateMatch(chunk, self.predicates), attrs = attrs)

                
                
        ## Main Body
        #Find matches in doc
        matches = self.matcher(doc)
        
        pairs = [] # set up dictionary containing pairs
        
        # If none are found then return None
        if not matches:
            return pairs

        for match_id, start, end in matches:
            predicate = nlp.vocab.strings[match_id]
            
            if predicate in self.last: # if the predicate is in the list where the hypernym is last
                hypernym = doc[end - 1]
                hyponym = doc[start]
            else:
                hypernym = doc[start] # if the predicate is in the list where the hypernym is first
                hyponym = doc[end - 1]

            # create a list of dictionary objects with the format:
            # {
            # "predicate" : " predicate term based from pattern name,
            # "pairs" : [(hypernym, hyponym)] + [hyponym conjuncts (tokens linked by and | or)]
            # "sent" : sentence in which the pairs originate
            # }
            
            pairs.append(dict({"predicate" : predicate, 
                               "pairs" : [(hypernym, hyponym)] + [(hypernym, token) for token in hyponym.conjuncts if token != hypernym],
                               "sent" : (hyponym.sent.text).strip()}))

        return pairs