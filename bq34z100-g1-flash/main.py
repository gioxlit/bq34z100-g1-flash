#!/usr/env/python
# -*- coding: utf-8 -*-
"""bq34z100-g1-flash: A firmware flasher for the TI Fuel Gauge

This module flashes firmware on to the TI bq34z100-g1 fuel gauge for use in the OpenROV Trident

Reference documentation: http://www.ti.com/lit/an/slua665/slua665.pdf

Example:
	$ python main.py [-f | --flash] [path to image.srec]

Todo:

"""
import argparse
import os
import smbus
import sys
import time

# Script wide vars
FUEL_GAUGE_ADDRESS = 0x55

# Device switches i2c address when in ROM mode
ROM_ADDRESS = 0x0b

def flash_image(image_in, port=1):
    """Main function to flash an .srec image to the fuel gauge

    Args:
        image_in (str): Path to the image file
        port (int, optional): The i2c port to open

    Returns:
        None. Script will fail if there is a failure
    """
    print("Starting flashing process...")

    # Set up an SMBus object to interface with the i2c
    # Port Example: 1 = /dev/i2c-1
    try:
        bus = smbus.SMBus(port)
    except IOError:
        # port couldn't be opened. Let the user know
        i2c_port = '/dev/i2c-' + str(port)
        print('Could not open: {}'.format(i2c_port))
        print('Aborting.')
        sys.exit()

    # Put the device into ROM Mode
    put_device_into_rom_mode(bus)

    # mass erase data flash
    mass_erase_data_flash(bus)

def mass_erase_data_flash(bus):
    """Mass erases data flash as per the TI documentation

    Args:
        bus (SMBus): A handle to the SMBus object to interface with the i2c

    Returns:
        None
    """
    print("Starting mass erase data flash...")
    





def is_valid_image_file(file_in):
    """Checks the user provided path to the firmware image to see if it is valid

    Args:
        file_in (str): The path to the image file

    Returns:
        bool: if the image is valid. True for success, False otherwise
    """
    
    # Check if the file is, ya know, a file
    if not os.path.isfile(file_in):
        return False

    # Check if it has the srec extension
    filename, file_extension = os.path.splitext(file_in)
    if not file_extension == '.srec':
        return False

    return True

def put_device_into_rom_mode(bus):
    """Drops the device into ROM mode to begin flashing data

    Args:
        bus (SMBus): A handle to a SMBus object to interface to the i2c
    
    Returns:
        None: The script will exit out if there is a problem
    """
    print("Putting the fuel gauge into ROM mode...")
    
    output_values = [0xff, 0xff]
    control_reg = 0x00
   
    # Init?
    write_block_data(bus, control_reg, output_values, FUEL_GAUGE_ADDRESS)
    write_block_data(bus, control_reg, output_values, FUEL_GAUGE_ADDRESS)
    
    # Wait for 0.2 seconds
    wait(0.2)

    # Write more
    output_values_2 = [0x0f, 0x00]
    write_block_data(bus, control_reg, output_values_2, FUEL_GAUGE_ADDRESS)

    # Wait more
    wait(0.2)

    # Fuel gauge should be in ROM mode. New address should now be i2c 0x16
    print("Fuel gauge is in ROM mode.")

def swapbytes(bytes_in):
    """Swaps a list of bytes to conform with TI's documentation

    Example:
        input = [0x0f, 0x00]
        output = swapbytes(input)
        print output
        >>> [0x00, 0x0f]

    Args:
        bytes_in (2 element list): a list of bytes to swap
    Returns:
        list: The swapped bytes
    """
    bytes_in[0], bytes_in[1] = bytes_in[1], bytes_in[0]
    return bytes_in

def wait(sec):
    """Waits for a specified amount of seconds. Wrapper

    Args:
        sec (float): The amount of seconds to wait
    
    Returns:
        None
    """
    time.sleep(sec)

def write_block_data(bus, register, values, device):
    """Wrapper over the SMBus write block data to conform with the TI documentation

    Args: 
        bus (SMBus): A handle to the i2c interface
        register (hex): The register to write to
        values (list): The bytes to write to the devive register
        device (hex): The device i2c address

    Returns:
        None
    """
    bus.write_i2c_block_data(device, register, swapbytes(values))

def write_byte_data(bus, register, value, device):
    """Wrapper over the SMBus write byte data to conform with the TI documentation

    Args:
        bus (SMBus): A handle to the i2c interface
        register (hex): The register to write to
        values (list): The byte to write to the devive register
        device (hex): The device i2c address
    Returns:
        None
    """
    bus.write_byte_data(device, register, value)

def main():
    """Main function, the main entry point to the script
    
    Args:
        None
    Returns:
        None
    """

    # Get the argurments passed from the command line
    argument_parser = argparse.ArgumentParser(description='Firmware flasher for TI Fuel Gauge')
    argument_parser.add_argument('-f', '--flash', help='The path to the firmware.srec file', required=True)
    argument_parser.add_argument('-p', '--port', help='The i2c port to use. Default: 1', type=int, default=1)
    arguments = vars(argument_parser.parse_args())
    
    # Make sure this is actually a file, has the correct extension, etc.
    image_file = arguments['flash']
    if arguments['port']:
        port = arguments['port']

    print('Using: {} to flash fuel gauge'.format(image_file))

    if is_valid_image_file(image_file):
        print('{} is valid, starting flashing process.'.format(image_file))
        flash_image(image_file, port)
    else:
        print('{} is not a valid image file. Aborting flashing process.'.format(image_file))
        sys.exit()


if __name__ == "__main__":
    main()
