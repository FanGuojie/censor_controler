# -*- coding: utf-8 -*-
import numpy as np
import pylab as pl

from numpy import cos, sin, pi, absolute, arange
from scipy.signal import kaiserord, lfilter, firwin, freqz
from pylab import figure, clf, plot, xlabel, ylabel, xlim, ylim, title, grid, axes, show

#------------------------------------------------
# Create a signal for demonstration.
#------------------------------------------------

sample_rate = 512
fft_size = 256

t = np.arange(0, 1.0, 1.0/sample_rate)
# x = cos(2*pi*0.5*t) + 0.2*sin(2*pi*2.5*t+0.1) + \
#         0.2*sin(2*pi*15.3*t) + 0.1*sin(2*pi*16.7*t + 0.1) + \
#             0.1*sin(2*pi*23.45*t+.8) + sin(2*pi*50*t+.8) + 0.1*sin(2*pi*100*t+.8)

# x = 2*sin(2*pi*30*t) # 30Hz
# x = 2*sin(2*pi*30*t) + sin(2*pi*50*t) # 30Hz 50Hz

datas = np.loadtxt("C:/Users/newtonbob/Downloads/sensor_data_20181109162602.txt")
print(len(datas))

x = datas[:, 1]
t = np.arange(0, len(x))

xs = x[:fft_size]
xf = np.fft.rfft(xs)/fft_size
freqs = np.linspace(0, sample_rate/2, fft_size/2+1)
xfp = 20*np.log10(np.clip(np.abs(xf), 1e-20, 1e100))


#------------------------------------------------
# Create a FIR filter and apply it to x.
#------------------------------------------------

# The Nyquist rate of the signal.
nyq_rate = sample_rate / 2.0

# The desired width of the transition from pass to stop,
# relative to the Nyquist rate.  We'll design the filter
# with a 5 Hz transition width.
width = 10.0/nyq_rate

# The desired attenuation in the stop band, in dB.
ripple_db = 20.0

# Compute the order and Kaiser parameter for the FIR filter.
N, beta = kaiserord(ripple_db, width)
print(N)

# The cutoff frequency of the filter.
cutoff_hz = 10.0

# Use firwin with a Kaiser window to create a lowpass FIR filter.
taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))

# Use lfilter to filter x with the FIR filter.
filtered_x = lfilter(taps, 1.0, x)

filtered_xs = filtered_x[:fft_size]
filtered_xf = np.fft.rfft(filtered_xs)/fft_size
filtered_freqs = np.linspace(0, sample_rate/2, fft_size/2+1)
filtered_xfp = 20*np.log10(np.clip(np.abs(filtered_xf), 1e-20, 1e100))

#------------------------------------------------
# Plot the FIR filter coefficients.
#------------------------------------------------

figure(1)
plot(taps, 'bo-', linewidth=2)
title('Filter Coefficients (%d taps)' % N)
grid(True)

#------------------------------------------------
# Plot the magnitude response of the filter.
#------------------------------------------------

figure(2)
clf()
w, h = freqz(taps, worN=8000)
plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
xlabel('Frequency (Hz)')
ylabel('Gain')
title('Frequency Response')
ylim(-0.05, 1.05)
grid(True)

# Upper inset plot.
# ax1 = axes([0.42, 0.6, .45, .25])
# plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
# xlim(0,8.0)
# ylim(0.9985, 1.001)
# grid(True)

# Lower inset plot
# ax2 = axes([0.42, 0.25, .45, .25])
# plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
# xlim(12.0, 20.0)
# ylim(0.0, 0.0025)
# grid(True)

#------------------------------------------------
# Plot the original and filtered signals.
#------------------------------------------------

# The phase delay of the filtered signal.
delay = 0.5 * (N-1) / sample_rate

figure(3)
# Plot the original signal.
plot(t, x)

# Plot the filtered signal, shifted to compensate for the phase delay.
plot(t-delay, filtered_x, 'r-')

# Plot just the "good" part of the filtered signal.  The first N-1
# samples are "corrupted" by the initial conditions.
# plot(t[N-1:]-delay, filtered_x[N-1:], 'g', linewidth=4)

xlabel('t')
grid(True)

figure(4)
pl.subplot(221)
pl.plot(t[:fft_size], xs)
pl.xlabel(u"time(s)")
pl.title(u"wave freq")

pl.subplot(223)
pl.plot(freqs, xfp)
pl.xlabel(u"freq(Hz)")

pl.subplot(222)
pl.plot(t[:fft_size], filtered_xs)
pl.xlabel(u"time(s)")
pl.title(u"wave freq")

pl.subplot(224)
pl.plot(filtered_freqs, filtered_xfp)
pl.xlabel(u"filtered freq(Hz)")

show()