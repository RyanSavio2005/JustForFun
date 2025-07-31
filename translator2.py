import tkinter as tk
from tkinter import messagebox
from deep_translator import GoogleTranslator

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English to Korean Translator")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.setup_ui()
        self.create_ball_canvas()
        self.animate_ball()

    def setup_ui(self):
        self.input_label = tk.Label(self.root, text="Enter English:", font=("Arial", 12))
        self.input_label.pack(pady=(10, 0))

        self.input_text = tk.Text(self.root, height=4, width=50, font=("Arial", 12))
        self.input_text.pack(pady=5)

        self.translate_button = tk.Button(self.root, text="Translate", command=self.translate_text,
                                          bg="green", fg="white", font=("Arial", 12))
        self.translate_button.pack(pady=10)

        self.output_label = tk.Label(self.root, text="Korean Translation:", font=("Arial", 12))
        self.output_label.pack(pady=(10, 0))

        self.output_text = tk.Text(self.root, height=4, width=50, font=("Arial", 12), fg="blue")
        self.output_text.pack(pady=5)
        self.output_text.config(state=tk.DISABLED)

    def translate_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Needed", "Please enter some English text.")
            return
        try:
            translated = GoogleTranslator(source='en', target='ko').translate(text)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Translation Error", str(e))

    def create_ball_canvas(self):
        self.canvas = tk.Canvas(self.root, width=600, height=100, bg="black")
        self.canvas.pack(pady=10)
        # Simple dragon substitute: red oval (could be replaced with sprite)
        self.ball = self.canvas.create_oval(0, 30, 50, 80, fill="red")
        self.dx = 4  # movement speed

    def animate_ball(self):
        self.canvas.move(self.ball, self.dx, 0)
        pos = self.canvas.coords(self.ball)
        if pos[2] > 600 or pos[0] < 0:
            self.dx = -self.dx  # bounce back
        self.root.after(16, self.animate_ball)  # ~60 FPS

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

