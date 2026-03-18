def init():
	global A,X,Y,PC,IR,AB,ADL,ADH,DB,ALU,P,Cyc
	A = 0x00	#this is the accumulator you like add and subtract and shit to it and save it to places
	X = 0x00	#this is the index register so yes
	Y = 0x00 	#this is the second index register inde"x" then y get it?
	PC = 0x8000 #this is the program counter it is where we are
	IR = 0x02 	#this be the instruction reister okay
	AB = 0x0000 #Address bus
	ADL = 0x00  #Low-order byte used to set address bus
	ADH = 0x00	#High-order byte used to set address bus
	DB = 0x00 	#:( i think this will be required for doing things and stuff
	ALU = 0x00  #idek but i think it is neededdd
	P = 0x00 	#Processor status flag byte
	Cyc = 0 	#the current amount of cycles left for an instruction (set every fetch)
	global flags, Mem
	#Processor Status
	flags = 'CZIDB1VN'
	Mem = []
