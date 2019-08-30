"""Author: Shivin Gaba """
import socket 
import sys 
import time
import os 
from os import path
MAGICNO = 0x497E

def arguments_checks(HOST,PORT,FILENAME):
    """This function initally checks the arguments passed in the terminals which
    are the localhost information, port number and the file"""
    try:
        hostname = socket.getaddrinfo(HOST, PORT)
        host_info_tuple = hostname[0][4]#retrieving the info from the tuple(hostname,portno)    
    except socket.error:
        print("ERROR: FAILED TO GET THE HOST INFORMATION")
        sys.exit()    
    if PORT < 1024 or PORT > 64000:      #port number check 
        print("ERROR: PORT NUMBER OUT OF RANGE")
        sys.exit()  
    if path.exists(FILENAME):            # check if file already exist in the client's locl directory
        sys.exit("ERROR: The file exists locally")    
    if len(sys.argv) != 4: 
        print("NOT ENOUGH ARGUEMENTS PASSED!!")
        sys.exit()  
    return host_info_tuple
        
        
def socket_setup(host_info_tuple):
    """This function creates a socket and tries to binds it."""
    try:                               
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1) 
        print("Socket created successfully")
    except socket.error:
        print("ERROR SOCKET CREATION FAILED")
        sys.exit()    
    try:
        s.connect(host_info_tuple)
    except socket.error:
        print("ERROR WHILE CONNECTING TO THE SERVER")
        s.close()
        sys.exit()
    return s

def header_setup(HOST,PORT,FILENAME,s):
    """This function constructs the header for the file request and sends it to the server"""
    magic_number_type = bytearray([0x49, 0x7E, 0x1])   
    encoded_filename = FILENAME.encode('utf-8')
    filename_length_byte = len(encoded_filename).to_bytes(2,'big')          
    header =  magic_number_type + filename_length_byte + encoded_filename
    trigger = True
    while trigger==True:                    
        try:
            s.sendall(header) 
            trigger = False
        except socket.error:
            print("ERROR:HEADER SENDING FAILED")


def get_respose_header(s):
    """This function recieves 8 bytes of header data from the server"""
    try:
        fixed_header = s.recv(8)       
    except:
        print("ERROR WHILE RECEIVING THE FIXED HEADER")
        s.close() 
        sys.exit() 
    magic_number_r = int.from_bytes(fixed_header[0:2], 'big')
    file_type = fixed_header[2]
    StatusCode = fixed_header[3]
    data_length = int.from_bytes(fixed_header[4:8], "big") 
    return (magic_number_r, file_type, StatusCode, data_length)

def response_header_check(magic_number_r, file_type, StatusCode, data_length,FILENAME,s):
    """This function does all the initial checks on the recieved response header"""
    if MAGICNO == magic_number_r and  file_type == 2:
        if(StatusCode == 0):
            print("ERROR:THE FILE DOES NOT EXIST OR COULD NOT BE OPENED")
            s.close()
            sys.exit()
        else:
            number_of_bytes_recieved = receiving_data(FILENAME, s, data_length) 
        if number_of_bytes_recieved != data_length:
            print("The number of bytes recieved are not equal to the data lenght")
            s.close() 
            sys.exit() 
        else:
            print(f"File transfer is complete.The total of {number_of_bytes_recieved} bytes were recieved.")
    else:
        s.close()
        sys.exit()

def receiving_data(FILENAME,s,data_length):
    """ This function opens a new file and assigns it the same name as the file 
    that the client s trying to download. It recieves the data in blocks of 4096 
    bytes and writes it to the file"""
    
    number_of_bytes_recieved = 0
    loop_limit = 1 + data_length // 4096    
    remaining_data = data_length - (4096 * loop_limit)
    try:
        new_file = open(FILENAME, "wb+")
    except IOError:
        print("ERROR:FILE CANNOT BE OPEN")
    file_data_recieve = False
    while not file_data_recieve:
        try:
            recieve_data = s.recv(4096)
            number_of_bytes_recieved += len(recieve_data)
            if len(recieve_data) < 4096:
                new_file.write(recieve_data)  
                new_file.close()
                file_data_recieve = True
            else:
                new_file.write((recieve_data))  
        except socket.timeout:
            print("ERROR:SOCKET TIMEOUT")
            new_file.close()
            s.close() 
            sys.exit()
    return number_of_bytes_recieved
           
def main():
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    FILENAME = sys.argv[3]
    host_info_tuple = arguments_checks(HOST,PORT,FILENAME)
    s = socket_setup(host_info_tuple)
    header_setup(HOST,PORT,FILENAME,s)
    magic_number_r, file_type, StatusCode, data_length = get_respose_header(s)
    response_header_check(magic_number_r, file_type, StatusCode, data_length, FILENAME,s)
    
    
if __name__ == "__main__":
    main()
    
    
