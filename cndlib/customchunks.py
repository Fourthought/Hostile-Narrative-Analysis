from typing import Union, Iterator, Tuple
from spacy.tokens import Doc, Span, Token
from spacy.symbols import NOUN, PROPN, PRON, ADJ, ADV, ADP, VERB


def get_noun_phrase(doclike: Union[Doc, Span]) -> Iterator[Tuple[int, int, int]]:
    
    def is_preposition_subject(word):
        
        if next(word.rights, False) and word.pos in (NOUN, PROPN, PRON) and next(word.rights).pos == ADP:
            return True
        return False
    
    def is_nested_preposition(prep):
        
        # works only for the first ADP in a nested preposition
        
        preposition_object = next(prep.children, False)
        if not preposition_object:
            return False
        return is_preposition_subject(preposition_object)
    
    def get_preposition_head(word):
        
        head = word
        
        # get to the head of a conjunction
        while head.dep_ == "conj" and head.head.i < head.i:
            head = head.head
                    
        # get to the head of a preposition
        while not is_preposition_subject(head) and head.head.i < head.i:
            head = head.head
            
        # get to the head of a nested preposition
        if is_preposition_subject(head.head.head):
            head = head.head.head

        return head
        
    def get_left_edge(word):
        
        if word.left_edge.pos == PRON:
            return word.i
        return word.left_edge.i
    
    def get_right_edge(word):
            
        token = next(word.rights, False)
        if token and token.pos in (ADJ, ADV):
            return token.i
        return word.i 
        
    def is_conjunction_object(word):
        if word.dep_ == "conj":
            return True
        return False
    
    labels = [
        "oprd",
        "nsubj",
        "dobj",
        "nsubjpass",
        "pcomp",
        "pobj",
        "dative",
        "appos",
        "attr",
        "ROOT",
        
        # added
        "dep",    
    ]
    
    doc = doclike.doc  # Ensure works on both Doc and Span.
    
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    prep_dep = doc.vocab.strings.add("prep")
    poss_dep = doc.vocab.strings.add("poss")
    conj = doc.vocab.strings.add("conj")
    np_label = doc.vocab.strings.add("NP")
    
    if not doc.has_annotation("DEP"):
        raise ValueError(Errors.E029)
    
    prev_end = -1
    
    for i, word in enumerate(doclike):

        if word.pos not in (NOUN, PROPN, PRON, ADP):
#             print(f'"{word}" not in NOUN, PROPN, PRON, ADP ({word.i} right edge {prev_end})')
            continue
            
        if word.left_edge.i <= prev_end:
#             print(f'"{word}" {word.i} left edge {word.left_edge.i} < {prev_end}')
            continue
                    
        if is_preposition_subject(word):
#             print(f'"{word}" is preposition_subject ({word.i} right edge {prev_end})')
            continue
            
        if word.dep == prep_dep and is_nested_preposition(word):
#             print(f'"{word}" is a nested preposition ({word.i} right edge {prev_end})')
            continue
    
        # if word.dep == poss_dep:
        #     prev_end == word.i
            
#             print(f'"{word}" is a possessional modifier ({word.i} right edge {prev_end})')

            yield word.i, word.i + 1, np_label
    
        elif word.dep == prep_dep and is_preposition_subject(word.head):
            
            preposition_object = next(word.children)
            preposition_head = get_preposition_head(word.head)
                
            prev_end = get_right_edge(preposition_object)
            left_edge = get_left_edge(preposition_head)
            
#             print(f'"{word}: {Span(word.doc, left_edge, prev_end + 1)}" is a preposition ({word.i} right edge {prev_end})')
            
            yield left_edge, prev_end + 1, np_label
    
        elif word.dep in np_deps:
            
            prev_end = get_right_edge(word)
            left_edge = get_left_edge(word)
            
#             print(f'"{Span(word.doc, left_edge, prev_end + 1)}" is a noun phrase ({word.i} right edge {prev_end})')
            
            yield left_edge, prev_end + 1, np_label
            
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                
                prev_end = get_right_edge(word)
                left_edge = get_left_edge(word)
                
#                 print(f'"{Span(word.doc, left_edge, prev_end + 1)}" is a conjunction with head: {get_preposition_head(word)} ({word.i} right edge {prev_end})')
                
                yield left_edge, prev_end + 1, np_label
    
def chunker(doclike):

    # doc = doclike.doc
    # print(f'{doclike=} : {doc=}')
    for start, end, label in get_noun_phrase(doclike):
        chunk = Span(doclike.doc, start, end, label=label)
        yield chunk