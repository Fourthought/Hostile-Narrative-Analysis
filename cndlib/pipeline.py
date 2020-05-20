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