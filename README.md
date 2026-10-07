\# Voice-to-Task Notebook



A local application that turns spoken notes into reviewed task lists.



\## Features

\- Record audio through the browser microphone

\- Transcribe English speech locally with Faster Whisper

\- Edit transcription mistakes

\- Suggest tasks using simple text-splitting rules

\- Review and edit tasks before saving

\- Store tasks in SQLite

\- Mark tasks complete and preserve their status across restarts



\## How it works

Streamlit provides the interface.

Faster Whisper uses the pretrained base.en speech model on the CPU.

Python rules split reviewed text into task suggestions.

SQLite stores confirmed tasks in tasks.db.



Speech recognition is the AI component.

Task splitting is rule-based, not LLM-based.



\## Setup on Windows

Requires Python 3.13 and a microphone.



Create an environment:

`py -3.13 -m venv .venv`



Install dependencies:

`.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt`



Start the app:

`.\\.venv\\Scripts\\python.exe -m streamlit run app.py`



Allow microphone access in your browser.

The first transcription downloads the speech model.

No paid AI API or API key is required.



\## Workflow

Record → Transcribe → Correct → Suggest tasks → Review → Save



\## Manual checks

\- Recorded and transcribed a short English note

\- Corrected recognition errors before task extraction

\- Split three actions into separate tasks

\- Preserved "Buy bread and milk" as one task

\- Saved tasks and completion status across browser refreshes



\## Limitations

Transcription can misrecognize words.

Task splitting cannot reliably interpret narratives, negation,

completed actions, or due dates.

Users must review suggestions before saving.

This prototype is designed for local personal use.



\## Dependency compatibility

PyAV 19 removed an argument used by the installed Faster Whisper version.

Installing av<19 resolved the decoding error.

requirements.txt records the working package versions.



\## Privacy

Audio is processed locally when the app runs on your computer.

This code does not save recordings to disk.

Confirmed tasks are stored locally in tasks.db.

Personal recordings and the database are excluded from this repository.



\## Development

Built with AI coding assistance and manually tested.

