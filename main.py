from future.moves import tkinter as tk
from tkinter import *

from sys import byteorder
from array import array
from struct import pack
import pyaudio
import wave

#const NUM = 12


root = tk.Tk()
# width x height + x_offset + y_offset:
root.geometry("800x480+300+300")
root.configure(bg='#505050')


chart = tk.Label(root,
                 text="chart",
                 bg="grey")
chart.place(x=20, y=20, width=760, height=200)

slider = ['#1', '#2', '#3', '#4', '#5','#6', '#7', '#8', '#9', '#10', '#11', '#12']

slider_values = []
labels = range(12)

for i in range(12):
    slider_values.append(IntVar())
    bg_colour = '#808080'
    #l = tk.Label(root,
    #            text=slider[i],
    #            bg=bg_colour)
    scale = Scale(root, from_=50, to=-50, variable=slider_values[i], bg=bg_colour)

    scale.place(x=20 + i * 64, y=240, width=45, height=170)




# -----------------------------------------------------------------------------
import threading
import time


THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100


# def is_silent(snd_data):
#     "Returns 'True' if below the 'silent' threshold"
#     return max(snd_data) < THRESHOLD


def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i * times))
    return r


def trim(snd_data):
    "Trim the blank spots at the start and end"

    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i) > THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data


def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    silence = [0] * int(seconds * RATE)
    r = array('h', silence)
    r.extend(snd_data)
    r.extend(silence)
    return r


def record():
    """
    Record a word or words from the microphone and
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the
    start and end, and pads with 0.5 seconds of
    blank sound to make sure VLC et al can play
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    counter = 0

    while is_recording: # this is a global variable set from the button
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        "program stops after counter"
        counter = counter + 1
        # if counter > 300:
        #     break

        # silent = is_silent(snd_data)
        # if silent and snd_started:
        #     num_silent += 1
        # elif not silent and not snd_started:
        #     snd_started = True
        #
        # if snd_started and num_silent > 30:
        #     break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r


def record_to_file(path):
    print("record to file:" + path)
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    print("1")
    data = pack('<' + ('h' * len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

    print("record to file finished in " + path)

# -----------------------------------------------------------------------------


def print_selection():
    s = ""
    for i in range(12):
        s = s + " " + str(slider_values[i].get())
    chart.config(text='you have selected' + s)


INTERVAL = 1
is_recording = False


def thread_record(args):
    # while is_recording:
    #     print('Doing something imporant in the background')
    #     time.sleep(INTERVAL)

    # if __name__ == '__main__':
    record_to_file('demo.wav')
    print("done - result written to demo.wav")
    print("thread_run finished")


def button_record():
    global is_recording
    if not is_recording:
        is_recording = True
        ButtonRecord.config(text="Stop Recording")
        thread = threading.Thread(target=thread_record, args=(1,))
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution
        # record_to_file('demo.wav')
    else:
        is_recording = False
        ButtonRecord.config(text="Record")






def button_play():
    pass


ButtonRecord = tk.Button(
    text="Record",
    bg="#bb0d1c",
    fg="black",
    command=button_record)
ButtonRecord.place(
    x=150, y=425, width=150, height=40)


ButtonPlay = tk.Button(
    text="Play",
    bg="#bb0d1c",
    fg="black",
    command=button_play)
ButtonPlay.place(
    x=500, y=425, width=150, height=40)


ButtonDebug = tk.Button(
    text="Debug",
    bg="yellow",
    fg="black",
    command=print_selection)
ButtonDebug.place(
    x=355, y=425, width=90, height=40)



root.mainloop()

