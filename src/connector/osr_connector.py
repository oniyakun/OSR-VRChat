import serial
import threading
import sys 
import time
import asyncio
import glob
import socket
from loguru import logger


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class OSRConnector:
    def __init__(self, ip=None, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ip = ip
        self.ser = None
        self.sock = None
        self.reader_thread = None
        self.writer_lock = threading.Lock()


    async def connect(self):
        # Run the blocking `connect` method in a separate thread using asyncio.to_thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._connect)

    def _connect(self):
        if (self.ip == None):
            try:
                self.ser = serial.Serial(self.port, self.baudrate)
                # self.reader_thread = threading.Thread(target=self.read_from_serial, daemon=True)
                # self.reader_thread.start()
                logger.info(f"Connected to {self.port} at {self.baudrate} baud.")
            except Exception as e:
                logger.error(f"Error connecting to serial port: {e}")
                self.ser = None
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # def read_from_serial(self):
    #     #只发送，不接收
    #     raise NotImplemented
    #     while self.ser and self.ser.is_open:
    #         if self.ser.in_waiting > 0:
    #             data = self.ser.readline().decode('utf-8').strip()
    #             if data:
    #                 print(f"[READ] {data}")
    #         else:
    #             # Optionally, add a sleep here to avoid 100% CPU usage
    #             pass

    async def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info(f"Disconnected from {self.port}.")
        else:
            logger.info("No connection to disconnect.")
    
    async def write_to_udp(self, *lines):
        if self.sock:
            for line in lines:
                logger.info(f"[UDP SEND] {line}")
                self.sock.sendto(f"{line}\n".encode('utf-8'), (self.ip, self.port))

    async def write_to_serial(self, *lines):
        if self.ser and self.ser.is_open:
            with self.writer_lock:
                for line in lines:
                    logger.info(f"[SEND] {line}")
                    self.ser.write(f"{line}\n".encode('utf-8'))
        else:
            logger.info("[WARN] Disconnected, skipping stream write.")

# Usage
# if __name__ == "__main__":
#     controller = OSRConnector(port='COM3', baudrate=115200)
    
#     # Connect to serial
#     controller.connect()
#     print(serial_ports())
    
#     # Send commands to the ESP32 (example)
#     controller.write_to_serial("L017")
    
#     time.sleep(0.5)

#     controller.write_to_serial("L037")
    
#     time.sleep(0.5)

#     controller.write_to_serial("L057")
    
#     time.sleep(0.5)

#     controller.write_to_serial("L077")
    
#     time.sleep(0.5)
#     # Wait for some time to read responses
    
#     time.sleep(5)
    
#     # Disconnect from serial
#     controller.disconnect()
