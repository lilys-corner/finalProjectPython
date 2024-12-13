from tkinter import *
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, welch
from pydub import AudioSegment

config = {}

global theFileName
theFileName = '' # current file, begins as null

## MAIN PROCESS
def process(input_file, sample_rate, data, target, ifGraphed):
    # Define the time vector
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)

    if ifGraphed == 0:
        # Split channels and combine channels
        data = splitChannelsAndCombine(data, sample_rate, 0)
    else:
        # Split channels and combine channels
        data = splitChannelsAndCombine(data, sample_rate, 1)

    # Fourier transform
    spectrum, freqs = fourierTransform(data, sample_rate)

    # Find the target frequency
    target_frequency = find_target_frequency(freqs, target)

    # Bandpass filter
    filtered_data = bandpass_filter(data, target_frequency - 50, target_frequency + 50, sample_rate)

    # Compute decibel scale for filtered signal
    # Convert the filtered audio signal to decibel scale
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)  # Avoid log of zero
    # Plot the filtered signal in decibel scale
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='#004bc6')
    plt.title(f'RT60 Waveform at {int(target_frequency)} Hz')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    # Find the index of the maximum value
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    # Slice the array from the maximum value
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5

    # Find peak dB, -5 dB, -25 dB. Then compute R20, then R60. Output R60 time in the GUI
    rt60 = dBAndRT60(sliced_array, value_of_max_less_5, data_in_db, value_of_max, t)

    if ifGraphed == 0:
        resonant_frequency_var = resonant_frequency(data, sample_rate)
        _summary.set(f'Total duration of wave in sec: {t} s\n'
                     f'Resonant frequency: {resonant_frequency_var}\n'
                     f'')

        return rt60, target_frequency, resonant_frequency_var, t

    return rt60, target_frequency, t

# lowcut = target frequency - 50, highcut = target frequency + 50
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def add_log_entry(entry):
    _analysis_listbox.insert(END, entry)

def readTheFile(filename):
    sample_rate, data = wavfile.read(filename)

    #low
    rt60_low, target_frequency_low, resonant_freq, t = process(filename, sample_rate, data, 250, ifGraphed=0)
    #mid
    rt60_mid, target_frequency_mid, t = process(filename, sample_rate, data, 1000, ifGraphed=1)
    #high
    rt60_high, target_frequency_high, t = process(filename, sample_rate, data, 5000, ifGraphed=1)

    #update the summary listbox
    _summary.set('')
    add_log_entry(f'File: {filename}')
    add_log_entry(f'Sample rate: {sample_rate} Hz')
    length = data.shape[0] / sample_rate
    add_log_entry(f'Total duration of wave in sec: {length} s')
    add_log_entry(f'Resonant frequency: {resonant_freq} Hz')
    add_log_entry(f"RT60 (Low Freq): {round(abs(rt60_low), 2)} seconds at {int(target_frequency_low)} Hz")
    add_log_entry(f"RT60 (Mid Freq): {round(abs(rt60_mid), 2)} seconds at {int(target_frequency_mid)} Hz")
    add_log_entry(f"RT60 (High Freq): {round(abs(rt60_high), 2)} seconds at {int(target_frequency_high)} Hz")
    rt60_avg = (rt60_low + rt60_mid + rt60_high) / 3
    rt60_avg_diff = rt60_avg - 0.5
    add_log_entry(f"RT60 Difference: {round(abs(rt60_avg_diff), 2)} seconds")

def splitChannelsAndCombine(data, sample_rate, ifGraphed):
    # Check if the audio has 2 channels
    if len(data.shape) == 2:
        # Split into left and right channels
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        # Optionally, combine the channels (e.g., average)
        data = (left_channel + right_channel) / 2

        if ifGraphed == 0:
            length = data.shape[0] / sample_rate
            time = np.linspace(0., length, data.shape[0])
            plt.figure(1)
            plt.title('Two Channel Waveform')
            plt.plot(time, left_channel, label="Left channel")
            plt.plot(time, right_channel, label="Right channel")
            plt.legend()
            plt.xlabel("Time [s]")
            plt.ylabel("Amplitude")
            plt.show()

        return data

    else:
        # Mono audio, no change needed
        data = data
        if ifGraphed == 0:
            spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024, cmap=plt.get_cmap('autumn_r'))
            plt.figure(1)
            cbar = plt.colorbar(im)
            plt.title('Spectrogram')
            plt.xlabel('Time (s)')
            plt.ylabel('Frequency (Hz)')
            cbar.set_label('Intensity (dB)')
            plt.show()

            length = data.shape[0] / sample_rate
            time = np.linspace(0., length, data.shape[0])
            plt.figure(2)
            plt.title('Mono Waveform')
            plt.plot(time, data)
            plt.xlabel("Time [s]")
            plt.ylabel("Amplitude")
            plt.show()


        return data


# Calculate the Fourier Transform of the signal
def fourierTransform(data, sample_rate):
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)  # Get magnitude spectrum
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)

    # Use only positive frequencies
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]
    return spectrum, freqs


# Find the target frequency closest to 1000 Hz
def find_target_frequency(freqs, target):
    nearest_freq = freqs[np.abs(freqs - target).argmin()]
    return nearest_freq


# Function to find the nearest value in the array
def find_nearest_value(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def dBAndRT60(sliced_array, value_of_max_less_5, data_in_db, value_of_max, t):
    # Find the nearest value for max-5dB and its index
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')

    # Find the nearest value for max-25dB and its index
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')

    # Calculate RT60 time
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20

    # Show plot
    plt.grid()
    plt.show()

    return rt60


def resonant_frequency(data, sample_rate):
    frequencies, power = welch(data, sample_rate, nperseg=4096)
    dominant_frequency = frequencies[np.argmax(power)]

    n = len(data) # length of the signal
    k = np.arange(n)
    T = n/sample_rate
    frq = k/T # two sides frequency range
    frq = frq[:len(frq)//2] # one side frequency range
    Y = np.fft.fft(data)/n
    Y = Y[:n//2]
    plt.title('Dominant Frequency')
    plt.yscale('symlog')
    plt.plot(frq, abs(Y)) # plot the power
    plt.xlim(0, 1500) # limit x-axis to 1.5Khz
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power')
    plt.show()

    return dominant_frequency

# get a da file!
def open_file():
    global theFileName
    theFileName = filedialog.askopenfilename()
    file_conversion(theFileName)


def file_conversion(file_path):
    # Do something with the selected file path
    nameOfFile = file_path.split('/')[-1]

    fileType = nameOfFile.split('.')[-1]

    if fileType == 'wav':
        _status_msg.set('Analyzing ' + nameOfFile + ' now')
        readTheFile(nameOfFile)

    elif fileType == 'mp3':

        src = nameOfFile
        dst = "new_wav.wav"

        # convert wav to mp3
        # convert wav to mp3
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")

        sound = AudioSegment.from_mp3(src)
        _status_msg.set('Analyzing ' + nameOfFile + ' now')

        readTheFile(dst)

    else:
        # error
        _status_msg.set('ERROR: Wrong file type! Only .wav and .mp3 are supported')

def combine_RT60():
    if theFileName != '':
        return
    else:
        _status_msg.set('ERROR: No file selected for the Combine RT60 operation')


if __name__ == "__main__":  # execute logic if run directly
    _root = Tk()  # instantiate instance of Tk class
    _root.title('Acoustic Modeling')

    # THIS IS THE TOP BAR OF CLOSE AND MAXIMIZE/MINIMIZE, AND THE TITLE
    _mainframe = ttk.Frame(_root, padding='5 5 5 5 ')  # root is parent of frame
    _mainframe.grid(row=0, column=0, sticky=("E", "W", "N", "S"))  # placed on first row,col of parent
    # frame can extend itself in all cardinal directions

    # THIS CREATES A WINDOW THAT FITS TO WHATEVER IS ON IT
    _window_frame = ttk.LabelFrame(
        _mainframe, text='Select file:', padding='5 5 5 5')  # label frame
    _window_frame.grid(row=0, column=0, sticky=("E", "W"))  # only expands E W
    _window_frame.columnconfigure(0, weight=1)
    _window_frame.rowconfigure(0, weight=1)  # behaves when resizing

    # BUTTON TO THE RIGHT OF THE TEXT BOX TO INITIATE A COMMAND THAT FINDS THE FILE IN THE TEXT BOX
    # FILE MUST BE IN THE SAME DIRECTORY
    # grid mgr places object at position
    _getfile_button = ttk.Button(
        _window_frame, text='Get file', command=open_file)  # create button, MAKE A COMMAND LATER FOR FINDING THE FILE
    # fetch_window() is callback for button press
    _getfile_button.grid(row=0, column=0, sticky=E, padx=5)
    ####### END IMPORT DATA MAIN FUNCTION

    _combine_button = ttk.Button(
        _window_frame, text='Combine RT60 graphs', command=combine_RT60)  # create button, MAKE A COMMAND LATER FOR FINDING THE FILE
    # fetch_window() is callback for button press
    _combine_button.grid(row=0, column=1, sticky=E, padx=5)

    # NEW WINDOW SECTION
    # analysis_frame contains Listbox and Radio Frame
    _analysis_frame = ttk.LabelFrame(
        _mainframe, text='Summary', padding='9 0 0 0')
    _analysis_frame.grid(row=3, column=0, sticky=(N, S, E, W))

    ####### DATA ANALYSIS SECTION
    # Set _analysis_frame as parent of Listbox and _summary is variable tied to
    # IN THIS, "GENERATE SUMMARY STATISTICS AND DESCRIPTIVE MEASURES SUCH AS LENGTH OF AUDIO
    # SAMPLE AND RT60 VALUE"
    # Basically, put the summary statistics like length of audio and rt60 into this box
    # Show graphs as you fill this in a function
    _summary = StringVar()
    _analysis_listbox = Listbox(
        _analysis_frame, listvariable=_summary, height=6, width=50)
    _analysis_listbox.grid(row=0, column=0, sticky=(E, W), pady=5)

    _scrollbar = ttk.Scrollbar(
        _analysis_frame, orient=VERTICAL, command=_analysis_listbox.yview)
    _scrollbar.grid(row=0, column=1, sticky=(S, N), pady=6)
    _analysis_listbox.configure(yscrollcommand=_scrollbar.set)

    # MESSAGE AT THE BOTTOM
    # To change the message, do _status_msg.set('INSERT TEXT HERE')
    _status_frame = ttk.Frame(
        _root, relief='sunken', padding='2 2 2 2')
    _status_frame.grid(row=1, column=0, sticky=("E", "W", "S"))
    _status_msg = StringVar()  # need modified when update status text
    _status_msg.set('Insert a .wav file to start analyzing...')
    _status = ttk.Label(
        _status_frame, textvariable=_status_msg, anchor=W)
    _status.grid(row=0, column=0, sticky=(E, W))

    _root.mainloop()  # listens for events, blocks any code that comes after it
