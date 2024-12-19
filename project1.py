import bluetooth
import json
import os
import time

# ESP32 MAC Addresses (replace with your ESP32 devices' MAC addresses)
ESP32_MAC_ADDRESS_1 = "C0:5D:89:B0:4A:C6"  # ESP32_1
ESP32_MAC_ADDRESS_2 = "C0:5D:89:AF:F7:6E"  # ESP32_2
PORT = 1
MAX_RETRIES = 5
FILE_NAME = "timestamps.json"

def connect_bluetooth(mac_address):
    """Connect to a Bluetooth device with the given MAC address."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Connecting to {mac_address} (Attempt {attempt}/{MAX_RETRIES})")
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((mac_address, PORT))
            sock.setblocking(False)  # Set socket to non-blocking mode
            print(f"Connected successfully to {mac_address}!")
            return sock
        except bluetooth.btcommon.BluetoothError as e:
            print(f"Connection failed: {e}")
            time.sleep(2)
    print(f"Failed to connect to {mac_address} after {MAX_RETRIES} attempts.")
    return None

def save_to_json(t1, T1):
    """Save t1 and T1 timestamps from both ESP32 devices to a JSON file."""
    data = {"t1": t1, "T1": T1}
    try:
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'w') as file:
                json.dump([data], file, indent=4)
        else:
            with open(FILE_NAME, 'r+') as file:
                file_data = json.load(file)
                file_data.append(data)
                file.seek(0)
                json.dump(file_data, file, indent=4)
        print(f"Saved to {FILE_NAME}: {data}")
    except Exception as e:
        print(f"Error saving to file: {e}")

def receive_timestamp(sock, device_name):
    """Receive a timestamp from the ESP32 device."""
    try:
        data = sock.recv(1024).decode("utf-8").strip()
        if data:
            print(f"{device_name} Received: '{data}'")
            if data.startswith("t1:") or data.startswith("T1:"):
                timestamp = float(data.split(":")[1].strip())
                return timestamp
    except bluetooth.btcommon.BluetoothError:
        pass  # No data received (non-blocking mode)
    return None

def main():
    """Main function to connect to ESP32 devices and handle communication."""
    sock1 = connect_bluetooth(ESP32_MAC_ADDRESS_1)
    sock2 = connect_bluetooth(ESP32_MAC_ADDRESS_2)

    if not sock1 or not sock2:
        print("Failed to establish Bluetooth connection to one or both ESP32 devices.")
        return

    try:
        while True:
            print("\nWaiting for timestamps from both ESP32 devices...")
            t1 = T1 = None

            # Wait up to 15 seconds to receive data from both devices
            timeout = 15
            end_time = time.time() + timeout

            while time.time() < end_time:
                t1 = t1 or receive_timestamp(sock1, "ESP32_1")
                T1 = T1 or receive_timestamp(sock2, "ESP32_2")

                if t1 is not None and T1 is not None:
                    break

                time.sleep(0.1)  # Small delay to prevent CPU overuse

            if t1 is not None and T1 is not None:
                save_to_json(t1, T1)
            else:
                print("Failed to receive timestamps from one or both devices.")

    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        sock1.close()
        sock2.close()
        print("Bluetooth connections closed.")

if __name__ == "__main__":
    main()
