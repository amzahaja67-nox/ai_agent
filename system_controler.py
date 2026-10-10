import os
import platform
import shutil
import subprocess


class SystemController:
    def __init__(self):
        self.os_type = platform.system()

    def open_application(self, app_name):
        """Buka aplikasi sesuai sistem operasi."""
        app_name = (app_name or "").strip()
        if not app_name:
            return False

        app_lower = app_name.lower()

        try:
            if self.os_type == "Windows":
                mapping = {
                    "chrome": "start chrome",
                    "google chrome": "start chrome",
                    "notepad": "notepad",
                    "text editor": "notepad",
                    "paint": "mspaint",
                    "mspaint": "mspaint",
                    "calculator": "calc",
                    "kalkulator": "calc",
                    "explorer": "explorer",
                    "file explorer": "explorer",
                    "cmd": "cmd",
                    "command prompt": "cmd",
                    "terminal": "cmd",
                    "powershell": "powershell",
                    "task manager": "taskmgr",
                    "taskmgr": "taskmgr",
                    "settings": "start ms-settings:",
                    "windows settings": "start ms-settings:",
                    "pengaturan": "start ms-settings:",
                }

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

                os.system(f'start "" "{app_name}"')
                return True

            elif self.os_type == "Darwin":
                if app_lower == "chrome":
                    subprocess.Popen(["open", "-a", "Google Chrome"])
                    return True
                subprocess.Popen(["open", "-a", app_name])
                return True

            elif self.os_type == "Linux":
                if app_lower == "chrome":
                    subprocess.Popen(["google-chrome"])
                    return True
                subprocess.Popen([app_name.lower()])
                return True

            return False

        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            return False

    def open_file_explorer(self, path=None):
        """Buka file explorer di path tertentu."""
        if path is None:
            path = os.path.expanduser("~")

        try:
            if self.os_type == "Windows":
                os.startfile(path)
            elif self.os_type == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return True
        except Exception as e:
            print(f"Error opening explorer: {e}")
            return False

    def open_folder(self, path):
        """Buka folder tertentu di file explorer."""
        if not path:
            return self.open_file_explorer()

        if os.path.exists(path):
            return self.open_file_explorer(path)

        print(f"Folder tidak ditemukan: {path}")
        return False

    def open_file(self, file_path):
        """buka file menggunakan aplikasi default."""
        if not file_path or not os.path.exists(file_path):
            print(f"File tidak ditemukan: {file_path}")
            return False

        try:
            if self.os_type == "Windows":
                os.startfile(file_path)
            elif self.os_type == "Darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False

    def open_terminal(self):
        """Buka terminal command prompt pada Windows."""
        try:
            if self.os_type == "Windows":
                subprocess.Popen("cmd /k cd /d %USERPROFILE%", shell=True)
                return True
            return False
        except Exception as e:
            print(f"Error opening terminal: {e}")
            return False

    def shutdown_computer(self, seconds=10):
        """Matikan komputer setelah beberapa detik."""
        try:
            if self.os_type == "Windows":
                subprocess.run(["shutdown", "/s", "/t", str(seconds)], check=False)
                return True
            return False
        except Exception as e:
            print(f"Error shutdown: {e}")
            return False

    def restart_computer(self, seconds=10):
        """Restart komputer setelah beberapa detik."""
        try:
            if self.os_type == "Windows":
                subprocess.run(["shutdown", "/r", "/t", str(seconds)], check=False)
                return True
            return False
        except Exception as e:
            print(f"Error restart: {e}")
            return False

    def lock_computer(self):
        """Kunci komputer."""
        try:
            if self.os_type == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
                return True
            return False
        except Exception as e:
            print(f"Error lock: {e}")
            return False