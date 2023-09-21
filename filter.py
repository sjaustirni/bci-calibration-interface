import numpy as np
from scipy.signal import lfilter_zi, lfilter, iirfilter


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
        self.bandpassed = []
        self.output = []
        
        self.b, self.a = self._create_bandpass()
        self.zi = lfilter_zi(self.b, self.a)
        
        self.baseline_start = None
        self.baseline_end = None
        self.baseline = None
        self.baseline_std = None
    
    def _create_bandpass(self):
        b, a = iirfilter(self.bandpass_order, [self.bandpass_low, self.bandpass_high], fs = self.fs, btype='band', ftype='butter')
        return b, a
    
    def apply(self, sample):
        """
        :param sample: New sample to be filtered
        :return: Filtered sample
        """
        # Add the sample to the input buffer
        self.input.append(sample)
        
        # Apply the bandpass filter
        sample, self.zi = lfilter(self.b, self.a, [sample], zi=self.zi)
        sample = abs(sample[0])
        self.bandpassed.append(sample)
        
        # Apply mean filter
        if len(self.bandpassed) > self.mean_kernel_size:
            sample = np.mean(self.bandpassed[-self.mean_kernel_size:] + [sample])
        else:
            sample = np.mean(self.bandpassed + [sample])

        self.output.append(sample)
        
        return sample
    
    def mark_as_baseline(self):
        if self.baseline_start is None:
            self.baseline_start = len(self.output)
    
    def mark_as_NOT_baseline(self):
        if self.baseline_start is None:
            return
        if self.baseline_end is None:
            self.baseline_end = len(self.output)
            actual_end = int(250 / 2)  # half a second
            actual_start = 250 * 3 + actual_end  # 3 seconds
            data = self.output[self.baseline_end - actual_start:self.baseline_end - actual_end]
            self.baseline = np.mean(data)
            self.baseline_std = np.std(data)
    
    def reset_baseline(self):
        self.baseline_start = None
        self.baseline_end = None
