# button1 - login, button2 - register

from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage,Label
from tkinter import messagebox
import gui.chat_gui as chat_gui

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\ליאב\Desktop\Root\software\chatroomAPP\gui\assets\frame0")


def only_alphabet(new_value):
    if  new_value!="" and not new_value.isalnum():
        messagebox.showwarning("Invalid Input", "Only letters and numbers are allowed!")
        return False
    return True


def no_spaces(new_value):
    if  " " in new_value:
        messagebox.showwarning("Invalid Input", "Spaces are not allowed!")
        return False
    return True


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.title("LiavChat") 
window.geometry("1280x720")
window.configure(bg = "#FFFFFF")
vcmd_username = (window.register(only_alphabet), "%P") 
vcmd_password = (window.register(no_spaces), "%P") 

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 720,
    width = 1280,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    902.0,
    378.0,
    image=image_image_1
)

canvas.create_text(
    900.0,
    140.0,
    anchor="center",
    text="Username",
    fill="#69C5FF",
    font=("Roboto Bold", 62 * -1)
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    900.0,
    206.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Roboto", 32),
    justify="center",
    validate="key",
    validatecommand=vcmd_username  

)
entry_1.place(
    x=615.0,
    y=170.0,
    width=570.0,
    height=71.0
)

canvas.create_text(
    904.0,
    375.0,
    anchor="center",
    text="Password",
    fill="#69C5FF",
    font=("Roboto Bold", 62 * -1)
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    904.0,
    446.5,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0,
    font=("Roboto", 32),
    justify="center",
    show="*",
    validate="key",
    validatecommand=vcmd_password
)
entry_2.place(
    x=619.0,
    y=410.0,
    width=570.0,
    height=71.0
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: chat_gui.open_chat_gui("register",entry_1.get(), entry_2.get(), window),
    relief="flat"
)
button_1.place(
    x=665.0,
    y=558.0,
    width=204.0,
    height=78.0
)

button_image_hover_1 = PhotoImage(
    file=relative_to_assets("button_hover_1.png"))

def button_1_hover(e):
    button_1.config(
        image=button_image_hover_1
    )
def button_1_leave(e):
    button_1.config(
        image=button_image_1
    )

button_1.bind('<Enter>', button_1_hover)
button_1.bind('<Leave>', button_1_leave)


button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: chat_gui.open_chat_gui("login",entry_1.get(), entry_2.get(), window),
    relief="flat"
)
button_2.place(
    x=944.0,
    y=558.0,
    width=203.0,
    height=78.0
)

button_image_hover_2 = PhotoImage(
    file=relative_to_assets("button_hover_2.png"))

def button_2_hover(e):
    button_2.config(
        image=button_image_hover_2
    )
def button_2_leave(e):
    button_2.config(
        image=button_image_2
    )

button_2.bind('<Enter>', button_2_hover)
button_2.bind('<Leave>', button_2_leave)


image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    262.0,
    360.0,
    image=image_image_2
)
window.resizable(False, False)
window.mainloop()
