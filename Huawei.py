import telnetlib
import logging
from datetime import datetime
import os

class Huawei:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.tn = None
        self.current_mode = None
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

    def telnet_session(self):
        try:
            self.tn = telnetlib.Telnet(self.host, timeout=360)
            self.tn.read_until(b"Username:")
            self.tn.write(self.username.encode('ascii') + b"\n")
            self.tn.read_until(b"Password:")
            self.tn.write(self.password.encode('ascii') + b"\n")
            self.current_mode = 'user_exec'
            self.logger.info("Telnet session established successfully")
        except Exception as e:
            self.logger.error(f"Failed to establish Telnet session: {e}")

    def enter_user_exec_mode(self):
        if self.current_mode != 'user_exec':
            self.tn.write(b"\n")
            self.tn.read_until(b">")
            self.current_mode = 'user_exec'
            self.logger.info("Entered user exec mode")

    def enter_privilege_exec_mode(self):
        if self.current_mode != 'privilege_exec':
            if self.current_mode == 'global_config':
                self.exit_global_config_mode()
            self.tn.write(b"enable\n")
            index, _, _ = self.tn.expect([b"Password:", b"#"], timeout=5)
            if index == 0:
                self.tn.write(self.password.encode('ascii') + b"\n")
                self.tn.read_until(b"#")
            self.current_mode = 'privilege_exec'
            self.logger.info("Entered privilege exec mode")

    def enter_global_config_mode(self):
        if self.current_mode != 'global_config':
            self.enter_privilege_exec_mode()
            self.tn.write(b"configure terminal\n")
            self.tn.read_until(b"(config)#")
            self.current_mode = 'global_config'
            self.logger.info("Entered global config mode")

    def exit_global_config_mode(self):
        if self.current_mode == 'global_config':
            self.tn.write(b"exit\n")
            self.tn.read_until(b"#")
            self.current_mode = 'privilege_exec'
            self.logger.info("Exited global config mode")

    def send_command(self, command):
        self.logger.info(f"Sending command: {command}")
        self.tn.write(command.encode('ascii') + b"\n")
        response = self.tn.read_until(b"#").decode('ascii')
        self.logger.info(f"Response: {response}")
        return response

    def close_session(self):
        self.tn.write(b"exit\n")
        self.tn.close()
        self.logger.info("Telnet session closed")

