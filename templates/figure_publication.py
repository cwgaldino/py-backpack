#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create publication quality figure."""

# standard imports
import numpy as np
from pathlib import Path

# matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox
from matplotlib.ticker import MultipleLocator
from matplotlib import gridspec

# backpack
import sys
sys.path.append('/home/galdino/github/py-backpack')
import backpack.figmanip as figmanip
import importlib
importlib.reload(figmanip)

#plt.ion()
%matplotlib qt5

# %% ====================== Close all other figures ===========================
plt.close('all')

# %% =========================== Negative? ====================================
negative = 0
if negative:
    plt.style.use('dark_background')
else:
    plt.style.use('default')

# %% ============================= Fonts ======================================
# Check system available fonts
# from matplotlib.font_manager import findSystemFonts
# font_list = findSystemFonts()
# matching = [s for s in font_list if 'cmr10' in s]
# print(matching)

# Configure fonts
font0 = FontProperties(fname='/home/galdino/github/py-backpack/templates/ttf/cmr10.ttf')
#font0 = FontProperties(fname=str(Path(r'C:\Users\carlo\github\py-backpack\templates\ttf\cmr10.ttf')))
font0.set_size(9)

mpl.rcParams['mathtext.fontset'] = 'cm'  # Change mathtext to CMR ("latex")
mpl.rcParams['svg.fonttype'] = 'none'  # Change text to text, and not paths.
# Note: mathtext output relies on absolute glyph positioning. Therefore, text
# objects that contain mathtext are trick to edit on vector graphics editors
# (inkscape, illustrator, etc...) This was reported as a bug:
# https://github.com/matplotlib/matplotlib/issues/13200

# %% ============================ Figure ======================================
# Figure position on screen
# figmanip.getWindowPosition()
xPosition = 1500
yPosition = 100

# Figure size on the paper (in cm)
# PRB, 2 column: Column width 8.6 cm or 3 3/8 in.
width = 8.6
height = 5

# Use the pyplot interface for creating figures, and then use the object
# methods for the rest
fig = figmanip.figure(figsize=figmanip.cm2inch(width, height))
figmanip.setWindowPosition(xPosition, yPosition)

# %% Axes: Create axes instance ===============================================
number_of_lines = 1
number_of_columns = 1
height_ratios=[1]*number_of_lines
width_ratios=[1]*number_of_columns
gs = gridspec.GridSpec(number_of_lines, number_of_columns, height_ratios=height_ratios, width_ratios=width_ratios)
fig.subplots_adjust(hspace=0, wspace=.3) #Set distance between subplots

ax = list()
ax.append(fig.add_subplot(gs[0]))
for i in range(1, number_of_lines):
    ax.append(fig.add_subplot(gs[i], sharex=ax[0]))

# %% ================================ Plot ====================================
x = np.linspace(0, 10*np.pi, 100)
y = np.sin(x)
y2 = np.cos(x)

scale = 1e1

colors = ['black', 'red', 'blue', 'green', 'magenta']
linestyles = ['-', '--', '-.', ':', '-']
markers =    [None, 'o', None, None, 'x']
color = iter(colors)
linestyle = iter(linestyles)
marker = iter(markers)

marker = None
markevery = 2
markersize = 0
linewidth = 1
line1, = ax[0].plot(x, y*scale,
                 linestyle=next(linestyle),
                 linewidth=linewidth,
                 color=next(color),
                 marker='o',
                 markevery=markevery,
                 markersize=markersize,
                 markerfacecolor='blue',
                 markeredgecolor='blue',
                 markeredgewidth=0.5,
                 label='$y=\sin(x)$')

line2, = ax[0].plot(x, y2*scale,
                 linestyle=next(linestyle),
                 linewidth=linewidth,
                 color=next(color),
                 marker='o',
                 markevery=markevery,
                 markersize=markersize,
                 markerfacecolor='blue',
                 markeredgecolor='blue',
                 markeredgewidth=0.5,
                 label='$y=\cos(x)$')

# %% =========================== Text =========================================
if True:
    plt.vlines(6, -10, 7, linestyles='dotted', linewidth=1)
    plt.hlines(-5, 0, 7, linestyles='dotted', linewidth=1)
    plt.text(13, -6, 'text', fontproperties=font0)

# %% =========================== Axis Labels ==================================
ax[-1].set_xlabel(r'x axis ($\mu$ unit)', fontproperties=font0, labelpad=None)

for i in range(len(ax)):
    ax[0].set_ylabel(r'y axis', fontproperties=font0, labelpad=None)

# %% =========================== Axis ticks ==================================
ticks_default = dict( min_value        = None,
                      max_value        = None,
                      n_ticks          = None,
                      ticks_sep        = None,
                      pad              = None,
                      n_minor_ticks    = 1,
                      n_decimal_places = None,
                      fontproperties   = font0,
                     )

for i in range(len(ax)):
    figmanip.set_ticks(ax[i], axis='x', **ticks_default)
    figmanip.set_ticks(ax[i], axis='y', **ticks_default)

# ticks properties
# ax[0].tick_params(which='major', direction='in', top=True, right=True, labelbottom=False)
for i in range(len(ax)):
    ax[i].tick_params(which='major', direction='in', top=True, right=True, labelright=False, labeltop=False)
    ax[i].tick_params(which='minor', direction='in', top=True, right=True)

for i in range(len(ax)):
    figmanip.remove_ticks_edge(ax[i])
# %% =============== Axes position on figure ==================================
left   = 0.16
bottom = 0.18
right  = 0.98
top    = 0.98
fig.subplots_adjust(left=left, bottom=bottom, right=right, top=top)
# ax[0].set_position(Bbox([[left, bottom], [right, top]]))

# %% ====================== Legend ============================================
for i in range(len(ax)):
    leg = ax[i].legend(frameon=0, labelspacing=.1, prop=font0)

# %% ======================= Inset ============================================
ax2putInset = [ax[0], ]
x_init      = [20, ]
x_final     = [31, ]
y_init      = [-8, ]
y_final     = [-5, ]

insets = []
if True:
    for i in range(len(ax2putInset)):
        # create inset
        insets.append(fig.add_axes(figmanip.axBox2figBox(ax2putInset[i], [x_init[i], y_init[i], x_final[i], y_final[i]])))
        # ax_inset = fig.add_axes([0.13, 0.81, 0.17, 0.17])
        # ax_inset = fig.add_axes(Bbox([[.25, .38], [.3, .5]]))
        # ax_inset.set_position([.685,.32,.25,.3], which='both')

        line2, = insets[i].plot(x, y,
                              ls='-',
                              linewidth=1,
                              marker = 'o',
                              markevery=2,
                              ms=2,
                              color='blue',
                              markerfacecolor='blue',
                              markeredgewidth=0.5,
                              label='example: $y=\sin x$')

    for i in range(len(insets)):
        figmanip.set_ticks(insets[i], axis='x', **ticks_default)
        figmanip.set_ticks(insets[i], axis='y', **ticks_default)

    for i in range(len(insets)):
        insets[i].tick_params(which='major', direction='in', top=True, right=True, labelright=False, labeltop=False)
        insets[i].tick_params(which='minor', direction='in', top=True, right=True)

# %% ======================== Save figure =====================================
dirpath = '.'
name_prefix = 'plot'

# pdf is for fast visualization (svg is for editing on inkscape)
if True:
    if negative:
        plt.savefig(str(Path(dirpath) / (name_prefix + '_negative.pdf')))
        plt.savefig(str(Path(dirpath) / (name_prefix + '_negative.svg')), transparent=False)
    else:
        plt.savefig(str(Path(dirpath) / (name_prefix + '_raw.pdf')))
        plt.savefig(str(Path(dirpath) / (name_prefix + '_raw.svg')), transparent=True)