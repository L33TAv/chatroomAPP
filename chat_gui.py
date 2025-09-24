from pathlib import Path
from tkinter import Toplevel, Tk, Canvas, Entry, Text, Button, PhotoImage, END, CENTER, messagebox
import client
import queue

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ליאב\Desktop\Root\software\chatroomAPP\GUI\assets\frame1")
message_queue = queue.Queue()


def process_queue(text_area,chat_window,window):
    while not message_queue.empty():
        msg,is_user = message_queue.get_nowait()
        if is_user:
            tag_name = "my_message"
            text_area.tag_configure(tag_name, foreground="blue")
        else:
            tag_name = "other_message"
            text_area.tag_configure(tag_name, foreground="black")
        text_area.config(state="normal")
        text_area.insert(END, f"{msg}\n", ("center",tag_name))
        text_area.see(END)
        text_area.config(state="disabled")
    if client.stop_thread:
        messagebox.showerror("Server error","Connection with the server has stopped.")
        close_chat(chat_window,window)
    else:
        text_area.after(100, lambda: process_queue(text_area,chat_window,window)) 


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def auth(login_type, username, password):
    '''login_type = register/login'''
    if username == "" or password == "":
        messagebox.showwarning("Invalid Input", "Must type username and password!")
        return False
    else:
        return client.connect(login_type,username,password)

def open_chat_gui(type, username, password, window):
    if not auth(type, username, password):
        return
        
    window.withdraw()

    chat_window = Toplevel(window)
    chat_window.title(f"LiavChat - {username}")
    chat_window.geometry("1280x720")
    chat_window.configure(bg="#FFFFFF")
    chat_window.resizable(False, False)
    chat_window.images = []

    canvas = Canvas(chat_window, bg="#FFFFFF", height=720, width=1280, bd=0, highlightthickness=0)
    canvas.place(x=0, y=0)

    image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    canvas.create_image(0, 360, image=image_image_1, anchor='w')
    chat_window.images.append(image_image_1)

    canvas.create_text(
        640, 25,
        text=f"Welcome {username}!",
        fill="#7FAA4A",
        font=("Roboto Bold", 32),
        anchor="n"
    )

    text_area = Text(
        chat_window,
        bd=0,
        bg="#FFFFFF",
        fg="#000000",
        highlightthickness=1,
        font=("Roboto", 18),
        wrap="word"
    )
    text_area.tag_configure("center", justify=CENTER)
    text_area.place(x=30, y=70, width=1220, height=480)
    text_area.config(state="disabled")

    text_area.after(100, lambda: process_queue(text_area,chat_window,window))


    entry_width, entry_height, entry_x, entry_y = 1050, 71, 30, 600
    entry_msg = Entry(
        chat_window,
        bd=0,
        bg="#FFFFFF",
        fg="#000716",
        font=("Roboto", 24),
        justify=CENTER
    )
    entry_msg.place(x=entry_x, y=entry_y, width=entry_width, height=entry_height)

    button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
    button_send = Button(
        chat_window,
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: send_message(text_area, entry_msg, username),
        relief="flat",
        bg=None,
        activebackground=None
    )
    button_send.place(x=entry_x + entry_width + 5, y=entry_y, width=160, height=71)
    chat_window.images.append(button_image_2)

    Button(
        chat_window,
        text="Exit",
        font=("Roboto", 14),
        bg="#FF5555",
        fg="#FFFFFF",
        command=lambda: close_chat(chat_window, window)
    ).place(x=1160, y=10, width=100, height=40)

def send_message(text_area, entry_msg, username):
    msg = entry_msg.get()
    if msg.strip():
        client.write(username,msg)
        entry_msg.delete(0, END)

def close_chat(chat_window, window):
    client.close_chat()
    chat_window.destroy()
    window.deiconify()
