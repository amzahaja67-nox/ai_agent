# System Controller

Python utility sederhana untuk mengontrol sistem operasi dari kode.

## Fitur

- membuka aplikasi seperti Chrome, Notepad, Calculator, Explorer, Terminal
- membuka file atau folder
- membuka file explorer ke path tertentu
- mengunci komputer
- mematikan atau restart komputer dengan delay

## Contoh penggunaan

```python
from system_controler import SystemController

controller = SystemController()

controller.open_application("chrome")
controller.open_file_explorer(r"C:\Users\YourName\Downloads")
controller.open_folder(r"C:\Users\YourName\Documents")
controller.open_file(r"C:\Users\YourName\Documents\notes.txt")
controller.open_terminal()
```

## Sistem operasi yang didukung

- Windows
- macOS
- Linux

## Peringatan

Fungsi seperti `shutdown_computer()`, `restart_computer()`, dan `lock_computer()` dapat memengaruhi sistem secara langsung. Gunakan dengan hati-hati dan hanya pada komputer yang Anda kendalikan.

## License

MIT / bebas digunakan untuk kebutuhan personal dan edukasi.
