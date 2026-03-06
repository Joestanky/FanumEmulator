file = open("code.txt", 'r')
out = open("code.nes", 'wb')
code = file.read()

from main import INSSTR
lines = code.split('\n')
print(lines)

outputcode = True

def toHex(byte):
	hexes = ['0', '1', '2', '3',
			'4', '5', '6', '7',
			'8', '9', 'A', 'B',
			'C', 'D', 'E', 'F',]
	nib1 = hexes.index(byte[0])
	nib2 = hexes.index(byte[1])
	return (nib1<<4)+nib2

ByteDump = []

Markers = {
}

addressingMode = ''

#Programs Lines
print("decoding line...")
for line in lines:
	sections = line.split(' ')
	opcode = sections[0]
	#Non Implied Instructions
	if ":" in line:
		print("Marker at ", hex(len(ByteDump)))
		Markers[line[:-1]] = len(ByteDump)
		print(": ", Markers[line[:-1]])
	if len(sections) == 2:
		fullOperand = sections[1]

		addressingMode = '~~'

		#Addressing Modes
		if 		'd' == 'f':
			pass
		elif 	"#" in fullOperand:
			addressingMode = 'IM'
		elif '(' in fullOperand:
			if 		'X' in fullOperand: addressingMode = 'IX' 	#Indirect X
			elif 	'Y' in fullOperand: addressingMode = 'IY' 	#Indirect Y
		elif 	len(fullOperand) >3:
			addressingMode = 'A'
			if 		'X' in fullOperand: addressingMode += 'X' 	#Absolute X
			elif 	'Y' in fullOperand: addressingMode += 'Y' 	#Absolute Y
			else: 	addressingMode += 'B' 						#Absolute
		else:
			addressingMode = 'Z'
			if 		'X' in fullOperand: addressingMode += 'X' 	#Zero Page X
			else:	addressingMode += 'P' 						#Zero Page

		opcodeByte = INSSTR.index(opcode+addressingMode)
		print(opcode+addressingMode, hex(opcodeByte), '|', fullOperand)

		#Operand
		operandBytes = []
		if addressingMode in ['AB','AX','AY']: 
			first = sections[1][3:5]
			second = sections[1][1:3]
			operandBytes.append(toHex(first))
			operandBytes.append(toHex(second))
		elif addressingMode in ['ZP','ZX','IM']:
			operandBytes.append(toHex(sections[1][-2:]))
		elif addressingMode in ['IX','IY']:
			operandBytes.append(toHex(sections[1][2:4]))
		opBytes = ''	
		for i in operandBytes:
			opBytes += hex(i) +' '
		print(opBytes)

		#Dumping
		ByteDump.append(opcodeByte)
		for byte in operandBytes:
			ByteDump.append(byte)


#Header

PRGSize = int(len(ByteDump)/(16*1024))+1
print("PRG Size: ", PRGSize)

CHRSize = 1 #i havent implemented this quite yet

Flags6 = 0b00000001
Flags7 = 0b00000000
Flags8 = 0b00000000
Flags9 = 0b00000000
Flags10 = 0b00000000

Header = [	0x4E,0x45,0x53,0x1A,	 #"NES", then MS-DOS EOF (dunno why EOF there)
			PRGSize,CHRSize,Flags6, Flags7,
			Flags8,Flags9,Flags10, 0x00,
			0x00,0x00,0x00,0x00]		

for i in range(len(Header)):
	ByteDump.insert(i, Header[i])




#ByteDump.append()

RawDump = bytearray(PRGSize*16384+CHRSize*8192+16)

ByteDumpHex = []

for x,byte in enumerate(ByteDump):
	ByteDumpHex.append(hex(byte))
	RawDump[x] = byte

print("Byte Dump ---")
print(ByteDumpHex)


if outputcode: 
	#print(RawDump)
	print("Dumped")
	out.write(RawDump)

print("---")


out.close()
file.close()