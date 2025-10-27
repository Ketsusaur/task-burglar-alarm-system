import serial.tools.list_ports

class SerialComm:
    def __init__(self):
        ports = serial.tools.list_ports.comports()
        portID = 'COM4'
        baudrate = 9600
        self.serialInst = serial.Serial(portID, baudrate)
    def Read(self):
        while True:
          #read from serial port
            readline = self.serialInst.readline()
            stringline = readline.decode('utf-8').strip()
            print(stringline)

            return(stringline)
    def Write(self,command):
        self.serialInst.write((command+'\n').encode('utf-8'))
    def UserInput(self,request):
            command = input(request)
            self.serialInst.write(command.encode('utf-8'))