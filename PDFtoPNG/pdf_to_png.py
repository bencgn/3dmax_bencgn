import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import fitz  # PyMuPDF

class PDFToPNGConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PDF to PNG Auto Converter")
        self.geometry("700x500")

        self.pdf_files = [] # Store dicts with path, total_pages, target_pages
        self.selected_folder = ""

        # UI Setup
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)

        self.btn_browse = tk.Button(self.top_frame, text="Select Folder", command=self.browse_folder)
        self.btn_browse.pack(side=tk.LEFT)

        self.lbl_folder = tk.Label(self.top_frame, text="No folder selected", fg="gray")
        self.lbl_folder.pack(side=tk.LEFT, padx=10)

        # Treeview to display PDFs
        columns = ("Filename", "Total Pages", "Pages to Convert")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("Filename", text="Filename")
        self.tree.heading("Total Pages", text="Total Pages")
        self.tree.heading("Pages to Convert", text="Pages to Convert")
        
        self.tree.column("Filename", width=300)
        self.tree.column("Total Pages", width=100, anchor=tk.CENTER)
        self.tree.column("Pages to Convert", width=250, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<Double-1>", self.edit_pages)

        # Bottom Frame
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        self.lbl_edit_hint = tk.Label(self.bottom_frame, text="Double-click a row to specify pages (e.g., '1, 3, 5-10' or 'All')", fg="gray")
        self.lbl_edit_hint.pack(side=tk.LEFT)

        self.btn_convert = tk.Button(self.bottom_frame, text="Convert All to PNG", command=self.convert_pdfs, bg="green", fg="white")
        self.btn_convert.pack(side=tk.RIGHT)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder containing PDFs")
        if folder:
            self.selected_folder = folder
            self.lbl_folder.config(text=self.selected_folder, fg="black")
            self.load_pdfs()

    def load_pdfs(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.pdf_files.clear()

        if not self.selected_folder:
            return

        for f in os.listdir(self.selected_folder):
            if f.lower().endswith(".pdf"):
                full_path = os.path.join(self.selected_folder, f)
                try:
                    doc = fitz.open(full_path)
                    total_pages = len(doc)
                    doc.close()
                    
                    data = {
                        "path": full_path,
                        "filename": f,
                        "total_pages": total_pages,
                        "pages_to_convert": "All"
                    }
                    self.pdf_files.append(data)
                    
                    self.tree.insert("", tk.END, iid=full_path, values=(f, total_pages, "All"))
                except Exception as e:
                    print(f"Error reading {f}: {e}")

    def edit_pages(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item_id = selected_item[0]
        values = self.tree.item(item_id, "values")
        filename = values[0]
        current_pages = values[2]
        
        # Simple custom dialog
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Edit Pages - {filename}")
        edit_win.geometry("400x150")
        
        tk.Label(edit_win, text=f"Specify pages to convert (e.g., 1, 3, 5-7, or All)\nfor {filename}:").pack(pady=10)
        
        entry = tk.Entry(edit_win, width=40)
        entry.insert(0, current_pages)
        entry.pack(pady=5)
        
        def save():
            new_val = entry.get().strip()
            if not new_val:
                new_val = "All"
            
            # Update tree
            self.tree.item(item_id, values=(values[0], values[1], new_val))
            
            # Update data
            for pdf in self.pdf_files:
                if pdf["path"] == item_id:
                    pdf["pages_to_convert"] = new_val
                    break
                    
            edit_win.destroy()

        btn_save = tk.Button(edit_win, text="Save", command=save)
        btn_save.pack(pady=10)
        
        # Make modal
        edit_win.transient(self)
        edit_win.grab_set()
        self.wait_window(edit_win)

    def parse_page_string(self, page_str, total_pages):
        if page_str.lower() == "all" or not page_str.strip():
            return list(range(total_pages))
            
        pages = set()
        parts = page_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = part.split('-')
                    start = max(1, int(start))
                    end = min(total_pages, int(end))
                    if start <= end:
                        pages.update(range(start - 1, end))
                except ValueError:
                    pass
            else:
                try:
                    p = int(part)
                    if 1 <= p <= total_pages:
                        pages.add(p - 1)
                except ValueError:
                    pass
        return sorted(list(pages))

    def convert_pdfs(self):
        if not self.pdf_files:
            messagebox.showinfo("Info", "No PDF files to convert.")
            return

        output_dir = os.path.join(self.selected_folder, "Converted_PNGs")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        total_converted = 0
        total_pdfs = 0

        for pdf in self.pdf_files:
            file_path = pdf["path"]
            filename = pdf["filename"]
            pages_to_convert_str = pdf["pages_to_convert"]
            total_pages = pdf["total_pages"]

            pages_list = self.parse_page_string(pages_to_convert_str, total_pages)
            if not pages_list:
                continue

            try:
                doc = fitz.open(file_path)
                base_name = os.path.splitext(filename)[0]
                
                for page_num in pages_list:
                    page = doc.load_page(page_num)
                    # Higher resolution (zoom)
                    zoom = 2.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    out_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.png")
                    pix.save(out_path)
                    total_converted += 1
                
                doc.close()
                total_pdfs += 1
            except Exception as e:
                print(f"Error converting {filename}: {e}")

        messagebox.showinfo("Success", f"Converted {total_converted} pages from {total_pdfs} PDF files.\nSaved in:\n{output_dir}")

if __name__ == "__main__":
    app = PDFToPNGConverter()
    app.mainloop()
