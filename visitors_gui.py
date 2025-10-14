import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox


# ===== Custom Exceptions =====
class DuplicateVisitorError(Exception):
    pass

class VisitorWaitError(Exception):
    pass


# ===== Main Application =====
class VisitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Visitor Log System")
        self.root.geometry("600x500")
        self.root.config(bg="#f8f9fa")

        self.filename = "visitors.txt"
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as file:
                file.write("=== Visitor Log ===\n")

        # Title Label
        tk.Label(
            root, text="Visitor Log System",
            font=("Segoe UI", 18, "bold"), fg="#212529", bg="#f8f9fa"
        ).pack(pady=10)

        # Table (Treeview)
        self.tree = ttk.Treeview(root, columns=("Name", "Timestamp"), show="headings", height=12)
        self.tree.heading("Name", text="Name")
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.column("Name", width=200)
        self.tree.column("Timestamp", width=200)
        self.tree.pack(pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=565, y=90, height=260)

        # Entry field
        form_frame = tk.Frame(root, bg="#f8f9fa")
        form_frame.pack(pady=15)

        tk.Label(form_frame, text="Enter Visitor Name:", font=("Segoe UI", 11), bg="#f8f9fa").grid(row=0, column=0, padx=5)
        self.name_entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=25)
        self.name_entry.grid(row=0, column=1, padx=5)

        # Submit Button
        tk.Button(
            form_frame, text="Log Visitor", command=self.log_visitor,
            bg="#0d6efd", fg="white", font=("Segoe UI", 10, "bold"),
            padx=10, pady=3, relief="ridge"
        ).grid(row=0, column=2, padx=5)

        # Status Label
        self.status_label = tk.Label(root, text="", bg="#f8f9fa", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(pady=10)

        # Load initial visitors
        self.load_visitors()

    # ===== Functions =====
    def load_visitors(self):
        """Display all visitors in the table."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        with open(self.filename, "r") as file:
            lines = file.readlines()[1:]

        for line in lines:
            try:
                name, time_str = line.strip().split(" - ")
                self.tree.insert("", "end", values=(name, time_str))
            except ValueError:
                continue

    def log_visitor(self):
        name = self.name_entry.get().strip().title()
        if not name:
            messagebox.showwarning("Input Error", "Name cannot be empty.")
            return

        try:
            with open(self.filename, "r") as file:
                lines = file.readlines()[1:]

            visitors = []
            for line in lines:
                try:
                    visitor_name, time_str = line.strip().split(" - ")
                    visitors.append((visitor_name, datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")))
                except ValueError:
                    continue

            existing_names = [v[0] for v in visitors]
            if name in existing_names:
                raise DuplicateVisitorError(f"⚠️ Visitor '{name}' already exists in the record!")

            if visitors:
                _, last_time = visitors[-1]
                time_diff = datetime.now() - last_time
                if time_diff < timedelta(minutes=5):
                    remaining = timedelta(minutes=5) - time_diff
                    raise VisitorWaitError(
                        f"Please wait {remaining.seconds // 60} min {remaining.seconds % 60} sec before next entry."
                    )

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.filename, "a") as file:
                file.write(f"{name} - {timestamp}\n")

            self.status_label.config(text=f"✅ {name} added successfully!", fg="green")
            self.name_entry.delete(0, tk.END)
            self.load_visitors()

        except DuplicateVisitorError as e:
            self.status_label.config(text=str(e), fg="red")
        except VisitorWaitError as e:
            self.status_label.config(text=str(e), fg="orange")
        except Exception as e:
            self.status_label.config(text=f"⚠️ Unexpected error: {e}", fg="red")


# ===== Run Application =====
if __name__ == "__main__":
    root = tk.Tk()
    app = VisitorApp(root)
    root.mainloop()