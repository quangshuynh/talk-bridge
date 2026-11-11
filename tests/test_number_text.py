import pytest

from number_text import number_to_words_for_lang, prepare_number_text, vn_number_to_words


@pytest.mark.parametrize(
    ("n", "words"),
    [
        (0, "không"),
        (5, "năm"),
        (10, "mười"),
        (11, "mười một"),
        (15, "mười lăm"),
        (20, "hai mươi"),
        (21, "hai mươi mốt"),
        (24, "hai mươi bốn"),
        (25, "hai mươi lăm"),
        (55, "năm mươi lăm"),
        (99, "chín mươi chín"),
        (100, "một trăm"),
        (105, "một trăm lẻ năm"),
        (111, "một trăm mười một"),
        (121, "một trăm hai mươi mốt"),
        (1000, "một ngàn"),
        (1005, "một ngàn không trăm lẻ năm"),
        (1050, "một ngàn không trăm năm mươi"),
        (1500, "một ngàn năm trăm"),
        (2026, "hai ngàn không trăm hai mươi sáu"),
        (10_000, "mười ngàn"),
        (21_000, "hai mươi mốt ngàn"),
        (1_000_000, "một triệu"),
        (1_000_005, "một triệu không trăm lẻ năm"),
        (1_005_000, "một triệu không trăm lẻ năm ngàn"),
        (2_000_500, "hai triệu năm trăm"),
        (1_000_000_000, "một tỷ"),
        (999_999_999_999, "chín trăm chín mươi chín tỷ chín trăm chín mươi chín triệu "
                           "chín trăm chín mươi chín ngàn chín trăm chín mươi chín"),
    ],
)
def test_vietnamese_number_words(n, words):
    assert vn_number_to_words(n) == words


def test_vietnamese_numbers_past_the_vocabulary_stay_digits():
    # There is no word above "tỷ", so a trillion or more is left as digits.
    assert vn_number_to_words(1_000_000_000_000) == "1000000000000"


@pytest.mark.parametrize(
    ("digits", "words"),
    [
        ("0", "零"),
        ("7", "七"),
        ("10", "一零"),
        ("2026", "二零二六"),
        ("888", "八八八"),
    ],
)
def test_chinese_digits_are_read_one_by_one(digits, words):
    assert number_to_words_for_lang(digits, "zh-CN") == words


@pytest.mark.parametrize(
    ("text", "lang", "plain", "annotated"),
    [
        ("tôi có 21 quyển sách", "vi-VN", "tôi có hai mươi mốt quyển sách",
         "tôi có hai mươi mốt (21) quyển sách"),
        ("phòng 105 và 11 người", "vi-VN", "phòng một trăm lẻ năm và mười một người",
         "phòng một trăm lẻ năm (105) và mười một (11) người"),
        ("0", "vi-VN", "không", "không (0)"),
        ("007", "vi-VN", "bảy", "bảy (007)"),
        ("Giá 15.", "vi-VN", "Giá mười lăm.", "Giá mười lăm (15)."),
        ("我有3个苹果", "zh-CN", "我有三个苹果", "我有三 (3)个苹果"),
        ("房间2026号", "zh-CN", "房间二零二六号", "房间二零二六 (2026)号"),
        ("no numbers here", "vi-VN", "no numbers here", "no numbers here"),
    ],
)
def test_prepare_number_text_keeps_digits_in_parentheses(text, lang, plain, annotated):
    assert prepare_number_text(text, lang) == (plain, annotated)


def test_separators_split_a_number():
    # Each run of digits is read on its own, so "3,000" is "3" and "000".
    assert prepare_number_text("3,000", "vi-VN") == ("ba,không", "ba (3),không (000)")
