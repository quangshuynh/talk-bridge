import threading
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox

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
    "0": "\u96f6",  # 零
    "1": "\u4e00",  # 一
    "2": "\u4e8c",  # 二
    "3": "\u4e09",  # 三
    "4": "\u56db",  # 四
    "5": "\u4e94",  # 五
    "6": "\u516d",  # 六
    "7": "\u4e03",  # 七
    "8": "\u516b",  # 八
    "9": "\u4e5d",  # 九
}


def vn_number_to_words(n):
    if n < 0:
        return str(n)

    if n < 10:
        return VI_UNITS[n]

    if n == 10:
        return "mười"

    if n < 20:
        unit = n - 10
        if unit == 0:
            return "mười"
        if unit == 5:
            return "mười lăm"
        if unit == 1:
            return "mười một"
        return "muoi " + VI_UNITS[unit]

    if n < 100:
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

    if n < 1000:
        hundreds, remainder = divmod(n, 100)
        result = VI_UNITS[hundreds] + " trăm"
        if remainder == 0:
            return result
        if remainder < 10:
            return result + " le " + vn_number_to_words(remainder)
        return result + " " + vn_number_to_words(remainder)

    if n < 1000000:
        thousands, remainder = divmod(n, 1000)
        result = vn_number_to_words(thousands) + " nghìn"
        if remainder == 0:
            return result
        return result + " " + vn_number_to_words(remainder)

    return str(n)


def number_to_words_for_lang(digits, lang):
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


def prepare_number_text(text, lang):
    def replace_plain(match):
        digits = match.group(0)
        return number_to_words_for_lang(digits, lang)

    def replace_annotated(match):
        digits = match.group(0)
        words = number_to_words_for_lang(digits, lang)
        return f"{words} ({digits})"

    plain = re.sub(r"\d+", replace_plain, text)
    annotated = re.sub(r"\d+", replace_annotated, text)
    return plain, annotated


class TalkBridgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Talk Bridge")
        self.geometry("1500x600")
        self.minsize(800, 500)
        self.configure(padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Click a button and speak near the microphone.")

        self.viet_button = None
        self.chinese_button = None

        self.viet_original = None
        self.viet_to_chinese = None
        self.viet_to_english = None

        self.chinese_original = None
        self.chinese_to_viet = None
        self.chinese_to_english = None

        self._build_ui()

    def _build_ui(self):
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

    def _clear_all(self):
        for widget in (
            self.viet_original,
            self.viet_to_chinese,
            self.viet_to_english,
            self.chinese_original,
            self.chinese_to_viet,
            self.chinese_to_english,
        ):
            widget.delete("1.0", "end")

    def start_vietnamese(self):
        self._start_recording(
            recognizer_language="vi-VN",
            source_language="vi",
            other_language="zh-cn",
            original_widget=self.viet_original,
            other_widget=self.viet_to_chinese,
            english_widget=self.viet_to_english,
            label="Vietnamese",
        )

    def start_chinese(self):
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
        recognizer_language,
        source_language,
        other_language,
        original_widget,
        other_widget,
        english_widget,
        label,
    ):
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
        recognizer_language,
        source_language,
        other_language,
        original_widget,
        other_widget,
        english_widget,
        label,
    ):
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

    def _set_status(self, message):
        def update():
            self.status_var.set(message)

        self.after(0, update)

    def _append_text(self, widget, text):
        def update():
            widget.insert("end", text + "\n")
            widget.see("end")

        self.after(0, update)

    def _disable_buttons(self):
        def update():
            self.viet_button.configure(state="disabled")
            self.chinese_button.configure(state="disabled")

        self.after(0, update)

    def _enable_buttons(self):
        def update():
            self.viet_button.configure(state="normal")
            self.chinese_button.configure(state="normal")

        self.after(0, update)

    def _show_error(self, title, message):
        def show():
            messagebox.showerror(title, message)

        self.after(0, show)


def main():
    app = TalkBridgeApp()
    app.mainloop()


if __name__ == "__main__":
    main()

