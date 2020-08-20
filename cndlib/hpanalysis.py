from tqdm import tqdm
import hpspacy
import hpregex
import pandas as pd

class hp_Analysis(object):
    
    """
    object for testing the hearst pattern detection methods.
    
    inputs:
    - dict() object of hearst pattern detection methods {method name : method function}
    - dataset
    
    function:
    - iterates over the dataset
    - records the result for each method
    
    self.results output is a dataframe in the following structure
       orator | detected method 1 patterns | detected method 2 patterns | failed analysis (method 1) | failed analysis (method 2)
       #1     | result                     | result                     | result                     | result 
       #2     | result                     | result                     | result                     | result
   
    - hyponym_list: dict object of hyponym results for each orator and each method in the 
    {"orator": {"method" : [hyponyms]}}
    """
    
    def __init__(self, methods = None, iterable = None):
        
        
        self.hyponym_list = {orator.name.title() : {key : [] for key in methods.keys()} for orator in iterable}
        self.results = {orator.name.title() : {f'detected {key} patterns' : 0 for key in methods.keys()} for orator in iterable}
        for orator in self.results.keys():
            self.results[orator].update({f'failed analysis ({key})' : 0 for key in methods.keys()})
            self.results[orator].update({"improvement" : 0})


        for orator in iterable:

            if orator.ref == "hitler":
                continue

            self.hyponym_list.update()
            
            for text in tqdm(orator, desc = orator.ref):

                for key, method in methods.items():

                    try:
                        hyps = method(str(text))

                        self.hyponym_list[orator.name.title()][key].extend(hyps)

                        self.results[orator.name.title()][f'detected {key} patterns'] += len(hyps)
                    except:
                        self.results[orator.name.title()][f'failed analysis ({key})'] += 1
                        
        for orator in self.results:
            old = self.results[orator]['detected regex patterns']
            new = self.results[orator]['detected spaCy patterns']
            self.results[orator]['improvement'] = f'{str(round(((new - old) / old) * 100, 0))}%'
        
        self.results = pd.DataFrame(self.results)