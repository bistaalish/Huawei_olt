# main.py
from Huawei import Huawei

def main():
    # Replace with actual host, username, and password
    host = "100.126.255.7"
    username = "alishbista@firstlink.net.np"
    password = "password"

    # Creating an instance of the Huawei class
    huawei_device = Huawei(host, username, password)

    # Enter privilege exec mode
    huawei_device.enter_privilege_exec_mode()

    # Enter global configuration mode
    huawei_device.enter_global_config_mode()

    # Send a command and print the output
    output = huawei_device.send_command("display version")
    print(output)

    # Close the Telnet session
    huawei_device.close_session()

if __name__ == "__main__":
    main()
