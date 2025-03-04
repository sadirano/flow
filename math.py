"""
quiz_app.py

This module contains the main GUI quiz application.
It uses the utilities from utils.py and gui components from gui.py.
It supports both romaji and kana modes.
"""

import tkinter as tk
import random, time, threading, winsound, difflib, os, sys
from utils_math import (hide_parenthesis_info, load_questions, load_persistent_stats,
                   save_persistent_stats, get_weight, merge_stats)
from gui import AutocompleteEntry, FONT_BOLD_SMALL
from kana import convert_romaji_to_kana

# Configuration constants
LOOP_TIME = 90000 * 1000  # milliseconds between spawning new quiz windows
FACTOR_FAIL = 0.75
FACTOR_SUCCESS = 1.5

class QuizApplication:
    def __init__(self, filename, mode="romaji"):
        self.mode = mode  # "romaji" or "kana"
        self.filename = filename
        self.questions = load_questions(filename)
        if not self.questions:
            raise ValueError("No questions loaded. Check your file.")
        base, _ = os.path.splitext(filename)
        self.stats_filename = f"{base}.stats.json"
        # For GUI, answer candidates are used in autocomplete.
        self.answer_candidates = list({answer for (_, answer) in self.questions})
        # In kana mode, pre-convert candidates.
        if self.mode == "kana":
            self.answer_candidates = [convert_romaji_to_kana(ans) for ans in self.answer_candidates]
        self.persistent_stats = load_persistent_stats(self.stats_filename)
        self.session_stats = {}
        unique_visible = {hide_parenthesis_info(prompt) for (prompt, _) in self.questions}
        for vis in unique_visible:
            self.session_stats[vis] = {"asked": 0, "correct": 0, "incorrect": 0, "score": 1}
        self.weights = [get_weight(hide_parenthesis_info(prompt), self.persistent_stats) for (prompt, _) in self.questions]
        self.review_log = []
        self.open_entries = []
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window.
        self.loop_time = LOOP_TIME

    def schedule_quiz(self):
        for _ in range(10):
            if len(self.open_entries) >= 10:
                break
            prompt, correct_answer = random.choices(self.questions, weights=self.weights, k=1)[0]
            visible_prompt = hide_parenthesis_info(prompt)
            self.session_stats[visible_prompt]["asked"] += 1

            def callback(result, prompt=prompt, correct_answer=correct_answer):
                visible_prompt = hide_parenthesis_info(prompt)
                
                # Convert the correct answer to Kana if in Kana mode
                correct_kana = convert_romaji_to_kana(correct_answer) if self.mode == "kana" else correct_answer

                message = f"{prompt} reads as {correct_kana}" if self.mode == "kana" else f"{prompt} means {correct_answer}"
                
                if result.get("result") == "correct":
                    self.session_stats[visible_prompt]["correct"] += 1
                    self.session_stats[visible_prompt]["score"] *= FACTOR_SUCCESS
                    print(f"\033[92mCorrect! {message}\033[0m")
                    if len(self.open_entries) == 0:
                        self.root.after(10000, self.schedule_quiz)
                else:
                    self.session_stats[visible_prompt]["incorrect"] += 1
                    self.session_stats[visible_prompt]["score"] *= FACTOR_FAIL
                    suggestion = difflib.get_close_matches(result.get("user_answer", ""), self.answer_candidates, n=1, cutoff=0.6)
                    if suggestion and suggestion[0] == correct_answer:
                        print("Almost correct! (spelling issue)")
                    print(f"\033[91mWrong!   {message}\033[0m")
                    self.schedule_quiz()

                self.review_log.append({
                    "visible_prompt": visible_prompt,
                    "full_prompt": prompt,
                    "user_answer": result.get("user_answer", ""),
                    "correct_answer": correct_kana,  # Store Kana version in the review log
                    "time_taken": result.get("time_taken", 0),
                    "result": result.get("result", "wrong")
                })
            
            self.gui_ask_question_async(prompt, correct_answer, self.answer_candidates, callback)
        self.root.after(self.loop_time, self.schedule_quiz)

    def gui_ask_question_async(self, prompt, correct_answer, autocomplete_list, callback):
        result = {}
        growth_count = 0
        max_growth = 0
        growth_interval = 30000  # 30 seconds.
        font_increase = 2
        initial_font_size = 24

        quiz = tk.Toplevel(self.root)
        quiz.overrideredirect(True)
        quiz.attributes("-topmost", True)
        trans_color = "#010101"

        screen_width = quiz.winfo_screenwidth()
        screen_height = quiz.winfo_screenheight()
        win_width, win_height = 150, 100
        x = random.randint(0, max(0, screen_width - win_width))
        y = random.randint(0, max(0, screen_height - win_height))
        quiz.geometry(f"{win_width}x{win_height}+{x}+{y}")

        current_font_size = initial_font_size
        font_bold_large = ("Arial", current_font_size, "bold")
        visible_prompt = hide_parenthesis_info(prompt)
        question_label = tk.Label(quiz, text=visible_prompt + ' ●', font=font_bold_large, fg="white", bg=trans_color)
        question_label.pack(pady=10)

        entry = AutocompleteEntry(autocomplete_list, quiz, mode=self.mode, font=FONT_BOLD_SMALL,
                          fg="white", bg=trans_color, relief="flat", insertbackground="white", width=20)
        self.open_entries.append(entry)
        entry.bind("<Destroy>", lambda _, w=entry: self.open_entries.remove(w))
        entry.bind("<Control-Tab>", lambda _: self.focus_next_quiz())
        entry.bind("<Control-Shift-Tab>", lambda _: self.focus_previous_quiz())
        entry.set_suggestions(autocomplete_list)
        entry.pack(pady=5)
        entry.focus_set()
        entry.focus_force()

        start_time = time.time()

        def update_font():
            nonlocal current_font_size, growth_count
            if growth_count >= max_growth:
                return
            growth_count += 1
            current_font_size += font_increase
            new_font = ("Arial", current_font_size, "bold")
            question_label.config(font=new_font)
            quiz.after(growth_interval, update_font)
        quiz.after(growth_interval, update_font)

        def check_answer(_):
            user_ans = entry.get().strip().lower()
            end_time = time.time()
            time_taken = end_time - start_time

            # In kana mode, convert both user answer and correct answer.
            if self.mode == "kana":
                user_ans_conv = convert_romaji_to_kana(user_ans)
                correct_ans_conv = convert_romaji_to_kana(correct_answer)
            else:
                user_ans_conv = user_ans
                correct_ans_conv = correct_answer

            if user_ans_conv and user_ans_conv == correct_ans_conv:
                result["result"] = "correct"
            else:
                result["result"] = "wrong"
                winsound.PlaySound("wrong-choice.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
            result["user_answer"] = user_ans_conv
            result["time_taken"] = time_taken
            self.focus_next_quiz()
            quiz.destroy()
            callback(result)
        quiz.bind("<Return>", check_answer)

    def focus_next_quiz(self):
        if self.open_entries:
            try:
                current_focus = self.root.focus_get()
                idx = self.open_entries.index(current_focus)
            except ValueError:
                idx = 0
            next_idx = (idx + 1) % len(self.open_entries)
            self.open_entries[next_idx].focus_force()
        return "break"

    def focus_previous_quiz(self):
        if self.open_entries:
            try:
                current_focus = self.root.focus_get()
                idx = self.open_entries.index(current_focus)
            except ValueError:
                idx = 0
            prev_idx = (idx - 1) % len(self.open_entries)
            self.open_entries[prev_idx].focus_force()
        return "break"

    def end_session(self):
        persistent = merge_stats(self.persistent_stats, self.session_stats)
        save_persistent_stats(persistent, self.stats_filename)
        print("Session ended.")
        self.root.quit()

    def wait_for_console(self):
        input("Press Enter in the console to end the session...\n")
        self.root.after(0, self.end_session)

    def run(self):
        self.schedule_quiz()
        threading.Thread(target=self.wait_for_console, daemon=True).start()
        self.root.mainloop()

if __name__ == "__main__":
    # Usage: python quiz_app.py <quiz_file> [romaji|kana]
    if len(sys.argv) < 2:
        filename = input("Enter the quiz file name: ").strip()
        mode = "romaji"
    else:
        filename = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 else "romaji"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
    else:
        app = QuizApplication(filename, mode=mode)
        app.run()

