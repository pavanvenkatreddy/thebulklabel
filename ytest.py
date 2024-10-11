import os
import socket
import qrcode
from flask import Flask, request, jsonify, render_template
import threading
import tkinter as tk
from ZPLGeneratorApp import *
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import queue

app = Flask(__name__)

# Create a Queue for inter-thread communication
task_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('yss.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'csvFile' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['csvFile']

    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Put the file path into the queue for the Tkinter thread to process
        task_queue.put(file_path)

        return jsonify({"message": f"CSV file received. Processing started."}), 200
    else:
        return jsonify({"message": "File format not supported. Please upload a CSV file."}), 400

def start_flask():
    app.run(host='0.0.0.0', ssl_context='adhoc', port=5001, debug=True, use_reloader=False)

def get_local_ip():
    """Get the local IP address of the machine running Flask."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public DNS server (Google's, in this case)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

def start_tkinter_app():
    root = tk.Tk()
    root.title("ZPL Generator with QR Code")
    root.geometry("600x500")

    # Create an instance of ZPLGeneratorApp
    app_gui = ZPLGeneratorApp(root, task_queue)
    root.mainloop()

if __name__ == "__main__":
    # Ensure 'uploads' folder exists to save the files
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True  # Ensure it exits when the main thread exits
    flask_thread.start()

    # Start Tkinter in the main thread
    start_tkinter_app()
