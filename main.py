# main.py
from dotenv import load_dotenv
import os
from Huawei import Huawei

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Retrieve environment variables
    host = os.getenv('TELNET_HOST')
    username = os.getenv('TELNET_USERNAME')
    password = os.getenv('TELNET_PASSWORD')

    # Ensure all required environment variables are available
    if not all([host, username, password]):
        raise ValueError("Missing required environment variables. Please check your .env file.")

    # Create an instance of the Huawei class
    huawei_device = Huawei(host, username, password)
    huawei_device.privilege_exec_mode()
    huawei_device.enter_global_config_mode()

    # Send a command and print the output
    output = huawei_device.searchByDesc("hari")
    print(output)
    # print(huawei_device.output)

    # Close the Telnet session
    huawei_device.close_session()

if __name__ == "__main__":
    main()
