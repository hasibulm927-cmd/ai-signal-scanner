import tkinter as tk
import subprocess

root = tk.Tk()

root.title("AI SIGNAL")
root.geometry("300x180+1000+100")
root.attributes("-topmost", True)

root.configure(bg="black")

label = tk.Label(
    root,
    text="Loading...",
    fg="lime",
    bg="black",
    font=("Arial", 18, "bold")
)

label.pack(expand=True)

def update_signal():

    output = subprocess.getoutput("python backend\\scanner.py")

    best = "NO SIGNAL"

    for line in output.splitlines():

        if "Signal: BUY" in line or "Signal: SELL" in line:

            best = line
            break

    label.config(text=best[:120])

    root.after(15000, update_signal)

update_signal()

root.mainloop()