import socket 
import sys 
from datetime import datetime 
import time 
MAGICNO = 0x497E


def arguments_check():
    port_number = sys.argv[1]
    if len(sys.argv) != 2:
        print("NOT RECEIVED THE RIGHT NUMBER OF ARGUMENTS. ONLY 2 ARGUEMENTS TO BE PASSED")
        sys.exit()
    else:
        return port_number

def get_port(port_number):
    """Checking that if the port number is valid and lies within the range"""
    continue_scaning = True 
    try:
        port_number = int(port_number)
        if(port_number >= 1024 and port_number <= 64000):
            continue_scaning = False
        else:
            print("PORT NUMBER OUT OF RANGE")
            sys.exit()
    except ValueError:
        print("PLEASE ENTER A VALID INTEGER VALUE FOR THE PORT NUMBER!")
        sys.exit()
    return port_number
        
def create_socket(port_number):
    """This function creates the socket here and if successful then tries to bind it 
       and returns the socket"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket is created and listening...")
    except socket.error:
        print("ERROR:SOCKET CREATION FAILED")
        sys.exit()
    try:
        s.bind(("0.0.0.0",port_number))
    except OSError:
        print("ERROR:PORT NUMBER ALREADY IN USE")
        s.close()
        sys.exit()
    return s   
            
def listen(s, port_number):
    """This function starts listening, creates a clientsocket, recieves the header for the 
       file request from the client, makes a call to to the header_check function, and 
       if the header is valid and then makes a final call to the sending_data function
       to send the file"""
    try:   
        listening = True
        s.listen(1)
    except:
        print("ERROR WHILE LISTENING") 
        s.close() 
        sys.exit() 
    
    while listening:
        clientsocket, address = s.accept()               #creating a new socket 
        clientsocket.settimeout(1)
        print(f"Connection from {address} has been established on {datetime.now():%d-%m-%Y} at {datetime.now().strftime('%H:%M:%S')}!")
        try:
            fixed_header = clientsocket.recv(5)
            magic_number_received = int.from_bytes(fixed_header[0:2], 'big')
            file_type = fixed_header[2]
            filename_len = int.from_bytes(fixed_header[3:5], "big")
        except:
            print("ERROR INCOMPLETE HEADER DETAILS IN FILE REQUEST")
            clientsocket.close()
            continue
        file_request_header_check(magic_number_received, file_type, filename_len)
        try:
            file_data = clientsocket.recv(filename_len)
        except:
            print("ERROR WHILE TRYING TO RECIEVE THE FILE")
            clientsocket.close()
            continue
        
        if len(file_data) != filename_len:            #length of file data check  
            print("The length of the received file are not equal")
            clientsocket.close()
            sys.exit() 
        sending_file_data(clientsocket, file_data)
        continue  
            
              
def file_request_header_check(magic_number_received, file_type, filename_len):
    """Initial checking for the recieved header in FileRequest"""
    if magic_number_received != MAGICNO:               #magic_number check
        print("ERROR:MAGIC NUMBER DID NOT MATCH")
        clientsocket.close()
        sys.exit()
    if file_type != 1:                                  #file_type check                            
        print("ERROR: WRONG FILE TYPE RECIEVED")
        clientsocket.close()
        sys.exit()   
    if filename_len < 1 and filename_len > 1024:        #file content check
        print("The length of the recieved filename is out of the range")
        clientsocket.close()
        sys.exit() 
             
             
def sending_file_data(clientsocket, file_data):
    """ Thei function tries open the file requested by the client. If possible it makes the file
    response with the value for statuscode=1 and the filedata. If it has been unable to 
    locate the file oer open it, it still sends the file response back but with stauscode=0 and no 
    file data"""
    try:
        file =  open(file_data.decode('utf-8'),'rb')
        data = file.read()
        status_code = 1
        file_data = data
        data_length = len(file_data)
        length = data_length.to_bytes(4, byteorder='big')
        status_code_bytes = status_code.to_bytes(1, byteorder='big')
        file_response = bytearray([0x49, 0x7E, 0x2]) + status_code_bytes + length + file_data
        clientsocket.sendall(file_response)
        print(f"The total of {len(file_data)} bytes were transferred")
        file.close()
        clientsocket.close()                                   
    except FileNotFoundError:  #incase the file cannot be opened or does not exist
        status_code = 0        #then the statuscode is set to 0 
        status_code_bytes = status_code.to_bytes(1, byteorder='big')
        file_response = bytearray([0x49, 0x7E, 0x2]) + status_code_bytes    
        clientsocket.sendall(file_response)
        clientsocket.close()
          
    
    

def main():
    port_number = arguments_check()
    port_number = get_port(port_number) 
    s = create_socket(port_number)
    listen(s, port_number)


if __name__ == "__main__":
    main()
