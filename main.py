RUNCPU = True

import glob
from inst import *
from sys import exit

glob.init()

for i in range(1024*64):
	glob.Mem.append(0x00)

#ROM Data
NES = False
PRGSize = 0
CHRSize = 0
Nametable = ''
Battery = False
Trainer = False
AlternateNT = False
Mapper = 0
TV = ''
VsGame = False
NES2 = False


def LoadROM():
	global NES,PRGSize,CHRSize,Nametable,Battery
	global Trainer,AlternateNT,Mapper,TV,VsGame,NES2
	global Mem

	file = open("code.nes", 'rb')
	rom = file.read()

	Header = []
	for i in range(16):
		Header.append(rom[i])
	print(Header)

	if Header[0] == 0x4E and Header[1] == 0x45 and Header[2] == 0x53 and Header[3] == 0x1A:
		NES = True
	else:
		print("Non NES File. Consider finding appropriate rom")
		return

	print("NES File: ", NES)

	PRGSize = Header[4]
	CHRSize = Header[5]
	ntlist = ['vertical', 'horizontal']
	Nametable = ntlist[Header[6]&0x01]
	Battery = Header[6]&0x02 == 2
	Trainer = Header[6]&0x04 == 4
	AlternateNT = Header[6]&0x08 == 8
	Mapper = Header[6]>>4

	print("PRG ROM Size(16kB Blocks): ", PRGSize)
	print("CHR ROM Size(8kB Blocks): ", CHRSize)
	print("Nametable: ", Nametable, " arrangement")
	print("Battery-backed PRG RAM: ", Battery)
	print("512-byte Trainer: ", Trainer)
	print("Alternative Nametable Layout: ", AlternateNT)

	VsGame = Header[7]&0x01==1
	NES2 = Header[7]&0x0C==0x08
	Mapper += Header[7]&0xF0

	print("Vs Game: ", VsGame)
	print("NES 2.0 Format: ", NES2)
	print("Mapper Number: ", Mapper)

	tvlist = ["NTSC", "PAL"]
	TV = tvlist[Header[9]&0x01]

	print("TV System: ", TV)


	input("File format data complete. Press enter to load ROM.")

	Data = []

	Program = []
	Character = []
	for i in range(16, 16+(PRGSize*16384)+(CHRSize*8192)):
		if 16<= i <16+(PRGSize*16384):
			Program.append(rom[i])
		if 16+(PRGSize*16384)<=i<16+(PRGSize*16384)+(CHRSize*8192):
			Character.append(rom[i])

		Data.append(rom[i])


	file.close()

	if PRGSize > 1:
		for i in range(32*1024):
			glob.Mem[0x8000+i] = Program[i]
	else:
		for i in range(16*1024):
			glob.Mem[0x8000+i] = Program[i]
	print(hex(glob.Mem[0x8000]))




#registers and busses and things



FE = 0 		#this is fetch execute is 1 when executing thank yours
ITR = 0  	#interpreting = 0 or executing = 1 so i know if im figuring out or doing a code
#Cyc = 0 	#the current amount of cycles left for an instruction (set every fetch)
CycleNum = 0#total cycles ran (just debug)
FLW = True 	#flow being true means the PC will increment after instruction
ADR = ''



flags = 'CZIDB1VN'

glob.A = 0x00
glob.X = 0x01
glob.Y = 0x02

#Basic Byte Manipulation
def ByteCheck(byte):
	if byte >=256: 	#overflow
		byte -= 256
	elif byte <0:
		byte += 256 #underflow
	return byte

def WordCheck(word):
	if word >=0x10000: 	#overflow
		word -= 0x10000
	elif word <0:  		#underflow
		word += 0x10000
	return word

def Add(b):
	return ByteCheck(glob.ALU+b)
#--
def IncPC():
	glob.PC = WordCheck(glob.PC+1)

def DecPC():
	glob.PC = WordCheck(glob.PC-1)

def PAB(): #Pc to AddressBus
	glob.AB = glob.PC
	return(glob.AB)

def AHL(): #ADH and ADL combined to AB
	glob.AB = (glob.ADH<<8)+glob.ADL
	return glob.AB

#Printing/Debugging
def PCheck():
	print('---: Processor Status:')
	print('NV1BDIZC')
	print(f"{glob.P:08b}")

def RCheck():
	print('---: Registers:')
	print(" A| X| Y")
	regs = ''
	regs+=f"{glob.A:02x}".upper();regs+='|'
	regs+=f"{glob.X:02x}".upper();regs+='|'
	regs+=f"{glob.Y:02x}".upper()
	print(regs)

def FullCheck():
	PCheck()
	RCheck()	

#Cyclic Behaivors
def Addressing():
	if glob.Cyc == 1 and ADR != 'IP':
		IncPC()
		PAB()
	if (ADR == 'AB') and (glob.Cyc == 3): IncPC(); PAB()
	if (ADR == 'AX' or ADR == 'AY') and (glob.Cyc == 4): IncPC(); PAB()




def Cycle():
	global FE, IR, ITR, CycleNum, FLW, ADR
	print("----------------")
	print("Cycle: ", CycleNum)
	if FE == 0:				#If fetching
		FE = 1 				#Now Executing
		glob.DB = glob.Mem[PAB()]		#Push opcode to Data Bus
		print("_Fetched: ", hex(glob.DB))
		IncPC()				#Increment PC (apparently done right after retrieving byte)
		CycleNum += 1

	else:
		if ITR == 0: 		#If still needing to InTeRpret the code:
			ITR = 1 		#Now really executing
			IR = glob.DB 		#Set Instruction register
			ADR = INSSTR[IR][-2:]
			print("IR set: ", INSSTR[IR], hex(IR), ADR)
			glob.Cyc = INSCYC[IR]#Set cycles
			glob.Cyc -= 1 		#interpretation takes 1 cycle
			glob.DB = glob.Mem[PAB()]
			CycleNum += 1

		else:				#If interpreted and now executing
			print("Ins  |  AB  |Byte| Cyc")	#printing for debugging
			print(INSSTR[IR], '0x'+f"{glob.AB:04x}".upper(),hex(glob.Mem[glob.AB])," ",glob.Cyc)	#yes

			INSCOD[IR]()	#Run instruction

			#Addressing modes choose how PC acts 
			Addressing()


			glob.DB = glob.Mem[glob.AB]

			if glob.Cyc == 1:		#If instruction done with memory
				ITR = 0
				glob.DB = glob.Mem[PAB()] #Set data bus to next opcode
				print("Fetched: ", '0x'+f'{glob.DB:02x}'.upper())
				if glob.DB == 0x02:
					FullCheck()
					exit()
				if FLW: 		#If we are flowing normally
					if (ADR == 'IM'):
						IncPC()
					else:
						IncPC() 	#Set PC for next operand grab
					print(hex(glob.PC), "PC")
				else: 			#If i.e. our ins uses no operands
					FLW = True
					DecPC() 	#Go back one byte
					glob.DB = glob.Mem[PAB()] #Set that as next opcode
					IncPC() 	#Set PC back for next operand
				ADR = ''


			glob.Cyc -=1
			CycleNum += 1
			print("Cycle ended")
			print("----------------")



if __name__ == "__main__":
	print("------------==--------------")
	nigger()
	print(glob.A, "my nigga bro")
	LoadROM()
	while RUNCPU:
		Cycle()
