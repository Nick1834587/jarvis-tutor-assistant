import threading
import tkinter as tk
from tkinter import scrolledtext

from .assistant import handle_message
from .voice_input import listen_once
from .voice_output import speak


COLORS = {
    "app_bg": "#F2F4F8",
    "header": "#202B46",
    "header_muted": "#B8C3D8",
    "card": "#FFFFFF",
    "transcript": "#FAFBFD",
    "ink": "#24324A",
    "muted": "#66758C",
    "border": "#DDE3EC",
    "indigo": "#5B56C8",
    "indigo_hover": "#4B47B5",
    "mint": "#218C7D",
    "mint_hover": "#176F65",
    "gold": "#D39B3D",
    "coral": "#CF6C69",
    "user_bubble": "#EFEEFF",
    "jarvis_bubble": "#E8F5F1",
    "chip": "#E8EAF8",
    "chip_hover": "#DADDF1",
    "chip_gold": "#F8EED9",
}

BODY_FONT = "Candara"
DISPLAY_FONT = "Cambria"


class JarvisDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS — Tutor Assistant")
        self.root.geometry("960x720")
        self.root.minsize(760, 600)
        self.root.configure(bg=COLORS["app_bg"])
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self._message_in_progress = False
        self.speak_replies = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="LOCAL SYSTEM  •  READY")
        self._build_window()
        self.status.trace_add("write", self._update_status_light)
        self._update_status_light()
        self._append_message(
            "JARVIS",
            "Hi! Ask me a question, say 'what should I focus on today?', or plan a "
            "lesson on limits or derivatives. Say 'remember...' to save a detail "
            "between sessions, 'what do you remember?' to review it, or 'forget 1' "
            "to remove it. Recent chat clears when you close JARVIS.",
        )

    def _build_window(self):
        header = tk.Frame(self.root, bg=COLORS["header"], padx=24, pady=17)
        header.pack(fill="x")

        identity = tk.Frame(header, bg=COLORS["header"])
        identity.pack(side="left")

        title = tk.Label(
            identity,
            text="JARVIS",
            bg=COLORS["header"],
            fg="#FFFFFF",
            font=(DISPLAY_FONT, 25, "bold"),
        )
        title.pack(side="left")

        subtitle = tk.Label(
            identity,
            text="TUTOR ASSISTANT",
            bg=COLORS["header"],
            fg=COLORS["header_muted"],
            font=(BODY_FONT, 10, "bold"),
        )
        subtitle.pack(side="left", padx=(16, 0), pady=(9, 0))

        status_pill = tk.Frame(header, bg="#303B56", padx=11, pady=7)
        status_pill.pack(side="right", pady=(3, 0))
        self.status_orb = tk.Canvas(
            status_pill,
            width=20,
            height=20,
            bg="#303B56",
            highlightthickness=0,
        )
        self.status_orb.create_oval(2, 2, 18, 18, outline="#56627B", width=2)
        self._status_dot = self.status_orb.create_oval(
            7, 7, 13, 13, fill=COLORS["mint"], outline=""
        )
        self.status_orb.pack(side="left", padx=(0, 7))
        status_label = tk.Label(
            status_pill,
            textvariable=self.status,
            bg="#303B56",
            fg="#F1F4FA",
            font=(BODY_FONT, 10, "bold"),
        )
        status_label.pack(side="left")

        content = tk.Frame(self.root, bg=COLORS["app_bg"], padx=16, pady=15)
        content.pack(fill="both", expand=True)
        self.transcript = scrolledtext.ScrolledText(
            content,
            wrap="word",
            state="disabled",
            bg=COLORS["transcript"],
            fg=COLORS["ink"],
            insertbackground=COLORS["indigo"],
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["indigo"],
            padx=23,
            pady=20,
            font=(BODY_FONT, 12),
        )
        self.transcript.pack(fill="both", expand=True)
        self.transcript.tag_configure(
            "user_label",
            foreground=COLORS["indigo"],
            font=(BODY_FONT, 10, "bold"),
            spacing1=13,
        )
        self.transcript.tag_configure(
            "jarvis_label",
            foreground=COLORS["mint"],
            font=(BODY_FONT, 10, "bold"),
            spacing1=13,
        )
        self.transcript.tag_configure(
            "user_text",
            foreground=COLORS["ink"],
            background=COLORS["user_bubble"],
            font=(BODY_FONT, 12),
            lmargin1=12,
            lmargin2=12,
            rmargin=28,
            spacing1=3,
            spacing3=7,
        )
        self.transcript.tag_configure(
            "jarvis_text",
            foreground=COLORS["ink"],
            background=COLORS["jarvis_bubble"],
            font=(BODY_FONT, 12),
            lmargin1=12,
            lmargin2=12,
            rmargin=28,
            spacing1=3,
            spacing3=7,
        )

        quick_bar = tk.Frame(self.root, bg=COLORS["app_bg"], padx=18, pady=0)
        quick_bar.pack(fill="x", pady=(0, 10))
        quick_title = tk.Label(
            quick_bar,
            text="QUICK START",
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
            font=(BODY_FONT, 9, "bold"),
        )
        quick_title.pack(anchor="w", pady=(0, 6))

        quick_actions = tk.Frame(quick_bar, bg=COLORS["app_bg"])
        quick_actions.pack(fill="x")
        quick_prompts = [
            ("Today's brief", "What should I focus on today?", "chip"),
            ("My memory", "What do you remember?", "chip"),
            ("Limits lesson", "Plan a lesson on limits", "chip"),
            ("Derivative lesson", "Plan a lesson on derivatives", "chip"),
            ("Surprise me", "Tell me one interesting calculus fact.", "chip_gold"),
        ]
        for label, prompt, color_key in quick_prompts:
            chip = tk.Button(
                quick_actions,
                text=label,
                command=lambda value=prompt: self._run_quick_prompt(value),
                bg=COLORS[color_key],
                fg=COLORS["ink"],
                activebackground=(
                    COLORS["chip_hover"] if color_key == "chip" else "#F1E1BD"
                ),
                activeforeground=COLORS["ink"],
                relief="flat",
                borderwidth=0,
                highlightthickness=0,
                font=(BODY_FONT, 10, "bold"),
                padx=13,
                pady=7,
                cursor="hand2",
            )
            chip.pack(side="left", padx=(0, 8))

        controls = tk.Frame(
            self.root,
            bg=COLORS["card"],
            padx=18,
            pady=14,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        controls.pack(fill="x", padx=16, pady=(0, 8))

        self.entry = tk.Entry(
            controls,
            bg="#FFFFFF",
            fg=COLORS["ink"],
            insertbackground=COLORS["indigo"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["indigo"],
            font=(BODY_FONT, 13),
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 10))
        self.entry.bind("<Return>", self._on_enter)

        self.talk_button = tk.Button(
            controls,
            text="TALK",
            command=self.start_listening,
            bg=COLORS["mint"],
            fg="#FFFFFF",
            activebackground=COLORS["mint_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            font=(BODY_FONT, 10, "bold"),
            padx=17,
            pady=10,
            cursor="hand2",
        )
        self.talk_button.pack(side="left", padx=(0, 8))

        self.send_button = tk.Button(
            controls,
            text="SEND",
            command=self.send_message,
            bg=COLORS["indigo"],
            fg="#FFFFFF",
            activebackground=COLORS["indigo_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            font=(BODY_FONT, 10, "bold"),
            padx=19,
            pady=10,
            cursor="hand2",
        )
        self.send_button.pack(side="left")

        options = tk.Frame(self.root, bg=COLORS["app_bg"], padx=20, pady=0)
        options.pack(fill="x", pady=(0, 13))
        speech_toggle = tk.Checkbutton(
            options,
            text="Speak replies",
            variable=self.speak_replies,
            bg=COLORS["app_bg"],
            fg=COLORS["ink"],
            activebackground=COLORS["app_bg"],
            activeforeground=COLORS["indigo"],
            selectcolor=COLORS["card"],
            font=(BODY_FONT, 10),
        )
        speech_toggle.pack(side="left")

        self.preview_button = tk.Button(
            options,
            text="TEST VOICE",
            command=self._preview_voice,
            bg=COLORS["chip"],
            fg=COLORS["ink"],
            activebackground=COLORS["chip_hover"],
            activeforeground=COLORS["ink"],
            relief="flat",
            borderwidth=0,
            font=(BODY_FONT, 9, "bold"),
            padx=11,
            pady=5,
            cursor="hand2",
        )
        self.preview_button.pack(side="left", padx=(10, 0))

        privacy_note = tk.Label(
            options,
            text="Mic only on TALK • chat resets on close • saved memories stay local",
            bg=COLORS["app_bg"],
            fg=COLORS["muted"],
            font=(BODY_FONT, 9),
        )
        privacy_note.pack(side="right")

    def _update_status_light(self, *_):
        status = self.status.get()
        if "LISTENING" in status:
            color = COLORS["gold"]
        elif "THINKING" in status or "SPEAKING" in status:
            color = COLORS["indigo"]
        elif "UNAVAILABLE" in status:
            color = COLORS["coral"]
        else:
            color = COLORS["mint"]
        self.status_orb.itemconfigure(self._status_dot, fill=color)

    def _run_quick_prompt(self, prompt):
        if self._message_in_progress:
            return
        self.entry.delete(0, "end")
        self.entry.insert(0, prompt)
        self.send_message()

    def _append_message(self, speaker, text):
        self.transcript.configure(state="normal")
        if speaker == "YOU":
            label_tag, text_tag = "user_label", "user_text"
        else:
            label_tag, text_tag = "jarvis_label", "jarvis_text"
        self.transcript.insert("end", f"{speaker}\n", label_tag)
        self.transcript.insert("end", f"{text}\n\n", text_tag)
        self.transcript.configure(state="disabled")
        self.transcript.see("end")

    def _on_enter(self, event):
        self.send_message()
        return "break"

    def send_message(self):
        message = self.entry.get().strip()
        if not message or self._message_in_progress:
            return

        self.entry.delete(0, "end")
        self._append_message("YOU", message)
        self._message_in_progress = True
        self._set_message_controls_enabled(False)
        self.status.set("THINKING LOCALLY")
        threading.Thread(
            target=self._message_worker,
            args=(message,),
            daemon=True,
        ).start()

    def _message_worker(self, message):
        try:
            response, should_exit = handle_message(message)
        except Exception as error:
            response = f"I ran into a problem while preparing that reply: {error}"
            should_exit = False
        self.root.after(0, self._message_received, response, should_exit)

    def _message_received(self, response, should_exit):
        if response.startswith(
            (
                "Removed that saved memory",
                "Cleared all ",
                "There were no saved memories",
            )
        ):
            self.transcript.configure(state="normal")
            self.transcript.delete("1.0", "end")
            self.transcript.configure(state="disabled")
        self._append_message("JARVIS", response)

        if should_exit:
            self.status.set("SHUTTING DOWN")
            self._speak_in_background(response, close_when_done=True)
            return

        if self.speak_replies.get():
            self.status.set("SPEAKING")
            self._speak_in_background(response, on_done=self._message_ready)
        else:
            self._message_ready()

    def _message_ready(self):
        self._message_in_progress = False
        self._set_message_controls_enabled(True)
        self.status.set("LOCAL SYSTEM  •  READY")
        self.entry.focus_set()

    def _preview_voice(self):
        if self._message_in_progress:
            return
        self._message_in_progress = True
        self._set_message_controls_enabled(False)
        self.status.set("SPEAKING")
        self._speak_in_background(
            "Hello. I'm JARVIS. Ready when you are.",
            on_done=self._message_ready,
        )

    def _set_message_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)
        self.send_button.configure(state=state)
        self.talk_button.configure(state=state, text="TALK")
        self.preview_button.configure(state=state)

    def _speak_in_background(self, text, close_when_done=False, on_done=None):
        def worker():
            try:
                speak(text)
            except Exception as error:
                self.root.after(
                    0,
                    self._speech_failed,
                    str(error),
                    close_when_done,
                    on_done,
                )
                return
            if close_when_done:
                self.root.after(0, self.root.destroy)
            elif on_done is not None:
                self.root.after(0, on_done)
            else:
                self.root.after(0, self.status.set, "LOCAL SYSTEM  •  READY")

        threading.Thread(target=worker, daemon=True).start()

    def _speech_failed(self, message, close_when_done, on_done=None):
        self.status.set("VOICE UNAVAILABLE")
        self._append_message(
            "JARVIS",
            "I couldn't speak that reply. You can still read it here.",
        )
        if close_when_done:
            self.root.after(800, self.root.destroy)
        elif on_done is not None:
            on_done()

    def start_listening(self):
        self.talk_button.configure(state="disabled", text="LISTENING")
        self.status.set("LISTENING  •  UP TO 10 SECONDS")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        try:
            message = listen_once(max_seconds=10)
        except Exception as error:
            self.root.after(0, self._listening_failed, str(error))
            return
        self.root.after(0, self._received_speech, message)

    def _received_speech(self, message):
        self.talk_button.configure(state="normal", text="TALK")
        self.status.set("LOCAL SYSTEM  •  READY")
        if not message:
            self._append_message("JARVIS", "I didn't catch that. Press TALK and try again.")
            return

        self.entry.delete(0, "end")
        self.entry.insert(0, message)
        self.send_message()

    def _listening_failed(self, message):
        self.talk_button.configure(state="normal", text="TALK")
        self.status.set("MICROPHONE UNAVAILABLE")
        self._append_message(
            "JARVIS",
            "I couldn't use the microphone. Check that Windows allows microphone access. "
            f"Details: {message}",
        )

    def run(self):
        self.entry.focus_set()
        self.root.mainloop()


def run():
    JarvisDesktopApp().run()
