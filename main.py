import tkinter as tk
from app.window import AppWindow

def main():
    root = tk.Tk()
    app = AppWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
