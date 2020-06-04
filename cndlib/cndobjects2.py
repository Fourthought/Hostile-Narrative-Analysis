
import os

class Orator(object):

    """ 
    This is the Orator object which refers to the person giving the speech
    """

    def __init__(self, ref = '', name = '', filepath = ''):

        self.ref = ref

        self.name = name

        self.filepath = filepath

        self.filenames = []

        self.texts = []
        
        self.fulltext = (text for text in self.texts)

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
    
    def __add_text__(self):
        
        """
        holding function: will be developed to add a text to the Orator object
        """
        
        pass

    def __getitem__(self, indx):
        return(self.texts[indx])

    
class Text(object):
    
    """
    this object will become the Text object
    """
    
    def __init__(self, orator = '', title = '', date = '', filepath = '', text = ''):
        
        self.orator = orator
        
        self.title = title
        
        self.date = date
        
        self.filepath = filepath
        
        self.text = text

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

                # get the filenames in each orators folder
                for _, _, filenames in os.walk(self.orators_dict[surname].filepath): 

                    # iterate through the files
                    for file in filenames: 

                        with open(os.path.join(dirpath, orator_dir, file), 'r') as text:

                            if os.path.splitext(file)[1] == ".txt" and (file[:8]).isnumeric(): #check whether file meets speech filename format requirement
                                self.orators_dict[surname].texts.append(Text(
                                    orator = surname,
                                    title = file[8:],
                                    date = file[:8],
                                    text = text.read()
                                ))
                                
    def __getitem__(self, indx):
        return self.orators_dict[indx]
    
    def __iter__(self):

        """
        returns iterator of orators in the dataset
        """
        return iter(self.orators_dict[i] for i in self.orators_dict.keys())
    
