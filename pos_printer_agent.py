#!/usr/bin/env python3
"""
Kotyol ERP - Local POS Print Agent v1.5 (64-bit WOW64 Registry & POS Candidate Try-List)
Fonda ishlaydigan lokal termoprint servisi (Port: 9123)

Vazifasi: Web brauzerdan kelgan chek so'rovlarini tutib olib, 
kompyuterdagi termoprinterga (Xprinter, Rongta, POS-80, XP-80C va b.) 
RAW ESC/POS rejimida 0.05 sekundda 100% tiniq chop etadi va qog'ozni kesadi.
"""

import sys
import os
import json
import tempfile
import subprocess
import ctypes
import winreg
from ctypes import wintypes
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 9123

COMMON_POS_CANDIDATES = [
    "XP-80C", "XP-80", "POS-80", "POS-58", "POS80", "POS58",
    "Xprinter", "Rongta", "Epson", "XP-365B", "XP-80C (Copy 1)",
    "XP-80C (Copy 2)", "XP-80 (Copy 1)", "POS-80 Printer"
]

# Auto-ensure pywin32 if possible
win32print = None
try:
    import win32print
except ImportError:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import win32print
    except Exception:
        win32print = None


def free_port_9123():
    try:
        current_pid = os.getpid()
        cmd = f'powershell -Command "$p = (Get-NetTCPConnection -LocalPort {PORT} -ErrorAction SilentlyContinue).OwningProcess; if($p -and $p -ne {current_pid}){{ Stop-Process -Id $p -Force }}"'
        subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception:
        pass


def get_installed_printers():
    printers = []

    # Locations in Windows Registry
    locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Print\Printers"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print\Printers"),
        (winreg.HKEY_CURRENT_USER, r"Control Panel\Print\Printers"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Devices"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\PrinterPorts")
    ]

    flags = [
        winreg.KEY_READ,
        winreg.KEY_READ | getattr(winreg, 'KEY_WOW64_64KEY', 0x0100),
        winreg.KEY_READ | getattr(winreg, 'KEY_WOW64_32KEY', 0x0200)
    ]

    for hive, path in locations:
        for flag in flags:
            try:
                key = winreg.OpenKey(hive, path, 0, flag)
                if "Devices" in path or "PrinterPorts" in path:
                    i = 0
                    while True:
                        try:
                            val_name, _, _ = winreg.EnumValue(key, i)
                            if val_name and val_name.strip() and val_name.strip() not in printers:
                                printers.append(val_name.strip())
                            i += 1
                        except OSError:
                            break
                else:
                    i = 0
                    while True:
                        try:
                            sub_key = winreg.EnumKey(key, i)
                            if sub_key and sub_key.strip() and sub_key.strip() not in printers:
                                printers.append(sub_key.strip())
                            i += 1
                        except OSError:
                            break
                winreg.CloseKey(key)
            except Exception:
                pass

    if win32print:
        try:
            w32_p = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            for p in w32_p:
                if p not in printers:
                    printers.append(p)
        except Exception:
            pass

    try:
        cmd = 'powershell -Command "Get-Printer | Select-Object -ExpandProperty Name"'
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
        ps_printers = [line.strip() for line in out.splitlines() if line.strip()]
        for p in ps_printers:
            if p not in printers:
                printers.append(p)
    except Exception:
        pass

    return printers


def get_default_printer_name():
    # 1. Try HKCU Device
    flags = [
        winreg.KEY_READ,
        winreg.KEY_READ | getattr(winreg, 'KEY_WOW64_64KEY', 0x0100)
    ]
    for flag in flags:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Windows", 0, flag)
            val, _ = winreg.QueryValueEx(key, "Device")
            winreg.CloseKey(key)
            if val:
                p_name = val.split(',')[0].strip()
                if p_name:
                    return p_name
        except Exception:
            pass

    # 2. Try win32print
    if win32print:
        try:
            p = win32print.GetDefaultPrinter()
            if p:
                return p
        except Exception:
            pass

    # 3. Smart POS Keyword Match
    all_printers = get_installed_printers()
    pos_keywords = ["xp-", "pos", "thermal", "rongta", "xprinter", "epson", "bixolon", "80c", "58mm", "80mm", "receipt"]
    for p in all_printers:
        p_lower = p.lower()
        for kw in pos_keywords:
            if kw in p_lower:
                return p

    if all_printers:
        return all_printers[0]

    return "XP-80C"


def print_raw_via_ctypes(printer_name, data_bytes):
    try:
        winspool = ctypes.windll.winspool.drv

        winspool.OpenPrinterW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.HANDLE), ctypes.c_void_p]
        winspool.OpenPrinterW.restype = wintypes.BOOL

        winspool.StartDocPrinterW.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p]
        winspool.StartDocPrinterW.restype = wintypes.DWORD

        winspool.StartPagePrinter.argtypes = [wintypes.HANDLE]
        winspool.StartPagePrinter.restype = wintypes.BOOL

        winspool.WritePrinter.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
        winspool.WritePrinter.restype = wintypes.BOOL

        winspool.EndPagePrinter.argtypes = [wintypes.HANDLE]
        winspool.EndPagePrinter.restype = wintypes.BOOL

        winspool.EndDocPrinter.argtypes = [wintypes.HANDLE]
        winspool.EndDocPrinter.restype = wintypes.BOOL

        winspool.ClosePrinter.argtypes = [wintypes.HANDLE]
        winspool.ClosePrinter.restype = wintypes.BOOL

        handle = wintypes.HANDLE()
        if not winspool.OpenPrinterW(printer_name, ctypes.byref(handle), None):
            err = ctypes.GetLastError()
            return False, f"Printerni ochib bo'lmadi: '{printer_name}' (Xatolik {err})"

        class DOC_INFO_1W(ctypes.Structure):
            _fields_ = [
                ("pDocName", wintypes.LPCWSTR),
                ("pOutputFile", wintypes.LPCWSTR),
                ("pDatatype", wintypes.LPCWSTR),
            ]

        doc_info = DOC_INFO_1W("Kotyol POS Receipt", None, "RAW")

        try:
            job_id = winspool.StartDocPrinterW(handle, 1, ctypes.byref(doc_info))
            if job_id <= 0:
                err = ctypes.GetLastError()
                return False, f"StartDocPrinterW xatosi ({err}) on '{printer_name}'"

            try:
                winspool.StartPagePrinter(handle)
                written = wintypes.DWORD(0)
                winspool.WritePrinter(handle, data_bytes, len(data_bytes), ctypes.byref(written))
                winspool.EndPagePrinter(handle)
            finally:
                winspool.EndDocPrinter(handle)
        finally:
            winspool.ClosePrinter(handle)

        return True, f"Printerga muvaffaqiyatli uzatildi: {printer_name}"
    except Exception as e:
        return False, f"ctypes winspool xatosi: {str(e)}"


def print_raw_to_printer(printer_name, data_bytes):
    if not printer_name:
        printer_name = get_default_printer_name()

    printers_to_try = []
    if printer_name:
        printers_to_try.append(printer_name)

    all_printers = get_installed_printers()
    for p in all_printers:
        if p not in printers_to_try:
            printers_to_try.append(p)

    for cand in COMMON_POS_CANDIDATES:
        if cand not in printers_to_try:
            printers_to_try.append(cand)

    last_error = ""
    for target_printer in printers_to_try:
        # 1. Try win32print
        if win32print:
            try:
                hprinter = win32print.OpenPrinter(target_printer)
                try:
                    hjob = win32print.StartDocPrinter(hprinter, 1, ("Kotyol POS Receipt", None, "RAW"))
                    try:
                        win32print.StartPagePrinter(hprinter)
                        win32print.WritePrinter(hprinter, data_bytes)
                        win32print.EndPagePrinter(hprinter)
                    finally:
                        win32print.EndDocPrinter(hprinter)
                finally:
                    win32print.ClosePrinter(hprinter)
                return True, f"Printerga muvaffaqiyatli uzatildi: {target_printer}"
            except Exception as e:
                last_error = f"win32print ({target_printer}): {e}"

        # 2. Try ctypes winspool
        ok, msg = print_raw_via_ctypes(target_printer, data_bytes)
        if ok:
            return True, msg
        else:
            last_error = msg

    return False, f"Kompyuterda o'rnatilgan printer topilmadi. So'nggi xatolik: {last_error}"


class POSPrintHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        printers = get_installed_printers()
        default_p = get_default_printer_name()
        resp = {
            "status": "online",
            "agent": "Kotyol Local POS Print Agent v1.5",
            "port": PORT,
            "printers": printers,
            "default_printer": default_p or "XP-80C"
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        raw_text = data.get("raw_text") or data.get("text") or ""
        escpos_hex = data.get("escpos_hex") or ""
        printer_name = data.get("printer_name") or None

        if escpos_hex:
            try:
                print_bytes = bytes.fromhex(escpos_hex)
            except Exception:
                print_bytes = raw_text.encode('utf-8')
        else:
            # Init + Text + Cut paper ESC/POS bytes
            esc_init = b"\x1b\x40"
            esc_cut = b"\x1d\x56\x41\x03"
            print_bytes = esc_init + raw_text.encode('utf-8', errors='ignore') + esc_cut

        success, msg = print_raw_to_printer(printer_name, print_bytes)

        res = {
            "success": success,
            "message": msg
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        print(f"[POS Agent Log] {self.address_string()} - {format%args}")


def run():
    free_port_9123()
    default_p = get_default_printer_name()
    printers = get_installed_printers()
    print("=" * 60)
    print("  Kotyol ERP - Local POS Thermal Print Agent v1.5")
    print("=" * 60)
    print(f"  Server ishga tushdi: http://{HOST}:{PORT}")
    print(f"  Standart printer: {default_p or 'XP-80C'}")
    print(f"  Barcha printerlar: {', '.join(printers) if printers else 'XP-80C, POS-80'}")
    print("  Status va printerlarni ko'rish: http://localhost:9123/")
    print("  Brauzer so'rovlarini kutmoqda...")
    print("=" * 60)

    server = HTTPServer((HOST, PORT), POSPrintHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAgent to'xtatildi.")
        server.server_close()


if __name__ == "__main__":
    run()
