"""
kana.py

This module contains functions for converting romaji to kana (hiragana and katakana)
and setting up kana-specific autocompletion.
"""

import re
import difflib
import readline

# Mapping for romaji syllables to hiragana.
romaji_to_hiragana = {
    # Compound syllables (3 letters)
    "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
    "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
    "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
    "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
    "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
    "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
    "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",
    "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
    "ja":  "じゃ", "ju":  "じゅ", "jo":  "じょ",
    "bya": "びゃ", "byu": "びゅ", "byo": "びょ",
    "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
    # Two-letter syllables and special cases
    "tsu": "つ",
    "shi": "し",
    "chi": "ち",
    "fu": "ふ",
    # Basic vowels
    "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
    # K-group
    "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
    # S-group
    "sa": "さ", "su": "す", "se": "せ", "so": "そ",
    # T-group (note: "chi" already handled)
    "ta": "た", "te": "て", "to": "と",
    # N-group
    "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
    # H-group (note: "fu" already handled)
    "ha": "は", "hi": "ひ", "he": "へ", "ho": "ほ",
    # M-group
    "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
    # Y-group
    "ya": "や", "yu": "ゆ", "yo": "よ",
    # R-group
    "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
    # W-group and special
    "wa": "わ", "wi": "うぃ", "we": "うぇ", "wo": "を", "n": "ん",
    # Voiced consonants
    "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
    "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
    "da": "だ", "di": "ぢ", "du": "づ", "de": "で", "do": "ど",
    "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
    "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
    # Additional sounds for foreign words
    "fa": "ふぁ", "fi": "ふぃ", "fe": "ふぇ", "fo": "ふぉ",
}

# Pre-sort romaji keys by length (longest first) for greedy matching.
romaji_keys = sorted(romaji_to_hiragana.keys(), key=len, reverse=True)

def convert_romaji_to_kana(romaji):
    """
    Convert a romaji string to kana (hiragana by default).
    If the input is all uppercase, output katakana instead.
    """
    if romaji.isupper() and romaji:
        processed = romaji.lower()
        to_katakana = True
    else:
        processed = romaji.lower()
        to_katakana = False

    result = ""
    i = 0
    while i < len(processed):
        # Handle geminate consonants (double consonants -> small "っ")
        if i + 1 < len(processed) and processed[i] == processed[i + 1] and processed[i] not in "aeioun":
            result += "っ"
            i += 1
            continue
        matched = False
        for key in romaji_keys:
            if processed.startswith(key, i):
                result += romaji_to_hiragana[key]
                i += len(key)
                matched = True
                break
        if not matched:
            result += processed[i]
            i += 1

    if to_katakana:
        # Convert hiragana to katakana by shifting Unicode code points.
        result = "".join(chr(ord(ch) + 0x60) if "ぁ" <= ch <= "ん" else ch for ch in result)
    return result

def setup_autocomplete_kana(answer_candidates):
    """
    Set up autocompletion for input using kana.
    Converts the current input from romaji to kana before matching against the kana candidates.
    """
    readline.set_completer_delims('')
    def completer(text, state):
        kana_text = convert_romaji_to_kana(text)
        candidates = [word for word in answer_candidates if word.startswith(kana_text)]
        if not candidates:
            candidates = difflib.get_close_matches(kana_text, answer_candidates, n=len(answer_candidates), cutoff=0.4)
        if state < len(candidates):
            return candidates[state]
        else:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

