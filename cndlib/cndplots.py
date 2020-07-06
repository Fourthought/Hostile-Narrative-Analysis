from math import floor, ceil
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.offsetbox import AnchoredText

# define smooting algorithm
def smoothing(sentiment_list, window_size):
    window_size = window_size
    numbers_series = pd.Series(sentiment_list)
    windows = numbers_series.rolling(window_size)
    moving_averages = windows.mean()

    moving_averages_list = moving_averages.tolist()
    
    return moving_averages_list[window_size - 1:]

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