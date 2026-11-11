import re

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

VI_SCALES = [
    (1_000_000_000, "tỷ"),
    (1_000_000, "triệu"),
    (1000, "ngàn"),
]


def _vn_below_thousand(n: int, full: bool) -> list[str]:
    # full: a higher group was already read, so an empty hundreds place is
    # still said ("không trăm") and a lone unit gets "lẻ".
    hundreds, rest = divmod(n, 100)
    words = []
    if hundreds or full:
        words += [VI_UNITS[hundreds], "trăm"]
    if rest == 0:
        return words
    if rest < 10:
        if words:
            words.append("lẻ")
        return words + [VI_UNITS[rest]]

    tens, unit = divmod(rest, 10)
    words += ["mười"] if tens == 1 else [VI_UNITS[tens], "mươi"]
    if unit == 1 and tens > 1:
        words.append("mốt")
    elif unit == 5:
        words.append("lăm")
    elif unit:
        words.append(VI_UNITS[unit])
    return words


def vn_number_to_words(n: int) -> str:
    if n < 0:
        return "-" + vn_number_to_words(-n)
    if n >= 1_000_000_000_000:
        return str(n)
    if n < 10:
        return VI_UNITS[n]

    words = []
    for scale, name in VI_SCALES:
        group, n = divmod(n, scale)
        if group:
            words += _vn_below_thousand(group, bool(words)) + [name]
    if n:
        words += _vn_below_thousand(n, bool(words))
    return " ".join(words)


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
