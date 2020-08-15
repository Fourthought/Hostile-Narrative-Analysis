from collections import OrderedDict
import pandas as pd
from hurry.filesize import size
import humanize
from spacy.tokens import Token

def display_df(df, columns):

    """ function to standardise a dataframe object for display"""

    if isinstance(df, list):
        df = pd.DataFrame(df, columns = columns)
    
    if isinstance(df, pd.DataFrame):
        df = df
    
    # add a new row with totals for numerical columns
    totals = [None if value.dtype != "int64" else sum(value) for _ , value in df.iteritems()]
    totals[0] = "Totals"
    df.loc[df.index.max()+1] = totals

    index = [i for i in range(len(df.index))]
    
    for key, value in df.iteritems():
         # format numerical values with more human readable commas for columns containing numerical values
        if value.dtype == "int64" and "size" not in key.lower():
            update = dict(zip(index, [humanize.intcomma(entry) for entry in df[key]]))
            df[key].update(pd.Series(update))
        
        # uses size from humanize for formatting file size values to file size notation
        if "size" in key.lower():
            update = dict(zip(index, [humanize.naturalsize(entry, gnu = True) for entry in df[key]]))
            df[key].update(pd.Series(update))

    # capitalise column titles
    df.columns = [x.title() for x in df.columns]
    
    # merge ref column and switch with index
    if df.columns[0].lower() == "ref":
        df = df.set_index(df.columns[0], append=True).swaplevel(0,1)
    
    # show full contents of each cell
    pd.set_option('max_colwidth', 1000)

    return df.fillna('')

def heatmap(table):

    """
    function for displaying a heatmap of a table
    """

    cmp = "Reds"

    # show full contents of each cell
    pd.set_option('max_colwidth', 1000)

    return pd.DataFrame.from_dict(table) \
                                        .fillna("0") \
                                        .style.background_gradient(cmap=cmp).format("{:.0%}")

def sent_frame(doclike, extend = False):

    """
    returns a dataframe of sentence attributes
    """

    sent = doclike.doc

    df = OrderedDict([
        ("text", [t.lower_ for t in sent]),
        ("lemma", [t.lemma_ for t in sent]),
        ("head", [t.head for t in sent]),
        ("ent type", [t.ent_type_ for t in sent]),
        ("concept", [t._.CONCEPT for t in sent]), 
        ("attribute", [t._.ATTRIBUTE for t in sent]), 
        ("ideology", [t._.IDEOLOGY for t in sent])
    ])
    
    if extend == True:
        df.update(OrderedDict([
            ("pos", [t.pos_ for t in sent]),
            ("tag", [t.tag_ for t in sent]),
            ("dep", [t.dep_ for t in sent]),
        ]))
 
        # ("modifier", [t._.modifier if t._.modifier else "" for t in sent]),

    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    
    return pd.DataFrame.from_dict(df, orient = "index")

def token_deps(token):

    """
    returns a dataframe of token dependency attributes
    """

    # make sure the passed variable is of type Token
    if not isinstance(token, Token):
        return

    try:
        nbor = token.nbor()
    except:
        nbor = None

    df = OrderedDict([
    ("token", token.text),
    ("i", token.i),
    ("is_stop", token.is_stop),
    ("pos", token.pos_),
    ("ent_type_", token.ent_type_),
    ("tag", token.tag_),
    ("dep", token.dep_),
    ("head", token.head),
    ("nbor", nbor),    
    ("ancestors", list(token.ancestors)),
    ("conjuncts", list(token.conjuncts)),
    ("children", list(token.children)),
    ("lefts", list(token.lefts)),
    ("rights", list(token.rights)),
    ("n_lefts", token.n_lefts),
    ("n_rights", token.n_rights),
    ("subtree", list(token.subtree)),
    ("left span", token.doc[token.left_edge.i : token.i + 1]),
    ("right span", token.doc[token.i : token.right_edge.i + 1]),
    ])
    
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    
    return pd.DataFrame({key:pd.Series(value).astype('str') for key, value in df.items()}).fillna("")

def chunk_custom_attrs(chunks, json = False):

    df = list()

    for chunk in chunks:
        line = dict()
        line['text'] = str(chunk.text)
        line['root'] = str(chunk.root)
        line['root CONCEPT'] = str(chunk.root._.CONCEPT)
        line['modifier'] = str(chunk._.modifier)
        line['CONCEPT'] = chunk._.CONCEPT
        line['ATTRIBUTE'] = chunk._.ATTRIBUTE
        line['IDEOLOGY'] = chunk._.IDEOLOGY
        line['span_type'] = chunk._.span_type
        line["entity"] = str([ent.text for ent in chunk.ents if ent.label_ in ["GPE", "NORP", "PERSON", "ORG"]]).strip("['']")
        line['label'] = str(chunk.label_)
        line['start'] = chunk.start
        line["end"] = chunk.end
        
        df.append(line)

    if json:
        return df
    else:
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_columns', None)
        return pd.DataFrame(df).fillna("")

def sent_custom_chunks(doc):
    
    df = OrderedDict([
    ("token", [str(token) for token in doc]),
    ("CONCEPT", [token._.CONCEPT if token._.CONCEPT else "" for token in doc]),
    ("ATTRIBUTE", [token._.ATTRIBUTE if token._.ATTRIBUTE else "" for token in doc]),
    ("IDEOLOGY", [token._.IDEOLOGY if token._.IDEOLOGY else "" for token in doc]),
    ])
    
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    return pd.DataFrame({key:pd.Series(value).astype('str') for key, value in df.items()}).fillna("").T


