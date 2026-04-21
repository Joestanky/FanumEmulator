bit_length = 3
bit_letters = ['M','N','C']
BL = bit_letters
output_letters = ['Z']
OL = output_letters
output_math = f'((M&N)^C)&~(M^N)'

numb = 2**bit_length

print('|M|N|C | Z')
for i in range(numb):
	M = (i&0b100)>>2
	N = (i&0b10)>>1
	C = i&0b1
	Z = eval(output_math)
	print('|'+str(M)+'|'+str(N)+'|'+str(C)+' | '+str(Z))

	 