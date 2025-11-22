import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import asyncio
import threading
import os
import json
import logging
import re
from pyrogram.errors import FloodWait
from core.client import TgClient
from core.config import Config
from core.uploader import Uploader
from utils.status_utils import get_readable_file_size

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Setup console logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TG Upload V2")
        self.geometry("800x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)

        # --- Login Section ---
        self.login_frame = ctk.CTkFrame(self.main_frame)
        self.login_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.login_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.login_frame, text="API ID:").grid(row=0, column=0, padx=10, pady=5)
        self.api_id_entry = ctk.CTkEntry(self.login_frame)
        self.api_id_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.login_frame, text="API Hash:").grid(row=1, column=0, padx=10, pady=5)
        self.api_hash_entry = ctk.CTkEntry(self.login_frame)
        self.api_hash_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.login_frame, text="Bot Token:").grid(row=2, column=0, padx=10, pady=5)
        self.bot_token_entry = ctk.CTkEntry(self.login_frame)
        self.bot_token_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.login_btn = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Upload Section ---
        self.upload_frame = ctk.CTkFrame(self.main_frame)
        self.upload_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.upload_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.upload_frame, text="File/Folder:").grid(row=0, column=0, padx=10, pady=5)
        self.path_entry = ctk.CTkEntry(self.upload_frame)
        self.path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.browse_file_btn = ctk.CTkButton(self.upload_frame, text="File", width=60, command=self.browse_file)
        self.browse_file_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.browse_folder_btn = ctk.CTkButton(self.upload_frame, text="Folder", width=60, command=self.browse_folder)
        self.browse_folder_btn.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(self.upload_frame, text="Chat ID:").grid(row=1, column=0, padx=10, pady=5)
        self.chat_id_entry = ctk.CTkEntry(self.upload_frame)
        self.chat_id_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.topic_var = ctk.BooleanVar(value=False)
        self.topic_chk = ctk.CTkCheckBox(self.upload_frame, text="Upload to Topic", variable=self.topic_var, command=self.toggle_topic)
        self.topic_chk.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.topic_id_entry = ctk.CTkEntry(self.upload_frame)
        self.topic_id_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        self.topic_btn_frame = ctk.CTkFrame(self.upload_frame, fg_color="transparent")
        self.topic_btn_frame.grid(row=2, column=2, padx=5, pady=5)
        
        self.topic_help_btn = ctk.CTkButton(self.topic_btn_frame, text="?", width=30, command=self.show_topic_help)
        self.topic_help_btn.pack(side="left", padx=2)
        
        self.parse_link_btn = ctk.CTkButton(self.topic_btn_frame, text="Parse", width=40, command=self.parse_link)
        self.parse_link_btn.pack(side="left", padx=2)
        
        self.toggle_topic() # Initialize state

        ctk.CTkLabel(self.upload_frame, text="Caption:").grid(row=3, column=0, padx=10, pady=5)
        self.caption_entry = ctk.CTkEntry(self.upload_frame)
        self.caption_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.caption_entry.insert(0, "{filename} - {size}")
        
        self.caption_help_btn = ctk.CTkButton(self.upload_frame, text="?", width=30, command=self.show_caption_help)
        self.caption_help_btn.grid(row=3, column=2, padx=5, pady=5)

        self.as_doc_var = ctk.BooleanVar()
        self.as_doc_chk = ctk.CTkCheckBox(self.upload_frame, text="As Document", variable=self.as_doc_var)
        self.as_doc_chk.grid(row=4, column=0, columnspan=2, pady=5, sticky="w", padx=10)

        self.start_btn = ctk.CTkButton(self.upload_frame, text="Start Upload", command=self.start_upload)
        self.start_btn.grid(row=5, column=0, pady=10, padx=10)
        
        self.cancel_btn = ctk.CTkButton(self.upload_frame, text="Cancel", command=self.cancel_upload, fg_color="red")
        self.cancel_btn.grid(row=5, column=1, pady=10, padx=10, sticky="w")
        self.cancel_btn.configure(state="disabled")

        self.progress_bar = ctk.CTkProgressBar(self.upload_frame)
        self.progress_bar.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.upload_frame, text="Ready")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

        self.log_box = ctk.CTkTextbox(self.upload_frame, height=150)
        self.log_box.grid(row=8, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.uploader = None
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()
        
        # Load credentials at startup
        self.load_credentials()

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def log(self, message):
        self.after(0, lambda: self._log_impl(message))

    def _log_impl(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def toggle_topic(self):
        state = "normal" if self.topic_var.get() else "disabled"
        self.topic_id_entry.configure(state=state)
        self.topic_help_btn.configure(state=state)
        self.parse_link_btn.configure(state=state)

    def show_caption_help(self):
        # Create a dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Caption Variables")
        dialog.geometry("300x250")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Click to add to caption:", font=("Arial", 12, "bold")).pack(pady=10)
        
        variables = [
            ("{filename}", "File name"),
            ("{size}", "File size"),
        ]
        
        def add_variable(var):
            current = self.caption_entry.get()
            if current and not current.endswith(" - "):
                self.caption_entry.insert("end", " - ")
            self.caption_entry.insert("end", var)
            dialog.destroy()
        
        for var, description in variables:
            btn = ctk.CTkButton(
                dialog, 
                text=f"{var}\n{description}",
                command=lambda v=var: add_variable(v),
                height=50
            )
            btn.pack(pady=5, padx=20, fill="x")
        
        close_btn = ctk.CTkButton(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=10)

    def show_topic_help(self):
        messagebox.showinfo("How to get Topic ID", 
                            "Link format: https://t.me/c/2129051908/11053/11054\n\n"
                            "1. Chat ID: -1002129051908\n"
                            "   (Take the first number '2129051908' and add '-100' prefix)\n\n"
                            "2. Topic ID: 11053\n"
                            "   (Take the second number)\n\n"
                            "Tip: Use the 'Parse' button to auto-fill these!")

    def parse_link(self):
        link = simpledialog.askstring("Parse Link", "Paste your Telegram link here:\n(e.g. https://t.me/c/2129051908/11053/11054)")
        if not link:
            return
            
        # Regex for https://t.me/c/<chat_id>/<topic_id>/<msg_id>
        match = re.search(r"t\.me\/c\/(\d+)\/(\d+)", link)
        if match:
            chat_id_raw = match.group(1)
            topic_id = match.group(2)
            
            chat_id = f"-100{chat_id_raw}"
            
            self.chat_id_entry.delete(0, "end")
            self.chat_id_entry.insert(0, chat_id)
            
            self.topic_id_entry.delete(0, "end")
            self.topic_id_entry.insert(0, topic_id)
            
            self.topic_var.set(True)
            self.toggle_topic()
            
            self.log(f"Parsed Link: Chat ID={chat_id}, Topic ID={topic_id}")
        else:
            messagebox.showerror("Error", "Invalid link format. Expected: https://t.me/c/xxxxxxxxxx/yyyy/...")

    def get_config_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

    def load_credentials(self):
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    if "api_id" in data:
                        self.api_id_entry.delete(0, "end")
                        self.api_id_entry.insert(0, data["api_id"])
                    if "api_hash" in data:
                        self.api_hash_entry.delete(0, "end")
                        self.api_hash_entry.insert(0, data["api_hash"])
                    if "bot_token" in data:
                        self.bot_token_entry.delete(0, "end")
                        self.bot_token_entry.insert(0, data["bot_token"])
                    if "chat_id" in data:
                        self.chat_id_entry.delete(0, "end")
                        self.chat_id_entry.insert(0, data["chat_id"])
                    if "topic_id" in data:
                        self.topic_id_entry.delete(0, "end")
                        self.topic_id_entry.insert(0, data["topic_id"])
                        if data["topic_id"]:
                            self.topic_var.set(True)
                            self.toggle_topic()
                self.log("Credentials loaded.")
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_credentials(self):
        data = {
            "api_id": self.api_id_entry.get(),
            "api_hash": self.api_hash_entry.get(),
            "bot_token": self.bot_token_entry.get(),
            "chat_id": self.chat_id_entry.get(),
            "topic_id": self.topic_id_entry.get() if self.topic_var.get() else ""
        }
        try:
            with open(self.get_config_path(), "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def login(self):
        api_id = self.api_id_entry.get()
        api_hash = self.api_hash_entry.get()
        bot_token = self.bot_token_entry.get()

        if not api_id or not api_hash or not bot_token:
            messagebox.showerror("Error", "Please fill all login fields")
            return

        self.login_btn.configure(state="disabled", text="Logging in...")
        
        asyncio.run_coroutine_threadsafe(self.async_login(api_id, api_hash, bot_token), self.loop)

    async def async_login(self, api_id, api_hash, bot_token):
        try:
            await TgClient.start(api_id, api_hash, bot_token=bot_token)
            self.log("Logged in successfully!")
            self.after(0, lambda: self.login_btn.configure(text="Logged In", fg_color="green"))
            self.save_credentials()
        except FloodWait as e:
            self.log(f"Rate limited by Telegram. Please wait {e.value} seconds.")
            messagebox.showerror("Flood Wait", f"Telegram has rate-limited you. Please wait {e.value} seconds before trying again.")
            self.after(0, lambda: self.login_btn.configure(state="normal", text="Login"))
        except Exception as e:
            self.log(f"Login failed: {e}")
            self.after(0, lambda: self.login_btn.configure(state="normal", text="Login"))

    def browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def start_upload(self):
        path = self.path_entry.get()
        chat_id_str = self.chat_id_entry.get()
        topic_id = self.topic_id_entry.get()
        
        if not path or not chat_id_str:
            messagebox.showerror("Error", "Please select file and chat ID")
            return
            
        try:
            chat_id = int(chat_id_str)
        except ValueError:
            messagebox.showerror("Error", "Chat ID must be an integer (e.g., -100...)")
            return
        
        self.save_credentials()

        Config.AS_DOCUMENT = self.as_doc_var.get()
        Config.CAPTION = self.caption_entry.get()
        Config.TOPIC_ID = int(topic_id) if topic_id and self.topic_var.get() else 0
        
        self.log(f"DEBUG: AS_DOCUMENT={Config.AS_DOCUMENT}")

        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        
        self.uploader = Uploader(path, chat_id, Config.TOPIC_ID, self.update_progress, self.upload_done, self.log)
        asyncio.run_coroutine_threadsafe(self.uploader.upload(), self.loop)

    def cancel_upload(self):
        if self.uploader:
            self.uploader.cancel()
            self.log("Cancelling upload...")

    def update_progress(self, current, total, speed):
        self.after(0, lambda: self._update_progress_impl(current, total, speed))

    def _update_progress_impl(self, current, total, speed):
        progress = current / total if total > 0 else 0
        self.progress_bar.set(progress)
        speed_str = get_readable_file_size(speed)
        self.status_label.configure(text=f"Uploading... {int(progress*100)}% | {speed_str}/s")

    def upload_done(self):
        self.after(0, self._upload_done_impl)

    def _upload_done_impl(self):
        self.log("Upload completed!")
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.status_label.configure(text="Ready")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
