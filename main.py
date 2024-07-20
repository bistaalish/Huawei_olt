# main.py
from Huawei import Huawei

def main():
    # Creating an instance of the Huawei class
    huawei_device = Huawei("AX3 Pro", "1.0.0")

    # # Display the current information
    # print(huawei_device.display_info())

    # # Update the firmware
    # print(huawei_device.update_firmware("1.1.0"))

    # # Display the updated information
    print(huawei_device.display_info())

if __name__ == "__main__":
    main()
