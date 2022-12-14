import os
import sys
import pickle
from functools import reduce
from datetime import date, datetime
from collections.abc import MutableMapping, MutableSequence
import pandas as pd

#custom modules
from cndlib import pipeline
from cndlib import visuals
from cndlib import cndutils

class OratorMaster(MutableSequence):

    """ 
    OratorMaster() is an master class for Orator objects.
    
    Structure of OratorMaster() is a list object using MutableSequence inheritence from collections.abc

    Interrogate using normal list operations.

    Called from within DatasetMaster() object
    
    Additional functions:
    summarise() - display a summary of Text() objects in Orator()
    initialise() - create Text() objects from files within folder path
    
    format:
    
    Orator["orator.ref"][1..n]
    """

    #attrs = ["ref", "datestamp", "title", "word count", "file size"]
    attrs = ["ref", "datestamp", "title", "word count"]

    def __init__(self, ref = '', name = ''):

        self.ref = ref

        self.name = name

        self.texts = list()

    @property
    def summary(self):

        """
        create a summary array of the Text() objects in Orator()
        """

        df = []
        for text in self.__iter__():
            if isinstance(text, Text):
                df.append([str(getattr(text, attr)) for attr in OratorMaster.attrs[:3]])
                df[-1].append(len(text)) # get word count
                # df[-1].append(cndutils.get_object_size(text)) # get text() size
            
            else:
                df.append([str(getattr(text, attr)) for attr in OratorMaster.attrs[:3]])

        return df

    def __repr__(self):
        return f'{self.ref} containing {len(self.texts)} objects'
    
    def __setitem__(self, index, value):

        """ appends TextMaster() object to OratorMaster() """

        self.texts[index] = value

    def __getitem__(self, index):

        """
        single index returns single text associated with orator
        slice index returns slice of texts associated with orator
        """

        if type(index) is int:
            return self.texts[index]
        if type(index) is slice:
            return self.texts[index.start:index.stop]
        else:
            return 'incorrect index value'

    def insert(self, index, value):
        
        self.texts.insert(index, value)

    def __delitem__(self, index):

        del self.texts[index]

    def __iter__(self):

        """
        returns iterator of orators in the dataset
        """
        return iter(self.texts)

    def __len__(self):
        
        """
        returns the number of texts associated with the orator
        """
        return len(self.texts)

    def summarise(self):

            """
            returns a formatted dataframe which is visualised using display()
            1. create an array of each Text() derived from attrs list
            2. return formatted DataFrame from visuals module
            """

            return visuals.display_df(self.summary, OratorMaster.attrs[:len(self.summary[0])])

class Orator(OratorMaster):

    """ 
    Orator() is an object containing only Text() objects.

    Inherits from OratorMaster() class
    
    Structure of Orator() is a list object using MutableSequence inheritence from collections.abc

    Interrogate using normal list operations.

    Called from within Dataset() object
    
    Additional functions:
    summarise() - display a summary of Text() objects in Orator()
    initialise() - create Text() objects from files within folder path
    
    format:
    
    Orator["orator.ref"][1..n]
    """

    #attrs = ["ref", "datestamp", "title", "word count", "file size"]
    attrs = ["ref", "datestamp", "title", "word count"]

    def __init__(self, ref = '', name = '', filepath = ''):

        super().__init__(ref, name)
        
        self.filepath = filepath

        self.initialise()

    @property
    def ideologies(self):
        
        """
        getter to create a dict of ideology properties for each Text()
        iterates through each Text() object and append ideologies dicts
        returns a dict object:
        - key : datestamp of the Text()
        - value : Series of ideology count for the Text()
        """
        
        table = dict()

        for document in self.__iter__():
            table.update(document.ideologies)

        return table

    def __setitem__(self, index, value):

        """ appends Text() object to Orators() and writes the fulltext to disc"""

        if isinstance(value, Text):
            self.texts[index] = value
            self.texts.sort(key = lambda x: x.datestamp)
        else:
            return 'object not of type cndobjects.Text'

    def insert(self, index, value):

        if isinstance(value, Text):
            self.texts.insert(index, value)

            with open(os.path.join(self.filepath, "fulltext.txt"), "w") as f:
                f.write(self.__repr__())
        
        else:
            return 'object of not of type Text()'

    def __repr__(self):

        """
        return the complete text of all documents
        """
        fulltext = ""
        for text in self.__iter__():
            fulltext += str(text.doc)
        
        return fulltext
        
        #return reduce(lambda a, b : str(a) + str(b), self.texts, '')

    def initialise(self):

        for _, _, filenames in os.walk(self.filepath): 
            # iterate through the files
            
            if len(filenames) > 0: 
                for file in filenames: 

                    if os.path.splitext(file)[1] == Text.filetype_text and (file[:8]).isnumeric(): #check whether file meets speech filename format requirement
                        self.append(Text(ref = self.ref, 
                                                oratorname = self.name,
                                                title = file[9:-4], 
                                                datestamp = date(int(file[0:4]), int(file[4:6]), int(file[6:8])), 
                                                filename = os.path.join(self.filepath, file))
                                                )


###################################################################################
########## Text
###################################################################################

class TextMaster(object):
    
    """
    Parent class for text objects
    """

    def __init__(self, ref = '', title = '', datestamp = ''):
        
        self.ref = ref
        self.title = title
        self.datestamp = datestamp

    @property
    def reference(self):
        return f'{self.ref} ({self.datestamp}) {self.title}'

    def __repr__(self):
        return self.reference

class Text(TextMaster):
    
    """
    representation of the Text object

    inherits from TextMaster
    """
    filetype_text = ".txt"

    def __init__(self, ref = '', oratorname = '', title = '', datestamp = '', filepath = '', filename = '',):

        super().__init__(ref, title, datestamp)

        self.oratorname = oratorname
        
        self.filepath = filepath
        
        self.filename = filename
        
        # representation of parsed Doc object
        print('parsing: ', self.reference)
        with open(self.filename, 'r') as t:
            self.doc = Dataset.CND(t.read())
    
    @property
    def ideologies(self):
        return {self.datestamp : self.doc._.ideologies}

    def __repr__(self):

        """
        output: str of filetext from spaCy doc object
        """

        return (str(self.doc))

    def __len__(self):

        """
        return len() of text document
        """

        return(len(str(self.doc)))

###################################################################################
########## Dataset
###################################################################################

class DatasetMaster(MutableMapping):
    
    """ 
    DatasetMaster() is an is the master object for datasets to inherit from.
    
    Structure of DatasetMaster() is a dict object using MutableMapping inheritence from collections.abc

    Interrogate using normal dict operations.

    Additional functions:
    summarise() - display a summary of Orator() objects in Dataset()
    
    Interrogation format:
    
    Dataset["Orator().ref"]
    
    """

    # attrs = ["ref", "name", "text count", "word count", "file size"]
    attrs = ["ref", "name", "text count", "word count"]
    
    def __init__(self):

        self.orators_dict = {}

    @property
    def texts(self):

        """
        create an iterable for all the texts in the dataset
        """

        matrix = [[text for text in value.texts] for value in self.orators_dict.values()]
        
        return iter([val for sublist in matrix for val in sublist])

    @property
    def summary(self):

        """ 
        create a summary array of all Orators() in the Dataset() object
        """
        
        df = []
        for orator in self.__iter__():
            if isinstance(orator, Orator):
                df.append([str(getattr(orator, attr)) for attr in DatasetMaster.attrs[:2]]) # get ref and name attrs
                df[-1].append(len(orator)) # get text count
                df[-1].append(len(str(orator))) # get word count
                #df[-1].append(cndutils.get_object_size(orator)) # get file size
            
            else:
                df.append([str(getattr(orator, attr)) for attr in DatasetMaster.attrs[:2]])
                df[-1].append(len(orator))

        return df

    @property
    def text_summary(self):

        """ 
        create a summary of all Text() objects for each Orator() in the Dataset() object
        """

        df = []
        for orator in self.__iter__():
            df += orator.summary

        return df

    def __getitem__(self, key):

        """
        using the Orator().ref as a key, returns Orator() object
        """
        if key in self.orators_dict.keys():
            return self.orators_dict[key]
            
    def __delitem__(self, key):

        """
        using the Orator().ref as a key, deletes Orator() object
        """
        
        if key in self.orators_dict.keys():
            del self.orators_dict[key]

    def __setitem__(self, key, value):

        """ 
        object value is fixed to type Orator()
        """
        self.orators_dict[key] = value
                           
    def __iter__(self):

        """
        returns iterator of orators in the dataset if the orator() object contains a text
        """
        return iter(self.orators_dict)

    def __len__(self):
        return len(self.orators_dict)
                                                   
    def summarise(self):

        """
        returns a formatted summary of all Orator() objects within Dataset()
        1. retrieve self.summary property
        2. return formatted DataFrame from visuals module
        """

        return visuals.display_df(self.summary, DatasetMaster.attrs[:len(self.summary[0])])

    def text_summarise(self):

        """
        returns a formatted summary of all the Text() objects within Dataset()
        1. retrieve self.text_summary property
        2. return formatted DataFrame from visuals module
        """

        return visuals.display_df(self.text_summary, OratorMaster.attrs[:len(self.text_summary[0])])


class Dataset(DatasetMaster):
    
    """ 
    Dataset() is an object containing only Orator() objects each containing associated Text() objects.
    
    Inherits from DatasetMaster
    
    Structure of Dataset() is a dict object using MutableMapping inheritence from collections.abc

    Interrogate using normal dict operations.

    Called using directory path of folders containing texts with folder names referring to orator names
    
    Additional functions:
    summarise() - display a summary of Orator() objects in Dataset()
    initialise() - create orator objects from folder structure referred to by directory input
    
    Interrogation format:
    
    Dataset["Orator().ref"]
    
    """

    CND = None
    
    def __init__(self, nlp = None, dir = None):
        super().__init__()

        if nlp is not None and isinstance(nlp, pipeline.CND):
            Dataset.CND = nlp
        else:
            print('CND object not passed')
        
        if dir is not None:
            self.dir = dir
        else:
            dir = None

        self.initialise()

    def __setitem__(self, key, value):

        """ 
        object value is fixed to type Orator()
        """

        if isinstance(value, Orator):
            self.orators_dict[key] = value
        else:
            return "not of type Orator()"

    def __iter__(self):

        """
        returns iterator of orators in the dataset if the orator() object contains a text
        """
        return iter(self.orators_dict[i] for i in self.orators_dict.keys() if len(self.orators_dict[i]) > 0)

    def initialise(self):
        
        for dirpath, dirnames, _ in os.walk(self.dir): 

            # iterate through the folders in the speeches directory, which relates to each orator
            for orator_dir in dirnames:

                # if the directory contains relevant files then instantiate the object
                if [filename for filename in os.listdir(os.path.join(dirpath, orator_dir)) if os.path.splitext(filename)[1] == ".txt" and (filename[:8]).isnumeric()]:

                    # iniate orator object and add to orators dict()
                    ref = orator_dir.split()[-1].lower()
                    self.__setitem__(ref,  Orator(name = orator_dir, 
                                                ref = ref,
                                                filepath = os.path.join(dirpath, orator_dir)
                                                    ))

class SentimentData(DatasetMaster):
    
    apis = None
    
    def __init__(self, apis = [], filepath = "", filename = ""):
        super().__init__()
        
        self.__class__.apis = apis
        self.filepath = filepath
        self.filename = filename
        
    @property
    def file(self):
        return os.path.join(self.filepath, self.filename)
        
    @property
    def summarise(self):
    
        for orator in self.values():
            for document in orator:
                line = dict()
                line["ref"] = document["ref"]
                line["datestamp"] = document["datestamp"]
                line["title"] = document["title"]
                line["word count"] = document["wordcount"]
                line["sentence count"] = len(document["sentences"])
                
                for api in self.__class__.apis:
                    line[api] = document["sentiment_scores"][api]

                yield line
                
    @property
    def df(self):
        return pd.DataFrame(self.summarise)
    
    @property
    def reference(self, orator, text):
        return f'{orator} ({self.orators_dict[orator][text]["datestamp"]}) {self.orators_dict[orator][text]["title"]}'  
    
    @property
    def minmax(self):
        
        minmax = dict()

        for ref, orator in self.orators_dict.items():

            documents = list()

            for text in orator:

                document = dict()

                # list of sentences with a score of +1
                # list of sentence indicies with a score of -1
                document["most_pos_sents"] = dict()
                document["most_pos_sents"]["explain"] = "List of sentences an API has scored at +1"
                document["most_pos_sents"]["sentences"] = list()
                document["most_neg_sents"] = dict()
                document["most_neg_sents"]["explain"] = "List of sentences an API has scored at -1"
                document["most_neg_sents"]["sentences"] = list()

                # sentence indicies with highest score other than +1
                # sentence indicies with lowest score other than -1
                document["pos_sents"] = dict()
                document["pos_sents"]["explain"] = "Most positive sentence less than +1 for each API"
                document["pos_sents"]["sentences"] = dict()
                document["neg_sents"] = dict()
                document["neg_sents"]["explain"] = "Most negative sentence greater than -1 for each API"
                document["neg_sents"]["sentences"] = dict()
                
                # reference scores for determining max and min
                maximum = {api : 0 for api in self.__class__.apis}
                minimum = {api : 0 for api in self.__class__.apis}

                for sent in text["sentences"]:

                    # get the sentence text and scores
                    sent_scores = dict()
                    sent_scores["text"] = sent["text"]
                    sent_scores.update(sent["scores"])
                    sent_scores.update(sent["emotion"])

                    # iterate through each api score for the sentence
                    for api in self.__class__.apis:

                        # get scores equal to +1 or -1
                        if sent["scores"][api] == 1:
                            document["most_pos_sents"]["sentences"].append(sent_scores)

                        if sent["scores"][api] == -1:
                            document["most_neg_sents"]["sentences"].append(sent_scores)

                        # get min and max scores less than +1 or -1
                        if sent["scores"][api] < 1 and sent["scores"][api] > maximum[api]:
                            maximum[api] = sent["scores"][api]
                            document["pos_sents"]["sentences"][api] = sent_scores

                        if sent["scores"][api] > -1 and sent["scores"][api] < minimum[api]:
                            minimum[api] = sent["scores"][api]
                            document["neg_sents"]["sentences"][api] = sent_scores

                documents.append(document)

            minmax[ref] = documents
            
        return minmax

    def __len__(self):
        return sum(self.df["sentence count"])
    
    def toDisk(self):
        print("writing:", self.filename, "to:")
        print(self.filepath)
        pickle.dump(self.orators_dict, open(self.file, 'wb'))
            
    def fromDisk(self):
        print("loading:", self.filename, "from:")
        print(self.filepath)
        self.orators_dict = pickle.load(open(self.file, 'rb'))