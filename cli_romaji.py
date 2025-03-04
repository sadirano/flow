"""
cli_romaji.py

Command-line quiz application in Romaji mode.
Uses functions from utils.py and standard readline auto-completion.
"""

import sys, os, readline, re, difflib, time
from utils import (hide_parenthesis_info, load_questions, load_persistent_stats,
                   save_persistent_stats, get_weight, merge_stats, display_statistics,
                   display_detailed_review, pad_text)

def setup_autocomplete(answer_candidates):
    """
    Set up simple autocompletion for CLI using the answer candidates.
    """
    readline.set_completer_delims('')
    def completer(text, state):
        candidates = [word for word in answer_candidates if text.lower() in word.lower()]
        if not candidates:
            candidates = difflib.get_close_matches(text, answer_candidates, n=len(answer_candidates), cutoff=0.4)
        if state < len(candidates):
            return candidates[state]
        else:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

def quiz(questions, num_questions, persistent_stats, answer_candidates):
    """
    Run the CLI quiz in Romaji mode.
    """
    session_stats = {}
    unique_visible = {hide_parenthesis_info(prompt) for (prompt, _) in questions}
    for vis in unique_visible:
        session_stats[vis] = {"asked": 0, "correct": 0, "incorrect": 0, "score": 1}
    review_log = []
    weights = [get_weight(hide_parenthesis_info(prompt), persistent_stats) for (prompt, _) in questions]

    for _ in range(num_questions):
        prompt, correct_answer = __import__("random").choices(questions, weights=weights, k=1)[0]
        visible_prompt = hide_parenthesis_info(prompt)
        session_stats[visible_prompt]["asked"] += 1

        start_time = time.time()
        user_input = input(f"{visible_prompt} : ").strip().lower()
        end_time = time.time()
        time_taken = end_time - start_time

        if user_input and user_input == correct_answer:
            print(f"\033[92mCorrect! {prompt} means \"{correct_answer}\"\033[0m")
            session_stats[visible_prompt]["correct"] += 1
            session_stats[visible_prompt]["score"] *= 1.1
            result = "correct"
        else:
            suggestion = difflib.get_close_matches(user_input, answer_candidates, n=1, cutoff=0.6)
            if suggestion and suggestion[0] == correct_answer:
                print("Almost correct! It seems your spelling was off.")
            print(f"\033[91mWrong! {prompt} means \"{correct_answer}\"\033[0m")
            session_stats[visible_prompt]["incorrect"] += 1
            session_stats[visible_prompt]["score"] *= 0.5
            result = "wrong"

        review_log.append({
            "visible_prompt": visible_prompt,
            "full_prompt": prompt,
            "user_answer": user_input,
            "correct_answer": correct_answer,
            "time_taken": time_taken,
            "result": result
        })
    return session_stats, review_log

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"File '{filename}' not found. Please check the file name.")
            return
    else:
        filename = input("Enter the quiz file name: ").strip()

    questions = load_questions(filename)
    if not questions:
        print("No data loaded. Please check your file.")
        return

    base, _ = os.path.splitext(filename)
    stats_filename = f"{base}.stats.json"
    answer_candidates = list({answer for _, answer in questions})
    setup_autocomplete(answer_candidates)

    try:
        num_questions = int(input("How many questions do you want? "))
    except ValueError:
        print("Invalid number. Exiting.")
        return

    persistent_stats = load_persistent_stats(stats_filename)
    session_stats, review_log = quiz(questions, num_questions, persistent_stats, answer_candidates)
    display_statistics(session_stats, title="Session Statistics")
    persistent_stats = merge_stats(persistent_stats, session_stats)
    save_persistent_stats(persistent_stats, stats_filename)
    display_statistics(persistent_stats, title="Overall Statistics (Persisted)")
    display_detailed_review(review_log)
    
    # Restart the quiz after finishing.
    main()

if __name__ == "__main__":
    main()

