from tkinter import *
from tkinter import ttk, messagebox
from datetime import date, datetime
import sqlite3
import os

from PIL import Image, ImageTk, ImageDraw, ImageFont

import apod_desktop
import image_lib


apod_desktop.init_apod_cache()

cached_apods = []
current_apod = None

displayed_image = None

DB_PATH = apod_desktop.image_cache_db
CACHE_FIRST_APOD_DATE = date(1995, 6, 16)
DEFAULT_IMG_SIZE = (400, 300)


def load_cached_apods():
    """
    Loads cached APOD records from the image cache DB.
    Stores records in a global variable and populates the listbox.
    Each record is a dictionary containing id, title, explanation, and file_path.
    """
    global cached_apods
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, explanation, file_path FROM apod ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        cached_apods = []
        for row in rows:
            record = {
                'id': row[0],
                'title': row[1],
                'explanation': row[2],
                'file_path': row[3]
            }
            cached_apods.append(record)
        listbox_titles.delete(0, END)
        for rec in cached_apods:
            listbox_titles.insert(END, rec['title'])
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error loading cached APODs: {e}")


def display_default_image():
    """Creates and displays a default image in the GUI's image area."""
    global displayed_image
    img = Image.new("RGB", DEFAULT_IMG_SIZE, color="lightgray")
    draw = ImageDraw.Draw(img)
    text = "No APOD Loaded"
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception as e:
        font = None

    try:
        text_size = draw.textsize(text, font=font)
    except AttributeError:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    
    text_position = ((DEFAULT_IMG_SIZE[0] - text_size[0]) // 2, (DEFAULT_IMG_SIZE[1] - text_size[1]) // 2)
    draw.text(text_position, text, fill="black", font=font)
    displayed_image = ImageTk.PhotoImage(img)
    label_image.configure(image=displayed_image)
    label_image.image = displayed_image



def display_apod_info(apod_record):
    """Displays the APOD image and explanation in the GUI.
    
    Args:
        apod_record (dict): Dictionary with APOD info (id, title, explanation, file_path)
    """
    global displayed_image, current_apod
    current_apod = apod_record
    if os.path.exists(apod_record['file_path']):
        try:
            img = Image.open(apod_record['file_path'])
            new_size = image_lib.scale_image(img.size, max_size=DEFAULT_IMG_SIZE)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            displayed_image = ImageTk.PhotoImage(img)
            label_image.configure(image=displayed_image)
            label_image.image = displayed_image
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading image: {e}")
    else:
        display_default_image()
    
    text_explanation.configure(state=NORMAL)
    text_explanation.delete("1.0", END)
    text_explanation.insert(END, apod_record.get("explanation", ""))
    text_explanation.configure(state=DISABLED)


def download_apod():
    """Downloads an APOD for the date entered in the date_entry field.
    Updates the image display and refreshes the cache list.
    """
    dt_str = date_entry.get().strip()
    if dt_str == "":
        messagebox.showwarning("Input Error", "Please enter a date in YYYY-MM-DD format.")
        return
    try:
        apod_dt = date.fromisoformat(dt_str)
    except Exception as e:
        messagebox.showerror("Date Error", f"Invalid date format: {e}")
        return

    if apod_dt < CACHE_FIRST_APOD_DATE:
        messagebox.showerror("Date Error", "APOD date cannot be before 1995-06-16")
        return
    if apod_dt > date.today():
        messagebox.showerror("Date Error", "APOD date cannot be in the future")
        return

    apod_id = apod_desktop.add_apod_to_cache(apod_dt)
    if apod_id == 0:
        messagebox.showerror("Download Error", "Failed to download APOD.")
        return
    apod_info = apod_desktop.get_apod_info(apod_id)
    if not apod_info:
        messagebox.showerror("Download Error", "Failed to retrieve APOD info from database.")
        return
    display_apod_info(apod_info)
    load_cached_apods()


def on_listbox_select(evt):
    """Callback when a title in the listbox is selected.
    Displays the corresponding APOD.
    """
    w = evt.widget
    if not w.curselection():
        return
    index = int(w.curselection()[0])
    if index < 0 or index >= len(cached_apods):
        return
    apod_record = cached_apods[index]
    display_apod_info(apod_record)


def set_as_desktop():
    """Sets the currently displayed APOD as the desktop background."""
    if current_apod and os.path.exists(current_apod.get("file_path", "")):
        result = image_lib.set_desktop_background_image(current_apod["file_path"])
        if result:
            messagebox.showinfo("Success", "Desktop background updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to update desktop background.")
    else:
        messagebox.showwarning("No Image", "No APOD image is currently loaded.")


root = Tk()
root.title("APOD Viewer")
root.geometry("800x600")
root.minsize(600, 400)

root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

frame_top = Frame(root)
frame_top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

lbl_date = Label(frame_top, text="Enter APOD Date (YYYY-MM-DD):")
lbl_date.pack(side=LEFT, padx=(0, 5))

date_entry = Entry(frame_top, width=15)
date_entry.insert(0, date.today().isoformat())
date_entry.pack(side=LEFT)

btn_download = Button(frame_top, text="Download APOD", command=download_apod)
btn_download.pack(side=LEFT, padx=5)

frame_left = Frame(root, bd=2, relief=GROOVE)
frame_left.grid(row=1, column=0, sticky="ns", padx=5, pady=5)
frame_left.columnconfigure(0, weight=1)
frame_left.rowconfigure(0, weight=1)

lbl_cache = Label(frame_left, text="Cached APOD Titles:")
lbl_cache.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

listbox_titles = Listbox(frame_left, width=30)
listbox_titles.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
listbox_titles.bind('<<ListboxSelect>>', on_listbox_select)

btn_refresh = Button(frame_left, text="Refresh Cache", command=load_cached_apods)
btn_refresh.grid(row=2, column=0, pady=5)

frame_right = Frame(root, bd=2, relief=GROOVE)
frame_right.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
frame_right.columnconfigure(0, weight=1)
frame_right.rowconfigure(0, weight=1)
frame_right.rowconfigure(1, weight=0)

label_image = Label(frame_right)
label_image.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

text_explanation = Text(frame_right, height=6, wrap=WORD, state=DISABLED)
text_explanation.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

frame_bottom = Frame(root)
frame_bottom.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

btn_set_desktop = Button(frame_bottom, text="Set as Desktop", command=set_as_desktop)
btn_set_desktop.pack()

display_default_image()
load_cached_apods()

root.mainloop()
