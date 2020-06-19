import pandas as pd
from hurry.filesize import size
import humanize

def display_df(df, columns):

    """ function to format a dataframe object for display"""

    #.style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    
    if isinstance(df, list):
        df = pd.DataFrame(df, columns = columns)
    
    if isinstance(df, pd.DataFrame):
        df = df
    
    # add a new row with totals for numerical columns
    totals = [None if value.dtype != "int64" else sum(value) for _ , value in df.iteritems()]
    totals[0] = "Totals"
    df.loc[df.index.max()+1] = totals

    
    # index = dict(zip([i for i in range(len(df.index))], [size(entry) for entry in df["file size"]]))
    # df['file size'].update(pd.Series(index))

   
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

    return df.fillna('')

def heatmap(table):

    cmp = "Reds"

    return pd.DataFrame.from_dict(table) \
                                        .fillna("0") \
                                        .style.background_gradient(cmap=cmp).format("{:.0%}")

def sent_frame(doclike, compact = True):

    """
    returns a dataframe of sentence attributes

    this is not an elegent function, there does not seem to be a way to perform a
    getattr() on custom attributes
    """

    sent = doclike.doc
    columns = [t.i for t in sent]
    blank = ["" for t in sent]
    index = ["text", "ent_type", "concept", "attribute", "ideology"]
    df = []
    
    df.append([t for t in sent])
    df.append([t.ent_type_ for t in sent])
    
    if compact == False:
        index = ["text", "ent_type", "lemma", "pos", "tag", "dep", "concept", "attribute", "ideology"]
        df.append([t.lemma_ for t in sent])
        df.append([t.pos_ for t in sent])
        df.append([t.tag_ for t in sent])
        df.append([t.dep_ for t in sent])
    
    try:
        df.append([t._.CONCEPT for t in sent])
    except:
        df.append(blank)

    try:
        df.append([t._.ATTRIBUTE for t in sent])
    except:
        df.append(blank)

    try:
        df.append([t._.IDEOLOGY for t in sent])
    except:
        df.append(blank)

    pd.set_option('display.max_columns', None)
    
    return pd.DataFrame(df, index = index, columns = columns)