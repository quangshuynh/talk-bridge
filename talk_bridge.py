import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

import speech_recognition as sr
from googletrans import Translator


recognizer = sr.Recognizer()
translator = Translator()


class TalkBridgeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Talk Bridge")
        self.geometry("1500x600")
        self.minsize(800, 500)
        self.configure(padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Click a button and speak near the microphone.")

        self.viet_button: tk.Button
        self.chinese_button: tk.Button

        self.viet_original: scrolledtext.ScrolledText
        self.viet_to_chinese: scrolledtext.ScrolledText
        self.viet_to_english: scrolledtext.ScrolledText

        self.chinese_original: scrolledtext.ScrolledText
        self.chinese_to_viet: scrolledtext.ScrolledText
        self.chinese_to_english: scrolledtext.ScrolledText

        self._build_ui()

    def _build_ui(self) -> None:
        status_label = tk.Label(self, textvariable=self.status_var, fg="blue")
        status_label.pack(anchor="w", pady=(0, 10))

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        viet_frame = tk.LabelFrame(container, text="Vietnamese speaker")
        viet_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.viet_original = scrolledtext.ScrolledText(viet_frame, height=5, wrap="word")
        self.viet_original.pack(fill="both", expand=False, padx=5, pady=(5, 0))
        self.viet_original.insert("end", "Original Vietnamese...\n")
        self.viet_original.config(state="disabled")

        self.viet_to_chinese = scrolledtext.ScrolledText(viet_frame, height=5, wrap="word")
        self.viet_to_chinese.pack(fill="both", expand=False, padx=5, pady=(5, 0))
        self.viet_to_chinese.insert("end", "Vietnamese → Chinese...\n")
        self.viet_to_chinese.config(state="disabled")

        self.viet_to_english = scrolledtext.ScrolledText(viet_frame, height=5, wrap="word")
        self.viet_to_english.pack(fill="both", expand=True, padx=5, pady=(5, 5))
        self.viet_to_english.insert("end", "Vietnamese → English...\n")
        self.viet_to_english.config(state="disabled")

        self.viet_button = tk.Button(viet_frame, text="🎤 Speak Vietnamese", command=self.start_vietnamese)
        self.viet_button.pack(pady=(0, 5))

        chinese_frame = tk.LabelFrame(container, text="Chinese speaker")
        chinese_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.chinese_original = scrolledtext.ScrolledText(chinese_frame, height=5, wrap="word")
        self.chinese_original.pack(fill="both", expand=False, padx=5, pady=(5, 0))
        self.chinese_original.insert("end", "Original Chinese...\n")
        self.chinese_original.config(state="disabled")

        self.chinese_to_viet = scrolledtext.ScrolledText(chinese_frame, height=5, wrap="word")
        self.chinese_to_viet.pack(fill="both", expand=False, padx=5, pady=(5, 0))
        self.chinese_to_viet.insert("end", "Chinese → Vietnamese...\n")
        self.chinese_to_viet.config(state="disabled")

        self.chinese_to_english = scrolledtext.ScrolledText(chinese_frame, height=5, wrap="word")
        self.chinese_to_english.pack(fill="both", expand=True, padx=5, pady=(5, 5))
        self.chinese_to_english.insert("end", "Chinese → English...\n")
        self.chinese_to_english.config(state="disabled")

        self.chinese_button = tk.Button(chinese_frame, text="🎤 Speak Chinese", command=self.start_chinese)
        self.chinese_button.pack(pady=(0, 5))

        self.clear_button = tk.Button(self, text="Clear All", command=self._clear_all)
        self.clear_button.pack(pady=(5, 0))

    def _clear_all(self) -> None:
        self.viet_original.delete("2.0", "end")
        self.viet_to_chinese.delete("2.0", "end")
        self.viet_to_english.delete("2.0", "end")
        self.chinese_original.delete("2.0", "end")
        self.chinese_to_viet.delete("2.0", "end")
        self.chinese_to_english.delete("2.0", "end")
        self.viet_original.insert("end", "\n")
        self.viet_to_chinese.insert("end", "\n")
        self.viet_to_english.insert("end", "\n")
        self.chinese_original.insert("end", "\n")
        self.chinese_to_viet.insert("end", "\n")
        self.chinese_to_english.insert("end", "\n")

    def start_vietnamese(self) -> None:
        self.viet_original.config(state="normal")
        self.viet_to_chinese.config(state="normal")
        self.viet_to_english.config(state="normal")
        self._start_recording(
            recognizer_language="vi-VN",
            source_language="vi",
            other_language="zh-cn",
            original_widget=self.viet_original,
            other_widget=self.viet_to_chinese,
            english_widget=self.viet_to_english,
            label="Vietnamese",
        )

    def start_chinese(self) -> None:
        self.chinese_original.config(state="normal")
        self.chinese_to_viet.config(state="normal")
        self.chinese_to_english.config(state="normal")
        self._start_recording(
            recognizer_language="zh-CN",
            source_language="zh-cn",
            other_language="vi",
            original_widget=self.chinese_original,
            other_widget=self.chinese_to_viet,
            english_widget=self.chinese_to_english,
            label="Chinese",
        )

    def _start_recording(
        self,
        recognizer_language: str,
        source_language: str,
        other_language: str,
        original_widget: scrolledtext.ScrolledText,
        other_widget: scrolledtext.ScrolledText,
        english_widget: scrolledtext.ScrolledText,
        label: str,
    ) -> None:
        self._disable_buttons()
        thread = threading.Thread(
            target=self._record_and_translate,
            args=(
                recognizer_language,
                source_language,
                other_language,
                original_widget,
                other_widget,
                english_widget,
                label,
            ),
            daemon=True,
        )
        thread.start()

    def _record_and_translate(
        self,
        recognizer_language: str,
        source_language: str,
        other_language: str,
        original_widget: scrolledtext.ScrolledText,
        other_widget: scrolledtext.ScrolledText,
        english_widget: scrolledtext.ScrolledText,
        label: str,
    ) -> None:
        try:
            self._set_status(f"Listening for {label} speech...")
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except OSError as exc:
                self._set_status("No microphone found.")
                self._show_error("Microphone error", str(exc))
                return
            except sr.WaitTimeoutError:
                self._set_status("Listening timed out. Try again.")
                return

            self._set_status("Recognizing speech...")
            try:
                text = recognizer.recognize_google(audio, language=recognizer_language)
            except sr.UnknownValueError:
                self._set_status("Could not understand the audio.")
                return
            except sr.RequestError as exc:
                self._set_status("Speech service error.")
                self._show_error("Speech recognition error", str(exc))
                return

            self._append_text(original_widget, text)

            self._set_status("Translating...")
            try:
                translated_other = translator.translate(text, src=source_language, dest=other_language).text
                translated_english = translator.translate(text, src=source_language, dest="en").text
            except Exception as exc:
                self._set_status("Translation failed.")
                self._show_error("Translation error", str(exc))
                return

            self._append_text(other_widget, translated_other)
            self._append_text(english_widget, translated_english)

            self._set_status("Ready.")
        finally:
            self._enable_buttons()

    def _set_status(self, message: str) -> None:
        def update() -> None:
            self.status_var.set(message)

        self.after(0, update)

    def _append_text(self, widget: scrolledtext.ScrolledText, text: str) -> None:
        def update() -> None:
            widget.insert("end", text + "\n")
            widget.see("end")

        self.after(0, update)

    def _disable_buttons(self) -> None:
        def update() -> None:
            self.viet_button.configure(state="disabled")
            self.chinese_button.configure(state="disabled")

        self.after(0, update)

    def _enable_buttons(self) -> None:
        def update() -> None:
            self.viet_button.configure(state="normal")
            self.chinese_button.configure(state="normal")

        self.after(0, update)

    def _show_error(self, title: str, message: str) -> None:
        def show() -> None:
            messagebox.showerror(title, message)

        self.after(0, show)


def main() -> None:
    app = TalkBridgeApp()
    app.mainloop()


if __name__ == "__main__":
    main()

