import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from PIL import Image, ImageTk
from zebra import Zebra
import qrcode
import socket
import queue
import os
from fuzzywuzzy import process
from partone import *  # Importing functions

# Function to get the local IP address
def get_local_ip():
    """Get the local IP address of the machine running Flask."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public DNS server (Google's, in this case)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"  # Default to localhost if unable to get IP
    finally:
        s.close()
    return local_ip

class ZPLGeneratorApp:
    def __init__(self, root, task_queue):
        self.root = root
        self.task_queue = task_queue
        self.finds_file = None
        self.items_file = None

        self.create_ui()
        self.check_queue()

    def create_ui(self):
        # Frame for file selection
        self.file_frame = tk.Frame(self.root)
        self.file_frame.pack(pady=10)

        # Label and Button for 'items' CSV file
        self.items_label = tk.Label(self.file_frame, text="Select 'items' CSV File:")
        self.items_label.grid(row=0, column=0, padx=10)
        self.items_button = tk.Button(self.file_frame, text="Browse...", command=self.load_items_file)
        self.items_button.grid(row=0, column=1, padx=10)

        # Printer dropdown
        self.printer_label = tk.Label(self.file_frame, text="Select Printer:")
        self.printer_label.grid(row=1, column=0, padx=10)

        # Populate the dropdown with available printers
        printers = self.get_available_printers()
        self.printer_dropdown = ttk.Combobox(self.file_frame, values=printers)
        self.printer_dropdown.grid(row=1, column=1, padx=10)

        # Check if there are any printers available
        if printers:
            self.printer_dropdown.current(0)  # Select the first printer by default
        else:
            messagebox.showwarning("No Printers Found", "No printers are available. Please add a printer and restart the application.")

        # Comboboxes for selecting fields (UPC and Item Name)
        self.fields_frame = tk.Frame(self.root)
        self.fields_frame.pack(pady=20)

        # Combobox for selecting UPC field
        self.upc_label = tk.Label(self.fields_frame, text="Select UPC Field:")
        self.upc_label.grid(row=0, column=0, padx=10)
        self.upc_combobox = ttk.Combobox(self.fields_frame)
        self.upc_combobox.grid(row=0, column=1, padx=10)

        # Combobox for selecting Item Name field
        self.item_name_label = tk.Label(self.fields_frame, text="Select Item Name Field:")
        self.item_name_label.grid(row=1, column=0, padx=10)
        self.item_name_combobox = ttk.Combobox(self.fields_frame)
        self.item_name_combobox.grid(row=1, column=1, padx=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=350, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Display QR Code Button
        self.qr_code_button = tk.Button(self.root, text="Show QR Code for Web App", command=self.display_qr_code)
        self.qr_code_button.pack(pady=10)

        # Canvas to display the QR Code
        self.qr_canvas = tk.Canvas(self.root, width=250, height=250)
        self.qr_canvas.pack(pady=10)

    def get_available_printers(self):
        """Get a list of available Zebra printers."""
        zebra = Zebra()
        try:
            printers = zebra.getqueues()
        except Exception as e:
            printers = []
            messagebox.showerror("Error", f"Failed to retrieve printers: {e}")
        return printers

    def load_items_file(self):
        self.items_file = filedialog.askopenfilename(title="Select Items File", filetypes=[("CSV Files", "*.csv")])
        if self.items_file:
            self.items_label.config(text=f"Items File: {os.path.basename(self.items_file)}")
            items_df = pd.read_csv(self.items_file)
            self.populate_fields(items_df)

    def populate_fields(self, items_df):
        # Populate the comboboxes with column names from the items file
        columns = list(items_df.columns)
        self.upc_combobox['values'] = columns
        self.item_name_combobox['values'] = columns

        # Set default selections
        self.upc_combobox.current(0)
        self.item_name_combobox.current(0)

    def check_queue(self):
        try:
            # Check if there is a new task in the queue
            file_path = self.task_queue.get_nowait()
            self.finds_file = file_path
            self.process_csv()
        except queue.Empty:
            pass
        # Schedule to check the queue again after 100 ms
        self.root.after(100, self.check_queue)

    def display_qr_code(self):
        # Get the local IP address to generate the QR code
        local_ip = get_local_ip()
        url = f"https://{local_ip}:5001"  # This is the URL of your Flask app

        # Generate QR code
        qr_img = qrcode.make(url)

        # Convert the QR code into a format Tkinter can use (PIL -> ImageTk)
        qr_img = qr_img.resize((250, 250))  # Resize the image for display
        qr_tk_img = ImageTk.PhotoImage(qr_img)

        # Create a popup window (Toplevel)
        qr_popup = tk.Toplevel(self.root)
        qr_popup.title("QR Code")
        qr_popup.geometry("300x350")

        # Label to display the QR code inside the popup
        qr_label = tk.Label(qr_popup, image=qr_tk_img)
        qr_label.image = qr_tk_img  # Keep a reference to avoid garbage collection
        qr_label.pack(padx=10, pady=10)

        # Optionally, add a button to close the popup
        close_button = tk.Button(qr_popup, text="Close", command=qr_popup.destroy)
        close_button.pack(pady=10)


    def process_csv(self):
        if not self.finds_file:
            messagebox.showerror("Error", "No 'finds' CSV file provided.")
            return

        if not self.items_file:
            messagebox.showinfo("Information", "Please select the 'items' CSV file.")
            return

        try:
            finds = pd.read_csv(self.finds_file)
            items = pd.read_csv(self.items_file)

            # Get selected fields from the comboboxes
            upc_field = self.upc_combobox.get()
            item_name_field = self.item_name_combobox.get()

            finds[' Text'] = finds[' Text'].astype(str)

            # Reset progress bar
            self.progress_bar["value"] = 0

            zpl_codes, not_found_items = self.generate_zpl_for_fuzzy_matches(
                finds, items, item_name_field, upc_field
            )

            # Send ZPL code to the printer
            if zpl_codes:
                self.print_zpl_to_printer(zpl_codes)

            # Show not found items in a separate window
            if not_found_items:
                self.show_not_found_window(not_found_items)

            # Finalize progress bar
            self.progress_bar["value"] = 100

        except pd.errors.EmptyDataError:
            messagebox.showerror("Error", "The CSV file is empty.")
        except pd.errors.ParserError:
            messagebox.showerror("Error", "Error parsing the CSV file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_progress(self, progress):
        self.progress_bar["value"] = progress
        self.root.update_idletasks()

    def generate_zpl_for_fuzzy_matches(self, finds2, items_df, item_name_field, upc_field):
        results = []
        not_found_items = []
        total_items = len(finds2[" Text"])

        for idx, item in enumerate(finds2[" Text"]):
            choices = items_df[upc_field].astype(str).tolist()
            best_match, score = process.extractOne(str(item), choices)

            if score >= 80:
                result = items_df[items_df[upc_field] == best_match]
                if not result.empty:
                    product_name = str(result[item_name_field].values[0])
                    item_price = str(result['ItemPrice'].values[0])
                    size_name = str(result['SizeName'].values[0])

                    sale_price = result['SalePrice'].values[0]
                    sale_price = f"{sale_price:.2f}" if pd.notna(sale_price) else None

                    if sale_price and sale_price != item_price and float(sale_price) > 0:
                        zpl_code = generate_zpl_with_sale(product_name, item_price, sale_price, size_name)
                    else:
                        zpl_code = generate_zpl_without_sale(product_name, item_price, size_name)
                    results.append(zpl_code)
                else:
                    not_found_items.append(item)

            else:
                not_found_items.append(item)

            # Update progress bar
            progress = int((idx + 1) / total_items * 100)
            self.update_progress(progress)

        return results, not_found_items


    def print_zpl_to_printer(self, zpl_codes):
        try:
            zebra = Zebra()

            # Get the selected printer from the dropdown
            selected_printer = self.printer_dropdown.get()

            # Set the selected printer as the queue
            zebra.setqueue(selected_printer)

            for zpl_code in zpl_codes:
                zebra.output(zpl_code)  # Send ZPL code to the printer

            messagebox.showinfo("Success", "Labels sent to printer successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send labels to printer: {e}")

    def show_not_found_window(self, not_found_items):
        # Create a new Toplevel window
        not_found_window = tk.Toplevel(self.root)
        not_found_window.title("Items Not Found")
        not_found_window.geometry("600x300")

        # Label for not found items
        not_found_label = tk.Label(not_found_window, text="Items Not Found:")
        not_found_label.pack(pady=10)

        # Frame to hold the listbox and scrollbar
        frame = tk.Frame(not_found_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Listbox for not found items
        not_found_listbox = tk.Listbox(frame, width=80, height=15)
        not_found_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for the listbox
        not_found_scrollbar = tk.Scrollbar(frame)
        not_found_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Link the scrollbar to the listbox
        not_found_listbox.config(yscrollcommand=not_found_scrollbar.set)
        not_found_scrollbar.config(command=not_found_listbox.yview)

        # Add not found items to Listbox
        for item in not_found_items:
            not_found_listbox.insert(tk.END, item)

        # Force scrollbar to appear
        not_found_listbox.yview_scroll(1, 'units')
        not_found_listbox.yview_scroll(-1, 'units')
