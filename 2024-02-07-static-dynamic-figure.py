#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


bar_width = 0.35

##8dd3c7
#ffffb3
#bebada
#fb8072
#80b1d3
#fdb462
#b3de69
#fccde5
#d9d9d9
#bc80bd

colors = [
    '#8dd3c7',
    '#ffffb3',
    '#bebada',
    '#fb8072',
    '#80b1d3',
    '#fdb462',
    '#b3de69',
    '#fccde5',
    '#d9d9d9',
    '#bc80bd'
]



fig_1_values = [
    [0,0.5],
    [2,3],
    [0,1],
    [4,1.5],
    [0,1],
    [0,2],
    [4,0.5],
    [0,0.5]
]

index_fig_1 = np.arange(2)

index_fig_2 = np.arange(6)

fig_2_values = [
    [2.5, 2.6, 2.7,2.0,  0.5, 5.0],  # Row 1 becomes Column 1
    [1.8, 1.9, 2,0.25,  2.5, 0.5],  # Row 2 becomes Column 2
    [0.5, 0.6, 0.5,2.5,  0.25, 3.0],  # Row 3 becomes Column 3
    [2.0, 1.75, 1.8,4.25,  0.75, 0.0],  # Row 4 becomes Column 4
    [2.2, 2.3, 2.2,0.75,  5.5, 1.75],  # Row 5 becomes Column 5
    [1.0, 0.9, 0.9,0.25,  0.5, 0.0]   # Row 6 becomes Column 6
]

fig, axs = plt.subplots(1, 2, figsize=(10, 5), width_ratios=[2, 4])
# set subplot size so first plot is narrower
fig.subplots_adjust(wspace=0.5)
# set position of Static Complexity title higher

#axs[1].set_ylim(0, 10)
#axs[0].set_xticks(index_fig_1)
axs[0].set_ylabel('Abundance')

axs[1].set_xticks(index_fig_2)

fig_1_colors = colors[:len(fig_1_values)]
previous_bar = [0,0]
for i, bar in enumerate(fig_1_values):
    axs[0].bar(index_fig_1, bar, bar_width,bottom=previous_bar, color=fig_1_colors[i])
    previous_bar = np.add(previous_bar, bar)
#for index, label in zip(index_fig_1, ['Low', 'High']):
#    axs[0].text(index, 10.5, label, ha='center', va='center', color='black', fontsize=12)

previous_bar = [0,0,0,0,0,0]
for i, bar in enumerate(fig_2_values):
    axs[1].bar(index_fig_2, bar, bar_width, bottom=previous_bar, color=colors[i])
    previous_bar = np.add(previous_bar, bar)

for ax in axs:
    #disable spines on left, right, and top
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    #disable ticks and labels on left and right
    ax.yaxis.set_ticks_position('none')
    #disable tick labels
    ax.set_yticklabels([])


plt.tight_layout()
plt.show()

