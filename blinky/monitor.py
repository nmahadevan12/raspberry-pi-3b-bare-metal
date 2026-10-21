#!/usr/bin/env python3
"""Small serial monitor for bare-metal Raspberry Pi work.

Shows what the Pi sends over its UART, and sends whatever you type
(press Enter to send a line). Press Ctrl-C to quit.

Examples:
  python3 monitor.py                      auto-detect the USB-serial adapter, 115200 baud
  python3 monitor.py --list               list serial ports and exit
  python3 monitor.py -p /dev/cu.usbserial-0001 -b 115200
  python3 monitor.py --hex                hex + ASCII dump (good for binary data)
  python3 monitor.py --timestamps --log run1.txt

Needs pyserial:  pip install pyserial
"""

import argparse
import datetime
import glob
import sys
import threading
import time

try:
    import serial
    from serial import SerialException
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is not installed. Run: pip install pyserial")

# Names macOS (and Linux) give to common USB-serial adapters.
# Use the /dev/cu.* entries on a Mac, not /dev/tty.*.
PORT_PATTERNS = [
    "/dev/cu.usbserial*",
    "/dev/cu.usbmodem*",
    "/dev/cu.SLAB_USBtoUART*",
    "/dev/cu.wchusbserial*",
    "/dev/ttyUSB*",
    "/dev/ttyACM*",
]

EOLS = {"cr": b"\r", "lf": b"\n", "crlf": b"\r\n", "none": b""}


def find_ports():
    found = []
    for pattern in PORT_PATTERNS:
        found.extend(sorted(glob.glob(pattern)))
    return found


def timestamp():
    now = datetime.datetime.now()
    return now.strftime("[%H:%M:%S.") + f"{now.microsecond // 1000:03d}] "


class Output:
    """Writes to the screen and, optionally, a log file."""

    def __init__(self, log_path):
        self.log = open(log_path, "a", encoding="utf-8") if log_path else None

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()
        if self.log:
            self.log.write(text)
            self.log.flush()

    def close(self):
        if self.log:
            self.log.close()


class TextView:
    """Shows incoming bytes as text.

    CR is dropped (so CRLF becomes a normal newline). Bytes that are not
    printable ASCII are shown as \\xNN so nothing is silently lost.
    """

    def __init__(self, out, timestamps):
        self.out = out
        self.timestamps = timestamps
        self.at_line_start = True

    def feed(self, data):
        pieces = []
        for b in data:
            if b == 0x0D:
                continue
            if b == 0x0A:
                pieces.append("\n")
                self.at_line_start = True
                continue
            if self.at_line_start and self.timestamps:
                pieces.append(timestamp())
            self.at_line_start = False
            if b == 0x09 or 0x20 <= b < 0x7F:
                pieces.append(chr(b))
            else:
                pieces.append(f"\\x{b:02x}")
        if pieces:
            self.out.write("".join(pieces))

    def flush(self):
        pass


class HexView:
    """Shows incoming bytes as a hex dump: offset, 16 hex bytes, ASCII."""

    def __init__(self, out):
        self.out = out
        self.buf = bytearray()
        self.offset = 0

    def _row(self, row):
        hex_part = " ".join(f"{b:02x}" for b in row).ljust(47)
        ascii_part = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in row)
        line = f"{self.offset:08x}  {hex_part}  |{ascii_part}|\n"
        self.offset += len(row)
        return line

    def feed(self, data):
        self.buf.extend(data)
        lines = []
        while len(self.buf) >= 16:
            lines.append(self._row(bytes(self.buf[:16])))
            del self.buf[:16]
        if lines:
            self.out.write("".join(lines))

    def flush(self):
        """Print a partial last row (called when the line goes quiet)."""
        if self.buf:
            row = bytes(self.buf)
            self.buf.clear()
            self.out.write(self._row(row))


def send_lines(ser, eol):
    """Runs in a thread: sends each line you type."""
    try:
        for line in sys.stdin:
            ser.write(line.rstrip("\r\n").encode() + eol)
    except (SerialException, OSError, ValueError):
        pass


def parse_args():
    p = argparse.ArgumentParser(description="Serial monitor for the Pi's UART")
    p.add_argument("-p", "--port", help="serial port (default: auto-detect)")
    p.add_argument("-b", "--baud", type=int, default=115200, help="baud rate (default 115200)")
    p.add_argument("--hex", action="store_true", help="show a hex + ASCII dump instead of text")
    p.add_argument("--timestamps", action="store_true", help="prefix each text line with a time")
    p.add_argument("--log", metavar="FILE", help="also append the output to FILE")
    p.add_argument("--eol", choices=EOLS, default="crlf", help="line ending added to lines you send (default crlf)")
    p.add_argument("--list", action="store_true", help="list serial ports and exit")
    return p.parse_args()


def main():
    args = parse_args()

    if args.list:
        ports = list_ports.comports()
        if not ports:
            print("No serial ports found.")
        for port in ports:
            print(f"{port.device}  {port.description}")
        return 0

    port = args.port
    if not port:
        candidates = find_ports()
        if not candidates:
            print("No USB-serial adapter found. Plug it in, or pass --port.", file=sys.stderr)
            print("All ports: python3 monitor.py --list", file=sys.stderr)
            return 1
        port = candidates[0]
        if len(candidates) > 1:
            print(f"Several adapters found, using {port}. Others: {', '.join(candidates[1:])}", file=sys.stderr)

    try:
        ser = serial.Serial(port, args.baud, timeout=0.05)
    except SerialException as e:
        print(f"Could not open {port}: {e}", file=sys.stderr)
        print("If another program (screen, another monitor) has the port open, close it first.", file=sys.stderr)
        return 1

    out = Output(args.log)
    view = HexView(out) if args.hex else TextView(out, args.timestamps)
    print(f"Connected to {port} at {args.baud} baud. Type + Enter to send, Ctrl-C to quit.", file=sys.stderr)

    threading.Thread(target=send_lines, args=(ser, EOLS[args.eol]), daemon=True).start()

    total = 0
    last_rx = time.monotonic()
    status = 0
    try:
        while True:
            data = ser.read(ser.in_waiting or 1)
            if data:
                total += len(data)
                last_rx = time.monotonic()
                view.feed(data)
            elif args.hex and time.monotonic() - last_rx > 0.25:
                view.flush()
    except KeyboardInterrupt:
        pass
    except (SerialException, OSError) as e:
        print(f"\nSerial error: {e}", file=sys.stderr)
        status = 1
    finally:
        view.flush()
        out.close()
        try:
            ser.close()
        except Exception:
            pass
        print(f"\n{total} bytes received.", file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main())

