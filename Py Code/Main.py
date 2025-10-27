from SerialComm import SerialComm
from FacialRecognition import FaceRecogniser
from GUI import GUI
import threading
import time
import tkinter as tk

Hermes = SerialComm()

def Main():
    root = tk.Tk()
    app = GUI(root)

    def backend_loop():
        result = {"auth": None}
        event = threading.Event()

        def set_auth_result(success):
            result["auth"] = success
            event.set()

        app.ask_password_popup("placeholder", set_auth_result)
        event.wait()

        if result["auth"]:
            Hermes.Write("SystemStart")
        else:
            root.quit()
            return

        while True:
            Recieved = Hermes.Read()
            if Recieved == "AlarmActive":
                root.after(0, app.show_alarm_popup, Hermes.Write)
            elif Recieved == "FacialRecognition":
                try:
                    recogniser = FaceRecogniser()
                    Message = recogniser.run_realtime_recognition()
                except Exception as e:
                    print(f"Error: {e}")
                    Message = "Error"
                finally:
                    if 'recogniser' in locals():
                        recogniser.release_resources()
                Hermes.Write(Message)
            elif is_StateCode(Recieved):
                root.after(0, app.update_disp, Recieved)

    thread = threading.Thread(target=backend_loop, daemon=True)
    thread.start()

    root.mainloop()

def ask_password(correct_password: str, attempts: int = 3):
    for _ in range(attempts):
        entered = input("Enter password: ")
        if entered == correct_password:
            print("Access granted.")
            return True
        else:
            print("Incorrect password.")
    print("Too many failed attempts.")
    return False


def is_StateCode(msg):
    return len(msg) == 10 and all(c in '01' for c in msg)


if __name__ == '__main__':
    Main()