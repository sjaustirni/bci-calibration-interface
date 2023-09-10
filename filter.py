import numpy as np
from scipy import signal


class Filter:
    def __init__(self, sampling_frequency: int = 4000, bandpass_low: int = 20, bandpass_high: int = 200,
                 bandpass_order: int = 4, mean_kernel_size: int = None):
        """
        :param sampling_frequency: Sampling frequency of the signal in Hz
        :param bandpass_low: Low cut for the bandpass filter in Hz
        :param bandpass_high: High cut for the bandpass filter in Hz
        :param bandpass_order: Order of the bandpass filter
        :param mean_kernel_size: Size of the kernel for the mean filter. Default is a third of a second.
        """
        # Define the parameters of the bandpass filter
        self.fs = sampling_frequency
        self.bandpass_low = bandpass_low
        self.bandpass_high = bandpass_high
        self.bandpass_order = bandpass_order
        self.mean_kernel_size = mean_kernel_size if mean_kernel_size else int(self.fs / 3)
        
        self.input = []
        self.output = []
        
        self.b, self.a = self._create_bandpass()
    
    def _create_bandpass(self):
        nyquist = 0.5 * self.fs
        low = self.bandpass_low / nyquist
        high = self.bandpass_high / nyquist
        
        b, a = signal.butter(self.bandpass_order, [low, high], btype='band')
        return b, a
    
    def apply(self, sample):
        """
        :param sample: New sample to be filtered
        :return: Filtered sample
        """
        # Rectify the input signal
        sample = abs(sample)
        
        # Add the sample to the input buffer
        self.input.append(sample)
        
        # Apply the bandpass filter
        if len(self.input) >= self.bandpass_order:
            sample = signal.lfilter(self.b, self.a, self.input[-self.bandpass_order:] + [sample])[self.bandpass_order]
        # Apply the mean filter
        if len(self.input) >= self.mean_kernel_size:
            sample = np.mean(self.input[-self.mean_kernel_size:] + [sample])
        
        self.output.append(sample)
        
        return sample
