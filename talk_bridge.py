import threading
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, scrolledtext

import speech_recognition as sr
from googletrans import Translator


recognizer = sr.Recognizer()
translator = Translator()


VI_UNITS = [
    "không",
    "một",
    "hai",
    "ba",
    "bốn",
    "năm",
    "sáu",
    "bảy",
    "tám",
    "chín",
]

ZH_DIGITS = {
    "0": "零",
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
}


def vn_number_to_words(n: int) -> str:
    if n < 0:
        return "-" + vn_number_to_words(-n)

    if n < 10:
        return VI_UNITS[n]
    elif n == 10:
        return "mười"
    elif n < 20:
        unit = n - 10
        if unit == 0:
            return "mười"
        if unit == 5:
            return "mười lăm"
        if unit == 1:
            return "mười mot"
        return "mười " + VI_UNITS[unit]
    elif n < 100:
        tens, unit = divmod(n, 10)
        tens_part = VI_UNITS[tens] + " mười"
        if unit == 0:
            return tens_part
        if unit == 1:
            unit_word = "một"
        elif unit == 5:
            unit_word = "lăm"
        else:
            unit_word = VI_UNITS[unit]
        return tens_part + " " + unit_word
    elif n < 1000:
        hundreds, remainder = divmod(n, 100)
        result = VI_UNITS[hundreds] + " trăm"
        if remainder == 0:
            return result
        if remainder < 10:
            return result + " le " + vn_number_to_words(remainder)
        return result + " " + vn_number_to_words(remainder)
    elif n < 1_000_000:
        thousands, remainder = divmod(n, 1000)
        result = vn_number_to_words(thousands) + " ngàn"
        if remainder == 0:
            return result
        return result + " " + vn_number_to_words(remainder)
    elif n < 1_000_000_000:
        millions, remainder = divmod(n, 1_000_000)
        result = vn_number_to_words(millions) + " triệu"
        if remainder == 0:
            return result
        return result + " " + vn_number_to_words(remainder)
    elif n < 1_000_000_000_000:
        billions, remainder = divmod(n, 1_000_000_000)
        result = vn_number_to_words(billions) + " tỷ"
        if remainder == 0:
            return result
        return result + " " + vn_number_to_words(remainder)

    return str(n)


def number_to_words_for_lang(digits: str, lang: str) -> str:
    if not digits:
        return digits

    if lang.startswith("vi"):
        try:
            n = int(digits)
        except ValueError:
            return digits
        return vn_number_to_words(n)

    if lang.startswith("zh"):
        return "".join(ZH_DIGITS.get(ch, ch) for ch in digits)

    return digits


def prepare_number_text(text: str, lang: str) -> tuple[str, str]:
    """Return (plain_words, annotated_words_with_digits)."""

    def replace_plain(match: re.Match) -> str:
        digits = match.group(0)
        return number_to_words_for_lang(digits, lang)

    def replace_annotated(match: re.Match) -> str:
        digits = match.group(0)
        words = number_to_words_for_lang(digits, lang)
        return f"{words} ({digits})"

    plain = re.sub(r"\d+", replace_plain, text)
    annotated = re.sub(r"\d+", replace_annotated, text)
    return plain, annotated


class TalkBridgeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Talk Bridge")
        self.geometry("1500x600")
        self.minsize(800, 500)
        self.configure(padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Click a button and speak near the microphone.")

        self.viet_button: tk.Button | None = None
        self.chinese_button: tk.Button | None = None

        self.viet_original: scrolledtext.ScrolledText | None = None
        self.viet_to_chinese: scrolledtext.ScrolledText | None = None
        self.viet_to_english: scrolledtext.ScrolledText | None = None

        self.chinese_original: scrolledtext.ScrolledText | None = None
        self.chinese_to_viet: scrolledtext.ScrolledText | None = None
        self.chinese_to_english: scrolledtext.ScrolledText | None = None

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

        self.viet_to_chinese = scrolledtext.ScrolledText(viet_frame, height=5, wrap="word")
        self.viet_to_chinese.pack(fill="both", expand=False, padx=5, pady=(5, 0))

        self.viet_to_english = scrolledtext.ScrolledText(viet_frame, height=5, wrap="word")
        self.viet_to_english.pack(fill="both", expand=True, padx=5, pady=(5, 5))

        self.viet_button = tk.Button(viet_frame, text="Speak Vietnamese", command=self.start_vietnamese)
        self.viet_button.pack(pady=(0, 5))

        chinese_frame = tk.LabelFrame(container, text="Chinese speaker")
        chinese_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.chinese_original = scrolledtext.ScrolledText(chinese_frame, height=5, wrap="word")
        self.chinese_original.pack(fill="both", expand=False, padx=5, pady=(5, 0))

        self.chinese_to_viet = scrolledtext.ScrolledText(chinese_frame, height=5, wrap="word")
        self.chinese_to_viet.pack(fill="both", expand=False, padx=5, pady=(5, 0))

        self.chinese_to_english = scrolledtext.ScrolledText(chinese_frame, height=5, wrap="word")
        self.chinese_to_english.pack(fill="both", expand=True, padx=5, pady=(5, 5))

        self.chinese_button = tk.Button(chinese_frame, text="Speak Chinese", command=self.start_chinese)
        self.chinese_button.pack(pady=(0, 5))

        clear_button = tk.Button(self, text="Clear All", command=self._clear_all)
        clear_button.pack(pady=(5, 0))

    def _clear_all(self) -> None:
        for widget in (
            self.viet_original,
            self.viet_to_chinese,
            self.viet_to_english,
            self.chinese_original,
            self.chinese_to_viet,
            self.chinese_to_english,
        ):
            if widget is not None:
                widget.delete("1.0", "end")

    def start_vietnamese(self) -> None:
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
        original_widget: scrolledtext.ScrolledText | None,
        other_widget: scrolledtext.ScrolledText | None,
        english_widget: scrolledtext.ScrolledText | None,
        label: str,
    ) -> None:
        if original_widget is None or other_widget is None or english_widget is None:
            return

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

            plain_text, display_text = prepare_number_text(text, source_language)
            self._append_text(original_widget, display_text)

            self._set_status("Translating...")
            try:
                translated_other = translator.translate(plain_text, src=source_language, dest=other_language).text
                translated_english = translator.translate(plain_text, src=source_language, dest="en").text
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
            if self.viet_button is not None:
                self.viet_button.configure(state="disabled")
            if self.chinese_button is not None:
                self.chinese_button.configure(state="disabled")

        self.after(0, update)

    def _enable_buttons(self) -> None:
        def update() -> None:
            if self.viet_button is not None:
                self.viet_button.configure(state="normal")
            if self.chinese_button is not None:
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

