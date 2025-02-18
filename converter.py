import pandas as pd
from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, messagebox, simpledialog
from datetime import datetime, timedelta
import os
import hashlib
import base64
import sys

# Initialize the Tkinter root
root = Tk()
root.withdraw()  # Hide the root window initially

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
    current_date = datetime.now()
    if not os.path.exists(LOCK_FILE):
        # No license file exists, require activation key
        messagebox.showwarning(
            "License Required",
            "No license file found. Please enter an activation key to unlock.",
            parent=root
        )
        prompt_unlock()
        return True

    try:
        with open(LOCK_FILE, "r") as f:
            stored_data = f.read().strip()
            stored_date = datetime.strptime(stored_data.split(":")[0], "%Y-%m-%d")
            stored_hash = stored_data.split(":")[1]

        # Check if stored hash matches the hash of the stored date
        if hash_date(stored_date.strftime("%Y-%m-%d")) != stored_hash:
            raise ValueError("Invalid license file hash.")

        # Check if the trial period has expired
        if (current_date - stored_date).days > TRIAL_PERIOD_DAYS:
            messagebox.showwarning(
                "Trial Expired",
                "Your trial period has expired. Please enter an activation key to continue.",
                parent=root
            )
            prompt_unlock()
            return True
    except Exception as e:
        messagebox.showerror("Error", f"License file is invalid or corrupted: {str(e)}")
        prompt_unlock()
        return True

    return False

def validate_unlock_key(key):
    """Validates the provided unlock key."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    valid_key = hashlib.sha256((current_date + SECRET_KEY).encode()).hexdigest()
    return key == valid_key

def prompt_unlock():
    """Prompts the user for an unlock key."""
    while True:
        root.attributes('-topmost', True)
        key = simpledialog.askstring("Unlock", "Enter the unlock key:")
        root.attributes('-topmost', False)
        if key is None:
            # User canceled the prompt
            exit()

        if validate_unlock_key(key):
            root.attributes('-topmost', True)
            messagebox.showinfo("Success", "The software has been unlocked!")
            root.attributes('-topmost', False)

            # Update license file with the current date and hash
            with open(LOCK_FILE, "w") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d')}:{hash_date(datetime.now().strftime('%Y-%m-%d'))}\n")
            break
        else:
            root.attributes('-topmost', True)
            messagebox.showerror("Error", "Invalid unlock key. Please try again.")
            root.attributes('-topmost', False)


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
            # Add commas every three digits
            formatted = f"{int(integer_part):,}.{decimal_part}"
        elif style == "nepali":
            # Add commas in Indian style
            integer_part = integer_part[::-1]
            grouped = ','.join([integer_part[:3]] + [integer_part[i:i+2] for i in range(3, len(integer_part), 2)])
            formatted = grouped[::-1] + f".{decimal_part}"
        return formatted
    except ValueError:
        return number  # Return the original number if it cannot be formatted

def process_csv(input_file: str, output_style: str):
    """Processes the input CSV, converts to Nepali numbers in Preeti font, and saves the output."""
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

        # Define the output file name in the same directory as the input file
        input_dir = os.path.dirname(input_file)
        output_file = os.path.join(input_dir, f"output_{output_style}.csv")

        # Save to a new CSV file
        data.to_csv(output_file, index=False, header=False, encoding='utf-8-sig')
        messagebox.showinfo("Success", f"File saved successfully at {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        raise

def select_file():
    """Opens a file dialog for the user to select the CSV file."""
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        selected_file.set(file_path)

def run_conversion():
    """Runs the CSV conversion process."""
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
        print(f"Debug Error: {e}")  # Log for debugging purposes

# Before launching the GUI, check trial status
if not create_or_check_lock_file():
    if messagebox.askyesno("Trial Expired", "Your trial has expired. Do you want to unlock it?"):
        prompt_unlock()
    else:
        exit()

# Run the GUI application
root = Tk()
root.title("English to Preeti Font Number Converter")
root.geometry("500x300")

# Variables to store file paths and format choice
selected_file = StringVar()
format_choice = StringVar(value="english")  # Set default value

# Labels and buttons
Label(root, text="Select Input CSV File:").pack(pady=5)
Button(root, text="Browse", command=select_file).pack(pady=5)
Label(root, textvariable=selected_file, wraplength=400).pack(pady=5)

Label(root, text="Select Output Format:").pack(pady=5)
OptionMenu(root, format_choice, "english", "nepali").pack(pady=5)

Button(root, text="Convert and Save", command=run_conversion).pack(pady=20)

# Run the application
root.mainloop()
