import numpy as np
from scipy import signal

class FilterConfiguration():
    def __init__(self, order: int, cutoff: float, appendage: int):
        self.order = order
        self.cutoff = cutoff
        self.appendage = appendage
        self.sample_frequency = 0

def add_appendage(data: np.ndarray, config: FilterConfiguration):
    if data.ndim == 1:
        front = np.repeat(np.take(data, 0), config.appendage)
        end = np.repeat(np.take(data, -1), config.appendage)
        data = np.concatenate((front, data, end))
    else:
        front = np.repeat(np.take(data, 0, axis=1)[:, None], \
            config.appendage, axis=1)
        end = np.repeat(np.take(data, -1, axis=1)[:, None], \
            config.appendage, axis=1)
        data = np.concatenate((front, data, end), axis=1)
    return data

def remove_appendage(data: np.ndarray, config: FilterConfiguration):
    if data.ndim == 1:
        length = data.shape[0]
        axis = 0
    else:
        length = data.shape[1]
        axis = 1
    indices = [i for i in range(length)]
    indices = indices[:config.appendage] + indices[-config.appendage:]
    return np.delete(data, indices, axis=axis)

def FIR_filter(data: np.ndarray, config: FilterConfiguration, axis: int=-1):
    '''
    :arg data: The data to be filtered.
	:arg config: The filter configuration.

    :return filtered_data: The filtered data.
    :return delay: The time delay introduced by the signal, in seconds.
    '''
    if data.ndim == 1:
        axis = -1
    filter = signal.firwin(numtaps=config.order, cutoff=config.cutoff, \
        fs=config.sample_frequency)
    filtered_data = signal.lfilter(filter, 1.0, data, axis=axis)
    delay = 0.5 * (config.order - 1) / config.sample_frequency
    return filtered_data, delay

def FIR_filter_kaiser(data: np.ndarray, sample_time: float, \
    attenuation_frequency: float, transition_frequency: float, \
    cutoff_frequency: float, axis: int=0):
    '''
    :arg data: The data to be filtered.
    :arg sample_time: The sample time of the data.
    :arg attenuation_frequency: The attenuation frequency of the filter in dB.
    :arg transition_frequency: The transition frequency of the filter in dB.
    :arg cutoff_frequency: The cutoff frequency of the filter in dB.
    '''
    # Calculate frequencies and passband width.
    sample_frequency = 1 / sample_time
    nyquist_frequency = sample_frequency / 2.0
    width = transition_frequency / nyquist_frequency

    # Create filter.
    order, beta = signal.kaiserord(attenuation_frequency, width)
    filter = signal.firwin(order, cutoff_frequency/nyquist_frequency, \
        window=('kaiser', beta))
    filtered_data = signal.lfilter(filter, 1.0, data, axis=axis)
    return filtered_data
