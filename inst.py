print("inst start")

#from main import X, Y, ADL, ADH, ALU, AB, Cyc, PC
import glob
from main import *




def SEF(flag):  		#Set Flag
	bits = glob.flags.index(flag)
	glob.P = glob.P | (1<<bits) 	#move one to appropriate bit and if 0 make 1 (0|1=1, 1|1=1)

def CLF(flag):  		#Clear Flag
	bits = glob.flags.index(flag)
	mask = 0b11111111-(1<<bits) #i.e. bits = 4, 1<<bits = 00010000, 11111111-00010000=11101111
	glob.P = glob.P & mask 		#the one bit thats 0 gets anded with the bit we're checking for
	 					#all other bits = 1 so if checking byte bit is 0 we get 0 and is 1 we get 1 hooray!

#Instructions 

#-------------------
#Load A------------
#-------------------
def LDAend(): #the flags n shit
	if glob.A == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.A >= 0x80:
		SEF('N')
	else:
		CLF('N')


def LDAIM(): #load to a immediately, 2 Cycs, $A9 *RC*
	if glob.Cyc == 1:
		glob.A = glob.DB 		#Push Data Bus to Accumulator
		LDAend()

def LDAZP(): #load to a from zero page address, 3 Cycs, $A5 *RC*
	if glob.Cyc == 2:
		glob.ADL = glob.DB 	#Get zero page address
		glob.ADH = 0x00 	#set high to zero page 
		AHL() 		#Combine ADH and ADL to 16-bit AB

	elif glob.Cyc == 1:
		glob.A = glob.DB 		#Data Bus to Accumulator
		LDAend()

def LDAZX(): #load a from zero page address + X, 4 Cycs, $B5 *RC*
	if Cyc == 3:
		glob.ADL = glob.DB 		#Data Bus to Address Low
		glob.ALU = glob.ADL 		#Address Low to ALU 
	elif Cyc == 2:
		glob.ADL = Add(X) 	#ALU plus X to ADL
		glob.ADH = 0x00 		#ADH = 0 for zero page
		AHL()  			#Combine ADH and ADL to AB
	elif Cyc == 1:
		glob.A = glob.DB  		#A to zero page byte
		LDAend()


def LDAAB(): #Load to a absolutely, 4Cycs, $AD *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.A = glob.DB
		LDAend()

def LDAAX(): #Load to a absolutely + X, 4+Cycs, $BD *RC*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		print(hex(ADL), "1")
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		print(hex(glob.ADH), "2")
		if (glob.ADL+glob.X)<=0xFF: glob.Cyc -= 1; glob.ADL = Add(glob.X) #not overflowing so just add x and skip next
		else: glob.ADL = Add(X); glob.ALU = glob.ADH #overflowing so add with byte correction and push ADH to ALU
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1) #overflowed so add 1
		print(hex(glob.ADH), "3")
		AHL()
	elif glob.Cyc == 1:
		glob.A = glob.DB
		print(hex(glob.A), "4")
		LDAend()

def LDAAY(): #Load to a abslutely+Y, 4+Cycs, $B9 *RC*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(glob.Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		glob.A = glob.DB
		LDAend()

def LDAIX(): #Load to A from address at zp+X, 6Cycs, $A1 *RC*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.A = glob.DB
		LDAend()

def LDAIY(): #Load to A from address+Y at zp, 5+1Cycs, $B1 *RC*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		glob.A = glob.DB
		LDAend()


#-------------------
#Store A------------
#-------------------
def STAZP(): #Store from A to zp address, 3Cycs, $85 *RC*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.A

def STAZX(): #Store from A to zp address+X, 4Cycs, $95 *RC*
	if glob.Cyc == 3:
		glob.ADL = DB
		glob.ALU = ADL
		glob.ADH = 0x00
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[AB] = glob.A

def STAAB(): #Store from A to absolute address, 4Cycs, $8D *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.A

def STAAX(): #Store from A to absolute address+X, 5Cycs, $9D *RC*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADL = Add(glob.X)
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.A


def STAAY(): #Store from A to absolute address+Y, 5Cycs, $99 *RC*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADL = Add(glob.Y)
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.A

def STAIX(): #Store from A to address at zp+X, 6Cycs, $81 *RC*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.A

def STAIY(): #Store from A to address+Y at zp, 6Cycs, $91 *RC*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.AB+=1
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADL = Add(glob.Y)
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.A


def NOPIP():
	if glob.Cyc == 1:
		pass

#-------------------
#Load X------------
#-------------------
def LDXend():
	if glob.X == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.X >= 0x80:
		SEF('N')
	else:
		CLF('N')

def LDXIM(): #Load to X immediately, 2Cycs, $A2 *RC*
	if glob.Cyc == 1:
		glob.X = glob.DB
		LDXend()

def LDXZP(): #Load to X from zero page, 3Cycs, $A6 *RC*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		glob.X = glob.DB
		LDXend()

def LDXZY(): #Load to X from zero page + Y, 4Cycs, $B6 *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		glob.ADH = 0x00
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.Y)
		AHL()
	elif glob.Cyc == 1:
		glob.X = glob.DB
		LDXend()

def LDXAB(): #Load to X from absolute address, 4Cycs, $AE *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.X = glob.DB
		LDXend()

def LDXAY(): #Load to X from absolute address + Y, 4+1Cycs, $BE *RC*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADH == glob.DB
		if (Add(glob.Y))<=0xFF:
			glob.Cyc -= 1
		glob.ADL = Add(glob.Y)
		AHL()
	elif glob.Cyc == 2:
		glob.ALU = glob.ADH
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		glob.X = glob.DB
		LDXend()


#-------------------
#Load Y------------
#-------------------
def LDYend():
	if glob.Y == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.Y >= 0x80:
		SEF('N')
	else:
		CLF('N')

def LDYIM(): #Load to Y Immediately, 2Cyc, $A0 *RC*
	if glob.Cyc == 1:
		glob.Y = glob.DB
		LDYend()

def LDYZP(): #Load to Y from zero page, 3Cyc, $A4 *RC*
	if glob.Cyc == 2:
		glob.ADH = 0x00
		glob.ADL = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Y = glob.DB
		LDYend()

def LDYZX(): #Load to Y from zero page + X, 4Cyc, $B4 *RC*
	if glob.Cyc == 3:
		glob.ADH = 0x00
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		glob.Y = glob.DB
		LDYend()

def LDYAB(): #Load to Y from absolute, 4Cyc, $AC *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Y = glob.DB
		LDYend()

def LDYAX(): #Load to Y from absolute + X, 4+1cyc, $BC *RC*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (Add(glob.X)) <= 0xFF:
			glob.Cyc -= 1
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 2:
		glob.ALU = glob.ADH
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		glob.Y = glob.DB
		LDYend()


#-------------------
#Store X------------
#-------------------


def STXZP(): #Store from X to zeropage, 3Cyc, $86 *RC*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.X

def STXZY(): #Store from X to zeropage+Y, 4 Cyc, $96 *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.Y)
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.X

def STXAB(): #Store from X to absolute, 4Cyc, $8E *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.X


#-------------------
#Store Y------------
#-------------------


def STYZP(): #Store from Y to zeropage, 3Cyc, $84 *RC*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.Y

def STYZX(): #Store from Y to zeropage+X, 4 Cyc, $94 *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.Y

def STYAB(): #Store from Y to absolute, 4Cyc, $8C *RC*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.Y


#-------------------
#Flags00------------
#-------------------

def CLCIP(): #Clear Carry Flag, 2Cyc, $18 *RC*
	if glob.Cyc == 1:
		CLF("C")

def CLDIP(): #Clear Decimal Flag, 2Cyc, $D8 *RC*
	if glob.Cyc == 1:
		CLF("D")

def CLIIP(): #Clear Interrupt Flag, 2Cyc, $58 *RC*
	if glob.Cyc == 1:
		CLF("I")

def CLVIP(): #Clear Overflow Flag, 2Cyc, $B8 *RC*
	if glob.Cyc == 1:
		CLF("V")

def SECIP(): #Set Carry Flag, 2Cyc, $38 *RC*
	if glob.Cyc == 1:
		SEF("C")

def SEDIP(): #Set Decimal Flag, 2Cyc, $F8 *RC*
	if glob.Cyc == 1:
		SEF("D")

def SEIIP(): #Set Interrupt Flag, 2Cyc, $78 *RC*
	if glob.Cyc == 1:
		SEF("I")


#-------------------
#Increments---------
#-------------------

def INCend():
	if glob.ALU == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.ALU >= 0x80:
		SEF('N')
	else:
		CLF('N')


def INCZP(): #Increment zeropage, 5Cyc, $E6 *RC*
	if glob.Cyc == 4:
		glob.ADH = 0x00
		glob.ADL = glob.DB
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Add(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		INCend()

def INCZX(): #Increment zeropage+X, 6Cyc, $F6 *RC*
	if glob.Cyc == 5:
		glob.ADH = 0x00
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	if glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Add(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		INCend()

def INCAB(): #Increment absolute, 6Cyc, $EE *RC*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
	elif glob.Cyc == 4:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Add(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		INCend()

def INCAX(): #Increment absolute+X, 7Cyc, $FE *RC*
	if glob.Cyc == 6:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 5:
		glob.ADH = glob.DB
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Add(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		INCend()


def INXIP(): #Increment X, 2Cyc, $E8 *RC*
	if glob.Cyc == 1:
		glob.ALU = glob.X
		glob.X = Add(1)
	if glob.X == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.X >= 0x80:
		SEF('N')
	else:
		CLF('N')

def INYIP(): #Increment Y, 2Cyc, $C8 *RC*
	if glob.Cyc == 1:
		glob.ALU = glob.Y
		glob.Y = Add(1)
	if glob.Y == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.Y >= 0x80:
		SEF('N')
	else:
		CLF('N')



#-------------------
#Decrements---------
#-------------------

def DECend():
	if glob.ALU == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.ALU >= 0x80:
		SEF('N')
	else:
		CLF('N')

def DECZP(): #Decrement zeropage, 5Cyc, $C6 *RC*
	if glob.Cyc == 4:
		glob.ADH = 0x00
		glob.ADL = glob.DB
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Sub(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		DECend()

def DECZX(): #Decrement zeropage+X, 6Cyc, $D6 *RC*
	if glob.Cyc == 5:
		glob.ADH = 0x00
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	if glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Sub(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		DECend()

def DECAB(): #Decrement absolute, 6Cyc, $CE *RC*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
	elif glob.Cyc == 4:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Sub(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		DECend()

def DECAX(): #Decrement absolute+X, 7Cyc, $DE *RC*
	if glob.Cyc == 6:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	if glob.Cyc == 5:
		glob.ADH = glob.DB
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ALU = glob.Mem[glob.AB] 
	elif glob.Cyc == 2:
		glob.ALU = Sub(1)
	elif glob.Cyc == 1:
		glob.Mem[glob.AB] = glob.ALU
		DECend()


def DEXIP(): #Decrement X, 2Cyc, $CA *RC*
	if glob.Cyc == 1:
		glob.ALU = glob.X
		glob.X = Sub(1)
	if glob.X == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.X >= 0x80:
		SEF('N')
	else:
		CLF('N')

def DEYIP(): #Decrement Y, 2Cyc, $88 *RC*
	if glob.Cyc == 1:
		glob.ALU = glob.Y
		glob.Y = Sub(1)
	if glob.Y == 0x00:
		SEF('Z')
	else:
		CLF('Z')

	if glob.Y >= 0x80:
		SEF('N')
	else:
		CLF('N')


#-------------------
#Branches---------
#-------------------

def BRANCH(): #general branch for like them all ok!
	HLA() 								# push AB to ADL and ADH

	nov = False 						# checks if we have overflowed
	if (glob.ADL + glob.ALU <= 0xFF and glob.ALU<128):  		# if adding and it no overflow
		glob.Cyc -= 1
		nov = True
		glob.np = 1 											# do adding mode 
	if (glob.ADL - (256-glob.ALU) >= 0x00 and glob.ALU>=128): 	# if subtracting and no underflows
		glob.Cyc -= 1
		nov = True
		glob.np = -1 											# do subtracting mode

	#print(hex(AddSign(glob.ADL)), 'hello look here')
	glob.ADL = AddSign(glob.ADL) 		# add/subtract to/from ADL
	glob.ALU = glob.ADH 				# push ADH to be added IF over/underflowed
	if nov == True:
		AHL() 							# if no overflow the push ADH and ADL to AB
		ABP() 							# push AB to PC
		#print(hex(glob.ADH), hex(glob.ADL))


def BNERL(): #Branch if Not Equal, 2+1+1Cyc, $D0 *RC*
	if glob.Cyc == 3:
		print(glob.P&0x02, "look here my friend yes")
		if (glob.P & 0x02) == 0x02: 		# if zero flag set
			glob.Cyc -= 2 					# skip next 2 cycles
		else:
			glob.ALU = glob.DB 				# push addend to ALU
	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1) 				# if overflowed add 1
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BEQRL(): #Branch if Equal, 2+1+1Cyc, $F0 *RC*
	if glob.Cyc == 3:
		if (glob.P&2) == 0x02: 				# if zero flag set
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BCCRL(): #Branch if Carry Clear, 2+1+1Cyc, $90 *RC*
	if glob.Cyc == 3:
		if (glob.P&1) != 0x01: 				# if carry flag clear
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BCSRL(): #Branch if Carry Set, 2+1+1Cyc, $B0 *RC*
	if glob.Cyc == 3:
		if (glob.P&1) == 0x01: 				# if carry flag set
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BMIRL(): #Branch if Minus, 2+1+1Cyc, $30 *RC*
	if glob.Cyc == 3:
		if (glob.P&0x80) == 0x80: 			# if negative flag set
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BPLRL(): #Branch if Plus, 2+1+1Cyc, $10 *RC*
	if glob.Cyc == 3:
		if (glob.P&0x80) != 0x80: 			# if negative flag clear
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BVCRL(): #Branch if Overflow Clear, 2+1+1Cyc, $50 *RC*
	if glob.Cyc == 3:
		if (glob.P&0x40) != 0x40: 			# if overflow flag clear
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0

def BVSRL(): #Branch if Overflow Set, 2+1+1Cyc, $70 *RC*
	if glob.Cyc == 3:
		if (glob.P&0x40) == 0x40: 			# if overflow flag set
			glob.ALU = glob.DB 				# push addend to ALU
		else:
			glob.Cyc -= 2 					# skip next 2 cycles

	elif glob.Cyc == 2:
		BRANCH()

	elif glob.Cyc == 1:
		if glob.np == 1:
			glob.ADH = Add(1)
		elif glob.np == -1:
			glob.ADH = Sub(1)
		AHL()
		ABP()
		glob.np = 0


#-------------------
#Add w/Carry--------
#-------------------


def ADCend():
	if glob.np == 1:			# if overflowed from end of instr
		SEF("C")
	else:
		CLF("C")
	glob.np = 0

	if glob.vv == 1:
		SEF("V")
	else:
		CLF("V")
	glob.vv = 0

	if glob.A >127:
		SEF("N")
	else:
		CLF("N")

	if glob.A == 0:
		SEF("Z")
	else:
		CLF("Z")

def ADC():
	glob.ALU = glob.DB
	if glob.ALU + glob.A + (glob.P&1)>= 0x100: 		# if overflowing,
		glob.np = 1 					# set emulator's overflow
		print("SEXYY NIGGGGGAAA")
	else: 
		glob.np = 0
	C = (((glob.ALU&0x7F)+(glob.A&0x7F))&0x80)>>7
	M = (glob.ALU&0b10000000)>>7
	N = (glob.A&0b10000000)>>7
	glob.vv = ((M&N)^C)&~(M^N)
	glob.A = Add(glob.A+(glob.P&1))
	ADCend()

def ADCIM(): #Add with Carry Immediate, 2Cyc, $69 *CR*
	if glob.Cyc == 1:
		ADC()
		

def ADCZP(): #Add with Carry Zero page, 3Cyc, $65 *CR*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		ADC()

def ADCZX(): #Add with Carry Zero page + X, 4Cyc, $75 *CR*
	if glob.Cyc == 3:
		glob.ALU = glob.DB
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		ADC()

def ADCAB(): #Add with Carry Absolute, 4Cyc, $6D *CR*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		ADC()

def ADCAX(): #Add with Carry Absolute + X, 4+1Cyc, $7D *CR*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.X)<=0xFF: glob.Cyc -= 1; glob.ADL = Add(glob.X) 
		else: glob.ADL = Add(X); glob.ALU = glob.ADH
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1) #overflowed so add 1
		AHL()
	elif glob.Cyc == 1:
		ADC()

def ADCAY(): #Add with Carry Absolute + Y, 4+1Cyc, $79 *CR*
	if glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.Cyc -= 1; glob.ADL = Add(glob.Y) 
		else: glob.ADL = Add(Y); glob.ALU = glob.ADH
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1) #overflowed so add 1
		AHL()
	elif glob.Cyc == 1:
		ADC()

def ADCIX(): #Add with Carry indexed indirect, 6Cycs, $61 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		ADC()

def ADCIY(): #Add with Carry indirect indexed, 5+1Cycs, $71 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		glob.AB+=1
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(glob.Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		ADC()


#-------------------
#Sub w/Carry--------
#-------------------

def SBCend():
	if glob.np == 1: 				# if overflowed
		CLF("C")					# "Need borrow"
		glob.np = 0
	else:
		SEF("C")

	if glob.vv == 1:
		SEF("V")
		glob.vv = 0
	else:
		CLF("V")

	if glob.A >127:
		SEF("N")
	else:
		CLF("N")


def SBC():
	glob.ALU = glob.DB
	if glob.A+(256-glob.ALU)+~(glob.P&0b1) >=0x100: #if #A-B+C >255
		glob.np = 1 								#overflowed
	else:
		glob.np = 0

	glob.ALU = 256-glob.ALU 		#2's complement

	#overflow flag boolean logic
	C = (((glob.ALU&0x7F)+(glob.A&0x7F))&0x80)>>7
	M = (glob.ALU&0b10000000)>>7
	N = (glob.A&0b10000000)>>7
	glob.vv = ((M&N)^C)&~(M^N)

	glob.A = Add(glob.A)#-1+glob.P&1 this breaks everything?
	glob.A = ByteCheck(glob.A-1+(glob.P&1))
	print(glob.A)
	SBCend()


def SBCIM(): #Sub with Carry Immediate, 2Cyc, $E9 *CR*
	if glob.Cyc == 1:
		SBC()

def SBCZP(): #Sub with Carry Zero Page, 3Cyc, $E5 *CR*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		SBC()

def SBCZX(): #Sub with Carry Zero + X, 4Cyc, $F5 *CR*
	if glob.Cyc == 3:
		glob.ALU = glob.DB
		glob.ADH = 0x00
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		SBC()

def SBCAB(): #Sub with Carry Absolute, 4Cyc, $ED *CR*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		SBC()

def SBCAX(): #Sub with Carry Absolute+X, 4+1Cyc, $FD **
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.X>0xFF: 
			glob.ADL = Add(glob.X)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.X)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		SBC()

def SBCAY(): #Sub with Carry Absolute+Y, 4+1Cyc, $F9 *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.Y>0xFF: 
			glob.ADL = Add(glob.Y)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.Y)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		SBC()

def SBCIX(): #Sub with Carry indexed indirect, 6Cycs, $E1 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		SBC()

def SBCIY(): #Sub with Carry indirect indexed, 5+1Cycs, $F1 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		glob.AB+=1
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(glob.Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		SBC()


#-------------------
#Logican And--------
#-------------------

def ANDend():
	if A == 0:
		SEF("Z")
	else:
		CLF("Z")
	if A >=0x80:
		SEF("N")
	else:
		CLF("N")

def AND():
	glob.A = ByteCheck(glob.A&glob.DB)

def ANDIM(): #And with Carry Immediate, 2Cyc, $29 *CR*
	if glob.Cyc == 1:
		AND()

def ANDZP(): #And with Carry Zero Page, 3Cyc, $25 *CR*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		AND()

def ANDZX(): #And with Carry Zero + X, 4Cyc, $35 *CR*
	if glob.Cyc == 3:
		glob.ALU = glob.DB
		glob.ADH = 0x00
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		AND()

def ANDAB(): #And with Carry Absolute, 4Cyc, $2D *CR*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		AND()

def ANDAX(): #And with Carry Absolute+X, 4+1Cyc, $3D *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.X>0xFF: 
			glob.ADL = Add(glob.X)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.X)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		AND()

def ANDAY(): #And with Carry Absolute+Y, 4+1Cyc, $39 *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.Y>0xFF: 
			glob.ADL = Add(glob.Y)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.Y)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		AND()

def ANDIX(): #And with Carry indexed indirect, 6Cycs, $21 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		AND()

def ANDIY(): #And with Carry indirect indexed, 5+1Cycs, $31 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		glob.AB+=1
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(glob.Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		AND()


#-------------------
#Exclusive Or--------
#-------------------

def EORend():
	if A == 0:
		SEF("Z")
	else:
		CLF("Z")
	if A >=0x80:
		SEF("N")
	else:
		CLF("N")

def EOR():
	glob.A = ByteCheck(glob.A^glob.DB)

def EORIM(): #And with Carry Immediate, 2Cyc, $49 *CR*
	if glob.Cyc == 1:
		EOR()

def EORZP(): #And with Carry Zero Page, 3Cyc, $45 *CR*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		EOR()

def EORZX(): #And with Carry Zero + X, 4Cyc, $55 *CR*
	if glob.Cyc == 3:
		glob.ALU = glob.DB
		glob.ADH = 0x00
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		EOR()

def EORAB(): #And with Carry Absolute, 4Cyc, $4D *CR*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		EOR()

def EORAX(): #And with Carry Absolute+X, 4+1Cyc, $5D *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.X>0xFF: 
			glob.ADL = Add(glob.X)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.X)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		EOR()

def EORAY(): #And with Carry Absolute+Y, 4+1Cyc, $59 *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.Y>0xFF: 
			glob.ADL = Add(glob.Y)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.Y)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		EOR()

def EORIX(): #And with Carry indexed indirect, 6Cycs, $41 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		EOR()

def EORIY(): #And with Carry indirect indexed, 5+1Cycs, $51 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		glob.AB+=1
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(glob.Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		EOR()


#-------------------
#Logical Or---------
#-------------------

def ORAend():
	if A == 0:
		SEF("Z")
	else:
		CLF("Z")
	if A >=0x80:
		SEF("N")
	else:
		CLF("N")

def ORA():
	glob.A = ByteCheck(glob.A|glob.DB)

def ORAIM(): #And with Carry Immediate, 2Cyc, $09 *CR*
	if glob.Cyc == 1:
		ORA()

def ORAZP(): #And with Carry Zero Page, 3Cyc, $05 *CR*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		ORA()

def ORAZX(): #And with Carry Zero + X, 4Cyc, $15 *CR*
	if glob.Cyc == 3:
		glob.ALU = glob.DB
		glob.ADH = 0x00
	elif glob.Cyc == 2:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 1:
		ORA()

def ORAAB(): #And with Carry Absolute, 4Cyc, $0D *CR*
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		ORA()

def ORAAX(): #And with Carry Absolute+X, 4+1Cyc, $1D *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.X>0xFF: 
			glob.ADL = Add(glob.X)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.X)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		ORA()

def ORAAY(): #And with Carry Absolute+Y, 4+1Cyc, $19 *CR*
	if glob.Cyc == 4:
		glob.ALU = glob.DB
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if glob.ALU+glob.Y>0xFF: 
			glob.ADL = Add(glob.Y)
			glob.ALU = glob.ADH
		else:
			glob.ADL = Add(glob.Y)
			glob.Cyc -= 1
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		ORA()

def ORAIX(): #And with Carry indexed indirect, 6Cycs, $01 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		glob.ALU = glob.ADL
	elif glob.Cyc == 4:
		glob.ADL = Add(glob.X)
		AHL()
	elif glob.Cyc == 3:
		glob.ADL = glob.DB
		glob.AB+=1
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		ORA()

def ORAIY(): #And with Carry indirect indexed, 5+1Cycs, $11 *CR*
	if glob.Cyc == 5:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 4:
		glob.ADL = glob.DB
		glob.ALU = glob.ADL
		glob.AB+=1
	elif glob.Cyc == 3:
		glob.ADH = glob.DB
		if (glob.ADL+glob.Y)<=0xFF: glob.ADL=Add(glob.Y); glob.Cyc -=1
		else: glob.ADL = Add(glob.Y); glob.ALU = glob.ADH 
		AHL()
	elif glob.Cyc == 2:
		glob.ADH = Add(1)
		AHL()
	elif glob.Cyc == 1:
		ORA()


#-------------------
#Bit Test-----------
#-------------------

def BIT():
	it = ByteCheck(glob.A&glob.DB)
	en = (it&0b10000000)>>7
	ve = (it&0b01000000)>>6
	if en == 1:
		glob.P = glob.P|en<<7
	else:
		glob.P = ByteCheck(glob.P&~(en<<7))
	if ve == 1:
		glob.P = glob.P|ve<<6
	else:
		glob.P = ByteCheck(glob.P&~(ve<<6))
	if it == 0:
		SEF("Z")
	else:
		CLF("Z")
def BITZP(): #Bit Test Zero Page, 3Cyc, $24 *CR*
	if glob.Cyc == 2:
		glob.ADL = glob.DB
		glob.ADH = 0x00
		AHL()
	elif glob.Cyc == 1:
		BIT()
def BITAB(): #Bit Test Absolute, 4Cyc, $2C **
	if glob.Cyc == 3:
		glob.ADL = glob.DB
	elif glob.Cyc == 2:
		glob.ADH = glob.DB
		AHL()
	elif glob.Cyc == 1:
		BIT()


INSCOD = [0x0,ORAIX,0x2,0x3,0x4,ORAZP,0x6,0x7,0x8,ORAIM,0xA,0xB,0xC,ORAAB,0xE,0xF, #0x0
			BPLRL,ORAIY,0x2,0x3,0x4,ORAZX,0x6,0x7,CLCIP,ORAAY,0xA,0xB,0xC,ORAAX,0xE,0xF,
			0x0,ANDIX,0x2,0x3,BITZP,ANDZP,0x6,0x7,0x8,ANDIM,0xA,0xB,BITAB,ANDAB,0xE,0xF, #0x2
			BMIRL,ANDIY,0x2,0x3,0x4,ANDZX,0x6,0x7,SECIP,ANDAY,0xA,0xB,0xC,ANDAX,0xE,0xF,
			0x0,EORIX,0x2,0x3,0x4,EORZP,0x6,0x7,0x8,EORIM,0xA,0xB,0xC,EORAB,0xE,0xF, #0x4
			BVCRL,EORIY,0x2,0x3,0x4,EORZX,0x6,0x7,CLIIP,EORAY,0xA,0xB,0xC,EORAX,0xE,0xF,
			0x0,ADCIX,0x2,0x3,0x4,ADCZP,0x6,0x7,0x8,ADCIM,0xA,0xB,0xC,ADCAB,0xE,0xF, #0x6
			BVSRL,ADCIY,0x2,0x3,0x4,ADCZX,0x6,0x7,SEIIP,ADCAY,0xA,0xB,0xC,ADCAX,0xE,0xF,
			0x0,STAIX,0x2,0x3,STYZP,STAZP,STXZP,0x7,DEYIP,0x9,0xA,0xB,STYAB,STAAB,STXAB,0xF, #0x8
			BCCRL,STAIY,0x2,0x3,STYZX,STAZX,STXZY,0x7,0x8,STAAY,0xA,0xB,0xC,STAAX,0xE,0xF,
			LDYIM,LDAIX,LDXIM,0x3,LDYZP,LDAZP,LDXZP,0x7,0x8,LDAIM,0xA,0xB,LDYAB,LDAAB,LDXAB,0xF, #0xA
			BCSRL,LDAIY,0x2,0x3,LDYZX,LDAZX,LDXZY,0x7,CLVIP,LDAAY,0xA,0xB,LDYAX,LDAAX,LDXAY,0xF,
			0x0,0x1,0x2,0x3,0x4,0x5,DECZP,0x7,INYIP,0x9,DEXIP,0xB,0xC,0xD,DECAB,0xF, #0xC
			BNERL,0x1,0x2,0x3,0x4,0x5,DECZX,0x7,CLDIP,0x9,0xA,0xB,0xC,0xD,DECAX,0xF,
			0x0,SBCIX,0x2,0x3,0x4,SBCZP,INCZP,0x7,INXIP,SBCIM,NOPIP,0xB,0xC,SBCAB,INCAB,0xF, #0xE
			BEQRL,SBCIY,0x2,0x3,0x4,SBCZX,INCZX,0x7,SEDIP,SBCAY,0xA,0xB,0xC,SBCAX,INCAX,0xF,]

INSCYC = [0x0,6,0x2,0x3,0x4,3,0x6,0x7,0x8,2,0xA,0xB,0xC,4,0xE,0xF, #0x0
			4,6,0x2,0x3,0x4,1,0x6,0x7,2,3,0xA,0xB,0xC,5,0xE,0xF,
			0x0,6,0x2,0x3,3,3,0x6,0x7,0x8,2,0xA,0xB,4,4,0xE,0xF, #0x2
			4,6,0x2,0x3,0x4,4,0x6,0x7,2,5,0xA,0xB,0xC,5,0xE,0xF,
			0x0,6,0x2,0x3,0x4,3,0x6,0x7,0x8,2,0xA,0xB,0xC,4,0xE,0xF, #0x4
			4,6,0x2,0x3,0x4,4,0x6,0x7,2,5,0xA,0xB,0xC,5,0xE,0xF,
			0x0,6,0x2,0x3,0x4,3,0x6,0x7,0x8,2,0xA,0xB,0xC,4,0xE,0xF, #0x6
			4,6,0x2,0x3,0x4,4,0x6,0x7,2,5,0xA,0xB,0xC,5,0xE,0xF,
			0x0,6,0x2,0x3,3,3,3,0x7,2,0x9,0xA,0xB,4,4,4,0xF, #0x8
			4,6,0x2,0x3,4,4,4,0x7,0x8,5,0xA,0xB,0xC,5,0xE,0xF,
			2,6,2,0x3,3,3,3,0x7,0x8,2,0xA,0xB,4,4,4,0xF, #0xA
			4,6,0x2,0x3,4,4,4,0x7,2,5,0xA,0xB,5,5,5,0xF,
			0x0,0x1,0x2,0x3,0x4,0x5,5,0x7,2,0x9,2,0xB,0xC,0xD,6,0xF, #0xC
			4,0x1,0x2,0x3,0x4,0x5,6,0x7,2,0x9,0xA,0xB,0xC,0xD,7,0xF,
			0x0,6,0x2,0x3,0x4,3,5,0x7,2,2,2,0xB,0xC,4,6,0xF, #0xE
			4,6,0x2,0x3,0x4,4,6,0x7,2,5,0xA,0xB,0xC,5,7,0xF,]

INSSTR = [0x0,"ORAIX",0x2,0x3,0x4,"ORAZP",0x6,0x7,0x8,"ORAIM",0xA,0xB,0xC,"ORAAB",0xE,0xF, #0x0
			"BPLRL","ORAIY",0x2,0x3,0x4,"ORAZX",0x6,0x7,"CLCIP","ORAAY",0xA,0xB,0xC,"ORAAX",0xE,0xF,
			0x0,"ANDIX",0x2,0x3,"BITZP","ANDZP",0x6,0x7,0x8,"ANDIM",0xA,0xB,"BITAB","ANDAB",0xE,0xF, #0x2
			"BMIRL","ANDIY",0x2,0x3,0x4,"ANDZX",0x6,0x7,"SECIP","ANDAY",0xA,0xB,0xC,"ANDAX",0xE,0xF,
			0x0,"EORIX",0x2,0x3,0x4,"EORZP",0x6,0x7,0x8,"EORIM",0xA,0xB,0xC,"EORAB",0xE,0xF, #0x4
			"BVCRL","EORIY",0x2,0x3,0x4,"EORZX",0x6,0x7,"CLIIP","EORAY",0xA,0xB,0xC,"EORAX",0xE,0xF,
			0x0,"ADCIX",0x2,0x3,0x4,"ADCZP",0x6,0x7,0x8,"ADCIM",0xA,0xB,0xC,"ADCAB",0xE,0xF, #0x6
			"BVSRL","ADCIY",0x2,0x3,0x4,"ADCZX",0x6,0x7,"SEIIP","ADCAY",0xA,0xB,0xC,"ADCAX",0xE,0xF,
			0x0,"STAIX",0x2,0x3,"STYZP","STAZP","STXZP",0x7,"DEYIP",0x9,0xA,0xB,"STYAB","STAAB","STXAB",0xF, #0x8
			"BCCRL","STAIY",0x2,0x3,"STYZX","STAZX","STXZY",0x7,0x8,"STAAY",0xA,0xB,0xC,"STAAX",0xE,0xF,
			"LDYIM","LDAIX","LDXIM",0x3,"LDYZP","LDAZP","LDXZP",0x7,0x8,"LDAIM",0xA,0xB,"LDYAB","LDAAB","LDXAB",0xF, #0xA
			"BCSRL","LDAIY",0x2,0x3,"LDYZX","LDAZX","LDXZY",0x7,"CLVIP","LDAAY",0xA,0xB,"LDYAX","LDAAX","LDXAY",0xF,
			0x0,0x1,0x2,0x3,0x4,0x5,"DECZP",0x7,"INYIP",0x9,"DEXIP",0xB,0xC,0xD,"DECAB",0xF, #0xC
			"BNERL",0x1,0x2,0x3,0x4,0x5,"DECZX",0x7,"CLDIP",0x9,0xA,0xB,0xC,0xD,"DECAX",0xF,
			0x0,"SBCIX",0x2,0x3,0x4,"SBCZP","INCZP",0x7,"INXIP","SBCIM","NOPIP",0xB,0xC,"SBCAB","INCAB",0xF, #0xE
			"BEQRL","SBCIY",0x2,0x3,0x4,"SBCZX","INCZX",0x7,"SEDIP","SBCAY",0xA,0xB,0xC,"SBCAX","INCAX",0xF,]