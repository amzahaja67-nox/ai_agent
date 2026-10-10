import datetime
import os
import shutil
import subprocess
import webbrowser
import winsound

from browse_controler import BrowserController
from system_controler import SystemController

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class AsistenAI:
    def __init__(self):
        self.is_running = True
        self.recognizer = None
        self.microphone = None
        self.device_index = self._select_microphone_device()
        self.engine = None
        self.browser_controller = BrowserController()
        self.system_controller = SystemController()
        self.chrome_path = self._find_chrome()
        self._init_voice()

    def _select_microphone_device(self):
        if sr is None:
            print("[DEBUG] SpeechRecognition tidak tersedia, tidak bisa memilih mic")
            return None

        try:
            devices = sr.Microphone.list_microphone_names()
            print(f"[DEBUG] Device audio ditemukan: {len(devices)} item")
            for idx, name in enumerate(devices):
                print(f"[DEBUG] Mic[{idx}] = {name}")
        except Exception as e:
            print(f"[DEBUG] Gagal membaca daftar mic: {e}")
            return None

        if not devices:
            print("[DEBUG] Tidak ada perangkat microfon yang terdeteksi")
            return None

        priority = [
            "microphone (realtek",
            "microphone",
            "realtek",
            "usb",
            "headset",
            "default",
        ]

        for keyword in priority:
            for index, name in enumerate(devices):
                if name and keyword in (name.lower()):
                    if "mapper" not in name.lower() and "output" not in name.lower() and "speaker" not in name.lower() and "stereo mix" not in name.lower():
                        print(f"[DEBUG] Memilih mic dengan keyword '{keyword}' pada index {index}: {name}")
                        return index

        for index, name in enumerate(devices):
            if name and "microphone" in name.lower():
                if "mapper" not in name.lower() and "output" not in name.lower() and "speaker" not in name.lower() and "stereo mix" not in name.lower():
                    print(f"[DEBUG] Memilih mic fallback pada index {index}: {name}")
                    return index

        print(f"[DEBUG] Tidak ada mic valid ditemukan, memakai index 0 default")
        return 0

    def _init_voice(self):
        if sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 300
                print(f"[DEBUG] energy_threshold = {self.recognizer.energy_threshold}")
                if self.device_index is not None:
                    self.microphone = sr.Microphone(device_index=self.device_index)
                    print(f"[*] Mikrofon dipilih: index {self.device_index}")
                else:
                    self.microphone = sr.Microphone()
                    print("[*] Mikrofon default dipakai")
            except Exception as e:
                print(f"[!] Microphone tidak tersedia: {e}")
                self.microphone = None

        if pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 150)
            except Exception as e:
                print(f"[!] Text-to-speech tidak tersedia: {e}")
                self.engine = None

    def _find_chrome(self):
        """Cari lokasi Chrome atau Edge di Windows"""
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]

        for path in candidates:
            if path and os.path.exists(path):
                return path

        for command in ("chrome", "google-chrome", "msedge", "microsoft-edge"):
            found = shutil.which(command)
            if found:
                return found

        return None

    def speak(self, text):
        print(f"[AI] {text}")

        if self.engine is not None:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                print(f"[TTS Error] {e}")
                try:
                    self.engine = pyttsx3.init()
                    self.engine.setProperty("rate", 150)
                    self.engine.say(text)
                    self.engine.runAndWait()
                    return
                except Exception:
                    pass

        try:
            winsound.Beep(700, 180)
            winsound.Beep(900, 160)
        except Exception as e:
            print(f"[Audio fallback error] {e}")

    def listen(self):
        if self.recognizer is None:
            print("[DEBUG] recognizer tidak dibuat, jadi mode suara tidak aktif")
            return None

        if self.microphone is None:
            print("[DEBUG] microphone tidak tersedia / gagal diinisialisasi")
            return None

        try:
            with self.microphone as source:
                print("\n[*] Mendengarkan...")
                print(f"[DEBUG] Mencoba rekam audio dengan mic index {self.device_index}")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"[DEBUG] threshold setelah calibrasi: {self.recognizer.energy_threshold}")
                audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=7)
                print(f"[DEBUG] Audio berhasil ditangkap: sample_rate={getattr(audio, 'sample_rate', 'unknown')}, len={len(audio.frame_data) if hasattr(audio, 'frame_data') else 'unknown'}")

            print("[DEBUG] Mengirim audio ke Google Speech Recognition...")
            command = self.recognizer.recognize_google(audio, language="id-ID")
            print(f"[Anda] {command}")
            return command.lower()

        except sr.WaitTimeoutError:
            print("[DEBUG] Timeout saat mendengarkan audio: tidak ada suara yang masuk dalam 7 detik")
            return None
        except sr.UnknownValueError:
            print("[DEBUG] Audio diterima tetapi tidak bisa dipahami oleh recognizer")
            print("[!] Tidak dapat mengenali suara, coba lagi...")
            return None
        except sr.RequestError as e:
            print(f"[DEBUG] RequestError Google Speech: {e}")
            print(f"[!] Koneksi ke Google Speech gagal: {e}")
            return None
        except Exception as e:
            print(f"[DEBUG] Error pendengaran detail: {type(e).__name__}: {e}")
            print(f"[!] Error pendengaran: {e}")
            return None

    def open_chrome(self, url=None):
        try:
            if self.chrome_path:
                if url:
                    subprocess.Popen([self.chrome_path, url])
                else:
                    subprocess.Popen([self.chrome_path])
                return True

            if os.name == "nt":
                if url:
                    os.system(f'start "" "{url}"')
                else:
                    os.system('start "" "chrome"')
                return True

            if url:
                webbrowser.open(url)
            else:
                webbrowser.open("https://www.google.com")
            return True

        except Exception as e:
            print(f"[!] Gagal membuka browser: {e}")
            if url:
                webbrowser.open(url)
            return False

    def search_in_chrome(self, query):
        import urllib.parse
        encoded = urllib.parse.quote(query)
        self.open_chrome(f"https://www.google.com/search?q={encoded}")

    def process_command(self, command):
        cmd = command.strip().lower()
        if not cmd:
            return

        if any(key in cmd for key in ["open chrome", "buka chrome", "buka krom"]):
            self.open_chrome()
            self.speak("Chrome berhasil dibuka")
            return

        if any(key in cmd for key in ["search", "serch", "cari"]):
            query = ""
            for keyword in ["search", "serch", "cari"]:
                if keyword in cmd:
                    query = cmd.split(keyword, 1)[1].strip()
                    break

            if not query:
                self.speak("Mau cari apa?")
                return

            sites = {
                "youtube": "https://www.youtube.com",
                "yutub": "https://www.youtube.com",
                "facebook": "https://www.facebook.com",
                "instagram": "https://www.instagram.com",
                "twitter": "https://www.twitter.com",
                "github": "https://www.github.com",
                "gmail": "https://mail.google.com",
                "google": "https://www.google.com",
                "whatsapp": "https://web.whatsapp.com",
                "tiktok": "https://www.tiktok.com",
            }

            for site_name, site_url in sites.items():
                if site_name in query:
                    self.open_chrome(site_url)
                    self.speak(f"Membuka {site_name}")
                    return

            self.search_in_chrome(query)
            self.speak(f"Mencari {query} di Google")
            return

        if any(key in cmd for key in ["buka youtube", "open youtube"]):
            self.open_chrome("https://www.youtube.com")
            self.speak("Membuka YouTube")
            return

        if any(key in cmd for key in ["buka github", "open github"]):
            self.open_chrome("https://www.github.com")
            self.speak("Membuka GitHub")
            return

        if any(key in cmd for key in ["buka whatsapp", "open whatsapp", "whatsapp web"]):
            self.open_chrome("https://web.whatsapp.com")
            self.speak("Membuka WhatsApp Web")
            return

        if any(key in cmd for key in ["buka gmail", "open gmail", "buka email", "open email"]):
            self.open_chrome("https://mail.google.com")
            self.speak("Membuka Gmail")
            return

        if any(key in cmd for key in ["buka drive", "open drive", "buka google drive", "open google drive"]):
            self.open_chrome("https://drive.google.com")
            self.speak("Membuka Google Drive")
            return

        if any(key in cmd for key in ["buka docs", "open docs", "buka google docs", "open google docs"]):
            self.open_chrome("https://docs.google.com")
            self.speak("Membuka Google Docs")
            return

        if any(key in cmd for key in ["buka facebook", "open facebook"]):
            self.open_chrome("https://www.facebook.com")
            self.speak("Membuka Facebook")
            return

        if any(key in cmd for key in ["buka instagram", "open instagram"]):
            self.open_chrome("https://www.instagram.com")
            self.speak("Membuka Instagram")
            return

        if any(key in cmd for key in ["tab baru", "new tab", "buka tab baru", "open new tab"]):
            self.browser_controller.new_browser_tab()
            self.speak("Membuka tab baru")
            return

        if any(key in cmd for key in ["tutup tab", "close tab", "close browser tab", "tutup browser tab"]):
            self.browser_controller.close_browser_tab()
            self.speak("Menutup tab aktif")
            return

        if any(key in cmd for key in ["refresh", "reload", "segarkan halaman"]):
            self.browser_controller.refresh_page()
            self.speak("Memuat ulang halaman")
            return

        if any(key in cmd for key in ["kembali", "back", "halaman sebelumnya"]):
            self.browser_controller.go_back()
            self.speak("Kembali ke halaman sebelumnya")
            return

        if any(key in cmd for key in ["maju", "forward", "halaman berikutnya"]):
            self.browser_controller.go_forward()
            self.speak("Ke halaman berikutnya")
            return

        if any(key in cmd for key in ["incognito", "mode incognito", "private tab"]):
            self.browser_controller.open_incognito()
            self.speak("Membuka browser dalam mode incognito")
            return

        if any(key in cmd for key in ["buka notepad", "open notepad", "notepad"]):
            self.system_controller.open_application("notepad")
            self.speak("Membuka Notepad")
            return

        if any(key in cmd for key in ["buka paint", "open paint", "paint", "mspaint"]):
            self.system_controller.open_application("mspaint")
            self.speak("Membuka Paint")
            return

        if any(key in cmd for key in ["buka kalkulator", "open calculator", "kalkulator", "calculator"]):
            self.system_controller.open_application("calculator")
            self.speak("Membuka Kalkulator")
            return

        if any(key in cmd for key in ["buka task manager", "open task manager", "task manager", "taskmgr"]):
            self.system_controller.open_application("taskmgr")
            self.speak("Membuka Task Manager")
            return

        if any(key in cmd for key in ["buka settings", "open settings", "windows settings", "pengaturan"]):
            self.system_controller.open_application("ms-settings:")
            self.speak("Membuka Pengaturan Windows")
            return

        if any(key in cmd for key in ["buka explorer", "buka file explorer", "buka folder", "open explorer", "open file explorer", "open folder"]):
            path = ""
            for keyword in [
                "buka folder",
                "open folder",
                "buka file explorer",
                "open file explorer",
                "buka explorer",
                "open explorer",
            ]:
                if keyword in cmd:
                    remainder = cmd.split(keyword, 1)[1].strip()
                    path = remainder.strip('"\'').strip()
                    break

            if path:
                self.system_controller.open_folder(path)
                self.speak(f"Membuka folder {path}")
            else:
                self.system_controller.open_file_explorer()
                self.speak("Membuka File Explorer")
            return

        if any(key in cmd for key in ["buka cmd", "open cmd", "buka terminal", "open terminal"]):
            self.system_controller.open_terminal()
            self.speak("Membuka terminal")
            return

        if any(key in cmd for key in ["jam berapa", "jam", "waktu"]):
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"Sekarang jam {now}")
            return

        if any(key in cmd for key in ["tanggal", "hari ini", "date"]):
            today = datetime.datetime.now().strftime("%d %B %Y")
            self.speak(f"Tanggal hari ini {today}")
            return

        if any(key in cmd for key in ["matikan komputer", "shutdown", "turn off"]):
            self.system_controller.shutdown_computer(10)
            self.speak("Komputer akan dimatikan dalam 10 detik")
            return

        if any(key in cmd for key in ["restart komputer", "restart"]):
            self.system_controller.restart_computer(10)
            self.speak("Komputer akan di restart dalam 10 detik")
            return

        if any(key in cmd for key in ["kunci komputer", "lock computer"]):
            self.system_controller.lock_computer()
            self.speak("Komputer telah dikunci")
            return

        if any(key in cmd for key in ["keluar", "exit", "stop", "berhenti"]):
            self.speak("Sampai jumpa!")
            self.is_running = False
            return

        self.speak("Perintah tidak dikenali. Coba: open chrome, search youtube, buka notepad, jam berapa, atau keluar")

    def run(self):
        print("=" * 60)
        print("AI ASSISTANT - WINDOWS READY")
        print("=" * 60)
        print()

        self.speak("Halo! Saya asisten AI Anda.")
        self.speak("Coba perintah seperti open chrome, atau search youtube")

        if self.recognizer is not None and self.microphone is not None:
            print("[*] Kalibrasi microphone...")
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("[OK] Microphone siap!")
            except Exception as e:
                print(f"[!] Error microphone: {e}")
                self._text_mode()
                return

            print()
            print("Perintah suara yang tersedia:")
            print("  - 'open chrome'         -> Buka Chrome")
            print("  - 'search youtube'      -> Buka YouTube")
            print("  - 'tab baru'            -> Buka tab baru")
            print("  - 'tutup tab'           -> Tutup tab aktif")
            print("  - 'refresh'             -> Refresh halaman")
            print("  - 'kembali'             -> Halaman sebelumnya")
            print("  - 'maju'                -> Halaman berikutnya")
            print("  - 'incognito'           -> Browser private")
            print("  - 'buka notepad'        -> Buka Notepad")
            print("  - 'buka kalkulator'     -> Buka Kalkulator")
            print("  - 'buka folder D:\\'     -> Buka folder")
            print("  - 'jam berapa'          -> Tampilkan jam")
            print("  - 'tanggal'             -> Tampilkan tanggal")
            print("  - 'matikan komputer'    -> Shutdown")
            print("  - 'exit' / 'keluar'     -> Keluar")
            print()

            while self.is_running:
                command = self.listen()
                if command:
                    self.process_command(command)
        else:
            print("[!] Mikrofon tidak tersedia. Mode teks aktif.")
            self._text_mode()

    def _text_mode(self):
        print()
        print("Mode input teks aktif. Ketik perintah:")
        print("  - open chrome")
        print("  - search youtube")
        print("  - tab baru")
        print("  - tutup tab")
        print("  - refresh")
        print("  - kembali")
        print("  - buka notepad")
        print("  - jam berapa")
        print("  - exit")
        print()

        while self.is_running:
            try:
                command = input(">>> ").strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                self.is_running = False
                break

            if command:
                self.process_command(command)


if __name__ == "__main__":
    asisten = AsistenAI()
    asisten.run()