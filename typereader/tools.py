

""" Internal Tools """

import numpy as np


def spiderplot(categories, values, ax=None,
               axfc = None,
               lcolor="k", lsize="small", 
               rcolor="0.7", rsize="small", rarray=None,
               title=None, titlecolor="k", titlesize="medium",
               fillcolor = "C0", fillalpha=0.1,               
               highlight_unique=True,
               highlight_color="C0", 
                **kwargs):
    """ Create a spider plot with Matplotlib

    Parameters
    ----------
    categories: [list]
        Name of the categories (defines the spider arms)

    values: [list]
        Value associated to each arm (categories). This define the distance to the center.

    // Options

    ax: [matplotlib.Axes] -optional-
        axes in which the spider plot will be draw. 
        If None, this will create a new figure and a single axis within.

    axfc: [matplotlib color] -optional-
        Color of the axes background (facecolor in axes definition)
        [Ignored if `ax` prodived]

    lcolor, lsize: [color, fontsize]  -optional-
        color and size of the `categories` labels
        
    rcolor, rsize, rarray: [color,fontsize, tick_location] -optional-
        color, size and position of the radial contours (associated to `values`)

    title, titlecolor, titlesize: [string, fontcolor, fontsize] -optional-
        A title could be provided.
        If so,  `titlecolor` and `titlesize` will be set to fontcolor and fontsize respectively.
        
    fillcolor, fillalpha= [color, float] -optional-
        color and alpha of the filled part of the spider plot

    highlight_unique: [bool] -optional-
        If solely one categories have non-zero values, shall it's label be highlighted ?
        If so, the label will be slightly bigger and its color will be changed to `highlight_color`
    
    highlight_color: [color] -optional-
        Color of the highlighted label. 
        See highlight_unique. [Ignored if highlight_unique is False]

        
    **kwargs goes to ax.plot(). It affects the spider plot contours.
    
    Returns
    -------
    {fig, ax}
    """
    import matplotlib.pyplot as mpl
    
    if highlight_unique:
        flagnonzero = np.asarray(values)>0 
        highlight = np.argwhere(flagnonzero)[0] if np.sum(flagnonzero) == 1 else None
        lcolor = "0.5"
    else:
        highlight = None
        
    # But we need to repeat the first value to close the circular graph:
    values = list(values)
    values += values[:1]
    ncategories = len(categories)
    
    
        # == Plot
    if ax is None:
        fig = mpl.figure(figsize=[3,3.5])
        ax  = fig.add_axes([0.1,0.12,0.8,0.7], polar=True, 
                           facecolor=axfc,
                               zorder=1)
    else:
        ax  = ax
        fig = ax.figure

    # What will be the angle of each axis in the plot? (we divide the plot / number of variable)
    angles = [n / float(ncategories) * 2 * np.pi for n in range(ncategories)]
    angles += angles[:1]
  
    # Draw one axe per variable + add labels labels yet
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, color=lcolor, size=lsize)
    
    if highlight is not None and highlight_unique:
        xtick = ax.get_xticklabels()[highlight[0]]
        xtick.set_color(highlight_color)
        xtick.set_weight("bold")
        xtick.set_size(xtick.get_size()*1.2)
            

        
        # Draw ylabels
    ax.set_rlabel_position(0)
        
    # Scaling
    if rarray is not None:    
        ax.set_yticks(rarray[:-1])
        ax.set_ylim(0,rarray[-1])
        
    ax.set_yticklabels(np.asarray(ax.get_yticks(), dtype="str"), 
                       color=rcolor, size=rsize)
    
    # --------------- #
    #  Actual Plot    #
    # --------------- #
    # Plot data
    prop = dict(linewidth=1.5, linestyle='solid', color=fillcolor)
    for k,v in kwargs.items():
        prop[k] = v
    # python 3 -> prop = {**dict(linewidth=1.5, linestyle='solid'), **kwarg}
    ax.plot(angles, values, **prop)
 
        # Fill area
    ax.fill(angles, values, fillcolor, alpha=fillalpha)
        
    # Additional Info
    # First entry
    if title is not None:
        ax.set_title(title, size=titlesize, color=titlecolor)
        
    return {"ax":ax, "fig":fig, "highlight":highlight}
