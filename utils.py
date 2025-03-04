"""
utils.py

This module contains common utility functions for the quiz project:
- Loading questions from file.
- Loading and saving persistent statistics.
- Calculating weights and merging stats.
- Formatting and displaying statistics.
"""

import json
import os
import re
import difflib
from wcwidth import wcswidth

def hide_parenthesis_info(text):
    """
    Remove any text in parentheses (and the parentheses themselves) from the given string.
    """
    return re.sub(r'\s*\([^)]*\)', '', text)

def load_questions(filename):
    """
    Load questions from the file.
    Each line should be in the format:
        prompt : answer
    Returns a list of tuples: (prompt, answer)
    """
    questions = []
    with open(filename, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            parts = line.split(" : ")
            if len(parts) != 2:
                print(f"Skipping invalid line: {line}")
                continue
            prompt = parts[0].strip()
            answer = parts[1].strip().lower()
            questions.append((prompt, answer))
    return questions

def load_persistent_stats(stats_filename):
    """
    Load overall statistics from a JSON file if it exists; otherwise return an empty dict.
    """
    if os.path.exists(stats_filename):
        with open(stats_filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_persistent_stats(stats, stats_filename):
    """
    Save the given statistics dictionary to a JSON file.
    """
    with open(stats_filename, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def get_weight(question_key, persistent_stats, multiplier=4):
    """
    Calculate a weight for a question based on historical performance.
    Uses the following strategy:
      - If the question has been asked, lower accuracy results in a higher weight.
      - For new questions, apply a default boost.
    """
    if question_key in persistent_stats and persistent_stats[question_key].get("asked", 0) > 0:
        stats = persistent_stats[question_key]
        asked = stats["asked"]
        correct = stats["correct"]
        accuracy = correct / asked
        factor = 1 + 1/(asked + 1)
        weight = 1 + (1 - accuracy) * multiplier * factor

        if (stats["score"] < 1):
            weight = 0
            stats["extra"] = "Study"


        if (stats["score"] > 200):
            weight = 0
            stats["extra"] = "Known"


    else:
        weight = 1 + multiplier * 2
    return weight

def merge_stats(persistent, session):
    """
    Merge session statistics into persistent statistics.
    """
    for key, data in session.items():
        if key not in persistent:
            persistent[key] = {"asked": 0, "correct": 0, "incorrect": 0, "score": 10}
        persistent[key]["asked"]    += data["asked"]
        persistent[key]["correct"]  += data["correct"]
        persistent[key]["incorrect"]+= data["incorrect"]
        persistent[key]["score"]    *= data["score"]
    return persistent

def pad_text(text, width):
    """
    Pad text to align properly, taking full-width characters into account.
    """
    text_width = wcswidth(text)
    return text + " " * (width - text_width)

def display_statistics(stats, title="Statistics"):
    """
    Display statistics for each question (by its visible prompt) that was asked at least once,
    showing the number of times asked and the accuracy.
    Only questions with less than 100% accuracy are shown, sorted by accuracy ascending.
    """
    filtered = []
    for question, data in stats.items():
        if data["asked"] > 0:
            accuracy = data["correct"] / data["asked"]
            if accuracy < 1.0:
                filtered.append((question, data["asked"], accuracy))
    filtered.sort(key=lambda x: x[2])
    if not filtered:
        return
    input(f"\n{title}: Press Enter to continue...")
    for question, asked, accuracy in filtered:
        print(f"{pad_text(question, 25)} {accuracy*100:5.1f}% ({asked:2d})")
    print()

def display_detailed_review(review_log):
    """
    Display a detailed review of the quiz session, including wrong answers and timing statistics.
    """
    input("\nDetailed Review: Press Enter to continue...")
    wrong = [e for e in review_log if e["result"] == "wrong"]
    if wrong:
        print("Wrong Answers:")
        for e in wrong:
            print(f"  {pad_text(e['full_prompt'], 40)} | {pad_text(e['correct_answer'], 15)} | {e['time_taken']:.2f}s")
    else:
        print("All correct!")
    print()
    slowest = sorted(review_log, key=lambda e: e["time_taken"], reverse=True)[:5]
    print("Slowest:")
    for _, e in enumerate(slowest, 1):
        print(f"  {pad_text(e['full_prompt'], 40)} {e['time_taken']:.2f}s")
    print()
    fastest = sorted(review_log, key=lambda e: e["time_taken"])[:5]
    print("Fastest:")
    for _, e in enumerate(fastest, 1):
        print(f"  {pad_text(e['full_prompt'], 40)} {e['time_taken']:.2f}s")
    print()

