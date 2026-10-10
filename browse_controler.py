import os
import shutil
import subprocess
import urllib.parse
import webbrowser

try:
    import pyautogui
except ImportError:
    pyautogui = None


class BrowserController:
    def __init__(self):
        self.browser = None
        if os.name == 'nt':
            self.os_type = "Windows"
        elif os.name == 'posix':
            if os.uname().sysname == 'Darwin':
                self.os_type = "Darwin"
            else:
                self.os_type = "Linux"
        else:
            self.os_type = "Unknown"

    def _hotkey(self, *keys):
        if pyautogui is None:
            return False
        pyautogui.hotkey(*keys)
        return True

    def search_google(self, query):
        """Buka Google dengan query tertentu."""
        if not query:
            return False
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(search_url)
        return True

    def open_website(self, url):
        """Buka website tertentu."""
        if not url:
            return False
        if not url.startswith('http'):
            url = 'https://' + url
        webbrowser.open(url)
        return True

    def open_incognito(self, url=None):
        """Buka Chrome dalam mode incognito."""
        try:
            if url and not url.startswith('http'):
                url = 'https://' + url

            if self.os_type == "Windows":
                args = ['cmd', '/c', 'start', '', 'chrome', '--incognito']
                if url:
                    args.append(url)
                subprocess.Popen(args)
                return True

            if self.os_type == "Darwin":
                args = ['open', '-a', 'Google Chrome', '--args', '--incognito']
                if url:
                    args.append(url)
                subprocess.Popen(args)
                return True

            if self.os_type == "Linux":
                args = ['google-chrome', '--incognito']
                if url:
                    args.append(url)
                try:
                    subprocess.Popen(args)
                    return True
                except FileNotFoundError:
                    try:
                        args[0] = 'chromium'
                        subprocess.Popen(args)
                        return True
                    except FileNotFoundError:
                        pass

            if url:
                webbrowser.open(url)
            else:
                webbrowser.open('https://www.google.com')
            return True
        except Exception as e:
            print(f"[!] Gagal membuka incognito: {e}")
            return False

    def search_youtube(self, query):
        """Cari di YouTube."""
        if not query:
            return False
        encoded_query = urllib.parse.quote(query)
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(youtube_url)
        return True

    def close_browser_tab(self):
        """Tutup tab aktif."""
        return self._hotkey('ctrl', 'w')

    def new_browser_tab(self):
        """Buka tab baru."""
        return self._hotkey('ctrl', 't')

    def refresh_page(self):
        """Refresh halaman aktif."""
        return self._hotkey('ctrl', 'r')

    def go_back(self):
        """Kembali ke halaman sebelumnya."""
        return self._hotkey('alt', 'left')

    def go_forward(self):
        """Ke halaman berikutnya."""
        return self._hotkey('alt', 'right')

    def open_new_window(self):
        """Buka jendela browser baru."""
        return self._hotkey('ctrl', 'n')

    def open_application(self, app_name):
        """Buka aplikasi tertentu berdasarkan nama."""
        if not app_name:
            return False

        app_lower = app_name.lower()
        mapping = {
            "chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "vlc": "vlc",
            "spotify": "spotify",
        }

        try:
            if self.os_type == "Windows":
                if app_lower in mapping:
                    command = mapping[app_lower]
                    if " " in command or command.startswith("start "):
                        subprocess.Popen(command, shell=True)
                    else:
                        subprocess.Popen(command.split())
                    return True

                found = shutil.which(app_name)
                if found:
                    subprocess.Popen([found])
                    return True

                subprocess.Popen(['cmd', '/c', 'start', '', app_name])
                return True

            elif self.os_type == "Darwin":
                if app_lower == "chrome":
                    subprocess.Popen(["open", "-a", "Google Chrome"])
                    return True
                subprocess.Popen(["open", "-a", app_name])
                return True

            elif self.os_type == "Linux":
                if app_lower == "chrome":
                    try:
                        subprocess.Popen(["google-chrome"])
                    except FileNotFoundError:
                        subprocess.Popen(["chromium"])
                    return True
                subprocess.Popen([app_name.lower()])
                return True

            return False

        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            return False

    def close_browser_window(self):
        """Tutup jendela browser aktif."""
        return self._hotkey('alt', 'f4')

    def scroll_down(self):
        """scroll ke bawah."""
        if pyautogui is None:
            return False
        pyautogui.scroll(-500)
        return True

    def scroll_up(self):
        """scroll ke atas."""
        if pyautogui is None:
            return False
        pyautogui.scroll(500)
        return True
