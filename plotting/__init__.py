__author__ = 'agolovko'
# from __future__ import (absolute_import, division, print_function, unicode_literals)
import numpy as np
import seaborn as plotSns; plotSns.set(style="ticks", color_codes=True)

def doPlotting(csvData, useful_cols):
    ## Plot: pair plot for all featured, used later for regression
    # plotSns.pairplot(csvData[useful_cols], hue='makeIdModelId', size=2.5).savefig('output/feature_correlation_pairplots.png')
    plotSns.pairplot(csvData[useful_cols]).savefig('output/feature_correlation_pairplots.png')

    # TODO: Prevent the following SNS plots to overlap with the first one
    # ## Plot: heat map, where the color corresponds to the price
    # heatMapX = 'makeId'
    # heatMapY = 'numOfPrevOwners'
    # heatMapZ = 'priceEur'
    # figName = 'output/heatmap_{}_{}_{}.png'.format(heatMapX, heatMapY, heatMapZ)
    # plotSns.heatmap(
    #     csvData.pivot_table(
    #         index=heatMapX,
    #         columns=heatMapY,
    #         values=heatMapZ ,
    #         aggfunc=np.mean)
    #         .fillna(0)
    #         .applymap(float)
    #     , annot=True, fmt=".1f", linewidths=.5)\
    #     .figure\
    #     .savefig(figName)


    ## Plot
    # plotSns.distplot(csvData.priceEur).figure.savefig('output/prices_in_eur.png')

    ## Plot:
    # plotSns.jointplot(csvData.priceEur, csvData.kmState).savefig('output/priceEur_by_kmState.png')

    # Теперь посмотрим на распределения всех интересующих нас количественных признаков
    # df[useful_cols].hist(figsize=(20,12))

    # sns.pairplot(df[useful_cols + ['priceEur']], hue='priceEur')

    # not work, the "priceEur" is a numeric, but should be categorical
    # fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(16, 10))
    # for idx, feat in enumerate(useful_cols):
    #     sns.boxplot(x='priceEur', y=feat, data=df, ax=axes[idx / 4, idx % 4])
    #     axes[idx / 4, idx % 4].legend()
    #     axes[idx / 4, idx % 4].set_xlabel('priceEur')
    #     axes[idx / 4, idx % 4].set_ylabel(feat);