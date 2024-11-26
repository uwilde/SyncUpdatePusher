import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd

class DuplicateRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Remover")
        
        self.file_path = ctk.StringVar()
        self.column_name = ctk.StringVar()
        self.duplicates_removed = ctk.StringVar()
        
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self.root, text="Select CSV/XLSX file:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_entry = ctk.CTkEntry(self.root, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(self.root, text="Enter column name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.column_entry = ctk.CTkEntry(self.root, textvariable=self.column_name, width=180)
        self.column_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(self.root, text="Remove Duplicates", command=self.remove_duplicates).grid(row=2, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(self.root, textvariable=self.duplicates_removed).grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        
        ctk.CTkButton(self.root, text="Help", command=self.show_help).grid(row=4, column=1, padx=5, pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if file_path:
            self.file_path.set(file_path)

    def remove_duplicates(self):
        file_path = self.file_path.get()
        column_name = self.column_name.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return
        if not column_name:
            messagebox.showerror("Error", "Please enter a column name.")
            return
    
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format. Please select a CSV or XLSX file.")
                return
                
            initial_rows = df.shape[0]
            df.drop_duplicates(subset=[column_name], keep='first', inplace=True)
            
            output_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
            if output_file_path:
                if output_file_path.endswith('.csv'):
                    df.to_csv(output_file_path, index=False)
                elif output_file_path.endswith('.xlsx'):
                    df.to_excel(output_file_path, index=False)
                removed_rows = initial_rows - df.shape[0]
                self.duplicates_removed.set(f"{removed_rows} duplicate(s) removed and saved to {output_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_help(self):
        help_text = """Duplicate Remover

This program allows you to remove duplicate rows from a CSV or XLSX file based on a selected column.

Instructions:
1. Click on the 'Browse' button and select a CSV or XLSX file.
2. Enter the column name in the 'Enter column name' field.
3. Click on the 'Remove Duplicates' button to remove duplicate rows from the selected file and save the processed file.
4. The program will display the number of duplicate rows removed and the path to the processed file.

For further assistance, contact support@example.com"""
        
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("Help")
        
        ctk.CTkLabel(help_window, text=help_text, justify="left").pack(padx=10, pady=10)

if __name__ == "__main__":
    root = ctk.CTk()
    app = DuplicateRemoverApp(root)
    root.mainloop()
