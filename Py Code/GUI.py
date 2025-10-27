import tkinter as tk
#from Main import ask_password
from tkinter import simpledialog, messagebox

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Status Panel")

        self.led_states = [False] * 6  # 6 LEDs

        self.canvas = tk.Canvas(root, width=400, height=1080)
        self.canvas.pack()

        self.led_circles = []
        self.comp_labels = [None]*5

        self.draw_leds()
        self.draw_components()

    def draw_leds(self):
        for i in range(5,-1,-1):
            x = 25 + (i % 3) *   50
            y = 50 + (i // 3) * 475
            circle = self.canvas.create_oval(x, y, x+30, y+30, fill='gray')
            self.led_circles.append(circle)

    def draw_components(self):
        self.canvas.create_rectangle(20, 30, 160, 575, outline='black')
        self.canvas.create_rectangle(25, 100, 155, 475, outline='orange')
        x = 175
        y = 300
        label = tk.Label(self.root, text = f"Motion Sensor: Clear", bg='lightgray', width=20)
        label.place(x=x,y=y)
        self.comp_labels[0] = label
        for i in range(2):
            x = 175
            y = 25 + (i % 2) * 475
            label = tk.Label(self.root, text=f"Solenoid: Disengaged", bg='lightgray', width=20)
            label.place(x=x, y=y + 40)
            self.comp_labels[2*i+1] = label
            y = 0 + (i % 2) * 475
            label = tk.Label(self.root, text=f"Magnetic Sensor: Off", bg='lightgray', width=20)
            label.place(x=x, y=y+40)
            self.comp_labels[2*i+2] = label

    def update_disp(self,StateFeedback):
        if StateFeedback[7] == '1':
            self.comp_labels[0].config(text=f"Motion Sensor: Detected" ,bg='green')
        else:
            self.comp_labels[0].config(text=f"Motion Sensor: Clear" ,bg='lightgray')
        if StateFeedback[0] == '1':
            if StateFeedback[8] == '1':
                self.comp_labels[1].config(text=f"Solenoid: Engaged", bg='green')
            else:
                self.comp_labels[1].config(text=f"Solenoid: Disengaged", bg='lightgray')
            if StateFeedback[9] == '1':
                self.comp_labels[2].config(text=f"Magentic Sensor: On", bg='green')
            else:
                self.comp_labels[2].config(text=f"Magnetic Sensor: Off", bg='lightgray')
        else:
            if StateFeedback[8] == '1':
                self.comp_labels[3].config(text=f"Solenoid: Engaged", bg='green')
            else:
                self.comp_labels[3].config(text=f"Solenoid: Disengaged", bg='lightgray')
            if StateFeedback[9] == '1':
                self.comp_labels[4].config(text=f"Magentic Sensor: On", bg='green')
            else:
                self.comp_labels[4].config(text=f"Magnetic Sensor: Off", bg='lightgray')

        k = 0
        for i in range(2):
            for j in range(3):
                k += 1
                if StateFeedback[k] == '1' and j == 0:
                    self.canvas.itemconfig(self.led_circles[k-1], fill='red')
                elif StateFeedback[k] == '1' and j == 1:
                    self.canvas.itemconfig(self.led_circles[k-1], fill='orange')
                elif StateFeedback[k] == '1' and j == 2:
                    self.canvas.itemconfig(self.led_circles[k-1], fill='green')
                else:
                    self.canvas.itemconfig(self.led_circles[k - 1], fill='gray')

    def ask_password_popup(self, correct_password, callback, attempts=3):
        def attempt():
            for _ in range(attempts):
                password = simpledialog.askstring("Authentication", "Enter Password:", show='*')
                if password is None:
                    break
                if password == correct_password:
                    messagebox.showinfo("Access Granted", "Correct password.")
                    callback(True)
                    return
                else:
                    messagebox.showwarning("Incorrect", "Password is incorrect.")
            messagebox.showerror("Access Denied", "Too many failed attempts.")
            callback(False)

        self.root.after(0, attempt)

    def show_alarm_popup(self, write_callback):
        response = messagebox.askyesno("Alarm Triggered", "Abort alarm?")
        if response:
            write_callback("Abort")
