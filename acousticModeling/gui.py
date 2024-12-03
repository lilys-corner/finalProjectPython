from tkinter import *
from tkinter import ttk,filedialog,messagebox
import base64
import json
from pathlib import Path
from bs4 import BeautifulSoup
from scipy.io import wavfile
from scipy.signal import butter, filtfilt
import requests
from os import path
from pydub import AudioSegment
from pydub.playback import play
from ffmpeg import *

config = {}

#probably would need for it to take in a file name instead
#of the file name (src) being built into the function
def convertMp3_wav():
    #convert from mp3 to wav
    src = "ourRecordingMP3.mp3"
    dst = "convertedOurRecordingWAV.wav"

    # convert wav to mp3
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")

    sound = AudioSegment.from_mp3(src)

def dataFromWav():
    #get data from wavs
    wav_fname = '16bit2chan.wav'
    samplerate, data = wavfile.read(wav_fname)
    print(f"number of channels = {data.shape[len(data.shape) - 1]}")
    print(f'this is data shape {data.shape}')
    print(f"sample rate = {samplerate}Hz")
    length = data.shape[0] / samplerate
    print(f"length = {length}s")


def fetch_url():
    url = _url.get()
    config['images'] = []
    _images.set(())  # initialised as an empty tuple

    try:
        page = requests.get(url)
    except requests.RequestException as err:
        sb(str(err))
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        images = fetch_images(soup, url)

        if images:
            _images.set(tuple(img['name'] for img in images))
            sb('Images found: {}'.format(len(images)))
        else:
            sb('No images found')

        config['images'] = images


def fetch_images(soup, base_url):
    url=_url.get()
    images = []
    for img in soup.findAll('img'):
        src = img.get('src')
        img_url = f'{base_url}/{src}'
        name = img_url.split('/')[-1]
        images.append(dict(name=name, url=img_url))
    return images

def sb(msg):
    _status_msg.set(msg)


def alert(msg):
    messagebox.showinfo(message=msg)



if __name__ == "__main__": # execute logic if run directly
    _root = Tk() # instantiate instance of Tk class
    _root.title('Acoustic Modeling')

    # THIS IS THE TOP BAR OF CLOSE AND MAXIMIZE/MINIMIZE, AND THE TITLE
    _mainframe = ttk.Frame(_root, padding='5 5 5 5 ') # root is parent of frame
    _mainframe.grid(row=0, column=0, sticky=("E", "W", "N", "S")) # placed on first row,col of parent
    # frame can extend itself in all cardinal directions

    # THIS CREATES A WINDOW THAT FITS TO WHATEVER IS ON IT
    _window_frame = ttk.LabelFrame(
        _mainframe, text='Select file:', padding='5 5 5 5')  # label frame
    _window_frame.grid(row=0, column=0, sticky=("E", "W"))  # only expands E W
    _window_frame.columnconfigure(0, weight=1)
    _window_frame.rowconfigure(0, weight=1)  # behaves when resizing

    ####### IMPORT DATA MAIN FUNCTION (CALL COMMAND)
    # NO FUNCTIONALITY YET
    # CREATES SMALL TEXT BOX
    _window = StringVar()
    _window.set('')  # sets initial value of _window (it is blank)
    _window_entry = ttk.Entry(
        _window_frame, width=40, textvariable=_window)  # text box
    _window_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)

    # BUTTON TO THE RIGHT OF THE TEXT BOX TO INITIATE A COMMAND THAT FINDS THE FILE IN THE TEXT BOX
    # FILE MUST BE IN THE SAME DIRECTORY
    # grid mgr places object at position
    _fetch_info_btn = ttk.Button(
        _window_frame, text='Get file', )  # create button, MAKE A COMMAND LATER FOR FINDING THE FILE
    # fetch_window() is callback for button press
    _fetch_info_btn.grid(row=0, column=1, sticky=W, padx=2)
    ####### END IMPORT DATA MAIN FUNCTION

    ####### CLEAN DATA IS INTERNAL FUNCTIONS, NOT GUI, BUT STILL DO IT LATER

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
    # Show graphs etc as you fill this in a function
    _summary = StringVar()
    _analysis_listbox = Listbox(
        _analysis_frame, listvariable=_summary, height=6, width=50)
    _analysis_listbox.grid(row=0, column=0, sticky=(E, W), pady=5)


    # SCROLLBAR, DELETE at the end if it's redundant
    _scrollbar = ttk.Scrollbar(
        _analysis_frame, orient=VERTICAL, command=_analysis_listbox.yview)
    _scrollbar.grid(row=0, column=1, sticky=(S, N), pady=6)
    _analysis_listbox.configure(yscrollcommand=_scrollbar.set)
    '''
    #Listbox occupies (0,0) on _analysis_frame.
    # Scrollbar occupies (0,1) so _radio_frame goes to (0,2)
    _radio_frame = ttk.Frame(_analysis_frame)
    _radio_frame.grid(row=0, column=2, sticky=(N, S, W, E))'''

    _status_frame = ttk.Frame(
        _root, relief='sunken', padding='2 2 2 2')
    _status_frame.grid(row=1, column=0, sticky=("E", "W", "S"))
    _status_msg = StringVar() # need modified when update status text
    _status_msg.set('Insert a .wav file to start analyzing...')
    _status= ttk.Label(
        _status_frame, textvariable=_status_msg, anchor=W)
    _status.grid(row=0, column=0, sticky=(E, W))

_root.mainloop() # listens for events, blocks any code that comes after it
