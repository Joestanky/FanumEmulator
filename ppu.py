import glob

#------- Meta
SCANLINE = 0
CYCLES = 0

#------- Registers
ppuctrl = 0x00
ppumask = 0x00
ppustatus = 0x00
oamaddr = 0x00
oamdata = 0x00
ppuscroll = 0x00
ppuaddr = 0x00
ppudata = 0x00
oamdma = 0x00

#--- Reading
def ReadPPUVars():
	PPUVars = {
		"ppuctrl": {
			"NN":	{ppuctrl&0b00000011},
			"I": 	{(ppuctrl&0b00000100)>>2},
			"S": 	{(ppuctrl&0b00001000)>>3},
			"B": 	{(ppuctrl&0b00010000)>>4},
			"H": 	{(ppuctrl&0b00100000)>>5},
			"P": 	{(ppuctrl&0b01000000)>>6},
			"V": 	{(ppuctrl&0b10000000)>>7}
		},
		"ppumask": {
			"g": 	{(ppuctrl&0b00000001)},
			"m": 	{(ppuctrl&0b00000010)<<1},
			"M": 	{(ppuctrl&0b00000100)<<2},
			"b": 	{(ppuctrl&0b00001000)<<3},
			"s": 	{(ppuctrl&0b00010000)<<4},
			"R": 	{(ppuctrl&0b00100000)<<5},
			"G": 	{(ppuctrl&0b01000000)<<6},
			"B": 	{(ppuctrl&0b10000000)<<7},
		},
		"ppustatus": {
			"xxxxx":{(ppuctrl&0b00000001)},
			"R": 	{(ppuctrl&0b00100000)<<5},
			"G": 	{(ppuctrl&0b01000000)<<6},
			"B": 	{(ppuctrl&0b10000000)<<7},
		},
	}
	return PPUVars


#------- Memory
MemPPU = []
for i in range(16*1024):
	MemPPU.append(0x00)

#--- Map
#$0000-$0FFF 	$1000 	Pattern table 0 		Cartridge
#$1000-$1FFF 	$1000 	Pattern table 1 		Cartridge
#$2000-$23BF 	$03c0 	Nametable 0 			Cartridge
#$23C0-$23FF 	$0040 	Attribute table 0 		Cartridge
#$2400-$27BF 	$03c0 	Nametable 1 			Cartridge
#$27C0-$27FF 	$0040 	Attribute table 1 		Cartridge
#$2800-$2BBF 	$03c0 	Nametable 2 			Cartridge
#$2BC0-$2BFF 	$0040 	Attribute table 2 		Cartridge
#$2C00-$2FBF 	$03c0 	Nametable 3 			Cartridge
#$2FC0-$2FFF 	$0040 	Attribute table 3 		Cartridge
#$3000-$3EFF 	$0F00 	Unused 	Cartridge
#$3F00-$3F1F 	$0020 	Palette RAM indexes 	Internal to PPU
#$3F20-$3FFF 	$00E0 	Mirrors of $3F00-$3F1F 	Internal to PPU

#-offset
pt0ofs = 0x0000
pt1ofs = 0x1000

nt0ofs = 0x2000
at0ofs = 0x23C0
nt1ofs = 0x2400
at1ofs = 0x27C0
nt2ofs = 0x2800
at2ofs = 0x2BC0
nt3ofs = 0x2C00
at4ofs = 0x2FC0

palofs = 0x3F00



statusflags = '00000OSV'

def SES(flag):  		#Set Flag
	global ppustatus
	bits = statusflags.index(flag)
	ppustatus = ppustatus | (1<<bits)

def CLS(flag):  		#Clear Flag
	bits = glob.flags.index(flag)
	mask = 0b11111111-(1<<bits)
	glob.P = glob.P & mask

#SES('S')
#print(f'{ppustatus:08b}')
def recieve():
	ppuctrl = glob.PPUCTRL
	ppumask = glob.PPUMASK
	#ppustatus = glob.PPUSTATUS
	oamaddr = glob.OAMADDR
	oamdata = glob.OAMDATA
	ppuscroll = glob.PPUSCROLL
	ppuaddr = glob.PPUADDR
	ppudata = glob.PPUDATA
	oamdma = glob.OAMDMA

def transmit():
	glob.PPUCTRL = ppuctrl
	glob.PPUMASK = ppumask
	glob.PPUSTATUS = ppustatus
	glob.OAMADDR = oamaddr
	glob.OAMDATA = oamdata
	glob.PPUSCROLL = ppuscroll
	glob.PPUADDR = ppuaddr
	glob.PPUDATA = ppudata
	glob.OAMDMA = oamdma
	

def Dot():
	recieve()
	
	SES('V')

	transmit()

if __name__ == "__main__":
	pass