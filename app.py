import sqlite3
from pathlib import Path
from contextlib import closing
import re
import hashlib
from io import BytesIO

import streamlit as st
from faster_whisper import WhisperModel

st.set_page_config(
    page_title="Voice-to-Task Notebook",
    page_icon="🎙️"
)

DB_PATH = Path(__file__).resolve().parent / "tasks.db"

with closing(sqlite3.connect(DB_PATH)) as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
    """)
    connection.commit()


def save_reviewed_tasks():
    draft = st.session_state.get("task_draft", "")
    titles = [
        line.strip() for line in draft.splitlines()
        if line.strip()
    ]

    if not titles:
        return

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.executemany(
            "INSERT INTO tasks (title) VALUES (?)",
            [(title,) for title in titles]
        )
        connection.commit()

    # A button callback can clear the editor before the page reruns.
    st.session_state["task_draft"] = ""
    st.session_state["save_message"] = f"Saved {len(titles)} tasks."


def load_tasks():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        return connection.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id DESC"
        ).fetchall()


def update_completion(task_id, widget_key):
    completed = int(st.session_state[widget_key])

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (completed, task_id)
        )
        connection.commit()

@st.cache_resource
def load_model():
    return WhisperModel(
        "base.en",
        device="cpu",
        compute_type="int8"
    )


st.title("🎙️ Voice-to-Task Notebook")
st.write("Record a short English note and turn it into text.")
st.caption("Transcription runs on your computer without a paid API.")

recording = st.audio_input("Record your note")

if recording is not None:
    audio_bytes = recording.getvalue()
    recording_id = hashlib.sha256(audio_bytes).hexdigest()

    # Clear the previous transcript when a new recording is made.
    if st.session_state.get("recording_id") != recording_id:
        st.session_state["recording_id"] = recording_id
        st.session_state.pop("transcript", None)
        st.session_state.pop("task_draft", None)

    st.audio(audio_bytes, format="audio/wav")

    if st.button("Transcribe recording"):
        try:
            with st.spinner("Loading the model and transcribing..."):
                model = load_model()

                segments, info = model.transcribe(
                    BytesIO(audio_bytes),
                    language="en",
                    beam_size=5,
                    vad_filter=True
                )

                transcript = " ".join(
                    segment.text.strip() for segment in segments
                ).strip()

            st.session_state["transcript"] = transcript

            if not transcript:
                st.warning(
                    "No speech was detected. Try recording again."
                )
        except Exception as error:
            st.error(f"Transcription failed: {error}")

    if st.session_state.get("transcript"):
        st.subheader("Review your transcript")
        st.text_area(
            "Correct any transcription mistakes",
            key="transcript",
            height=150
        )
        st.caption(
            "This draft is held in the current session. "
            "Permanent task saving will be added next."
        )
        if st.button("Suggest tasks"):
            reviewed_text = st.session_state["transcript"].strip()

            # Split at punctuation or "and" before common action verbs.
            parts = re.split(
                r"[.!?;\n]+|,\s*|\band\s+(?=(?:buy|book|call|"
                r"schedule|send|pay|pick|collect|clean|check|"
                r"renew|return|email|visit)\b)",
                reviewed_text,
                flags=re.IGNORECASE
            )

            tasks = [
                part.strip() for part in parts if part.strip()
            ]

            st.session_state["task_draft"] = "\n".join(tasks)

        if st.session_state.get("task_draft"):
            st.subheader("Review suggested tasks")
            st.text_area(
                "One task per line — edit or remove anything incorrect",
                key="task_draft",
                height=150
            )
            st.caption(
                "Suggestions use simple splitting rules. "
                "Check that each line is an intended task."
            )
            st.button(
                "Save reviewed tasks",
                on_click=save_reviewed_tasks
            )
else:
    st.info("Use the microphone button to record a short note.")
st.divider()
st.subheader("Saved tasks")

if "save_message" in st.session_state:
    st.success(st.session_state.pop("save_message"))

saved_tasks = load_tasks()

if not saved_tasks:
    st.info("No saved tasks yet. Record, review, and save your first note.")
else:
    completed_count = sum(
        completed for task_id, title, completed in saved_tasks
    )
    st.caption(
        f"{completed_count} completed out of {len(saved_tasks)} tasks"
    )

    for task_id, title, completed in saved_tasks:
        widget_key = f"saved_task_{task_id}"

        st.checkbox(
            title,
            value=bool(completed),
            key=widget_key,
            on_change=update_completion,
            args=(task_id, widget_key)
        )