import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import urllib.request
import re
import subprocess
import os
import threading
import tempfile
import shutil
import html

def parse_time_to_seconds(t_str):
    """Parse HH:MM:SS.mmm or MM:SS.mmm or SS.mmm into total float seconds."""
    try:
        parts = t_str.strip().split(':')
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(parts[0])
    except Exception:
        return 0.0

def get_video_info(infile):
    """Retrieve width, height, fps of video using ffprobe if available."""
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "csv=p=0",
        infile
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        out, err = proc.communicate(timeout=3)
        if proc.returncode == 0:
            text = out.decode('utf-8', errors='ignore').strip()
            if text:
                parts = text.split(',')
                if len(parts) >= 3:
                    w = int(parts[0])
                    h = int(parts[1])
                    fps_str = parts[2]
                    if '/' in fps_str:
                        num, den = fps_str.split('/')
                        fps = float(num) / float(den) if float(den) != 0 else 30.0
                    else:
                        fps = float(fps_str)
                    return w, h, fps
    except Exception:
        pass
    return None, None, None

class MPCClipper:
    def __init__(self, root):
        self.root = root
        self.root.title("MPC-HC Multi-Clip Extractor")
        self.root.geometry("540x700")
        self.root.resizable(False, False)

        self.setup_icon()

        # styling
        style = ttk.Style()
        try:
            style.theme_use('vista')
        except:
            pass

        # Custom styling for buttons
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

        # Variables
        self.filepath = tk.StringVar()
        self.start_time = tk.StringVar(value="00:00:00.000")
        self.end_time = tk.StringVar(value="00:00:00.000")
        self.clips = [] # List of tuples (infile, start, end)
        
        # Render / Sync settings
        self.render_mode = tk.StringVar(value="reencode") # "reencode" or "copy"
        self.preset_var = tk.StringVar(value="veryfast")  # "ultrafast", "veryfast", "fast", "medium"
        self.res_var = tk.StringVar(value="Auto")        # "Auto", "1080p", "720p", "4K"
        
        self.create_widgets()

    def setup_icon(self):
        """Program ve Görev Çubuğu (Taskbar) ikonunu ayarlar."""
        if os.name == 'nt':
            try:
                import ctypes
                myappid = 'mpc.clipper.extractor.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass

        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_icons = [
            os.path.join(base_dir, "icon.ico"),
            os.path.join(base_dir, "favicon.ico"),
            os.path.join(base_dir, "icon.png"),
            os.path.join(base_dir, "assets", "icon.ico"),
            os.path.join(base_dir, "assets", "icon.png"),
        ]

        for icon_path in possible_icons:
            if os.path.exists(icon_path):
                try:
                    if icon_path.endswith(".ico"):
                        self.root.iconbitmap(icon_path)
                    elif icon_path.endswith(".png"):
                        self.icon_img = tk.PhotoImage(file=icon_path)
                        self.root.iconphoto(True, self.icon_img)
                    break
                except Exception:
                    pass

    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="MPC-HC Multi-Clip Extractor", font=("Segoe UI", 16, "bold"))
        header.pack(pady=8)

        # File info
        file_frame = ttk.LabelFrame(self.root, text="Video File / Aktif Video")
        file_frame.pack(fill="x", padx=15, pady=4)
        
        ttk.Entry(file_frame, textvariable=self.filepath, state="readonly", font=("Segoe UI", 9)).pack(fill="x", padx=5, pady=5)
        
        # Time controls
        time_frame = ttk.Frame(self.root)
        time_frame.pack(fill="x", padx=15, pady=5)
        
        # Start time
        start_frame = ttk.LabelFrame(time_frame, text="Start Time / Başlangıç")
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Entry(start_frame, textvariable=self.start_time, justify="center", font=("Segoe UI", 10)).pack(fill="x", padx=5, pady=5)
        ttk.Button(start_frame, text="Set Start (from MPC)", command=lambda: self.get_time_from_mpc(self.start_time)).pack(pady=4)
        
        # End time
        end_frame = ttk.LabelFrame(time_frame, text="End Time / Bitiş")
        end_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ttk.Entry(end_frame, textvariable=self.end_time, justify="center", font=("Segoe UI", 10)).pack(fill="x", padx=5, pady=5)
        ttk.Button(end_frame, text="Set End (from MPC)", command=lambda: self.get_time_from_mpc(self.end_time)).pack(pady=4)

        # Add to list button
        ttk.Button(self.root, text="Add Clip to List ⬇️", command=self.add_clip_to_list, style="Accent.TButton").pack(pady=4)

        # List of clips
        list_frame = ttk.LabelFrame(self.root, text="Clips to Combine / Birleştirilecek Klipler")
        list_frame.pack(fill="both", expand=True, padx=15, pady=4)

        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.clip_listbox = tk.Listbox(list_frame, font=("Segoe UI", 9), yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        self.clip_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.clip_listbox.yview)

        # List controls
        list_ctrl_frame = ttk.Frame(self.root)
        list_ctrl_frame.pack(fill="x", padx=15, pady=2)
        ttk.Button(list_ctrl_frame, text="Remove Selected", command=self.remove_selected_clip).pack(side="left", padx=5)
        ttk.Button(list_ctrl_frame, text="Clear All", command=self.clear_all_clips).pack(side="left", padx=5)

        # Render & Sync Settings Frame
        settings_frame = ttk.LabelFrame(self.root, text="Render & Senkronizasyon Ayarları")
        settings_frame.pack(fill="x", padx=15, pady=6)

        # Mode Selection
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(fill="x", padx=5, pady=3)
        
        ttk.Radiobutton(mode_frame, text="Yeniden Kodla (Kesin Senkronize & Donmasız) [Önerilen]", 
                        variable=self.render_mode, value="reencode").pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="Hızlı Kopya (Stream Copy - Bazı videolarda kayma/donma yapabilir)", 
                        variable=self.render_mode, value="copy").pack(anchor="w")

        # Sub-options (Preset & Resolution)
        opt_frame = ttk.Frame(settings_frame)
        opt_frame.pack(fill="x", padx=5, pady=4)

        ttk.Label(opt_frame, text="Hız / Preset:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", padx=(0, 5))
        preset_cb = ttk.Combobox(opt_frame, textvariable=self.preset_var, values=["ultrafast", "veryfast", "fast", "medium"], state="readonly", width=12)
        preset_cb.grid(row=0, column=1, sticky="w", padx=(0, 15))

        ttk.Label(opt_frame, text="Çözünürlük:", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=(0, 5))
        res_cb = ttk.Combobox(opt_frame, textvariable=self.res_var, values=["Auto", "1080p (1920x1080)", "720p (1280x720)", "4K (3840x2160)"], state="readonly", width=18)
        res_cb.grid(row=0, column=3, sticky="w")

        # Action buttons
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=15, pady=8)
        
        self.extract_btn = ttk.Button(action_frame, text="Extract & Combine All ✂️", command=self.extract_clips)
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
                return response.read().decode('utf-8')
        except Exception:
            return None

    def get_time_from_mpc(self, time_var):
        html_data = self.get_mpc_data()
        if not html_data:
            messagebox.showerror("Connection Error", 
                                 "Could not connect to MPC.\n\n"
                                 "Make sure MPC is open and Web Interface is enabled:\n"
                                 "View -> Options -> Player -> Web Interface\n"
                                 "Check 'Listen on port' (must be 13579).")
            return

        # Extract filepath
        filepath_match = re.search(r'<p id="filepath">(.*?)</p>', html_data)
        if filepath_match:
            raw_path = filepath_match.group(1)
            self.filepath.set(html.unescape(raw_path))

        # Extract position in milliseconds
        pos_match = re.search(r'<p id="position">(\d+)</p>', html_data)
        if pos_match:
            ms = int(pos_match.group(1))
            seconds = ms / 1000.0
            
            # Format to HH:MM:SS.ms
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = seconds % 60
            
            formatted_time = f"{h:02d}:{m:02d}:{s:06.3f}"
            time_var.set(formatted_time)
            self.status_var.set("Time updated successfully.")

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
            
        start_sec = parse_time_to_seconds(start)
        end_sec = parse_time_to_seconds(end)
        
        if start_sec > end_sec:
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
            
        # Check if all files still exist
        for infile, _, _ in self.clips:
            if not os.path.exists(infile):
                messagebox.showerror("Error", f"File not found:\n{infile}\n\nDid you move or rename the video after adding it to the list?")
                return

        # Use the first clip's file to determine default save location and extension
        first_infile = self.clips[0][0]
        base, _ = os.path.splitext(first_infile)
        default_out = f"{base}_combined.mp4"
        
        outfile = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            initialfile=os.path.basename(default_out),
            title="Save Combined Clip As",
            filetypes=[("MP4 Video File", "*.mp4"), ("All Files", "*.*")]
        )
        
        if not outfile:
            return

        self.extract_btn.config(state="disabled")
        
        # Run ffmpeg in a background thread so UI doesn't freeze
        threading.Thread(target=self.run_ffmpeg_multi, args=(self.clips, outfile), daemon=True).start()

    def run_ffmpeg_multi(self, clips, outfile):
        temp_dir = None
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            mode = self.render_mode.get()
            preset = self.preset_var.get()
            res_choice = self.res_var.get()

            # Parse target dimensions if specified
            target_w, target_h = None, None
            if "1080p" in res_choice:
                target_w, target_h = 1920, 1080
            elif "720p" in res_choice:
                target_w, target_h = 1280, 720
            elif "4K" in res_choice:
                target_w, target_h = 3840, 2160
            elif res_choice == "Auto" and len(clips) > 0:
                # Check if multiple unique files are present
                infiles = set(c[0] for c in clips)
                if len(infiles) > 1:
                    w0, h0, _ = get_video_info(clips[0][0])
                    if w0 and h0:
                        target_w, target_h = w0, h0

            if len(clips) == 1:
                self.root.after(0, lambda: self.status_var.set("Klip işleniyor / Processing single clip..."))
                infile, start, end = clips[0]
                
                start_sec = parse_time_to_seconds(start)
                end_sec = parse_time_to_seconds(end)
                duration = end_sec - start_sec
                if duration <= 0:
                    raise Exception(f"Geçersiz zaman aralığı: Başlangıç ({start}) Bitişten ({end}) büyük veya eşit olamaz.")

                if mode == "copy":
                    cmd = ["ffmpeg", "-y", "-ss", start, "-to", end, "-i", infile, "-c", "copy", outfile]
                else:
                    cmd = [
                        "ffmpeg", "-y",
                        "-ss", f"{start_sec:.3f}",
                        "-i", infile,
                        "-t", f"{duration:.3f}",
                        "-c:v", "libx264",
                        "-preset", preset,
                        "-crf", "20",
                        "-pix_fmt", "yuv420p",
                        "-r", "30",
                        "-c:a", "aac",
                        "-b:a", "192k",
                        "-ar", "48000",
                        "-ac", "2",
                        "-af", "aresample=async=1",
                        "-avoid_negative_ts", "make_zero"
                    ]
                    if target_w and target_h:
                        vf = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
                        cmd.extend(["-vf", vf])
                    cmd.append(outfile)

                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"FFmpeg Hatası:\n{stderr.decode('utf-8', errors='ignore')}")

            else:
                # Multiple clips: extract each to temp, then concat
                temp_dir = tempfile.mkdtemp(prefix="mpc_clipper_")
                temp_files = []
                
                # Step 1: Extract individual clips
                for i, (infile, start, end) in enumerate(clips):
                    _, ext = os.path.splitext(infile)
                    self.root.after(0, lambda i=i: self.status_var.set(f"Klip {i+1}/{len(clips)} kesiliyor ve işleniyor..."))
                    temp_file = os.path.join(temp_dir, f"part_{i}.mp4" if mode == "reencode" else f"part_{i}{ext}")
                    temp_files.append(temp_file)

                    start_sec = parse_time_to_seconds(start)
                    end_sec = parse_time_to_seconds(end)
                    duration = end_sec - start_sec
                    if duration <= 0:
                        raise Exception(f"Klip {i+1} geçersiz zaman aralığı: {start} -> {end}")

                    if mode == "copy":
                        cmd = ["ffmpeg", "-y", "-ss", start, "-to", end, "-i", infile, "-c", "copy", temp_file]
                    else:
                        cmd = [
                            "ffmpeg", "-y",
                            "-ss", f"{start_sec:.3f}",
                            "-i", infile,
                            "-t", f"{duration:.3f}",
                            "-c:v", "libx264",
                            "-preset", preset,
                            "-crf", "20",
                            "-pix_fmt", "yuv420p",
                            "-r", "30",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-ar", "48000",
                            "-ac", "2",
                            "-af", "aresample=async=1",
                            "-avoid_negative_ts", "make_zero"
                        ]
                        if target_w and target_h:
                            vf = f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
                            cmd.extend(["-vf", vf])
                        cmd.append(temp_file)

                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                    stdout, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        raise Exception(f"Klip {i+1} işlenirken hata oluştu:\n{stderr.decode('utf-8', errors='ignore')}")

                # Step 2: Create concat.txt
                self.root.after(0, lambda: self.status_var.set("Klipler birleştiriliyor..."))
                concat_list_path = os.path.join(temp_dir, "concat.txt")
                with open(concat_list_path, "w", encoding="utf-8") as f:
                    for tfile in temp_files:
                        tfile_safe = os.path.abspath(tfile).replace("\\", "/").replace("'", "'\\''")
                        f.write(f"file '{tfile_safe}'\n")

                # Step 3: Concat
                cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", outfile]
                process = subprocess.Popen(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"Klipler birleştirilirken hata oluştu:\n{stderr.decode('utf-8', errors='ignore')}")

            self.root.after(0, lambda: self.status_var.set("İşlem tamamlandı! Video kaydedildi."))
            self.root.after(0, lambda: messagebox.showinfo("Başarılı / Success", f"Video başarıyla birleştirildi ve kaydedildi:\n{outfile}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Hata oluştu!"))
            self.root.after(0, lambda e=e: messagebox.showerror("Hata / Error", str(e)))
        finally:
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
            "5. Repeat steps 2-4 to add as many parts as you want (even from different video files!).\n"
            "6. Select 'Yeniden Kodla (Kesin Senkronize)' mode to prevent audio desync and video freezing.\n"
            "7. Click 'Extract & Combine All' to merge them into a single file.\n\n"
            "Modlar:\n"
            "- Yeniden Kodla (Önerilen): Ses kaymasını ve video donmasını tamamen engeller.\n"
            "- Hızlı Kopya (Stream Copy): Çok hızlıdır ancak keyframe sınırları nedeniyle ses/görüntü kayması yapabilir."
        )
        messagebox.showinfo("Setup & Help / Yardım", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MPCClipper(root)
    root.mainloop()
