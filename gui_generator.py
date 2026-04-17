import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk

# --- Словари переводов ---
LANG = {
    'en': {
        'title': 'GIF Generator for ESP32',
        'lbl_lang': 'Language / Idioma / Язык:',
        'lbl_pins': 'I2C Pins Configuration:',
        'lbl_sda': 'SDA Pin:',
        'lbl_scl': 'SCL Pin:',
        'lbl_libs': 'Required Arduino Libraries:\n- Adafruit GFX Library\n- Adafruit SSD1306',
        'btn_load': 'Load GIF',
        'btn_generate': 'Generate .ino File',
        'info_orig': 'Original Info:',
        'info_out': 'Output Info:',
        'msg_no_gif': 'Please load a GIF first!',
        'msg_success': 'Success! File saved as:\n',
        'err_pins': 'Pins must be numbers!',
        'lbl_preview': 'OLED Preview (128x64 B&W):'
    },
    'es': {
        'title': 'Generador de GIF para ESP32',
        'lbl_lang': 'Language / Idioma / Язык:',
        'lbl_pins': 'Configuración de Pines I2C:',
        'lbl_sda': 'Pin SDA:',
        'lbl_scl': 'Pin SCL:',
        'lbl_libs': 'Bibliotecas Arduino requeridas:\n- Adafruit GFX Library\n- Adafruit SSD1306',
        'btn_load': 'Cargar GIF',
        'btn_generate': 'Generar Archivo .ino',
        'info_orig': 'Info Original:',
        'info_out': 'Info de Salida:',
        'msg_no_gif': '¡Por favor carga un GIF primero!',
        'msg_success': '¡Éxito! Archivo guardado como:\n',
        'err_pins': '¡Los pines deben ser números!',
        'lbl_preview': 'Vista previa OLED (128x64 B/N):'
    },
    'ru': {
        'title': 'Генератор GIF для ESP32',
        'lbl_lang': 'Language / Idioma / Язык:',
        'lbl_pins': 'Настройка пинов I2C:',
        'lbl_sda': 'Пин SDA:',
        'lbl_scl': 'Пин SCL:',
        'lbl_libs': 'Необходимые библиотеки Arduino:\n- Adafruit GFX Library\n- Adafruit SSD1306',
        'btn_load': 'Загрузить GIF',
        'btn_generate': 'Сгенерировать .ino файл',
        'info_orig': 'Оригинал:',
        'info_out': 'На выходе:',
        'msg_no_gif': 'Сначала загрузите GIF!',
        'msg_success': 'Успешно! Файл сохранен как:\n',
        'err_pins': 'Пины должны быть цифрами!',
        'lbl_preview': 'Предпросмотр OLED (128x64 Ч/Б):'
    }
}

class GifGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = 'en'
        self.gif_path = None
        self.frames = []
        self.tk_frames = []
        self.frame_idx = 0
        self.anim_job = None
        self.frame_duration = 40 # ms default

        self.setup_ui()
        self.change_lang(None)

    def setup_ui(self):
        # Язык
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=5)
        self.lbl_lang = tk.Label(lang_frame, text="")
        self.lbl_lang.pack(side=tk.LEFT, padx=5)
        self.lang_var = tk.StringVar(value='en')
        lang_cb = ttk.Combobox(lang_frame, textvariable=self.lang_var, values=['en', 'es', 'ru'], state='readonly', width=5)
        lang_cb.pack(side=tk.LEFT)
        lang_cb.bind('<<ComboboxSelected>>', self.change_lang)

        # Пины
        pin_frame = tk.LabelFrame(self.root, text="")
        pin_frame.pack(pady=10, padx=10, fill="x")
        self.frame_pins = pin_frame
        
        self.lbl_sda = tk.Label(pin_frame, text="")
        self.lbl_sda.grid(row=0, column=0, padx=5, pady=5)
        self.entry_sda = tk.Entry(pin_frame, width=5)
        self.entry_sda.insert(0, "3")
        self.entry_sda.grid(row=0, column=1, padx=5, pady=5)

        self.lbl_scl = tk.Label(pin_frame, text="")
        self.lbl_scl.grid(row=0, column=2, padx=5, pady=5)
        self.entry_scl = tk.Entry(pin_frame, width=5)
        self.entry_scl.insert(0, "4")
        self.entry_scl.grid(row=0, column=3, padx=5, pady=5)

        # Библиотеки
        self.lbl_libs = tk.Label(self.root, text="", fg="blue", justify=tk.LEFT)
        self.lbl_libs.pack(pady=5)

        # Кнопка загрузки
        self.btn_load = tk.Button(self.root, text="", command=self.load_gif, width=20, bg="#e0e0e0")
        self.btn_load.pack(pady=10)

        # Информация
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        self.lbl_info_orig = tk.Label(info_frame, text="", justify=tk.LEFT)
        self.lbl_info_orig.pack(side=tk.LEFT, padx=20)
        self.lbl_info_out = tk.Label(info_frame, text="", justify=tk.LEFT)
        self.lbl_info_out.pack(side=tk.LEFT, padx=20)

        # Превью
        self.lbl_preview_title = tk.Label(self.root, text="")
        self.lbl_preview_title.pack(pady=5)
        self.canvas_preview = tk.Canvas(self.root, width=128, height=64, bg="black")
        self.canvas_preview.pack()
        self.preview_img_on_canvas = self.canvas_preview.create_image(0, 0, anchor=tk.NW)

        # Кнопка генерации
        self.btn_generate = tk.Button(self.root, text="", command=self.generate_code, width=30, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.btn_generate.pack(pady=20)

    def change_lang(self, event):
        l = self.lang_var.get()
        self.current_lang = l
        t = LANG[l]
        
        self.root.title(t['title'])
        self.lbl_lang.config(text=t['lbl_lang'])
        self.frame_pins.config(text=t['lbl_pins'])
        self.lbl_sda.config(text=t['lbl_sda'])
        self.lbl_scl.config(text=t['lbl_scl'])
        self.lbl_libs.config(text=t['lbl_libs'])
        self.btn_load.config(text=t['btn_load'])
        self.btn_generate.config(text=t['btn_generate'])
        self.lbl_preview_title.config(text=t['lbl_preview'])
        
        if not self.gif_path:
            self.lbl_info_orig.config(text=t['info_orig'] + "\n-")
            self.lbl_info_out.config(text=t['info_out'] + "\n-")

    def load_gif(self):
        path = filedialog.askopenfilename(filetypes=[("GIF Files", "*.gif")])
        if not path:
            return
        
        self.gif_path = path
        self.process_gif()

    def process_gif(self):
        img = Image.open(self.gif_path)
        
        # Инфа об оригинале
        orig_w, orig_h = img.size
        try:
            self.frame_duration = img.info['duration']
            if self.frame_duration == 0: self.frame_duration = 40
        except KeyError:
            self.frame_duration = 40
            
        self.frames = []
        self.tk_frames = []
        
        try:
            while True:
                # Масштабируем до 128x64 и применяем дизеринг ('1')
                frame = img.copy().resize((128, 64)).convert('1')
                self.frames.append(frame)
                # Подготовка для отображения в Tkinter
                self.tk_frames.append(ImageTk.PhotoImage(frame))
                img.seek(len(self.frames))
        except EOFError:
            pass

        total_frames = len(self.frames)
        total_time_ms = total_frames * self.frame_duration

        t = LANG[self.current_lang]
        self.lbl_info_orig.config(text=f"{t['info_orig']}\nSize: {orig_w}x{orig_h}\nFrames: {total_frames}\nDelay: {self.frame_duration}ms")
        self.lbl_info_out.config(text=f"{t['info_out']}\nSize: 128x64 (OLED)\nFrames: {total_frames}\nTotal Loop: {total_time_ms/1000:.2f}s")

        self.frame_idx = 0
        self.play_preview()

    def play_preview(self):
        if self.anim_job is not None:
            self.root.after_cancel(self.anim_job)
            
        if not self.tk_frames: return

        frame = self.tk_frames[self.frame_idx]
        self.canvas_preview.itemconfig(self.preview_img_on_canvas, image=frame)
        
        self.frame_idx = (self.frame_idx + 1) % len(self.tk_frames)
        self.anim_job = self.root.after(self.frame_duration, self.play_preview)

    def generate_code(self):
        t = LANG[self.current_lang]
        if not self.frames:
            messagebox.showwarning("Warning", t['msg_no_gif'])
            return

        sda_val = self.entry_sda.get()
        scl_val = self.entry_scl.get()

        if not sda_val.isdigit() or not scl_val.isdigit():
            messagebox.showerror("Error", t['err_pins'])
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".ino", filetypes=[("Arduino Sketch", "*.ino")])
        if not save_path:
            return

        frame_arrays = []
        for i, frame in enumerate(self.frames):
            pixels = list(frame.getdata())
            byte_array = []
            for y in range(64):
                for x_byte in range(0, 128, 8):
                    byte = 0
                    for bit in range(8):
                        if pixels[y * 128 + x_byte + bit] > 0:
                            byte |= (1 << (7 - bit))
                    byte_array.append(f"0x{byte:02X}")
            array_str = f"const unsigned char frame_{i}[] PROGMEM = {{\n  " + ", ".join(byte_array) + "\n};"
            frame_arrays.append(array_str)

        arrays_code = "\n\n".join(frame_arrays)
        pointers = "const unsigned char* const frames[] PROGMEM = {\n  "
        pointers += ", ".join([f"frame_{i}" for i in range(len(self.frames))])
        pointers += "\n};"

        ino_template = f"""#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

// Custom I2C Pins
#define I2C_SDA {sda_val}
#define I2C_SCL {scl_val}

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

{arrays_code}

{pointers}

#define FRAMES_COUNT {len(self.frames)}
#define FRAME_DELAY {self.frame_duration}

void setup() {{
  Wire.begin(I2C_SDA, I2C_SCL);
  
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {{
    for(;;);
  }}
  display.clearDisplay();
}}

// Эта функция по умолчанию в Arduino работает как бесконечный цикл (infinite loop)
void loop() {{
  for(int i = 0; i < FRAMES_COUNT; i++) {{
    display.clearDisplay();
    display.drawBitmap(0, 0, frames[i], SCREEN_WIDTH, SCREEN_HEIGHT, WHITE);
    display.display();
    delay(FRAME_DELAY);
  }}
}}
"""
        with open(save_path, "w", encoding='utf-8') as f:
            f.write(ino_template)
            
        messagebox.showinfo("Success", f"{t['msg_success']}{save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("450x550")
    root.resizable(False, False)
    app = GifGeneratorApp(root)
    root.mainloop()