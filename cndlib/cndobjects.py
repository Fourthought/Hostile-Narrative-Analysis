import os
import sys
from functools import reduce
from datetime import date, datetime
from collections.abc import MutableMapping, MutableSequence
import pandas as pd

#custom modules
import pipeline
import visuals
import cndutils


class Orator(MutableSequence):

    """ 
    Orator() is an object containing only Text() objects.
    
    Structure of Dataset() is a list object using MutableSequence inheritence from collections.abc

    Interrogate using normal list operations.

    Called from within Dataset() object
    
    Additional functions:
    summarise() - display a summary of Text() objects in Orator()
    initialise() - create Text() objects from files within folder path
    
    format:
    
    Orator["orator.ref"][1..n]
    """

    attrs = ["ref", "datestamp", "title", "word count", "file size"]

    def __init__(self, ref = '', name = '', filepath = ''):

        super(Orator, self).__init__()

        self.ref = ref

        self.name = name

        self.filepath = filepath

        self.filetype_text = ".txt"

        self.texts = list()

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

    @property
    def summary(self):

        """
        create a summary array of the Text() objects in Orator()
        """

        df = []
        for text in self.__iter__():
            df.append([str(getattr(text, attr)) for attr in Orator.attrs[:3]])
            df[-1].append(len(text)) # get word count
            df[-1].append(1000) # get text() size
            # df[-1].append(cndutils.get_object_size(text)) # get text() size

        return df

    def __setitem__(self, index, value):

        """ appends Text() object to Orators() and writes the fulltext to disc"""

        if isinstance(value, Text):
            self.texts[index] = value
            self.texts.sort(key = lambda x: x.datestamp)
        else:
            return 'object not of type cndobjects.Text'

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

        if isinstance(value, Text):
            self.texts.insert(index, value)

            with open(os.path.join(self.filepath, "fulltext.txt"), "w") as f:
                f.write(self.__repr__())
        
        else:
            return 'object of not of type Text()'

    def __delitem__(self, index):

        del self.texts[index]

    def __repr__(self):

        """
        return the complete text of all documents
        """
        fulltext = ""
        for text in self.__iter__():
            fulltext += str(text.doc)
        
        return fulltext
        
        #return reduce(lambda a, b : str(a) + str(b), self.texts, '')

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

    def initialise(self):

        for _, _, filenames in os.walk(self.filepath): 
            # iterate through the files
            for file in filenames: 

                if os.path.splitext(file)[1] == self.filetype_text and (file[:8]).isnumeric(): #check whether file meets speech filename format requirement
                    self.append(Text(ref = self.ref, 
                                            title = file[9:-4], 
                                            datestamp = date(int(file[0:4]), int(file[4:6]), int(file[6:8])), 
                                            filename = os.path.join(self.filepath, file))
                                            )

    def summarise(self):

        """
        returns a formatted dataframe which is visualised using display()
        1. create an array of each Text() derived from attrs list
        2. return formatted DataFrame from visuals module
        """

        return visuals.display_df(self.summary, Orator.attrs)

###################################################################################
########## Text
###################################################################################
class Text:
    
    """
    representation of the Text object
    """
    
    def __init__(self, ref = '', title = '', datestamp = '', filepath = '', filename = ''):
        
        self.ref = ref
        
        self.title = title
        
        self.datestamp = datestamp
        
        self.filepath = filepath

        self.filename = filename

        self.reference = f'{self.ref} ({self.datestamp}) {self.title}'

        # representation of parsed Doc object
        print('parsing: ', self.reference)
        with open(self.filename, 'r') as t:
            self.doc = Dataset.CND(t.read())
    
    @property
    def ideologies(self):
        return {self.datestamp : self.doc._.ideologies}

    def __repr__(self):

        """
        load representation of text from disc to save from holding text in memory.

        output: str of filetext
        """

        return (str(self.doc))

    def __len__(self):

        """
        return len() of text document
        """

        return(len(str(self.doc)))

class Dataset(MutableMapping):
    
    """ 
    Dataset() is an object containing only Orator() objects each containing associated Text() objects.
    
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

    attrs = ["ref", "name", "text count", "word count", "file size"]
    
    def __init__(self, nlp = None, dir = None):

        if nlp is not None and isinstance(nlp, pipeline.CND):
            Dataset.CND = nlp
        else:
            print('CND object not passed')
        
        if dir is not None:
            self.dir = dir
        else:
            dir = None

        self.orators_dict = {}

        self.initialise()

    @property
    def summary(self):

        """ 
        create a summary array of all Orators() in the Dataset() object
        """
        
        df = []
        for orator in self.__iter__():
            df.append([str(getattr(orator, attr)) for attr in Dataset.attrs[:2]]) # get ref and name attrs
            df[-1].append(len(orator)) # get text count
            df[-1].append(len(str(orator))) # get word count
            df[-1].append(1000)
            #df[-1].append(cndutils.get_object_size(orator)) # get file size

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

        if isinstance(value, Orator):
            self.orators_dict[key] = value
        else:
            return "not of type Orator()"
                           
    def __iter__(self):

        """
        returns iterator of orators in the dataset if the orator() object contains a text
        """
        return iter(self.orators_dict[i] for i in self.orators_dict.keys() if len(self.orators_dict[i]) > 0)

    def __len__(self):
        return len(self.orators_dict)

    def initialise(self):
        
        for dirpath, dirnames, _ in os.walk(self.dir): 

            # iterate through the folders in the speeches directory, which relates to each orator
            for orator_dir in dirnames: 
                # iniate orator object and add to orators dict()
                ref = orator_dir.split()[-1].lower()
                self.__setitem__(ref,  Orator(name  = orator_dir, 
                                            ref = ref,
                                            filepath = os.path.join(dirpath, orator_dir)
                                                   ))
                                                   
    def summarise(self):

        """
        returns a formatted summary of all Orator() objects within Dataset()
        1. retrieve self.summary property
        2. return formatted DataFrame from visuals module
        """

        return visuals.display_df(self.summary, Dataset.attrs)

    def text_summarise(self):

        """
        returns a formatted summary of all the Text() objects within Dataset()
        1. retrieve self.text_summary property
        2. return formatted DataFrame from visuals module
        """

        return visuals.display_df(self.text_summary, Orator.attrs)

