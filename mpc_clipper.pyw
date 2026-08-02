import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import urllib.request
import re
import subprocess
import os
import threading
import tempfile
import shutil

class MPCClipper:
    def __init__(self, root):
        self.root = root
        self.root.title("MPC-HC Multi-Clip Extractor")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        # styling
        style = ttk.Style()
        try:
            style.theme_use('vista')
        except:
            pass

        # Variables
        self.filepath = tk.StringVar()
        self.start_time = tk.StringVar(value="00:00:00.000")
        self.end_time = tk.StringVar(value="00:00:00.000")
        self.clips = [] # List of tuples (start, end)
        
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="MPC-HC Multi-Clip Extractor", font=("Segoe UI", 16, "bold"))
        header.pack(pady=10)

        # File info
        file_frame = ttk.LabelFrame(self.root, text="Video File")
        file_frame.pack(fill="x", padx=15, pady=5)
        
        ttk.Entry(file_frame, textvariable=self.filepath, state="readonly", font=("Segoe UI", 9)).pack(fill="x", padx=5, pady=5)
        
        # Time controls
        time_frame = ttk.Frame(self.root)
        time_frame.pack(fill="x", padx=15, pady=10)
        
        # Start time
        start_frame = ttk.LabelFrame(time_frame, text="Start Time")
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Entry(start_frame, textvariable=self.start_time, justify="center", font=("Segoe UI", 10)).pack(fill="x", padx=5, pady=5)
        ttk.Button(start_frame, text="Set Start (from MPC)", command=lambda: self.get_time_from_mpc(self.start_time)).pack(pady=5)
        
        # End time
        end_frame = ttk.LabelFrame(time_frame, text="End Time")
        end_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ttk.Entry(end_frame, textvariable=self.end_time, justify="center", font=("Segoe UI", 10)).pack(fill="x", padx=5, pady=5)
        ttk.Button(end_frame, text="Set End (from MPC)", command=lambda: self.get_time_from_mpc(self.end_time)).pack(pady=5)

        # Add to list button
        ttk.Button(self.root, text="Add Clip to List \u2b07\ufe0f", command=self.add_clip_to_list, style="Accent.TButton").pack(pady=5)

        # List of clips
        list_frame = ttk.LabelFrame(self.root, text="Clips to Combine")
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.clip_listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        self.clip_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.clip_listbox.yview)

        # List controls
        list_ctrl_frame = ttk.Frame(self.root)
        list_ctrl_frame.pack(fill="x", padx=15, pady=5)
        ttk.Button(list_ctrl_frame, text="Remove Selected", command=self.remove_selected_clip).pack(side="left", padx=5)
        ttk.Button(list_ctrl_frame, text="Clear All", command=self.clear_all_clips).pack(side="left", padx=5)

        # Action buttons
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=15, pady=10)
        
        self.extract_btn = ttk.Button(action_frame, text="Extract & Combine All \u2702\ufe0f", command=self.extract_clips)
        self.extract_btn.pack(side="right", padx=5, ipadx=10, ipady=3)
        
        ttk.Button(action_frame, text="Help / Setup", command=self.show_help).pack(side="left", padx=5, ipady=3)

        # Status label
        self.status_var = tk.StringVar(value="Ready. Set start/end times and add them to the list.")
        status_label = ttk.Label(self.root, textvariable=self.status_var, anchor="w", font=("Segoe UI", 9))
        status_label.pack(side="bottom", fill="x", padx=15, pady=5)

    def get_mpc_data(self):
        try:
            req = urllib.request.Request('http://localhost:13579/variables.html')
            with urllib.request.urlopen(req, timeout=1) as response:
                html = response.read().decode('utf-8')
                return html
        except Exception as e:
            return None

    def get_time_from_mpc(self, time_var):
        html = self.get_mpc_data()
        if not html:
            messagebox.showerror("Connection Error", 
                                 "Could not connect to MPC.\n\n"
                                 "Make sure MPC is open and Web Interface is enabled:\n"
                                 "View -> Options -> Player -> Web Interface\n"
                                 "Check 'Listen on port' (must be 13579).")
            return

        # Extract filepath
        filepath_match = re.search(r'<p id="filepath">(.*?)</p>', html)
        if filepath_match:
            self.filepath.set(filepath_match.group(1))

        # Extract position in milliseconds
        pos_match = re.search(r'<p id="position">(\d+)</p>', html)
        if pos_match:
            ms = int(pos_match.group(1))
            seconds = ms / 1000.0
            
            # Format to HH:MM:SS.ms
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = seconds % 60
            
            formatted_time = f"{h:02d}:{m:02d}:{s:06.3f}"
            time_var.set(formatted_time)
            self.status_var.set(f"Time updated successfully.")

    def add_clip_to_list(self):
        start = self.start_time.get()
        end = self.end_time.get()
        infile = self.filepath.get()

        if not infile:
            messagebox.showwarning("Warning", "Please get time from MPC first to load the video file.")
            return

        if start == end:
            messagebox.showerror("Error", "Start and End times cannot be the same!")
            return
            
        if start > end:
            start, end = end, start
            
        self.clips.append((infile, start, end))
        filename = os.path.basename(infile)
        self.clip_listbox.insert(tk.END, f"Clip {len(self.clips)}: [ {start}  -->  {end} ] ({filename})")
        self.status_var.set(f"Added Clip {len(self.clips)} to the list.")

    def remove_selected_clip(self):
        selection = self.clip_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.clip_listbox.delete(index)
        del self.clips[index]
        
        # Refresh listbox to fix numbering
        self.clip_listbox.delete(0, tk.END)
        for i, (infile, start, end) in enumerate(self.clips):
            filename = os.path.basename(infile)
            self.clip_listbox.insert(tk.END, f"Clip {i+1}: [ {start}  -->  {end} ] ({filename})")

    def clear_all_clips(self):
        self.clips.clear()
        self.clip_listbox.delete(0, tk.END)

    def extract_clips(self):
        if not self.clips:
            messagebox.showerror("Error", "No clips added to the list. Please add at least one clip.")
            return

        # Use the first clip's file to determine the default save location and extension
        first_infile = self.clips[0][0]
        base, ext = os.path.splitext(first_infile)
        default_out = f"{base}_combined{ext}"
        
        outfile = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=os.path.basename(default_out),
            title="Save Combined Clip As",
            filetypes=[("Video File", f"*{ext}"), ("All Files", "*.*")]
        )
        
        if not outfile:
            return

        self.extract_btn.config(state="disabled")
        
        # Run ffmpeg in a thread so UI doesn't freeze
        threading.Thread(target=self.run_ffmpeg_multi, args=(self.clips, outfile), daemon=True).start()

    def run_ffmpeg_multi(self, clips, outfile):
        temp_dir = None
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            if len(clips) == 1:
                self.root.after(0, lambda: self.status_var.set("Extracting single clip..."))
                infile, start, end = clips[0]
                cmd = ["ffmpeg", "-y", "-ss", start, "-to", end, "-i", infile, "-c", "copy", outfile]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"FFmpeg error:\n{stderr.decode('utf-8', errors='ignore')}")
            else:
                # Multiple clips: extract each to temp, then concat
                temp_dir = tempfile.mkdtemp(prefix="mpc_clipper_")
                temp_files = []
                
                # Step 1: Extract individual clips
                for i, (infile, start, end) in enumerate(clips):
                    _, ext = os.path.splitext(infile)
                    self.root.after(0, lambda i=i: self.status_var.set(f"Extracting clip {i+1} of {len(clips)}..."))
                    temp_file = os.path.join(temp_dir, f"part_{i}{ext}")
                    temp_files.append(temp_file)
                    
                    cmd = ["ffmpeg", "-y", "-ss", start, "-to", end, "-i", infile, "-c", "copy", temp_file]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                    stdout, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        raise Exception(f"Failed extracting clip {i+1}:\n{stderr.decode('utf-8', errors='ignore')}")

                # Step 2: Create concat.txt
                self.root.after(0, lambda: self.status_var.set("Combining clips..."))
                concat_list_path = os.path.join(temp_dir, "concat.txt")
                with open(concat_list_path, "w", encoding="utf-8") as f:
                    for tfile in temp_files:
                        # ffmpeg concat requires single quotes and escaped single quotes if any
                        # Using relative paths is safer. But absolute path with safe formatting:
                        tfile_safe = tfile.replace("'", "'\\''")
                        f.write(f"file '{tfile_safe}'\n")

                # Step 3: Concat
                cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", outfile]
                process = subprocess.Popen(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Failed combining clips:\n{stderr.decode('utf-8', errors='ignore')}")

            self.root.after(0, lambda: self.status_var.set("Extraction & combination complete!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Video saved successfully:\n{outfile}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Error during extraction!"))
            self.root.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
        finally:
            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            self.root.after(0, lambda: self.extract_btn.config(state="normal"))

    def show_help(self):
        help_text = (
            "MPC-HC Multi-Clip Extractor Guide:\n\n"
            "1. Open your video in MPC and enable Web Interface (Port 13579).\n"
            "2. Find the start of your first clip and click 'Set Start'.\n"
            "3. Find the end of your first clip and click 'Set End'.\n"
            "4. Click 'Add Clip to List'.\n"
            "5. Repeat steps 2-4 to add as many parts as you want.\n"
            "6. Click 'Extract & Combine All' to merge them into a single file.\n\n"
            "Note: Since this process doesn't re-encode the video (to be fast), "
            "make sure all clips are from the SAME original video."
        )
        messagebox.showinfo("Setup & Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MPCClipper(root)
    root.mainloop()
