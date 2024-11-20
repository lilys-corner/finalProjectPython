from tkinter import *
from tkinter import ttk,filedialog,messagebox
import base64
import json
from pathlib import Path
from bs4 import BeautifulSoup
import requests



config = {}

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

#ADDED TITLE FUNCTION START
def fetch_title():
    url= _url.get()
    try:
        page = requests.get(url)
    except requests.RequestException as err:
        sb(str(err))
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text
            config['title'] = title
            sb(f'Title: {title}')
        else:
            sb('No title found')
#ADDED TITLE FUNCTION END

#ADDED LINKS FUNCTION START
def fetch_links():
    url= _url.get()
    try:
        page = requests.get(url)
    except requests.RequestException as err:
        sb(str(err))
    else:
        links = []
        soup = BeautifulSoup(page.content, 'html.parser')
        base_domain = url.split('/')[2]
        for a in soup.findAll('a', href = True):
            href = a['href']
            if href.startswith(('http://', 'https://')) and base_domain not in href:
                links.append(href)
        if links:
            _images.set(tuple(links))
            sb('Links found: {}'.format(len(links)))
        else:
            sb('No links found')
#ADDED LINKS FUNCTION END

def save():
    if not config.get('images'):
        alert('No images to save')
        return

    if _save_method.get() == 'img':
        dirname = filedialog.askdirectory(mustexist=True)
        save_images(dirname)
    else:
        filename = filedialog.asksaveasfilename(
            initialfile='images.json',
            filetypes=[('JSON', '.json')])
        save_json(filename)


def save_images(dirname):
    if dirname and config.get('images'):
        for img in config['images']:
            img_data = requests.get(img['url']).content
            filename = Path(dirname).joinpath(img['name'])
            with open(filename, 'wb') as f:
                f.write(img_data)
        alert('Done')


def save_json(filename):
    if filename and config.get('images'):
        data = {}
        for img in config['images']:
            img_data = requests.get(img['url']).content
            b64_img_data = base64.b64encode(img_data)
            str_img_data = b64_img_data.decode('utf-8')
            data[img['name']] = str_img_data

        with open(filename, 'w') as ijson:
            ijson.write(json.dumps(data))
        alert('Done')


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
