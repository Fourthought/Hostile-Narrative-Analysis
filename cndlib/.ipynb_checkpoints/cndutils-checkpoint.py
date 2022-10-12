import sys
import os
import json
import jsonlines
import pickle
from IPython.display import clear_output
from hurry.filesize import size

from spacy import displacy
from cndlib.visuals import sent_frame

class doubleQuoteDict(dict):
    
    """ 
    function to create double quote entries for json objects
    input: dict object
    output: dict object with double quotes around keys and values
    """
    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self)

def get_object_size(data):

    """
    # function to get size of object: 
    # 1. serialises the object using pickle
    # 2. gets size of pickle serialisation
    # 3. returns human readable format using size from hurry.filesize
    """
    return sys.getsizeof(pickle.dumps(data))

def dump_jsonl(data, output_path, append=False):
    """
    Write list of objects to a JSON lines file.
    """
    mode = 'a+' if append else 'w'
    with open(output_path, mode, encoding='utf-8') as f:
        for line in data:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + '\n')
    print('Wrote {} records to {}'.format(len(data), output_path))

def load_jsonl(input_path) -> list:
    """
    Read list of objects from a JSON lines file.
    """
    data = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.rstrip('\n|\r')))
    print('Loaded {} records from {}'.format(len(data), input_path))
    return data

def dict_to_jsonl(path, file):

    """
    convert json file containing a dict object to jsonl file

    files are converted in place

    inputs:
    - path of input and output directory
    - json filename

    output:
    - converted jsonl file in directory
    """

    json_file_type = ".json"
    jsonl_file_type = ".jsonl"
    
    if os.path.splitext(file)[1] == json_file_type:

        temp_list = []

        with open(os.path.join(path, file)) as json_file:
            data = json.load(json_file)

        if isinstance(data, dict):
            
            print(f'writing to path: {path}')

            for key, value in data.items():
                temp = dict()
                temp[key] = value
                temp_list.append(temp)
                
            file_jsonl = "".join((os.path.splitext(file)[0], jsonl_file_type))

            with jsonlines.open(os.path.join(path, file_jsonl), 'w') as writer:
                writer.write_all(temp_list)
                
            print(f'from {file}, wrote {len(data)} records to {file_jsonl}')
            print()
                
        else:
            return "file does not contain dict object"
    else:
        return "not a json file"

class sent_select:
    
    """
    function to iterate through an input dict and select values for an output list in jsonl format
    input:
    - input_dict = {"int" : "str"}
    - output_list = [{"int" : str} ... {"n" : "str"}]
    """

    def __init__(self, path = None, file = None):

        self.output_list = []

        self.test = False

        ##########
        # set up jsonl files
        ##########
        
        self.jsonl_file_type = ".jsonl"
        self.file_jsonl = None
        self.jsonl_filepath = None
        self.path = path
        self.file = file
        
        # if a path and filename have been passed
        exists = False
        if self.path is not None and isinstance(self.file, str):

            #create filename and filepath
            self.file_jsonl = ''.join((self.file, self.jsonl_file_type))
            self.jsonl_filepath = os.path.join(self.path, self.file_jsonl)

            # if the filename already exists in the path then load it into output_list
            if self.file_jsonl in [f for f in os.listdir(self.path)]:
                print("file already exists")
                exists = True
                
                with jsonlines.open(self.jsonl_filepath) as f:
                    self.output_list = list(f.iter())
            
        ##########
        # set up index
        ##########
        
        self.filepath = r"C:\Users\Steve\OneDrive - University of Southampton\CNDPipeline\dataset"
        self.index = 0
        self.index_filepath = os.path.join(self.filepath, "index.json")
        try:
            # if the index and filename are pre-existing then load
            # else the file name didn't exist but the index did 
            # then reset index (index referring to old iterations)
            with open(self.index_filepath, 'r') as fp:
                if exists:
                    self.index = json.load(fp)
                else:
                    self.index = 0
        except:
            self.index = 0

    
    def __call__(self, nlp, input_dict, parse = False):
                 
        ##########
        # main body
        ##########    
        # iterate over input_dict until completion
        
        while self.index < len(input_dict):

            # record progress through dictionary object
            with open(self.index_filepath, "wb") as f:
                    f.write(json.dumps(self.index).encode("utf-8"))

            #####
            # if a filename was passed then write to file
            #####      

            if self.jsonl_filepath is not None:
                with jsonlines.open(self.jsonl_filepath, 'w') as writer:
                    writer.write_all(self.output_list)

            # test for whether the latest entries in output_list and input_dict are equal
            if len(self.output_list) > 0 and list(self.output_list[-1].values())[0] == input_dict[self.index - 1]:
                self.test = True
            else:
                self.test = False

            ##########
            # display data
            ##########
            
            # clear screen
            clear_output(wait=True)

            # show progress through input_dict
            print(f'{self.index} / {len(input_dict)}')

            # get text
            text = input_dict[self.index]

            # parse text
            doc = nlp(text)

            # if the option to show the dependency parse is passed display it
            if parse == True:
                displacy.render(doc, style="dep")

            # display the sentence frame in compact form
            display(sent_frame(doc))

            ########### 
            # get choice
            ##########
            
            choice = input("add to test_sents (y), delete previous (d), quit (q), back (b)").lower()

            # if the choice is y then add sentence text to output_list and continue iteration
            if choice == "y":

                self.output_list.append({len(self.output_list) : text})

                self.index += 1

            # if the choice is d and the last entries for input_dict and output_list are matching
            # then delete the last item from output_list go back by one step, otherwise ignore
            elif choice == "d":
                if self.test:
                    print(f'removing: {self.output_list.pop()}')
                    self.index -= 1
                    input()
                else:
                    continue

            # if the choice is b and the last entries for input_dict and output_list are not matching
            # then go back until they are matching, whereup delete is required
            elif choice == "b":
                if len(self.output_list) > 0 and not self.test:
                    self.index -= 1
                else:
                    continue

            # if the choice is q then quit
            elif choice == "q":
                break

            # if choice is none of the above then continue iteration
            else:
                self.index += 1

        if self.file_jsonl is not None:
            print(f'written {len(self.output_list)} entries to file: {self.file_jsonl}')
            print(self.path)
            
        if self.index == len(input_dict):
            os.remove(self.index_filepath)
        print('complete')
        return self.output_list

from IPython.display import display_html
def display_side_by_side(*args):
    html_str=''
    for df in args:
        html_str+=df.to_html()
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)