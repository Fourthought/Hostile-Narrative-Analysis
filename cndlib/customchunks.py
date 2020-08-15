from spacy.tokens import Span, Token

cust_stopwords = [
        'able', 'available', 'brief', 'certain',
        'different', 'due', 'enough', 'especially', 'few', 'fifth',
        'former', 'his', 'howbeit', 'immediate', 'important', 'inc',
        'its', 'last', 'latter', 'least', 'less', 'likely', 
        'little', 'mainly', 'many', 'ml', 'more', 'most', 'mostly', 'much', 
        'my', 'necessary', 'new', 'next', 'non', 'notably', 'old', 'other', 
        'our', 'ours', 'own', 'particular', 'particularly', 'principally',
        'past', 'possible', 'present', 'proud', 'recent', 'same', 'several', 
        'significant', 'similar', 'some', 'such', 'sup', 'sure', 'these', 'those'
    ]

def custom_chunk_iterator(doclike):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    
    This is a modification of the spaCy's noun chunker.
    
    Instead of using the <.left_edge.i> property to capture the span, this chunker also captures apositional
    phrases that are rightwards facing to a root noun.
    
    Signifying custom chunks, the Span objects are labeled with "CC"
    
    source code: https://github.com/explosion/spaCy/blob/master/spacy/lang/en/syntax_iterators.py
    """
    
    labels = [
        "nsubj",
        "dobj",
        "nsubjpass",
        "pcomp",
        "pobj",
        "dative",
        "appos",
        "attr",
        "ROOT",
        "conj"
    ]
    
    doc = doclike.doc  # Ensure works on both Doc and Span.

    np_deps = [doc.vocab.strings.add(label) for label in labels]
    ADP = doc.vocab.strings.add("ADP")
    pobj = doc.vocab.strings.add("pobj")
    cc_label = doc.vocab.strings.add("CC")
    
    def ADP_head(word):
        
        """
        function to check whether a word is the head of an adpositional phrase
        if there is a nested adpositional phrase, returns false
        TODO: modify with networkx library
        """
        
        if word.n_rights > 0:
            adp_i = list(word.rights)[0].i
            if doc[adp_i].pos == ADP and doc[adp_i].text not in ["to", "in"] and doc[adp_i].n_rights > 0:
                pobj_i = list(doc[adp_i].children)[0].i
                if doc[pobj_i].dep == pobj and doc[pobj_i].n_rights == 0:
                    return True

                # to replace ["to", "in"] clause, add a new test for when pobj.pos_ == conj, return false
                if doc[pobj_i].dep == pobj and doc[pobj_i].n_rights > 0:
                    if list(doc[pobj_i].rights)[0].pos != ADP:
                        return True
        return False
        
    def get_right_edge(word):
        
        """
        function to get the immediate right edge of a adpositional phrase
        """
        
        adp_i = None
        adp_i = list(word.rights)[0].i
        if doc[adp_i].n_rights > 0:
            pobj_i = list(doc[adp_i].rights)[-1].i
            if doc[pobj_i].pos_ not in ["NOUN", "PROPN", "PRON"]:
                return doc[pobj_i].right_edge.i
            
            return list(doc[adp_i].children)[-1].i
    prev_end = -1
    
    for word in doclike:
        
        if word.pos_ not in ["NOUN", "PROPN", "PRON"]:
            continue
       
        if word.left_edge.i <= prev_end:
            continue
            
        # if the token is an apositional head
        elif ADP_head(word):
            
            right_edge = word.right_edge.i
            
            if word.n_rights > 0:
                right_edge = get_right_edge(word)
                    
            elif word.n_rights > 0 and word.conjuncts:
                right_edge = get_right_edge(word)
                
            prev_end = right_edge 
            yield word.left_edge.i, right_edge + 1, cc_label
            
        # for when the word is not an apositional head    
        elif word.dep in np_deps:
            prev_end = word.i                    
            yield word.left_edge.i, word.i + 1, cc_label

def custom_chunks(doc):
    
    """
    Yields base customised noun-phrase `Span` objects from the custom chunk 
    iterator, if the document has been syntactically parsed. 
    Different to spaCy's inbuilt noun_chunks which uses the <.left_edge.i> property to capture the span, 
    this chunker uses the <.subtree> property.
    
    YIELDS (Span): Base customised chunk `Span` objects
    """
    
    # Accumulate the result before beginning to iterate over it. This
    # prevents the tokenisation from being changed out from under us
    # during the iteration. The tricky thing here is that Span accepts
    # its tokenisation changing, so it's okay once we have the Span
    # objects. See Issue #375

    spans = []    
    
    if doc._.custom_chunk_iterator is not None:
        for start, end, label in doc._.custom_chunk_iterator:
            
            # remove stopword tokens from left of the span
            for index in range(start, end):
                if doc[index].pos_ in ["PROPN", "NOUN", "PRON", "ADJ"]:
                    break
                if doc[index].lower_ in cust_stopwords or doc[index].is_stop:
                    start += 1
                    
            span = Span(doc, start, end, label=label)
            if span.root._.CONCEPT:
                span._.CONCEPT = span.root._.CONCEPT
            else:
                span._.CONCEPT = span._.modifier._.CONCEPT
            
            spans.append(span)
                  
    for span in spans:
        yield span

def merge_custom_chunks(doc):
    """Merge noun chunks into a single token.
    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged noun chunks.
    DOCS: https://spacy.io/api/pipeline-functions#merge_noun_chunks
    """
    if not doc.is_parsed:
        return doc

    with doc.retokenize() as retokenizer:
        for np in doc._.custom_chunks:
            attrs = {"tag": np.root.tag, 
                     "dep": np.root.dep,
                     "_" : {"span_type" : np._.span_type,
                            "CONCEPT" : np._.CONCEPT}}

            retokenizer.merge(np, attrs=attrs)
    return doc