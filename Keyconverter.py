import pandas as pd
from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, messagebox, simpledialog, Toplevel, Entry
from datetime import datetime, timedelta
import os
import hashlib
import base64

# Locking system configurations
LOCK_FILE = "license_info.txt"
TRIAL_PERIOD_DAYS = 90
SECRET_KEY = "SecretKey123"

def hash_date(date: str) -> str:
    """Hashes the date with a secret key."""
    hash_object = hashlib.sha256((date + SECRET_KEY).encode())
    return base64.urlsafe_b64encode(hash_object.digest()).decode()

def create_or_check_lock_file():
    """Creates or validates the lock file for the trial period."""
    return True

    # Read and validate the stored hash
    try:
        with open(LOCK_FILE, "r") as f:
            stored_hash = f.read().strip()
            for i in range(TRIAL_PERIOD_DAYS + 1):  # Allow for trial duration
                trial_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                if hash_date(trial_date) == stored_hash:
                    return True  # Valid date within the trial period
    except Exception as e:
        messagebox.showerror("Error", f"License file is invalid or corrupted: {str(e)}")
        exit()

    return False  # Trial expired

def validate_unlock_key(key):
    """Validates the provided unlock key."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    valid_key = hashlib.sha256((current_date + SECRET_KEY).encode()).hexdigest()
    return key == valid_key

def prompt_unlock():
    """Prompts the user for an unlock key."""
    key = simpledialog.askstring("Unlock", "Enter the unlock key:")
    if validate_unlock_key(key):
        messagebox.showinfo("Success", "The software has been unlocked!")
        # Extend the trial period
        with open(LOCK_FILE, "w") as f:
            f.write(hash_date(datetime.now().strftime("%Y-%m-%d")))
    else:
        messagebox.showerror("Error", "Invalid unlock key.")
        exit()

def generate_key():
    """Generates a SHA-256 key based on the current date and the secret key."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    key = hashlib.sha256((current_date + SECRET_KEY).encode()).hexdigest()
    return key

def show_key_generator():
    """Displays the key generator interface for the admin."""
    admin_window = Toplevel(root)
    admin_window.title("Key Generator")
    admin_window.geometry("400x200")

    generated_key_var = StringVar()

    # Label and Entry for displaying the key
    Label(admin_window, text="Generated Key:").pack(pady=5)
    Entry(admin_window, textvariable=generated_key_var, width=50, state="readonly").pack(pady=5)

    def on_generate_key():
        """Generates the key and updates the Entry field."""
        key = generate_key()
        generated_key_var.set(key)

    def copy_to_clipboard():
        """Copies the generated key to the clipboard."""
        key = generated_key_var.get()
        if key:
            admin_window.clipboard_clear()
            admin_window.clipboard_append(key)
            admin_window.update()  # Update the clipboard
            messagebox.showinfo("Copied", "Key copied to clipboard!", parent=admin_window)
        else:
            messagebox.showwarning("Warning", "No key to copy!", parent=admin_window)

    # Buttons for generating and copying the key
    Button(admin_window, text="Generate Key", command=on_generate_key).pack(pady=10)
    Button(admin_window, text="Copy Key", command=copy_to_clipboard).pack(pady=10)

# Mapping for English digits to Preeti font characters
english_to_preeti = {
    '0': ')',
    '1': '!',
    '2': '@',
    '3': '#',
    '4': '$',
    '5': '%',
    '6': '^',
    '7': '&',
    '8': '*',
    '9': '(',
    '.': '=',  
    ',': ','   
}

def convert_to_preeti_number(number: str) -> str:
    """Converts an English number string to Nepali digits using Preeti font."""
    return ''.join(english_to_preeti.get(char, char) for char in number)

def format_number(number: str, style: str) -> str:
    """Formats the number with commas in English or Nepali style."""
    try:
        integer_part, decimal_part = number.split(".")
        if style == "english":
            formatted = f"{int(integer_part):,}.{decimal_part}"
        elif style == "nepali":
            integer_part = integer_part[::-1]
            grouped = ','.join([integer_part[:3]] + [integer_part[i:i+2] for i in range(3, len(integer_part), 2)])
            formatted = grouped[::-1] + f".{decimal_part}"
        return formatted
    except ValueError:
        return number

def process_csv(input_file: str, output_style: str):
    """Processes the input CSV, converts to Nepali numbers in Preeti font, and saves the output in the same directory as the input."""
    try:
        # Load the CSV file
        data = pd.read_csv(input_file, header=None)

        # Convert each cell to Preeti numbers and format
        for col in data.columns:
            data[col] = data[col].apply(
                lambda x: convert_to_preeti_number(
                    format_number(f"{float(x):.2f}", output_style)
                )
                if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '', 1).isdigit())
                else x
            )

        # Determine the output directory (same as input directory)
        input_dir = os.path.dirname(input_file)
        output_file = os.path.join(input_dir, f"output_{output_style}.csv")

        # Save to the output CSV file
        data.to_csv(output_file, index=False, header=False, encoding='utf-8-sig')

        # Notify the user about the saved location
        messagebox.showinfo("Success", f"File saved successfully at {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        raise


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if file_path:
        selected_file.set(file_path)

def run_conversion():
    input_file = selected_file.get()
    output_style = format_choice.get()
    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return
    if not output_style:
        messagebox.showerror("Error", "Please select an output format.")
        return
    try:
        process_csv(input_file, output_style)
    except Exception as e:
        print(f"Debug Error: {e}")

# Before launching the GUI, check trial status
if not create_or_check_lock_file():
    if messagebox.askyesno("Trial Expired", "Your trial has expired. Do you want to unlock it?"):
        prompt_unlock()
    else:
        exit()

# Run the GUI application
root = Tk()
root.title("English to Preeti Font Number Converter")
root.geometry("500x400")

selected_file = StringVar()
format_choice = StringVar(value="english")

Label(root, text="Select Input CSV File:").pack(pady=5)
Button(root, text="Browse", command=select_file).pack(pady=5)
Label(root, textvariable=selected_file, wraplength=400).pack(pady=5)

Label(root, text="Select Output Format:").pack(pady=5)
OptionMenu(root, format_choice, "english", "nepali").pack(pady=5)

Button(root, text="Convert and Save", command=run_conversion).pack(pady=10)
Button(root, text="Key Generator", command=show_key_generator).pack(pady=10)

root.mainloop()
