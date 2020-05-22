import sys
for path in sys.path:
    print(path)

sys.path.insert(0, r"C:\Users\Steve\OneDrive - University of Southampton\CNDPipeline")

#del(sys.path)[0]


# from cndlib.pipeline import hearst_patterns
# from cndlib import entities
# import spacy



# print('preparing pipeline')
# nlp = spacy.load("en_core_web_md")

# for component in nlp.pipe_names:
#     if component not in ['tagger', "parser", "ner"]:
#         self.nlp.remove_pipe(component)

# merge_ents = nlp.create_pipe("merge_entities")
# nlp.add_pipe(merge_ents)

# print('generating database')

# dirpath  = r"C:\Users\Steve\OneDrive - University of Southampton\CNDPipeline\speeches"

# h = hearst_patterns(extended = True)
# orators = entities.Dataset(dirpath)

# for orator in orators:
#     print(f'object {orator.ref} called {orator.name} has {len(orator)} speeches')