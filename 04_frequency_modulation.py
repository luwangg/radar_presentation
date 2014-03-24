import numpy as np
import scipy as sp
import pylab as plt

from scipy import signal
from scipy.constants import c, pi

from pylab import style
#style.use('ggplot')

from utils import *

#############################################
# Variable Declarations
#############################################

# Sample frequency should be at least 2x the sum term of the carrier and
# reflected frequencies.
fs = 300000.0             # Sample Rate [Hz]

# The ADC sample rate only needs to be greater than 2x the difference term.
adc_fs = 25000.0          # Sample Rate [Hz]   
adc_samples = 2048        # Number of samples

carrier = Signal(
    amplitude = 3.3,      # [V]
    frequency = 75000,    # [Hz]
    phase = 0,            # [rad]
    )

tuning_fork = FMTarget(
    frequency = 5000,     # [Hz]
    mod_index = 0.5,      # Modulation Index, should be < 1
    r_pct = 1.0,
    )
#############################################

# Generate Carrier Signal
t = np.linspace(0, adc_samples/adc_fs, fs * (adc_samples/adc_fs))
tx, tx_90 = build_complex_signal(t, carrier)

# Generate FM component
fm = Signal(
    amplitude = tuning_fork.mod_index,
    frequency = tuning_fork.frequency,
    phase = pi/2,
    )
fm_x = build_real_signal(t, fm)

# Generate Return Signal
reflected = Signal(
    amplitude = carrier.amplitude * tuning_fork.r_pct,
    frequency = carrier.frequency,
    phase = fm_x,
    )
rx = build_real_signal(t, reflected)

# Mixer Stage
mixer_i = tx * rx
mixer_q = tx_90 * rx

# Low-pass Filter
# Note: This is a simplified example and not what is actually done in hardware.
h = signal.firwin(50, cutoff=0.5)
filtered_i = signal.filtfilt(h, [1.0], mixer_i)
filtered_q = signal.filtfilt(h, [1.0], mixer_q)

# Fourier Transform (For plotting)
f = np.linspace(-fs/2, fs/2, fs * (adc_samples/adc_fs)) 
tx_fft = fft(tx)
rx_fft = fft(rx)
mixer_product_fft = fft(mixer_i + 1j*mixer_q)
filtered_product_fft = fft(filtered_i + 1j*filtered_q)

# ADC Stage (Downsample)
adc_t = t[::fs/adc_fs]
baseband_i = filtered_i[::fs/adc_fs]
baseband_q = filtered_q[::fs/adc_fs]

# Fourier Transform
adc_f = np.linspace(-adc_fs/2, adc_fs/2, adc_samples)
baseband_fft = fft(baseband_i + 1j*baseband_q)

# Plot
plt.figure('RF Time Domain')
plt.title('RF Time Domain')
plt.xlabel('Seconds')
plt.ylabel('Volts')
plt.xlim([0, .0005])
plt.plot(t, tx, alpha=0.5, label='Carrier Signal')
plt.plot(t, rx, alpha=0.5, label='Recieve Signal')
plt.plot(t, mixer_i, label='Mixer Product')
plt.plot(t, filtered_i, linewidth=3, label='Filtered Product')
plt.legend()

plt.figure('RF Frequency Domain')
plt.title('RF Frequency Domain')
plt.xlabel('Hz')
plt.ylabel('Magnitude')
plt.plot(f, np.abs(tx_fft), label='Carrier Signal')
plt.plot(f, np.abs(rx_fft), label='Recieve Signal')
plt.plot(f, np.abs(mixer_product_fft), label='Mixer Product')
plt.plot(f, np.abs(filtered_product_fft), label='Filtered Product')
plt.legend()

plt.figure('Baseband Frequency Domain')
plt.title('Baseband Frequency Domain')
plt.xlabel('Hz')
plt.ylabel('Magnitude')
plt.xlim([-adc_fs/2, adc_fs/2])
plt.plot(adc_f, np.abs(baseband_fft), label='Baseband')
plt.legend()

plt.show()
