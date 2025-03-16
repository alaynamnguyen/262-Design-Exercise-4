import tkinter as tk
from tkinter import messagebox, Scrollbar
import grpc
from controller import client_login, communication, client_messages, accounts
from datetime import datetime
import sys
import argparse
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import chat_pb2
import chat_pb2_grpc
import configparser
import hashlib

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

# **Use argparse for flexible flag-based arguments**
parser = argparse.ArgumentParser(description="Start the Chat Client with optional parameters.")
parser.add_argument("--server-ip", type=str, help="Specify the server IP address")
parser.add_argument("--poll-frequency", type=int, help="Set the polling frequency in milliseconds")

args = parser.parse_args()

# **Use provided arguments or fallback to config.ini**
HOST = args.server_ip if args.server_ip else config["network"]["host"]
POLL_FREQUENCY = args.poll_frequency if args.poll_frequency else 10000  # Default to 10s polling
PORT = int(config["network"]["port"])
SERVER_ADDRESS = f"{HOST}:{PORT}"

def hash_password(password):
    """Hashes a password using SHA-256 before sending to the server."""
    return hashlib.sha256(password.encode()).hexdigest()

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Message App")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.user_exists = False
        self.client_uid = None
        self.selected_messages = set()  # Store selected messages for deletion
        self.selected_recipient = tk.StringVar()  # Store selected recipient for new messages
        self.received_message_cache = {}  # Cache for received messages (key: mid, value: message object)
        self.sent_message_cache = {}  # Cache for sent messages (key: mid, value: message object)

        self.displayed_mids = set()  # Tracks messages currently displayed in the UI
        # Counters
        self.total_unread_count = 0
        self.unfetched_unread_count = 0

        self.create_login_screen()

    def create_login_screen(self):
        """Creates the username entry screen."""
        self.clear_screen()

        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(expand=True)

        tk.Label(self.login_frame, text="Welcome", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.login_frame, text="Username:", font=("Arial", 12)).pack()

        self.username_entry = tk.Entry(self.login_frame, textvariable=self.username, font=("Arial", 12))
        self.username_entry.pack(pady=5)

        tk.Button(self.login_frame, text="Next", command=self.check_username, font=("Arial", 12)).pack(pady=10)

    def check_username(self):
        """Checks if username is valid and exists, then moves to password entry."""
        username = self.username.get().strip()

        if not username:
            messagebox.showerror("Error", "Username cannot be empty.")
            return
        if "," in username:
            messagebox.showerror("Error", "Username cannot contain commas.")
            return

        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            request = chat_pb2.LoginUsernameRequest(username=username)
            response = stub.LoginUsername(request)

        self.user_exists = response.user_exists
        self.create_password_screen()

    def create_password_screen(self):
        """Creates the password entry screen."""
        self.clear_screen()

        self.password_frame = tk.Frame(self.root)
        self.password_frame.pack(expand=True)

        title = "Welcome Back" if self.user_exists else "Create Account"
        tk.Label(self.password_frame, text=title, font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.password_frame, text="Password:", font=("Arial", 12)).pack()

        self.password_entry = tk.Entry(self.password_frame, textvariable=self.password, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)

        tk.Button(self.password_frame, text="Next", command=self.handle_password, font=("Arial", 12)).pack(pady=10)

    def handle_password(self):
        """Handles login process using gRPC."""
        password = self.password.get().strip()
        if not password:
            messagebox.showerror("Error", "Password cannot be empty.")
            return

        username = self.username.get()
        hashed_password = hash_password(password)

        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            stub = chat_pb2_grpc.ChatServiceStub(channel)
            request = chat_pb2.LoginPasswordRequest(username=username, password=hashed_password)
            
            try:
                response = stub.LoginPassword(request)
                if response.success:
                    self.client_uid = response.uid
                    messagebox.showinfo("Success", "Login successful!")
                    self.load_home_page()
                else:
                    messagebox.showerror("Error", "Incorrect password.")
            except grpc.RpcError as e:
                print("GRPC ERROR", e.details())
                messagebox.showerror("Error", "Login failed. Please check your credentials.")

    def load_home_page(self):
        """Loads the main page after successful login."""
        self.clear_screen()
        self.create_nav_buttons()
        
        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill=tk.BOTH, expand=True)
        
        self.load_received_messages()  # Default page

    def create_nav_buttons(self):
        """Creates persistent navigation buttons."""
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.TOP, pady=10)

        tk.Button(btn_frame, text="Received", command=self.load_received_messages).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Sent", command=self.load_sent_messages).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="New Message", command=self.load_new_message_page).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Account", command=self.load_delete_account_page).pack(side=tk.LEFT, padx=5)

    def load_delete_account_page(self):
        """Loads the delete account confirmation page."""
        self.clear_screen()
        self.create_nav_buttons()

        tk.Button(self.root, text="Confirm Delete Account", command=self.delete_account, bg="red", fg="black", font=("Arial", 14, "bold"), padx=20, pady=10).pack(pady=100)

    def delete_account(self):
        """Deletes the user account and closes the application."""
        response = communication.delete_account(SERVER_ADDRESS, self.client_uid)
        if response["success"]:
            messagebox.showinfo("Success", "Account successfully deleted. Closing application.")
            self.root.quit()  # Close the entire Tkinter app

    def update_character_count(self, event=None):
        """Updates the character counter and prevents exceeding the limit."""
        message_text = self.message_entry.get("1.0", tk.END).strip()

        if len(message_text) > 280:
            self.message_entry.delete("1.0", tk.END)
            self.message_entry.insert("1.0", message_text[:280])  # Trim to 280 chars

        remaining_chars = 280 - len(message_text)
        self.char_count_label.config(text=f"{remaining_chars} characters remaining")

    def load_new_message_page(self):
        """Loads the new message page with account selection and enforces a character limit on messages."""
        self.clear_screen()
        self.create_nav_buttons()

        tk.Label(self.root, text="To:", font=("Arial", 12)).pack(pady=5)

        search_frame = tk.Frame(self.root)
        search_frame.pack()

        self.search_entry = tk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="List", command=self.list_accounts).pack(side=tk.LEFT)

        self.recipient_listbox = tk.Listbox(self.root, height=5)
        self.recipient_listbox.pack(pady=5, expand=True, fill=tk.BOTH)

        scrollbar = Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recipient_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.recipient_listbox.yview)

        # Message Entry with Character Counter
        self.message_entry = tk.Text(self.root, height=5, width=50)
        self.message_entry.pack(pady=5)
        self.message_entry.bind("<KeyRelease>", self.update_character_count)  # Live character count update

        # Character Counter Label
        self.char_count_label = tk.Label(self.root, text="280 characters remaining", font=("Arial", 10), fg="gray")
        self.char_count_label.pack()

        tk.Button(self.root, text="Send", command=self.send_message).pack(pady=5)

    def list_accounts(self):
        """Fetches and displays accounts based on wildcard search."""
        wildcard = self.search_entry.get().strip() or "*"
        response = communication.list_accounts(SERVER_ADDRESS, wildcard)
        self.recipient_listbox.delete(0, tk.END)
        for account in response["accounts"]:
            self.recipient_listbox.insert(tk.END, account)

    def send_message(self):
        """Sends a message to the selected recipient with a 280-character limit."""
        selected_index = self.recipient_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a recipient.")
            return

        recipient = self.recipient_listbox.get(selected_index)
        message_text = self.message_entry.get("1.0", tk.END).strip()

        if not message_text:
            messagebox.showerror("Error", "Message cannot be empty.")
            return

        if len(message_text) > 280:
            messagebox.showerror("Error", "Message exceeds 280 characters.")
            return

        communication.send_message(SERVER_ADDRESS, self.client_uid, recipient, message_text, str(datetime.now()))
        
        messagebox.showinfo("Success", "Message sent successfully!")
        self.load_received_messages()

    def poll_for_new_messages(self):
        """Regularly fetches new messages and syncs cache with the server."""
        if self.current_page == "received":
            response = communication.get_messages(SERVER_ADDRESS, self.client_uid, True)
            mids = response["mids"]

            # Remove messages from cache that no longer exist on server
            cached_mids = set(self.received_message_cache.keys())
            server_mids = set(mids)

            for mid in cached_mids - server_mids:
                del self.received_message_cache[mid]
                self.displayed_mids.discard(mid)  # Remove from displayed tracking

            # Fetch new messages
            new_mids = [mid for mid in mids if mid not in self.received_message_cache]
            for mid in new_mids:
                self.received_message_cache[mid] = communication.get_message_by_mid(SERVER_ADDRESS, mid)

            # Update unread message counters correctly
            self.total_unread_count = sum(1 for msg in self.received_message_cache.values() if not msg["receiver_read"])
            
            # Unfetched count should track messages that are unread but not yet displayed
            self.unfetched_unread_count = sum(1 for mid in mids if mid not in self.displayed_mids and not self.received_message_cache[mid]["receiver_read"])

            self.unread_label.config(text=f"{self.total_unread_count} unread messages ({self.unfetched_unread_count} unfetched)")

        self.root.after(POLL_FREQUENCY, self.poll_for_new_messages)  # Poll every 10 seconds

    def load_received_messages(self):
        """Fetch and display only read messages. Resets fetch tracking when switching to 'Received'."""
        print("load_received_messages")
        self.clear_screen()
        self.create_nav_buttons()

        self.current_page = "received"

        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        # **Reset tracking every time the user switches to Received**
        self.displayed_mids.clear()

        # Fetch all received message IDs
        response = communication.get_messages(SERVER_ADDRESS, self.client_uid, True)
        mids = response["mids"]

        # Reset caches to ensure fresh data is stored
        self.received_message_cache.clear()

        # Fetch messages by MID and store them in the cache
        for mid in mids:
            self.received_message_cache[mid] = communication.get_message_by_mid(SERVER_ADDRESS, mid)

        # Sort messages by timestamp (latest first)
        sorted_messages = sorted(self.received_message_cache.values(), key=lambda x: x["timestamp"], reverse=True)

        # **Correctly update unread message counters**
        self.total_unread_count = sum(1 for msg in sorted_messages if not msg["receiver_read"])
        self.unfetched_unread_count = self.total_unread_count  # Ensure fetch count resets correctly

        # UI Controls for fetching unread messages
        control_frame = tk.Frame(self.home_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.unread_label = tk.Label(
            control_frame, 
            text=f"{self.total_unread_count} unread messages ({self.unfetched_unread_count} unfetched)", 
            font=("Arial", 14, "bold")
        )
        self.unread_label.pack(side=tk.LEFT, padx=5)

        self.num_messages_var = tk.IntVar(value=1)
        self.num_messages_dropdown = tk.Spinbox(
            control_frame, from_=1, to=self.unfetched_unread_count if self.unfetched_unread_count > 0 else 1,
            textvariable=self.num_messages_var, width=5
        )
        self.num_messages_dropdown.pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="Get N Unread", command=self.fetch_unread_messages, bg="blue").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Delete Selected", command=self.delete_selected_messages, bg="red").pack(side=tk.RIGHT, padx=5)

        # Scrollable Frame for Messages
        messages_container = tk.Frame(self.home_frame)
        messages_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(messages_container)
        scrollbar = Scrollbar(messages_container, orient="vertical", command=canvas.yview)

        # Ensure messages_frame expands properly inside the canvas
        self.messages_frame = tk.Frame(canvas, width=580)  # Ensure width matches the UI layout

        # Make sure the messages frame resizes properly within the canvas
        self.messages_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Ensure the messages frame expands horizontally within the canvas window
        canvas_frame = canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Ensure proper layout resizing
        self.messages_frame.update_idletasks()
        canvas.itemconfig(canvas_frame, width=messages_container.winfo_width())

        # **Show only read messages initially**
        for message in sorted_messages:
            if message["receiver_read"]:
                self.display_message(self.messages_frame, message, received=True)

        # Ensure polling continues
        self.poll_for_new_messages()

    def fetch_unread_messages(self):
        """Fetches unread messages and displays them, while ensuring proper tracking."""
        num_to_fetch = self.num_messages_var.get()

        if self.unfetched_unread_count == 0:
            messagebox.showinfo("Info", "No more unread messages.")
            return

        # **Refetch received messages to ensure up-to-date data**
        response = communication.get_messages(SERVER_ADDRESS, self.client_uid, True)
        mids = response["mids"]

        # **Ensure message cache is up-to-date before fetching unread**
        for mid in mids:
            if mid not in self.received_message_cache:
                self.received_message_cache[mid] = communication.get_message_by_mid(SERVER_ADDRESS, mid)

        # **Get only unread messages that are NOT already displayed**
        unread_messages = sorted(
            [msg for mid, msg in self.received_message_cache.items() if not msg["receiver_read"] and mid not in self.displayed_mids],
            key=lambda x: x["timestamp"]
        )

        messages_to_display = unread_messages[:num_to_fetch]

        if messages_to_display:
            for message in messages_to_display:
                self.display_message(self.messages_frame, message, received=True)
                self.displayed_mids.add(message["mid"])  # Mark message as displayed

            # **Update unfetched count only after successfully displaying messages**
            self.unfetched_unread_count = sum(1 for msg in self.received_message_cache.values() if not msg["receiver_read"] and msg["mid"] not in self.displayed_mids)

            # **Refresh UI counter to match unread messages**
            self.unread_label.config(text=f"{self.total_unread_count} unread messages ({self.unfetched_unread_count} unfetched)")

    def load_sent_messages(self):
        """Fetch and display sent messages using caching to reduce server requests."""
        self.clear_screen()
        self.create_nav_buttons()

        self.current_page = "sent"  # Track the current page to stay on Sent after deletion

        self.home_frame = tk.Frame(self.root)
        self.home_frame.pack(fill=tk.BOTH, expand=True)

        # "Delete Selected" button at the top
        control_frame = tk.Frame(self.home_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(control_frame, text="Delete Selected", command=self.delete_selected_messages, bg="red").pack(side=tk.RIGHT, padx=5)

        response = communication.get_messages(SERVER_ADDRESS, self.client_uid, False)
        mids = response["mids"]

        new_messages = []
        for mid in mids:
            if mid not in self.sent_message_cache:  # Only fetch new messages
                new_messages.append(mid)

        for mid in new_messages:
            self.sent_message_cache[mid] = communication.get_message_by_mid(SERVER_ADDRESS, mid)

        # Sort messages so newest appear first
        sorted_messages = sorted(self.sent_message_cache.values(), key=lambda x: x["timestamp"], reverse=True)

        # Scrollable Frame for Messages
        messages_container = tk.Frame(self.home_frame)
        messages_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(messages_container)
        scrollbar = Scrollbar(messages_container, orient="vertical", command=canvas.yview)
        self.messages_frame = tk.Frame(canvas)

        self.messages_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.messages_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display sorted messages
        for message in sorted_messages:
            self.display_message(self.messages_frame, message, received=False)

    def display_message(self, parent, message, received=True):
        """Displays a single message in the UI and tracks its ID for selective updates."""
        frame = tk.Frame(parent, bg="lightgray", padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)
        frame.message_mid = message["mid"]  # Store message ID for updates

        sender = "From" if received else "To"
        status = "🔴" if received and not message["receiver_read"] else ""

        header = f"{status} {sender} {message['sender_username'] if received else message['receiver_username']}\n{message['timestamp']}"
        tk.Label(frame, text=header, font=("Arial", 10), bg="lightgray").pack(anchor="w")

        tk.Label(frame, text=message["text"], font=("Arial", 12), bg="white", padx=5, pady=5).pack(fill=tk.X)

        btn_frame = tk.Frame(frame, bg="lightgray")
        btn_frame.pack(fill=tk.X)

        if received:
            mark_read_btn = tk.Button(btn_frame, text="Mark as Read", command=lambda: self.mark_message_read(message["mid"]), bg="green")

            mark_read_btn.pack(side=tk.RIGHT, padx=5)
            if message["receiver_read"]:
                mark_read_btn.config(state=tk.DISABLED)

        # Replace delete button with a checkbox
        delete_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(btn_frame, variable=delete_var, command=lambda: self.toggle_selection(message["mid"], delete_var))
        checkbox.pack(side=tk.RIGHT, padx=5)
        tk.Label(btn_frame, text="Select to Delete", font=("Arial", 10), bg="lightgray").pack(side=tk.RIGHT, padx=5)

    def toggle_selection(self, mid, var):
        """Tracks selected messages for deletion using checkboxes."""
        if var.get():
            self.selected_messages.add(mid)
        else:
            self.selected_messages.discard(mid)

    def refresh_display(self, messages):
        """Refreshes only the displayed messages without a full reload."""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        sorted_messages = sorted(messages, key=lambda x: x["timestamp"], reverse=True)

        for message in sorted_messages:
            self.display_message(self.messages_frame, message, received=(self.current_page == "received"))

    def delete_selected_messages(self):
        """Deletes selected messages from server and local cache."""
        if not self.selected_messages:
            messagebox.showerror("Error", "No messages selected for deletion.")
            return

        communication.delete_messages(SERVER_ADDRESS, self.client_uid, list(self.selected_messages))

        # Remove from local cache
        for mid in self.selected_messages:
            if self.current_page == "sent":
                self.sent_message_cache.pop(mid, None)
            else:
                self.received_message_cache.pop(mid, None)

        self.selected_messages.clear()

        # Refresh UI after deletion
        self.refresh_display(self.sent_message_cache.values() if self.current_page == "sent" else self.received_message_cache.values())

    def mark_message_read(self, mid):
        """Marks a message as read on both the client and server without refreshing everything."""
        communication.mark_message_read(SERVER_ADDRESS, mid)

        if mid in self.received_message_cache:
            self.received_message_cache[mid]["receiver_read"] = True

        # Find and update the message in the UI
        for widget in self.messages_frame.winfo_children():
            if hasattr(widget, "message_mid") and widget.message_mid == mid:
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, tk.Label) and "🔴" in sub_widget.cget("text"):
                        sub_widget.config(text=sub_widget.cget("text").replace("🔴", ""))
                    if isinstance(sub_widget, tk.Button) and sub_widget.cget("text") == "Mark as Read":
                        sub_widget.config(state=tk.DISABLED)

        # Update unread counters
        self.total_unread_count -= 1
        self.unread_label.config(text=f"{self.total_unread_count} unread messages ({self.unfetched_unread_count} unfetched)")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_content(self):
        """Clears content inside home_frame to prevent 'AttributeError'."""
        if hasattr(self, "home_frame") and isinstance(self.home_frame, tk.Frame):
            for widget in self.home_frame.winfo_children():
                widget.destroy()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(f"Starting ChatApp with server: {sys.argv[1]}:{PORT}")
    else:
        print(f"Starting ChatApp with default server from config: {HOST}:{PORT}")
    
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
