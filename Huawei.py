import telnetlib
import logging
from datetime import datetime
import os
import re


class Huawei:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.tn = None
        self.current_mode = None
        self.setup_logging()
        self.output = None
        self.setup_logging()
        self.logger.info("Establishing Telnet Session")
        self.telnet_session()
        
    def setup_logging(self):
        if not os.path.exists('log'):
            os.makedirs('log')
        log_filename = datetime.now().strftime("log/huawei_%Y-%m-%d_%H-%M-%S.log")
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger()

    def print_and_log(self, message):
        print(message)
        self.logger.info(message)
        
        
    def telnet_session(self):
        try:
            self.tn = telnetlib.Telnet(self.host, timeout=360)
            self.output = str(self.tn.read_until(b">>User name:"))
            self.tn.write(self.username.encode('ascii') + b"\n")
            self.output = self.output + "\n" + str(self.tn.read_until(b">>User password:"))
            self.tn.write(self.password.encode('ascii') + b"\n")
            self.current_mode = 'user_exec'
            self.output = self.output + "\n" + self.tn.read_until(b">>", timeout=5).decode('ascii').strip()
            self.logger.info("Telnet session established successfully")
        except Exception as e:
            self.logger.error(f"Failed to establish Telnet session: {e}")
        
    def privilege_exec_mode(self):
        if self.current_mode == "user_exec":
            self.tn.write(b"enable\n")
            index, _, _ = self.tn.expect([b"Password:", b"#"], timeout=5)
            if index == 0:
                self.tn.write(self.password.encode('ascii') + b"\n")
            self.tn.write(b"\n")
            self.output = self.output + "\n" + self.tn.read_until(b">>", timeout=5).decode('ascii').strip()
            self.current_mode = 'privilege_exec'
            self.print_and_log("Entered privilege exec mode")
        if self.current_mode == "global_config":
            self.tn.write(b"quit\n")
            self.tn.write(b"\n")
            self.output = self.output + "\n" + self.tn.read_until(b">>", timeout=5).decode('ascii').strip()
            self.current_mode = 'privilege_exec'
            self.print_and_log("Entered privilege exec mode")

    def enter_global_config_mode(self):
        if self.current_mode == "privilege_exec":
            self.tn.write(b"config\n")
            self.tn.write(b"\n")
            self.output = self.output + "\n" + self.tn.read_until(b">>", timeout=5).decode('ascii').strip()
            self.current_mode = "global_config"
            self.print_and_log("Entered Global configuration mode")
    
    def send_command(self, command):
        self.logger.info(f"Sending command: {command}")
        self.tn.write(command.encode('ascii') + b"\n")
        self.tn.write(b"\n")
        
        response = self.tn.read_until(b">>", timeout=5).decode('ascii').strip()
        self.output = self.output + "\n" + response
        self.logger.info(f"Response: {response}")
        
    
    def parse_ont_info(self, response):
        # Regular expressions to extract required information
        ont_info_pattern = re.compile(r'(\d+/\s*\d+/\d+)\s+(\d+)\s+(\w+)\s+\w+\s+(\w+)\s+\w+\s+\w+\s+\w+')
        description_pattern = re.compile(r'(\d+/\s*\d+/\d+)\s+(\d+)\s+(\S+)', re.MULTILINE)

        ont_info = ont_info_pattern.findall(response)
        descriptions = description_pattern.findall(response)

        result = []
        for ont in ont_info:
            fsp, ont_id, sn, state = ont
            for desc in descriptions:
                desc_fsp, desc_ont_id, description = desc
                if fsp == desc_fsp and ont_id == desc_ont_id and sn != description:
                    result.append({'fsp': fsp, 'ont_id': ont_id, 'sn': sn, 'state': state, 'description': description})
                    break

        return result
    
    def searchByDesc(self,desc):
        cmd = "display ont info by-desc " + desc +"\n"
        self.print_and_log(f"Search ByDescription : {desc}")
        self.tn.write(cmd.encode('ascii'))
        output = ""
        while True:
            # Read the output from the command
            chunk = self.tn.read_until(b"---- More ( Press 'Q' to break ) ----", timeout=10).decode('ascii')
            output += chunk
            if "---- More ( Press 'Q' to break ) ----" in chunk:
                # If the pagination prompt is found, send newlines to get more output
                self.tn.write(b"\n")
            else:
                # Break the loop if no pagination prompt is found
                break
        self.output = self.output + "\n" + output
        response = self.parse_ont_info(output)
        return response
    
    def close_session(self):
        self.tn.write(b"exit\n")
        self.tn.close()
        self.logger.info("Telnet session closed")

