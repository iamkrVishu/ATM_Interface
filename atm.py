import json
import bcrypt
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
from tkinter import Toplevel, Label, Entry, Button, messagebox
session_data = {'last_action_time': time.time()}
fast_withdraw_limits = {}

# Function to update session activity
def update_session_activity():
    session_data['last_action_time'] = time.time()

# Function to handle automatic logout
def auto_logout(root):
    while True:
        time.sleep(1)
        if time.time() - session_data['last_action_time'] > 300:  # 5 minutes
            messagebox.showinfo("Session Timeout", "You have been logged out due to inactivity.")
            show_login_frame()
            break

# Securely hash a PIN using bcrypt
def hash_pin(pin):
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

# Verify a hashed PIN
def verify_pin(pin, hashed_pin):
    return bcrypt.checkpw(pin.encode(), hashed_pin.encode())

# Load user data from JSON file
def load_user_data():
    try:
        with open('users_data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save user data to JSON file
def save_user_data(data):
    with open('users_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Register a new user
def register_user():
    update_session_activity()
    reg_frame.tkraise()

def save_registration():
    acc_number = acc_entry_reg.get()
    name = name_entry.get()
    pin = pin_entry_reg.get()
    pet_name = pet_entry.get()
    if not (acc_number and name and pin and pet_name):
        messagebox.showerror("Error", "All fields are required!")
        return
    if len(pin) != 4 or not pin.isdigit():
        messagebox.showerror("Error", "PIN must be 4 digits!")
        return

    user_data = load_user_data()
    if acc_number in user_data:
        messagebox.showerror("Error", "Account already exists!")
        return

    user_data[acc_number] = {
        'name': name,
        'pin': hash_pin(pin),
        'balance': 2000,
        'pet_name': pet_name,
        'transactions': [],
        'creation_date': str(datetime.now()),
        'last_login': str(datetime.now())
    }
    save_user_data(user_data)
    messagebox.showinfo("Success", "Registration Successful!")
    show_login_frame()

# Login function
def login():
    update_session_activity()
    acc_number = acc_entry.get()
    pin = pin_entry.get()
    user_data = load_user_data()
    if acc_number in user_data:
        user = user_data[acc_number]
        if 'name' in user and 'pin' in user:
            if verify_pin(pin, user['pin']):
                messagebox.showinfo("Login Success", f"Welcome, {user['name']}!")
                show_main_frame(acc_number)
            else:
                messagebox.showerror("Login Failed", "Invalid PIN")
        else:
            messagebox.showerror("Login Failed", "Account data is corrupted. Please contact support.")
    else:
        messagebox.showerror("Login Failed", "Invalid Account Number")

# Show login frame
def show_login_frame():
    login_frame.tkraise()

# Show main frame
def show_main_frame(acc_number):
    update_session_activity()
    main_frame.tkraise()
    user_data = load_user_data()
    name = user_data[acc_number]['name']
    welcome_label.config(text=f"Welcome, {name}")
    main_frame.acc_number = acc_number

# Logout function
def logout():
    show_login_frame()

# Close account function
def close_account():
    acc_number = main_frame.acc_number
    user_data = load_user_data()
    if acc_number in user_data:
        del user_data[acc_number]
        save_user_data(user_data)
        messagebox.showinfo("Success", "Account closed successfully!")
        logout()

# Deposit function
def deposit():
    update_session_activity()
    dep_frame.tkraise()

def perform_deposit():
    acc_number = main_frame.acc_number
    amount = amount_entry_dep.get()
    if not amount.isdigit() or int(amount) <= 0:
        messagebox.showerror("Error", "Invalid amount!")
        return

    user_data = load_user_data()
    user_data[acc_number]['balance'] += int(amount)
    user_data[acc_number]['transactions'].append({
        'type': 'Deposit',
        'amount': amount,
        'date': str(datetime.now())
    })
    save_user_data(user_data)
    messagebox.showinfo("Success", "Deposit Successful!")
    show_main_frame(acc_number)

# Withdraw function
def withdraw():
    update_session_activity()
    with_frame.tkraise()

def perform_withdraw():
    acc_number = main_frame.acc_number
    amount = amount_entry_with.get()
    pin = pin_entry_withdraw.get()
    if not amount.isdigit() or int(amount) <= 0:
        messagebox.showerror("Error", "Invalid amount!")
        return

    user_data = load_user_data()
    if not verify_pin(pin, user_data[acc_number]['pin']):
        messagebox.showerror("Error", "Invalid PIN!")
        return

    if user_data[acc_number]['balance'] < int(amount):
        messagebox.showerror("Error", "Insufficient balance!")
        return

    user_data[acc_number]['balance'] -= int(amount)
    user_data[acc_number]['transactions'].append({
        'type': 'Withdraw',
        'amount': amount,
        'date': str(datetime.now())
    })
    save_user_data(user_data)
    messagebox.showinfo("Success", "Withdrawal Successful!")
    show_main_frame(acc_number)

# Fast withdraw function
def fast_withdraw():
    update_session_activity()
    fast_frame.tkraise()

def perform_fast_withdraw(amount):
    acc_number = main_frame.acc_number
    user_data = load_user_data()
    if acc_number not in fast_withdraw_limits:
        fast_withdraw_limits[acc_number] = []

    if len(fast_withdraw_limits[acc_number]) >= 3:
        first_withdraw_time = datetime.strptime(fast_withdraw_limits[acc_number][0], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() - first_withdraw_time < timedelta(hours=24):
            messagebox.showerror("Error", "Fast withdraw limit reached. Try again later.")
            return
        else:
            fast_withdraw_limits[acc_number].pop(0)

    if user_data[acc_number]['balance'] < amount:
        messagebox.showerror("Error", "Insufficient balance!")
        return

    user_data[acc_number]['balance'] -= amount
    user_data[acc_number]['transactions'].append({
        'type': 'Fast Withdraw',
        'amount': amount,
        'date': str(datetime.now())
    })
    fast_withdraw_limits[acc_number].append(str(datetime.now()))
    save_user_data(user_data)
    messagebox.showinfo("Success", f"₹{amount} Withdrawn Successfully!")
    show_main_frame(acc_number)

# Mini statement function
def mini_statement():
    update_session_activity()
    mini_frame.tkraise()
    acc_number = main_frame.acc_number
    user_data = load_user_data()
    transactions = user_data[acc_number]['transactions'][-5:]
    for widget in mini_frame.winfo_children():
        widget.destroy()
    ttk.Label(mini_frame, text="Mini Statement", font=("Arial", 14), foreground="#ffffff", background="#1e1e2e").pack(pady=10)
    for transaction in transactions:
        ttk.Label(mini_frame, text=f"{transaction['date']}: {transaction['type']} of ₹{transaction['amount']}", foreground="#ffffff", background="#1e1e2e", font=("Arial", 12)).pack(pady=2)
    ttk.Button(mini_frame, text="Back", command=lambda: show_main_frame(acc_number), style="Accent.TButton").pack(pady=10)

# Balance inquiry function
def balance_inquiry():
    update_session_activity()
    bal_frame.tkraise()
    acc_number = main_frame.acc_number
    user_data = load_user_data()
    balance = user_data[acc_number]['balance']
    balance_label.config(text=f"Current Balance: ₹{balance}")

# Change PIN function
def change_pin():
    update_session_activity()
    pin_frame.tkraise()

def perform_change_pin():
    acc_number = main_frame.acc_number
    old_pin = old_pin_entry.get()
    new_pin = new_pin_entry.get()
    user_data = load_user_data()
    if not verify_pin(old_pin, user_data[acc_number]['pin']):
        messagebox.showerror("Error", "Old PIN is incorrect!")
        return
    if len(new_pin) != 4 or not new_pin.isdigit():
        messagebox.showerror("Error", "New PIN must be 4 digits!")
        return

    user_data[acc_number]['pin'] = hash_pin(new_pin)
    save_user_data(user_data)
    messagebox.showinfo("Success", "PIN Changed Successfully!")
    show_main_frame(acc_number)

# Fund transfer function
def fund_transfer():
    update_session_activity()
    transfer_frame.tkraise()

def perform_transfer():
    acc_number = main_frame.acc_number
    receiver_acc = receiver_entry.get()
    amount = amount_entry.get()
    user_data = load_user_data()
    if not amount.isdigit() or int(amount) <= 0:
        messagebox.showerror("Error", "Invalid amount!")
        return

    if receiver_acc not in user_data:
        messagebox.showerror("Error", "Receiver account does not exist!")
        return

    if user_data[acc_number]['balance'] < int(amount):
        messagebox.showerror("Error", "Insufficient balance!")
        return

    user_data[acc_number]['balance'] -= int(amount)
    user_data[receiver_acc]['balance'] += int(amount)
    user_data[acc_number]['transactions'].append({
        'type': 'Transfer Out',
        'amount': amount,
        'date': str(datetime.now()),
        'to': receiver_acc
    })
    user_data[receiver_acc]['transactions'].append({
        'type': 'Transfer In',
        'amount': amount,
        'date': str(datetime.now()),
        'from': acc_number
    })
    save_user_data(user_data)
    messagebox.showinfo("Success", "Transfer Successful!")
    show_main_frame(acc_number)

def reset_pin():
    # new window for resetting the PIN
    reset_window = Toplevel()
    reset_window.title("Reset PIN")
    reset_window.geometry("300x250")
    reset_window.config(bg="#1e1e2e")

    Label(reset_window, text="Account Number", bg="#1e1e2e", fg="#ffffff", font=("Arial", 12)).pack(pady=10)
    acc_entry = Entry(reset_window)
    acc_entry.pack(pady=5)

    Label(reset_window, text="Pet Name (Security Question)", bg="#1e1e2e", fg="#ffffff", font=("Arial", 12)).pack(pady=10)
    pet_name_entry = Entry(reset_window)
    pet_name_entry.pack(pady=5)

    Label(reset_window, text="New PIN", bg="#1e1e2e", fg="#ffffff", font=("Arial", 12)).pack(pady=10)
    new_pin_entry = Entry(reset_window, show="*")
    new_pin_entry.pack(pady=5)

    def verify_and_reset():
        account_number = acc_entry.get()
        pet_name = pet_name_entry.get().lower()
        new_pin = new_pin_entry.get()

        user_data = load_user_data()
        if account_number in user_data and user_data[account_number]['pet_name'].lower() == pet_name:
            if len(new_pin) == 4 and new_pin.isdigit():
                user_data[account_number]['pin'] = hash_pin(new_pin)
                save_user_data(user_data)
                messagebox.showinfo("Success", "PIN reset successfully!")
                reset_window.destroy()
            else:
                messagebox.showerror("Error", "New PIN must be 4 digits!")
        else:
            messagebox.showerror("Error", "Invalid Account Number or Pet Name!")

    Button(reset_window, text="Reset PIN", command=verify_and_reset, bg="#8b5cf6", fg="#ffffff").pack(pady=20)

root = ThemedTk(theme="black")
root.title("ATM Interface")
root.geometry("340x400")
root.configure(bg="#1e1e2e")

style = ttk.Style()
style.configure("TFrame", background="#1e1e2e")
style.configure("TLabel", background="#1e1e2e", foreground="#ffffff")
style.configure("TButton", background="#333333", foreground="#ffffff", borderwidth=1, focusthickness=3, focuscolor='none')
style.map("TButton", background=[('active', '#555555')])
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Frames
login_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame = ttk.Frame(root, padding="10 10 10 10")
reg_frame = ttk.Frame(root, padding="10 10 10 10")
dep_frame = ttk.Frame(root, padding="10 10 10 10")
with_frame = ttk.Frame(root, padding="10 10 10 10")
fast_frame = ttk.Frame(root, padding="10 10 10 10")
mini_frame = ttk.Frame(root, padding="10 10 10 10")
bal_frame = ttk.Frame(root, padding="10 10 10 10")
pin_frame = ttk.Frame(root, padding="10 10 10 10")
transfer_frame = ttk.Frame(root, padding="10 10 10 10")

for frame in (login_frame, main_frame, reg_frame, dep_frame, with_frame, fast_frame, mini_frame, bal_frame, pin_frame, transfer_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# Login Frame
logo_image = Image.open("C:/Users/vishu/Desktop/interface/img/bank_logo.png")
logo_image = logo_image.resize((100, 100), Image.LANCZOS)
logo = ImageTk.PhotoImage(logo_image)
ttk.Label(login_frame, image=logo, background="#1e1e2e").pack(pady=10)
ttk.Label(login_frame, text="Account Number", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
acc_entry = ttk.Entry(login_frame)
acc_entry.pack(pady=5)
ttk.Label(login_frame, text="PIN", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
pin_entry = ttk.Entry(login_frame, show="*")
pin_entry.pack(pady=5)
ttk.Button(login_frame, text="Login", command=login, style="Accent.TButton").pack(pady=10)
ttk.Button(login_frame, text="Register", command=register_user, style="Accent.TButton").pack(pady=10)
ttk.Button(login_frame, text="Reset PIN", command=reset_pin, style="Accent.TButton").pack(pady=10)

style = ttk.Style()
style.configure(
    "Custom.TButton",
    font=("Arial", 12),
    padding=10,
    width=20,
    anchor="center",
    foreground="#ffffff",
    background="#1e1e2e"
)

# Main Frame
welcome_label = ttk.Label(main_frame, text="Welcome, Vishnu", font=("Arial", 16), foreground="#ffffff", background="#1e1e2e")
welcome_label.pack(pady=20)

buttons = [
    ("Deposit", deposit),
    ("Withdraw", withdraw),
    ("Fast Withdraw", fast_withdraw),
    ("Mini Statement", mini_statement),
    ("Balance Inquiry", balance_inquiry),
    ("Change PIN", change_pin),
    ("Fund Transfer", fund_transfer),
    ("Close Account", close_account),
    ("Logout", logout),
]

for text, command in buttons:
    button = ttk.Button(main_frame, text=text, command=command, style="Custom.TButton")
    button.pack(pady=8)
    
# Register Frame
ttk.Label(reg_frame, text="Full Name", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
name_entry = ttk.Entry(reg_frame)
name_entry.pack(pady=5)
ttk.Label(reg_frame, text="Account Number", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
acc_entry_reg = ttk.Entry(reg_frame)
acc_entry_reg.pack(pady=5)
ttk.Label(reg_frame, text="PIN (4 digits)", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
pin_entry_reg = ttk.Entry(reg_frame, show="*")
pin_entry_reg.pack(pady=5)
ttk.Label(reg_frame, text="Pet Name (Security Question)", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
pet_entry = ttk.Entry(reg_frame)
pet_entry.pack(pady=5)
ttk.Button(reg_frame, text="Register", command=save_registration, style="Accent.TButton").pack(pady=10)
ttk.Button(reg_frame, text="Back", command=show_login_frame, style="Accent.TButton").pack(pady=10)

# Deposit Frame
ttk.Label(dep_frame, text="Amount to Deposit", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
amount_entry_dep = ttk.Entry(dep_frame)
amount_entry_dep.pack(pady=5)
ttk.Button(dep_frame, text="Deposit", command=perform_deposit, style="Accent.TButton").pack(pady=10)
ttk.Button(dep_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Withdraw Frame
ttk.Label(with_frame, text="Amount to Withdraw", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
amount_entry_with = ttk.Entry(with_frame)
amount_entry_with.pack(pady=5)
ttk.Label(with_frame, text="Enter PIN", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
pin_entry_withdraw = ttk.Entry(with_frame, show="*")
pin_entry_withdraw.pack(pady=5)
ttk.Button(with_frame, text="Withdraw", command=perform_withdraw, style="Accent.TButton").pack(pady=10)
ttk.Button(with_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Fast Withdraw Frame
ttk.Label(fast_frame, text="Select Amount", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
ttk.Button(fast_frame, text="₹100", command=lambda: perform_fast_withdraw(100), style="Accent.TButton").pack(pady=5)
ttk.Button(fast_frame, text="₹200", command=lambda: perform_fast_withdraw(200), style="Accent.TButton").pack(pady=5)
ttk.Button(fast_frame, text="₹500", command=lambda: perform_fast_withdraw(500), style="Accent.TButton").pack(pady=5)
ttk.Button(fast_frame, text="₹1000", command=lambda: perform_fast_withdraw(1000), style="Accent.TButton").pack(pady=5)
ttk.Button(fast_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Mini Statement Frame
ttk.Label(mini_frame, text="Mini Statement", font=("Arial", 14), foreground="#ffffff", background="#1e1e2e").pack(pady=10)
ttk.Button(mini_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Balance Inquiry Frame
balance_label = ttk.Label(bal_frame, text="", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14))
balance_label.pack(pady=10)
ttk.Button(bal_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Change PIN Frame
ttk.Label(pin_frame, text="Old PIN", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
old_pin_entry = ttk.Entry(pin_frame, show="*")
old_pin_entry.pack(pady=5)
ttk.Label(pin_frame, text="New PIN (4 digits)", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
new_pin_entry = ttk.Entry(pin_frame, show="*")
new_pin_entry.pack(pady=5)
ttk.Button(pin_frame, text="Change PIN", command=perform_change_pin, style="Accent.TButton").pack(pady=10)
ttk.Button(pin_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Fund Transfer Frame
ttk.Label(transfer_frame, text="Receiver Account Number", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
receiver_entry = ttk.Entry(transfer_frame)
receiver_entry.pack(pady=5)
ttk.Label(transfer_frame, text="Amount to Transfer", foreground="#ffffff", background="#1e1e2e", font=("Arial", 14)).pack(pady=5)
amount_entry = ttk.Entry(transfer_frame)
amount_entry.pack(pady=5)
ttk.Button(transfer_frame, text="Transfer", command=perform_transfer, style="Accent.TButton").pack(pady=10)
ttk.Button(transfer_frame, text="Back", command=lambda: show_main_frame(main_frame.acc_number), style="Accent.TButton").pack(pady=10)

# Start auto-logout thread
threading.Thread(target=auto_logout, args=(root,), daemon=True).start()

show_login_frame()
root.mainloop()
