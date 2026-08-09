RUNCPU = True
DEBUG = True

import glob
from ppu import Dot
from inst import *
from sys import exit

import time

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


	hi = input("File format data complete. Press enter to load ROM.")
	if hi.upper() == 'N':
		exit()

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
			glob.Mem[0xC000+i] = Program[i]
	#print(hex(glob.Mem[0x8000]))






FE = 0 		#this is fetch execute is 1 when executing thank yours
ITR = 0  	#interpreting = 0 or executing = 1 so i know if im figuring out or doing a code
#Cyc = 0 	#the current amount of cycles left for an instruction (set every fetch)
CycleNum = 0#total cycles ran (just debug)
FLW = True 	#flow being true means the PC will increment after instruction
ADR = ''



#flags = 'CZIDB1VN'

glob.A = 0x00
glob.X = 0x00
glob.Y = 0x00

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

def AddSign(b):
	sign = b&0x80 >> 7
	if sign == 1:
		newb = 256-b
		return ByteCheck(glob.ALU-newb)
	else:
		return ByteCheck(glob.ALU+b)

def SubSign(b):
	return ByteCheck(b-glob.ALU)

def Sub(b):
	return ByteCheck(glob.ALU-b)
#--
def IncPC():
	glob.PC = WordCheck(glob.PC+1)

def DecPC():
	glob.PC = WordCheck(glob.PC-1)

def PAB(): #PC to Address Bus
	glob.AB = glob.PC
	return(glob.AB)

def ABP(): #Address Bus to PC
	glob.PC = glob.AB
	return(glob.PC)

def AHL(): #ADH and ADL combined to AB
	glob.AB = (glob.ADH<<8)+glob.ADL
	return glob.AB

def HLA(): #Address Bus to ADH and ADL
	glob.ADH = glob.AB>>8
	glob.ADL = glob.AB&0xFF


#Printing/Debugging

MemoryWatch = []
watcher = 0

def LHex(array):
	newy = "|"
	for i in array:
		if len(hex(i)[2:]) == 1:
			newy += '0'
		newy += hex(i)[2:].upper()
		newy += "|"
	return newy


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
	print('---: ZP First 64:')
	print(LHex(glob.Mem[:64]))
	print('---: Memory Watch:')
	for i in MemoryWatch:
		print(f'{i:04x}'.upper(), ": ", f'{glob.Mem[i]:02x}'.upper())
	print('---: Stack:')
	print(LHex(glob.Mem[glob.S+0x100:0x200]))

#Cyclic Behaivors
def Addressing():
	if glob.Cyc == 1 and ADR != 'IP' and ADR != 'AC':
		IncPC()
		PAB()

	if INSSTR[IR][:3] in ["INC", "DEC", "ASL", "LSR", "ROL", "ROR"]: 
		if (ADR == 'AB') and (glob.Cyc == 5):
			IncPC()
			PAB()
		elif (ADR == 'AX') and (glob.Cyc == 6):
			IncPC()
			PAB()
		return

	if INSSTR[IR][:3] in ["JMP"]:
		if (ADR == 'AB') and glob.Cyc == 2:
			IncPC()
			PAB()
		if (ADR == 'IN') and glob.Cyc == 4:
			IncPC()
			PAB()
		return

	if INSSTR[IR][:3] in ["JSR"]:
		if glob.Cyc == 2:
			IncPC()
			PAB()
			return
	if (ADR in ['AB']) and (glob.Cyc == 3): IncPC(); PAB()
	if (ADR == 'AX' or ADR == 'AY') and (glob.Cyc == 4): IncPC(); PAB()

#PPU setting

def CPU2PPU():
	glob.PPUCTRL 	= glob.Mem[0x2000]
	glob.PPUMASK 	= glob.Mem[0x2001]
	glob.PPUSTATUS 	= glob.Mem[0x2002]
	glob.OAMADDR 	= glob.Mem[0x2003]
	glob.OAMDATA 	= glob.Mem[0x2004]
	glob.PPUSCROLL 	= glob.Mem[0x2005]
	glob.PPUADDR 	= glob.Mem[0x2006]
	glob.PPUDATA 	= glob.Mem[0x2007]
	glob.OAMDMA 	= glob.Mem[0x4014]

def PPU2CPU():
	glob.Mem[0x2000] = glob.PPUCTRL
	glob.Mem[0x2001] = glob.PPUMASK
	glob.Mem[0x2002] = glob.PPUSTATUS
	glob.Mem[0x2003] = glob.OAMADDR
	glob.Mem[0x2004] = glob.OAMDATA
	glob.Mem[0x2005] = glob.PPUSCROLL
	glob.Mem[0x2006] = glob.PPUADDR
	glob.Mem[0x2007] = glob.PPUDATA
	glob.Mem[0x4014] = glob.OAMDMA



framecyc = 0
tick = 0
frameNum = 0

def Cycle():
	global FE, IR, ITR, CycleNum, FLW, ADR
	if DEBUG: print("----------------")
	if DEBUG: print("Cycle: ", CycleNum)

	if FE == 0:				#If fetching
		FE = 1 				#Now Executing
		glob.DB = glob.Mem[PAB()]		#Push opcode to Data Bus
		if DEBUG: print("_Fetched: ", hex(glob.DB))
		HLA()
		IncPC()				#Increment PC (apparently done right after retrieving byte)
		CycleNum += 1

	else:
		if ITR == 0: 		#If still needing to InTeRpret the code:
			ITR = 1 		#Now really executing
			IR = glob.DB 		#Set Instruction register
			if DEBUG: print(IR)
			ADR = INSSTR[IR][-2:]
			if DEBUG: print("IR set: ", INSSTR[IR], hex(IR), ADR)
			glob.Cyc = INSCYC[IR]#Set cycles
			glob.Cyc -= 1 		#interpretation takes 1 cycle
			glob.DB = glob.Mem[PAB()]
			CycleNum += 1

		else:				#If interpreted and now executing
			if DEBUG: print("Ins  |  AB  |Byte| Cyc")	#printing for debugging
			if DEBUG: print(INSSTR[IR], '0x'+f"{glob.AB:04x}".upper(),hex(glob.Mem[glob.AB])," ",glob.Cyc)	#yes

			INSCOD[IR]()	#Run instruction

			#Addressing modes choose how PC acts 
			Addressing()


			glob.DB = glob.Mem[glob.AB]

			if glob.Cyc == 1:		#If instruction done with memory
				ITR = 0
				glob.DB = glob.Mem[PAB()] #Set data bus to next opcode

				if DEBUG: print("Fetched: ", '0x'+f'{glob.DB:02x}'.upper())
				if DEBUG: print(hex(glob.PC), "PC")			

				HLA()

				if glob.DB == 0x02 or CycleNum >= 256: #if done running
					endTime = time.time()
					FullCheck()
					print("Run Time: ", f"{(endTime-startTime):.9f}", "Cycles: ", CycleNum)
					print(framecyc)
					exit()

				IncPC()
				ADR = ''


			glob.Cyc -=1
			CycleNum += 1
			if DEBUG: print("Cycle ended")
			if DEBUG: print("----------------")



if __name__ == "__main__":
	print("------------==--------------")
	LoadROM()
	startTime = time.time()
	while RUNCPU:
		tick = time.time()
		framecyc = 0
		while (time.time()-tick) < (1/60):
			if framecyc < 29830:

				Cycle()
				CPU2PPU()
				Dot()
				Dot()
				Dot()
				PPU2CPU()
				print(glob.PPUSTATUS)
				framecyc += 1
			else:
				print(time.time()-tick)
		#MemoryWatch.append(watcher)
		#watcher += 1

"""
tick = time.time()
while (time.time()-tick) < sleepers:
	pass
"""