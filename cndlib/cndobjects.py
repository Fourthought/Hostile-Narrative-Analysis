import os
from functools import reduce
from datetime import date, datetime
import visuals


class Orator(object):

    """ 
    This is the object representation of an Orator
    """

    def __init__(self, ref = '', name = '', filepath = ''):

        self.ref = ref

        self.name = name

        self.filepath = filepath

        self.filenames = []
   
        self.texts = []

        for _, _, filenames in os.walk(self.filepath): 
            # iterate through the files
            for file in filenames: 

                if os.path.splitext(file)[1] == ".txt" and (file[:8]).isnumeric(): #check whether file meets speech filename format requirement
                    self.texts.append(Text(surname = self.ref, 
                                            title = file[9:-4], 
                                            datestamp = date(int(file[0:4]), int(file[4:6]), int(file[6:8])), 
                                            filename = os.path.join(self.filepath, file))
                                            )

    def __getitem__(self, indx):
        if type(indx) is int:
            return self.texts[indx]
        if type(indx) is slice:
            return self.texts[indx.start:indx.stop]

    def __repr__(self):

        return reduce(lambda a, b : str(a) + str(b), self.texts, '')

    def __iter__(self):

        """
        returns iterator of orators in the dataset
        """
        return iter(text for text in self.texts)

    def __len__(self):
        
        """
        returns the number of texts associated with the orator
        """
        return len(self.texts)

    def add_text(self):
        
        """
        holding function: will be developed to add a text to the Orator object
        """
        
        pass

    def summary(self):

        index = {
            "Orator" : [text.surname for text in self.texts],
            "Date" : [text.datestamp for text in self.texts],
            "Title" : [text.title for text in self.texts],
            "Word Count" : [len(str(text)) for text in self.texts]
        }

        display(visuals.display_table(index))

class Text(object):
    
    """
    representation of the Text object
    """
    
    def __init__(self, surname = '', title = '', datestamp = '', filepath = '', filename = ''):
        
        self.surname = surname.title()
        
        self.title = title
        
        self.datestamp = datestamp
        
        self.filepath = filepath

        self.filename = filename

        self.reference = f'{self.surname} ({self.datestamp}) {self.title}'

    def __repr__(self):

        """
        load representation of text from disc to save from holding text in memory.

        inputs: filename
        output: generator object of text
        """

        with open(self.filename, 'r') as t:
            return t.read()

# access the speeches directory
class Dataset(object):
    
    """ 
    this function creates a dict of orator objects, with each orator object containing
    associated texts.
    
    format:
    
    {"surname" : Orator Object}
    
    """
    def __init__(self, dir = ''):
    
        self.orators_dict = dict()
        self.dir = dir

        for dirpath, dirnames, _ in os.walk(self.dir): 

            # iterate through the folders in the speeches directory, which relates to each orator
            for orator_dir in dirnames: 
                # iniate orator object and add to orators dict()
                surname = orator_dir.split()[-1].lower()
                self.orators_dict[surname] = Orator(name  = orator_dir, 
                                                    ref = surname,
                                                    filepath = os.path.join(dirpath, orator_dir)
                                                   )
                                
    def __getitem__(self, key):
        return self.orators_dict[key]
    
    def __iter__(self):

        """
        returns iterator of orators in the dataset
        """
        return iter(self.orators_dict[i] for i in self.orators_dict.keys())

    def summary(self):

        index = {
             "ref" : [orator.ref for orator in self.orators_dict.values()]
        }
    
