file = open("code.txt", 'r')
out = open("code.nes", 'wb')
code = file.read()

from inst import INSSTR
lines = code.split('\n')
print(lines)

outputcode = True
debugend = True

reset = 0x0000
interrupt = 0x0000

def toHex(byte):
	hexes = ['0', '1', '2', '3',
			'4', '5', '6', '7',
			'8', '9', 'A', 'B',
			'C', 'D', 'E', 'F',]
	nib1 = hexes.index(byte[0])
	nib2 = hexes.index(byte[1])
	return (nib1<<4)+nib2

def littleEndian(word):
	leftByte = None
	rightByte = None
	if isinstance(word,str):
		word = word.replace("$", "")
		word = word.replace("#", "")
		leftByte = word[2:4]
		rightByte = word[:2]
	elif isinstance(word, int):
		leftByte = word>>8
		rightByte = word &0xF
	return [leftByte,rightByte]


ByteDump = []

Markers = {
}

addressingMode = ''
fullOperand = ''

#Programs Lines
print("decoding line...")
for line in lines:
	sections = line.split(' ')
	opcode = sections[0]
	#Non Implied Instructions
	if ":" in line: 			#marker thingity
		print("Marker at ", hex(len(ByteDump)))
		Markers[line[:-1]] = len(ByteDump)
		print(opcode, ": ", Markers[line[:-1]])
	else:
		if len(sections) == 1: 	#Instruction with no opcode
			addressingMode = 'IP'
		elif len(sections) == 2: 	#Instruction with opcode
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
			elif 	len(fullOperand) >5:
				addressingMode = 'A'
				if 		'X' in fullOperand: addressingMode += 'X' 	#Absolute X
				elif 	'Y' in fullOperand: addressingMode += 'Y' 	#Absolute Y
				else: 	addressingMode += 'B' 						#Absolute
			else:
				addressingMode = 'Z'
				sections[1] = sections[1].replace(',','')
				sections[1] = sections[1].replace('Y','')
				sections[1] = sections[1].replace('X','')
				if 		'X' in fullOperand: addressingMode += 'X' 	#Zero Page X
				elif 	'Y' in fullOperand: addressingMode += 'Y'   #Zero Page Y
				else:	addressingMode += 'P' 						#Zero Page

		opcodeByte = INSSTR.index(opcode+addressingMode)
		print(opcode+addressingMode, hex(opcodeByte), '|', fullOperand)

		#Operand
		operandBytes = []
		if len(sections) > 1:
			if sections[1] in Markers.keys():
				operandBytes.append(Markers[sections[1]])
		if addressingMode in ['AB','AX','AY']: 
			first = sections[1][3:5]
			second = sections[1][1:3]
			operandBytes.append(toHex(first))
			operandBytes.append(toHex(second))
		elif addressingMode in ['ZP','ZX', 'ZY','IM']:
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

if debugend:
	ByteDump.append(0x02)

RawDump = bytearray(PRGSize*16384+CHRSize*8192+16)

ByteDumpHex = []

for x,byte in enumerate(ByteDump):
	ByteDumpHex.append(hex(byte))
	RawDump[x] = byte

print("Byte Dump ---")
print(ByteDumpHex)
print("---")

if outputcode: 
	#print(RawDump)
	print("Dumped")
	out.write(RawDump)



out.close()
file.close()