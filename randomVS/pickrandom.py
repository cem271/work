import random


def getRandom(keywords):
	text = open(keywords+'.txt','r').read()
	source = text.splitlines()
	num1 = random.randint(0,len(source))
	num2 = random.randint(0,len(source))
	print source[num1]
	print source[num2]

getRandom('keywords')	


