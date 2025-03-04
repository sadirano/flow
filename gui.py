import tkinter as tk
from kana import convert_romaji_to_kana  # Import Kana conversion function

FONT_BOLD_SMALL = ("Arial", 12, "bold")

class AutocompleteEntry(tk.Entry):
    def __init__(self, autocomplete_list, master=None, mode="romaji", fg="white", bg="#010101", insertbackground="white", **kwargs):
        """
        AutocompleteEntry with support for both Romaji and Kana mode.
        - mode="romaji": Matches typed text directly.
        - mode="kana": Converts input to Kana before matching.
        - Matches text anywhere in words (not just from the start).
        """
        super().__init__(master, fg=fg, bg=bg, insertbackground=insertbackground, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.mode = mode  # "romaji" or "kana"
        self.var = self["textvariable"]
        if not self.var:
            self.var = self["textvariable"] = tk.StringVar()
        self.var.trace_add('write', self.changed)
        self.bind("<Tab>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)
        self.bind("<Control-w>", self.clear_text)
        self.bind("<Escape>", self.clear_text)
        self.listbox_up = False

    def clear_text(self, _=None):
        """Clears the text inside the entry."""
        self.delete(0, tk.END)
        return "break"

    def changed(self, *args):
        """Called when the user types something; updates the autocomplete suggestions."""
        raw_input = self.var.get()

        # Convert input to Kana if in Kana mode, otherwise keep as Romaji.
        search_text = convert_romaji_to_kana(raw_input) if self.mode == "kana" else raw_input.lower()

        if raw_input == '':
            if self.listbox_up:
                self.listbox.destroy()
                self.listbox_up = False
        else:
            words = self.comparison(search_text)  # Match anywhere in words
            if words:
                if not self.listbox_up:
                    self.listbox = tk.Listbox(self.master, font=FONT_BOLD_SMALL,
                                              fg=self["fg"], bg=self["bg"],
                                              relief="flat", bd=0, highlightthickness=0)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height(),
                                       width=self.winfo_width())
                    self.listbox_up = True
                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END, w)
            else:
                if self.listbox_up:
                    self.listbox.destroy()
                    self.listbox_up = False

    def selection(self, _=None):
        """Select the highlighted autocomplete suggestion and update the entry."""
        if self.listbox_up:
            self.var.set(self.listbox.get(tk.ACTIVE))
            self.listbox.destroy()
            self.listbox_up = False
            self.icursor(tk.END)
        return "break"

    def move_up(self, _=None):
        """Move selection up in the autocomplete listbox."""
        if self.listbox_up:
            if not self.listbox.curselection():
                index = '0'
            else:
                index = self.listbox.curselection()[0]
            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)
        return "break"

    def move_down(self, _=None):
        """Move selection down in the autocomplete listbox."""
        if self.listbox_up:
            if not self.listbox.curselection():
                index = '-1'
            else:
                index = self.listbox.curselection()[0]
            if int(index) < self.listbox.size() - 1:
                self.listbox.selection_clear(0, tk.END)
                index = str(int(index) + 1)
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)
        return "break"

    def comparison(self, search_text):
        """
        Find autocomplete suggestions that contain the search_text anywhere in the word.
        This ensures more flexible matching.
        """
        return [w for w in self.autocomplete_list if search_text in w]

    def set_suggestions(self, suggestions):
        """Update the autocomplete list."""
        self.autocomplete_list = sorted(suggestions)

    def set_mode(self, mode):
        """Change the input mode (romaji or kana)."""
        if mode in ["romaji", "kana"]:
            self.mode = mode
