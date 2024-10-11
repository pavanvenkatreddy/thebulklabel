import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import math
from fuzzywuzzy import process
import pandas as pd
from zebra import Zebra
import os

# Function definitions (from your original code)
def calculate_text_width(text, font_size):
    average_char_width = font_size * 0.6
    return average_char_width * len(text)

def calculate_text_height(font_size):
    return font_size * 1.2

def truncate_text(text, font_size, max_width):
    ellipsis_width = calculate_text_width("...", font_size)
    while calculate_text_width(text, font_size) + ellipsis_width > max_width:
        text = text[:-1]
    return text + "..."

def generate_zpl_with_sale(product_name, price, sale_price, size_identifier, label_width=500, label_height=240, font_size_name=20, font_size_price=40, font_size_sale_price=80):
    max_name_width = label_width - 40
    name_width = calculate_text_width(product_name, font_size_name)
    if name_width > max_name_width:
        product_name = truncate_text(product_name, font_size_name, max_name_width)
        name_width = calculate_text_width(product_name, font_size_name)

    name_height = calculate_text_height(font_size_name)
    sale_price_width = calculate_text_width(sale_price, font_size_sale_price)

    zpl_code = f"""
^XA
^PW{label_width}
^LL{label_height}
^CF0,{font_size_name}
^FO20,20^FD{product_name}^FS
^CF0,{font_size_sale_price}
^FO200,124^FD{sale_price}$^FS
^CF0,{font_size_price}
^FO240,54^FD{price}$^FS
^FO20,80^FD{size_identifier}^FS
^XZ
"""
    return zpl_code

def generate_zpl_without_sale(product_name, price, size_identifier, label_width=500, label_height=240, font_size_name=20, font_size_price=80):
    max_name_width = label_width - 40
    name_width = calculate_text_width(product_name, font_size_name)
    if name_width > max_name_width:
        product_name = truncate_text(product_name, font_size_name, max_name_width)
        name_width = calculate_text_width(product_name, font_size_name)

    zpl_code = f"""
^XA
^PW{label_width}
^LL{label_height}
^CF0,{font_size_name}
^FO20,20^FD{product_name}^FS
^CF0,{font_size_price}
^FO240,54^FD{price}$^FS
^FO20,80^FD{size_identifier}^FS
^XZ
"""
    return zpl_code
