file = open("code.txt", 'r')
code = file.read()

from main import INSSTR
lines = code.split('\n')
print(lines)

addressingMode = ''

def toHex(byte):
	hexes = ['0', '1', '2', '3',
			'4', '5', '6', '7',
			'8', '9', 'A', 'B',
			'C', 'D', 'E', 'F',]
	nib1 = hexes.index(byte[0])
	nib2 = hexes.index(byte[1])
	return (nib1<<4)+nib2

ByteDump = []

for line in lines:
	sections = line.split(' ')
	opcode = sections[0]
	if len(sections) == 2:
		fullOperand = sections[1]
		print(opcode, '|', fullOperand)

		addressingMode = '~~'
		if 		'd' == 'f':
			pass
		elif 	"#" in fullOperand:
			print(fullOperand, "bullshit gimme my money")
			addressingMode = 'IM'
		elif '(' in fullOperand:
			if 		'X' in fullOperand: addressingMode = 'IX'
			elif 	'Y' in fullOperand: addressingMode = 'IY'
		elif 	len(fullOperand) >3:
			addressingMode = 'A'
			if 		'X' in fullOperand: addressingMode += 'X'
			elif 	'Y' in fullOperand: addressingMode += 'Y'
			else: 	addressingMode += 'B'
		else:
			addressingMode = 'Z'
			if 		'X' in fullOperand: addressingMode += 'X'
			else:	addressingMode += 'P'
		print(opcode+addressingMode)
		opcodeByte = INSSTR.index(opcode+addressingMode)
		print(hex(opcodeByte))
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
		print(operandBytes)

		ByteDump.append(opcodeByte)
		for byte in operandBytes:
			ByteDump.append(byte)


RawDump = bytearray(0x8000)

ByteDumpHex = []

for x,byte in enumerate(ByteDump):
	ByteDumpHex.append(hex(byte))
	RawDump[x] = byte

print(ByteDumpHex)

print(RawDump)
