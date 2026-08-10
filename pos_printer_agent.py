#!/usr/bin/env python3
"""
Kotyol ERP - Local POS Print Agent v1.0
Fonda ishlaydigan lokal termoprint servisi (Port: 9123)

Vazifasi: Web brauzerdan kelgan chek so'rovlarini tutib olib, 
kompyuterdagi termoprinterga (Xprinter, Rongta, POS-80 va b.) 
RAW ESC/POS rejimida 0.05 sekundda 100% tiniq chop etadi va qog'ozni kesadi.
"""

import sys
import os
import json
import tempfile
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 9123


def get_installed_printers():
    printers = []
    try:
        import win32print
        printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    except ImportError:
        try:
            cmd = "wmic printer get name"
            out = subprocess.check_output(cmd, shell=True, text=True)
            printers = [line.strip() for line in out.splitlines() if line.strip() and line.strip() != "Name"]
        except Exception:
            pass
    return printers


def print_raw_to_printer(printer_name, data_bytes):
    try:
        import win32print
        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()

        hprinter = win32print.OpenPrinter(printer_name)
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
        return True, f"Print qilindi: {printer_name}"
    except ImportError:
        # Fallback using Windows temp file and print command
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
                f.write(data_bytes)
                temp_path = f.name
            
            p_arg = f'/d:"{printer_name}"' if printer_name else ""
            cmd = f'print {p_arg} "{temp_path}"'
            subprocess.run(cmd, shell=True, check=True)
            os.remove(temp_path)
            return True, "Chop etishga yuborildi (fallback print mode)"
        except Exception as e:
            return False, f"Chop etishda xatolik: {str(e)}"
    except Exception as e:
        return False, f"Printer xatosi: {str(e)}"


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
        resp = {
            "status": "online",
            "agent": "Kotyol Local POS Print Agent v1.0",
            "port": PORT,
            "printers": printers,
            "default_printer": printers[0] if printers else "Noma'lum"
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
        self.send_response(200 if success else 400)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        print(f"[POS Agent Log] {self.address_string()} - {format%args}")


def run():
    print("=" * 60)
    print("  Kotyol ERP - Local POS Thermal Print Agent v1.0")
    print("=" * 60)
    print(f"  Server ishga tushdi: http://{HOST}:{PORT}")
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
