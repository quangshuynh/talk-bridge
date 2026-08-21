# Talk Bridge

Talk Bridge is a desktop speech translation app built with Python and
Tkinter. It lets Vietnamese and Chinese speakers speak into a
microphone, converts the speech to text, and translates it into the
other language and English.

## Features

-   Speech recognition for Vietnamese (`vi-VN`) and Mandarin Chinese
    (`zh-CN`)
-   Vietnamese → Chinese and English translation
-   Chinese → Vietnamese and English translation
-   Side-by-side Tkinter interface for both speakers
-   Automatic microphone noise adjustment
-   Number handling for Vietnamese and Chinese text
-   Original recognized text displays converted number words with the
    original digits in parentheses
-   Background recording/translation threads so the interface stays
    responsive
-   Clear All button to reset all text fields
-   Status messages and error dialogs for microphone, recognition, and
    translation failures

## Requirements

-   Python 3.10+ recommended
-   A working microphone
-   Internet access for Google speech recognition and translation

Python packages:

-   `SpeechRecognition`
-   `googletrans`
-   `PyAudio` (normally required by `SpeechRecognition` for microphone
    input)

Tkinter is included with many Python installations, but on some Linux
distributions it must be installed separately.

## Installation

Clone or download the project, then create and activate a virtual
environment.

``` bash
python -m venv .venv
```

Windows:

``` bash
.venv\Scripts\activate
```

macOS/Linux:

``` bash
source .venv/bin/activate
```

Install the dependencies:

``` bash
pip install SpeechRecognition googletrans==4.0.0rc1 PyAudio
```

> **Note:** Installing `PyAudio` can require additional system packages
> depending on your operating system.

## Running the App

Run the Python file containing the application:

``` bash
python talk_bridge.py
```

If your Python file has a different name, replace `talk_bridge.py` with
that filename.

## How to Use

1.  Launch the application.
2.  Click **Speak Vietnamese** for Vietnamese speech or **Speak
    Chinese** for Chinese speech.
3.  Speak near the microphone.
4.  Wait while Talk Bridge recognizes and translates the speech.
5.  Read the original transcription and the two translations in the
    corresponding panel.
6.  Click **Clear All** to erase the displayed text.

The app listens for up to 10 seconds per recording attempt and times out
if speech does not begin within about 5 seconds.

## Interface

The window contains two main panels:

### Vietnamese speaker

Displays:

-   Recognized Vietnamese
-   Chinese translation
-   English translation

### Chinese speaker

Displays:

-   Recognized Chinese
-   Vietnamese translation
-   English translation

## Number Handling

Before translation, Talk Bridge preprocesses digit sequences.

For Vietnamese, supported integers are converted into Vietnamese number
words for translation. For Chinese, each Arabic digit is mapped to its
corresponding Chinese numeral. In the original transcription display,
the app keeps the recognized digits in parentheses after the converted
words.

For example, a recognized number may be displayed in a form similar to:

``` text
... number words ... (123)
```

## Error Handling

Talk Bridge reports common problems through its status area or an error
dialog, including:

-   No microphone detected
-   Listening timeout
-   Unrecognized audio
-   Speech-recognition service errors
-   Translation errors

## Project Structure

A minimal project can look like this:

``` text
talk-bridge/
├── talk_bridge.py
└── README.md
```

## Notes and Limitations

-   Speech recognition and translation depend on external online
    services.
-   Recognition quality depends on microphone quality, background noise,
    pronunciation, and network connectivity.
-   The current number-to-words logic is custom and does not cover every
    linguistic edge case.
-   The translation library/service may change behavior or become
    unavailable independently of this application.
