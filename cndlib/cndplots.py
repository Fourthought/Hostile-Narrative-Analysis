from math import floor, ceil
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

# define smooting algorithm
def smoothing(sentiment_list, window_size):
    window_size = window_size
    numbers_series = pd.Series(sentiment_list)
    windows = numbers_series.rolling(window_size)
    moving_averages = windows.mean()

    moving_averages_list = moving_averages.tolist()
    
    return moving_averages_list[window_size - 1:]

def get_doc_scores(dataset):
    
    for orator in dataset.values():
        for document in orator:
            line = dict()
            line["ref"] = document["ref"]
            line["datestamp"] = document["datestamp"]
            line["title"] = document["title"]
            line["word count"] = document["word count"]
            line["sentence count"] = len(document["sentences"])
            line["textblob"] = document["sentiment_scores"]["textblob"]
            line["watson"] = document["sentiment_scores"]["watson"]
            line["google"] = document["sentiment_scores"]["google"]
            
            yield line

# df = pd.DataFrame(get_doc_scores(sentiment_analysis))
# display(df.style.background_gradient(cmap="Blues", subset = df.columns[-3:]))

# create list of x-axis references based on smoothed y-axis data
def x_axis_smooth(sentiment_list):
    total_len = len(sentiment_list)
    return [(i / total_len)*100 for i in range(total_len)]

def sentiment_plot(plot_list, dataset, smooth = True, \
                    figtitle = "",
                    xlabel = "",
                    ylabel = "",
                    text_box = ""):
    
    SMALL_SIZE = 10
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 18

    matplotlib.rc('legend', fontsize=MEDIUM_SIZE)
    matplotlib.rc('axes', titlesize=BIGGER_SIZE)

    #instantiate subplots
    fig, axes = plt.subplots(nrows = ceil(len(plot_list)/2), ncols = floor(len(plot_list)/2), figsize = (30, 15))

    # iterate through each subplot to plot data
    for n, plot in enumerate(axes.flatten()):

        # get document and api references
        orator = plot_list[n][0]
        doc_index = plot_list[n][1]
        # api reference
        line_legend = list(dataset[orator][doc_index]["sentences"][0]["scores"])

        # set the y-axis limits from -1 to +1
        plot.set_ylim([-1,1])

        # turn on grid
        plot.grid()

        # get document title
        title = dataset[orator][doc_index]["title"]

        # add text box to plot
        doc_scores = {k : round(v, 2) for k, v in dataset[orator][doc_index]["sentiment_scores"].items()}
        plot.add_artist(AnchoredText(f'Document Sentiment Scores {doc_scores}', loc=8, prop={'size': MEDIUM_SIZE}))

        # iterate through lines reference and plot the results
        for line in line_legend:
            y_axis = [score["scores"][line] for score in dataset[orator][doc_index]["sentences"]]
            if smooth:
                y_axis = smoothing(y_axis, plot_list[n][2])
                plot.plot(x_axis_smooth(y_axis), y_axis, label = line)
            else:
                x_axis = [i for i in range(len(dataset[orator][doc_index]["sentences"]))]
                plot.plot(x_axis, y_axis, label = line)

        # turn on legend and set document metadata
        plot.legend(loc = "upper left")
        if n >= len(plot_list) - floor(len(plot_list)/2):
            plot.set_xlabel(xlabel)
        plot.set(ylabel=ylabel, title=title)
        fig.suptitle(figtitle, fontsize = 26)
    
    return fig

def heatmap(data, row_labels, col_labels, figtitle = None,
            ax=None, cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """
    SMALL_SIZE = 10
    MEDIUM_SIZE = 14
    BIGGER_SIZE = 18

    if not ax:
        ax = plt.gca()
    ax.set_title(figtitle, fontsize = 25)

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)


    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, orientation = "horizontal", **cbar_kw)
    cbar.mappable.set_clim(-1,1)
    cbar.ax.set_title(cbarlabel, fontdict = {"fontsize" : BIGGER_SIZE})

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, fontdict = {"fontsize" : MEDIUM_SIZE})
    ax.set_yticklabels(row_labels, fontdict = {"fontsize" : MEDIUM_SIZE})

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), fontsize = 16, **kw)
            texts.append(text)

    return texts