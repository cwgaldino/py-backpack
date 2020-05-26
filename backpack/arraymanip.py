#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Array manipulation utilities module."""

import numpy as np
from scipy.optimize import curve_fit
from .model_functions import fwhmVoigt


def index(array, value):
    """Return the closest index of a value in a array.

    :param array: an 1d array of float or int.
    :param value: a float or int value.

    :return: index (int)
    """
    return np.argmin(np.abs(np.array(array)-value))


def increasing_monotonicity(dataX, dataY):
    """Returns an array sorted and monotonic.

    The sorting is based on dataX and the monotonicity is done by averaging
    dataY for same dataX values.

    If you need decreasing monotonicity just run this function and invert the
    returned arrays.

    :param dataX: list of numbers
    :param dataY: list of numbers
    :return: two numpy arrays (x_monotonic, y_monotonic)

    Example:    dataX= [1, 2, 4, 2, 1]
                dataY = [5, 6, 9, 8, 9]

                x_return = [1, 2, 4]
                y_return = [7, 7, 9]
    """
    # sort increasingly
    data2sort = np.array(np.transpose([dataX, dataY]))
    data_sorted = data2sort[data2sort[:, 0].argsort()]

    done = False
    data_sorted_clean = np.copy(data_sorted)
    i = 0

    while not done:
        val = data_sorted_clean[i, 0]

#        print(i, val)
        if i == len(data_sorted_clean)-1:
#            print('aqui')
            done = True
            return data_sorted_clean[:, 0], data_sorted_clean[:, 1]

        #Find how many duplicates there is
        number_of_duplicates = 0
        k = np.copy(i)
        while val == data_sorted_clean[k+1, 0]:
            k = k+1
            number_of_duplicates = number_of_duplicates+1
            if k==(len(data_sorted_clean)-1):
                done = True
                break
#        print(i, val, k, number_of_duplicates)

        #Mean
        if number_of_duplicates>=1:
            data_sorted_clean[i, 1] = np.mean(data_sorted_clean[i:(i+number_of_duplicates+1), 1], dtype=np.float64)
#            print(data_sorted_clean)

            for j in range(number_of_duplicates):
#                print('e')
                data_sorted_clean = np.delete(data_sorted_clean, i+1, axis=0)
#                print(data_sorted_clean)
        i = i + 1

        if done:
            return data_sorted_clean[:, 0], data_sorted_clean[:, 1]


def extractFromData(x, y, ranges2extract):
    """
    Extract elements from x and y that are whithin intervals in ranges2extract.

    This function is useful for extracting parts from data. Like, supose you two lists
    interpreted as x and y data of a plot and y has a peak somewhere x=10 and x=20.
    Then you can use this function to build another pair os lists, like x_peak and y_peak
    with just the "peak part" of your data.

    :param x: 1darray to search for interval ranges
    :param y: 1darray
    :param ranges2extract: list of dataX range values
    :return: two numpy arrays

    Example: ranges2extract=[[783.7, 789.3], [797, 805]]
    """
    x_clean = []
    y_clean = []

    for xinit, xfinal in ranges2extract:
        choose_range = np.logical_and(x>xinit, x<xfinal)
        x_clean.append(x[choose_range])
        y_clean.append(y[choose_range])

    # # flatten without numpy
    # x_clean = [item for sublist in x_clean for item in sublist]
    # y_clean = [item for sublist in y_clean for item in sublist]

    # flatten
    return np.array(x_clean).flatten(), np.array(y_clean).flatten()



def fastPeakFit(dataX, dataY, guess_c, guess_A, guess_w, guess_offset=0,
                initX=None, finalX=None, assimetricPeak=True):
    """
    Fit a peak with a pseudo-voigt curve.

    IF assimetricPeak=True peak assimetry is taken into account by fiting first
    half of the peak with a different FHWM than the second half.

    "smoothed" data is (dataX, dataY) with 100 times more points.

    If initX=None and finalX=None, full data range is used.

    Center of the peak is assumed to be within initX and finalX.

    :param dataX: array X
    :param dataY: array Y
    :param guess_c: guess Center
    :param guess_A: guess Amplitude
    :param guess_w: guess FWHM
    :param guess_offset: guess Offset [0]
    :param initX: start X value to fit the peak [None]
    :param finalX: final X value to fit the peak [None]
    :param assimetricPeak: Bool value [True]

    :return:  1) array of the fitted peak.
              2) 2 column array with "Smooth" dataX and dataY.
              3) An array with the optimized parameters for Amplitude, Center, FWHM and offset.
    """
    if initX is None: initX=dataX[0]
    if finalX is None: finalX=dataX[-1]

    if assimetricPeak:
        p0 = [guess_A, guess_c, guess_w, 0.5, guess_w, 0.5, guess_offset]
        def function2fit(x, A, c, w1, m1, w2, m2, offset):
            f = np.heaviside(x-c, 0)*fwhmVoigt(x, A, c, w1, m1) + offset +\
                np.heaviside(c-x, 0)*fwhmVoigt(x, A, c, w2, m2)
            return f
        bounds=[[0,      initX,   0,      0, 0,      0, -np.inf],
                [np.inf, finalX,  np.inf, 1, np.inf, 1, np.inf]]
    else:
        p0 = [guess_A, guess_c, guess_w, 0.5, guess_offset]
        def function2fit(x, A, c, w, m, offset):
            return fwhmVoigt(x, A, c, w, m) + offset
        bounds=[[0,      initX,   0,      0, -np.inf],
                [np.inf, finalX,  np.inf, 1, np.inf]]

    # Fit data
    x2fit, y2fit = extractFromData(dataX, dataY, [[initX, finalX],])
    popt, pcov = curve_fit(function2fit, x2fit, y2fit, p0,  # sigma = sigma,
                           bounds=bounds)

    # smooth data
    arr100 = np.zeros([100*len(x2fit), 2])
    arr100[:, 0] = np.linspace(x2fit[0], x2fit[-1], 100*len(x2fit))
    arr100[:, 1] = function2fit(arr100[:, 0],  *popt)

    if assimetricPeak:
        popt_2 = (popt[0], popt[1], popt[2]/2+popt[4]/2, popt[-1])
    else:
        popt_2 = (popt[0], popt[1], popt[2], popt[-1])

    return function2fit(dataX, *popt), arr100, popt_2


def interpShift(dataX, dataY, shift):
    r"""Shift arrayY regarding arrayX.

    Shift is done by linear interpolating the dataY. This interpolation may
    not be perfect and may cause information loss. Make sure your data is
    smooth enough and always plot the residuals toghether with your data to
    make sure the error is acceptable.

    It is always better to smooth your data before doing this shift. Like, if
    your data has 300 points, interpolate the data to 1000 points and them do
    the shift. This tipically leads to better results.

    Deslocating dataY regarding dataX is useful because it keeps dataX
    unchanged.

    If you do not need to keep the dataX unchanged, it is much saffer to apply
    a \"hard Shift\" in which dataX is shifted instead of dataY.
    See arraymanip.hardShift().

    :param dataX: 1D array. It must be an increasing array (I am not sure about this).
    :param dataY: 1D array Y.
    :param shift: shift value (int or float).
    :return: (numpy array) dataY shifted regarding dataX and the residue.
    """
    dataX = np.array(dataX)
    dataY = np.array(dataY)

    yshifted = np.interp(dataX, dataX + shift, dataY)

    return yshifted, dataY - np.interp(dataX, dataX - shift, yshifted)


def hardShift(array, shift):
    """Shift a vector.

    Data form is perfectly preserved.

    :param array: 1D array
    :param shift: shift value (int or float)
    :return: numpy array
    """
    return np.array(array) + shift



# # OLD ==================================
# def extractFromData_old(dataX, dataY, Xranges2extract):
#     '''
#     Extract elements from dataX and dataY that are whithin intervals in Xranges2extract.
#
#     This function is useful for extracting parts from data. Like, supose you two lists
#     interpreted as x and y data of a plot and y has a peak somewhere x=10 and x=20.
#     Then you can use this function to build another pair os lists, like x_peak and y_peak
#     with just the "peak part" of your data.
#
#     :NOTE: data must be monotonic.
#
#     :param dataX: 1darray to search for interval ranges
#     :param dataY: 1darray
#     :param Xranges2extract: list of dataX range values
#     :return: two numpy arrays
#
#     Example: Xranges2extract=[[783.7, 789.3], [797, 805]]
#     '''
#
#     # Check if dataX is increasing or decreasing (must be increasing)
#     if dataX[0] > dataX[1]:  # if is decreasing, invert array
#         dataX = dataX[::-1]
#         dataY = dataY[::-1]
#
#     # Transforms bkgLimits in a numpy array in case it is not one yet
#     Xranges2extract = np.array(Xranges2extract)
#
#     # Transform energy limits in indexes
#     index = np.zeros([len(Xranges2extract), 2])  # Pre allocation
#     for i in range(0, len(Xranges2extract)):  # Loop trhough lines
#         index[i] = [np.argmin(np.abs(dataX-Xranges2extract[i, 0])),
#                     np.argmin(np.abs(dataX-Xranges2extract[i, 1]))]
#     index = index.astype(int)
#     # Return a list of indexes (same as Xranges2extract, but with indexes instead
#     #of X values)
#
#     # Isolate from data only the background
#     data2X = np.empty([1])  # Generate random 1 matrix
#     data2Y = np.empty([1])  # Generate random 1 matrix
#     for i in range(0, len(index)):  # Loop trhough lines of index
#         data2X = np.concatenate((data2X,dataX[index[i, 0]:index[i, 1]]))
#         data2Y = np.concatenate((data2Y,dataY[index[i, 0]:index[i, 1]]))
#     data2X = np.delete(data2X, (0), axis=0)  # Delete first line
#     data2Y = np.delete(data2Y, (0), axis=0)  # Delete first line
#     # Maybe in the future I will find a better way to do this, but when I pre alocate
#     # bkgData, the first comes with zeros, then later I have to delete it.
#
#     return data2X, data2Y
