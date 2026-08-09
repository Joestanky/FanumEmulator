file = open("code.txt", 'r')
out = open("code.nes", 'wb')
code = file.read()

from sys import exit

from inst import INSSTR

#print(code.upper().split('\n'))
lines = code.upper().split('\n')
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
		print("imma goofy goober rock")
		word = word.replace("$", "")
		word = word.replace("#", "")
		leftByte = word[2:4]
		rightByte = word[:2]
	elif isinstance(word, int):
		print("kcor reboog yfoog ammi")
		leftByte = word>>8
		rightByte = word &0xFF
	return [leftByte,rightByte]

def valueLE(bytepair):
	return (toHex(bytepair[1])<<8)+toHex(bytepair[0])

def toSigned(byte):
	if byte > 0xFF:
		byte = 0x100-byte
	return byte &0xFF

"""
one=0x80FF-0x8134
if one < 0:
	one = 0x100-one



print(hex(toSigned(one)))
exit()
"""

ByteDump = []

Markers = {
}


addressingMode = ''
fullOperand = ''

program = False

#Programs Lines
print("decoding lines...")
for line in lines:
	if not program:
		if line == ".PROGRAM":
			program = True
		else:
			sections = line.split(' ')
			if sections[0] in 'DEFINE':
				print("Label: ")
				Markers[sections[1]] = valueLE(littleEndian(sections[2]))
				print(sections[1], ": ", hex(Markers[sections[1]]))


	else:
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
				fullOperand = ''
			elif len(sections) == 2: 	#Instruction with opcode
				fullOperand = sections[1]
				hexes = fullOperand.replace('#','')
				hexes = hexes.replace('$','')
				hexes = hexes.replace('Y','')
				hexes = hexes.replace('X','')
				hexes = hexes.replace(',','')

				addressingMode = '~~'
				print(sections[0].upper())
				#Addressing Modes
				if 		fullOperand == 'A':
					addressingMode = "AC"

				elif sections[0].upper() in ('BNE', 'BEQ', 'BCC', 'BCS', 'BPL', 'BMI', 'BVC', 'BVS'):
					addressingMode = 'RL'

				elif 	"#" in fullOperand:
					addressingMode = 'IM'

				elif '(' in fullOperand:
					if 		'X' in fullOperand: addressingMode = 'IX' 	#Indirect X
					elif 	'Y' in fullOperand: addressingMode = 'IY' 	#Indirect Y
					else: 
						addressingMode = 'IN'
						sections[1] = sections[1].replace('(','')
						sections[1] = sections[1].replace('(','')

				elif 	len(hexes) >2:
					#print(hexes, "look here josef blizzard")
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
					print("you sexy lovah")
					if opcode.upper() in ['BNE', 'BEQ', 'BCC', 'BCS', 'BPL', 'BMI', 'BVC', 'BVS']:
						one = len(ByteDump)+2
						two = Markers[sections[1]]
						hre = two - one
						if hre < 0:
							hre = 0x100 - hre
						hre = toSigned(hre)
						print(hex(hre),one, two, hre, "joASFDddAl blifdgshard lookey heres")
						operandBytes.append(hre)
					else:
						first = Markers[sections[1]]&0xFF
						second = Markers[sections[1]]>>8
						operandBytes.append(first)
						operandBytes.append(second)
				elif addressingMode in ['AB','AX','AY', 'IN']: 
					first = sections[1][3:5]
					second = sections[1][1:3]
					operandBytes.append(toHex(first))
					operandBytes.append(toHex(second))
				elif addressingMode in ['ZP','ZX','ZY','IM']:
					operandBytes.append(toHex(sections[1][-2:]))
				elif addressingMode in ['IX','IY']:
					operandBytes.append(toHex(sections[1][2:4]))
				elif addressingMode == 'RL':
					one = len(ByteDump)+2
					two = valueLE(littleEndian(sections[1]))-32768
					print(sections[1], littleEndian(sections[1]), two, "hi")
					hre = two - one
					if hre < 0:
						hre = 0x100-hre
					hre = toSigned(hre)
					print(hex(hre),hex(one), hex(two), hre, "-=-=-")
					operandBytes.append(hre)

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

RawDump[0x0050] = 0x40
RawDump[0x4000] = 0xE8
RawDump[0x4001] = 0x60
RawDump[0x400C] = 0x00
RawDump[0x400D] = 0x80
RawDump[0x400E] = 0x40
RawDump[0x400F] = 0x80


if outputcode: 
	#print(RawDump)
	print("Dumped")
	out.write(RawDump)



out.close()
file.close()