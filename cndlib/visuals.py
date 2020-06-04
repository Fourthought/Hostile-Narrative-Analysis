import pandas as pd

def display_table(index):

    """ function to display a dictionary object """

    return pd.DataFrame(index, columns = index.keys()).style.set_properties(**{'text-align': 'left'}).set_table_styles([dict(selector='th', props=[('text-align', 'left')])])