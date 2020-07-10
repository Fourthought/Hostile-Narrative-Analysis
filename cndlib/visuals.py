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
        ("ent type", [t.ent_type_ for t in sent])
    ])
    
    if extend == True:
        df.update(OrderedDict([
            ("pos", [t.pos_ for t in sent]),
            ("tag", [t.tag_ for t in sent]),
            ("dep", [t.dep_ for t in sent]),
            ("ancestors", [list(t.ancestors) for t in sent])
        ]))
        
    df.update(OrderedDict([
        ("concept", [t._.CONCEPT for t in sent]), 
        ("attribute", [t._.ATTRIBUTE for t in sent]), 
        ("ideology", [t._.IDEOLOGY for t in sent]), 
        ("modifier", [t._.modifier if t._.modifier else "" for t in sent]),
    ]))

    pd.set_option('display.max_columns', None)
    # columns = [t.i for t in sent]
    # index = list(df.keys())
    
    return pd.DataFrame.from_dict(df, orient = "index")

def token_deps(token):

    """
    returns a dataframe of token dependency attributes
    """

    # make sure the passed variable is of type Token
    if not isinstance(token, Token):
        return

    df = OrderedDict([
    ("token", token.text),
    ("pos", token.pos_),
    ("tag", token.tag_),
    ("dep", token.dep_),
    ("head", token.head),
    ("nbor", token.nbor()),
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
    
    pd.set_option('display.max_columns', None)
    
    return pd.DataFrame({key:pd.Series(value).astype('str') for key, value in df.items()}).fillna("")

def chunk_custom_attrs(doc):

    df = OrderedDict([
        ("string", [str(chunk) for chunk in doc._.custom_chunks]),
        ("CONCEPT", [chunk._.CONCEPT if chunk._.CONCEPT else "" for chunk in doc._.custom_chunks]),
        ("ATTRIBUTE", [chunk._.ATTRIBUTE if chunk._.ATTRIBUTE else "" for chunk in doc._.custom_chunks]),
        ("IDEOLOGY", [chunk._.IDEOLOGY if chunk._.IDEOLOGY else "" for chunk in doc._.custom_chunks]),
        ("span_type", [chunk._.span_type if chunk._.span_type else "" for chunk in doc._.custom_chunks]),
        ("modifier", [chunk._.modifier if chunk._.modifier else "" for chunk in doc._.custom_chunks]),
        ("span modifiers", [list(chunk._.span_modifiers) if chunk._.span_modifiers else "" for chunk in doc._.custom_chunks]),
        ])

    pd.set_option('display.max_columns', None)
    return pd.DataFrame({key:pd.Series(value).astype('str') for key, value in df.items()}).fillna("").T

def sent_custom_chunks(doc):
    
    df = OrderedDict([
    ("token", [str(token) for token in doc]),
    ("CONCEPT", [token._.CONCEPT if token._.CONCEPT else "" for token in doc]),
    ("ATTRIBUTE", [token._.ATTRIBUTE if token._.ATTRIBUTE else "" for token in doc]),
    ("IDEOLOGY", [token._.IDEOLOGY if token._.IDEOLOGY else "" for token in doc]),
    ])
    
    pd.set_option('display.max_columns', None)
    return pd.DataFrame({key:pd.Series(value).astype('str') for key, value in df.items()}).fillna("").T


