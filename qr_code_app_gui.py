import tkinter as tk
from tkinter import ttk

# Line 1: Create the main desktop window instance
root = tk.Tk()

# Line 2: Set the text displayed on the window title bar
root.title("QR Code Utility Suite")

# Line 3: Set the window dimensions (Width x Height in pixels)
root.geometry("500x550")

# Line 4: Create a Notebook widget (manages tabbed views)
notebook = ttk.Notebook(root)

# Line 5: Attach the notebook to the main window with margin padding
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Line 6: Create the "QR Generator" tab frame
tab_generator = ttk.Frame(notebook)
notebook.add(tab_generator, text="QR Generator")

# Line 7: Create the "QR Scanner" tab frame
tab_scanner = ttk.Frame(notebook)
notebook.add(tab_scanner, text="QR Scanner")

# Line 8: Start the GUI event loop
root.mainloop()