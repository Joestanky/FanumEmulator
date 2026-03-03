file = open("code.txt", 'r')
out = open("code.nes", 'wb')
code = file.read()

from main import INSSTR
lines = code.split('\n')
print(lines)


def toHex(byte):
	hexes = ['0', '1', '2', '3',
			'4', '5', '6', '7',
			'8', '9', 'A', 'B',
			'C', 'D', 'E', 'F',]
	nib1 = hexes.index(byte[0])
	nib2 = hexes.index(byte[1])
	return (nib1<<4)+nib2

ByteDump = []


addressingMode = ''

#Programs Lines
for line in lines:
	sections = line.split(' ')
	opcode = sections[0]
	#Non Implied Instructions
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
Header = [0x4E,0x45,0x53,0x1A] #"NES", then MS-DOS EOF (dunno why EOF there)
ByteDump.insert(0, Header[0])
ByteDump.insert(1, Header[1])
ByteDump.insert(2, Header[2])
ByteDump.insert(3, Header[3])




ByteDump.append()

RawDump = bytearray(len(ByteDump))

ByteDumpHex = []

for x,byte in enumerate(ByteDump):
	ByteDumpHex.append(hex(byte))
	RawDump[x] = byte

print("Byte Dump ---")
print(ByteDumpHex)

print(RawDump)
out.write(RawDump)
print("---")


out.close()
file.close()