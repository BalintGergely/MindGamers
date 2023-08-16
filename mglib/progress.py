
from typing import Iterable

def progressTick(value,max):
	dmax = min(50,max)
	maxs = str(max)
	dval = (value * dmax) // max
	print(" [{}{}] ".format("=" * (dval)," " * (dmax - dval)),end="")
	print(f" {value:{len(maxs)}}/{maxs}",end="\r")

def progressInit(max):
	progressTick(0,max)

def progressEnd():
	print("",end="\n")

def filterThenSlice(source : Iterable,filter,count : int):

	found = 0
	result = []

	progressInit(count)

	for elem in source:
		if filter(elem):
			result.append(elem)
			found = found + 1
			progressTick(found,count)
		if found == count:
			break
	
	progressEnd()

	return result

def filterAll(source : Iterable,filter):

	count = len(source)
	found = 0
	result = []

	progressInit(count)

	for elem in source:
		if filter(elem):
			result.append(elem)
		found = found + 1
		progressTick(found,count)
	
	progressEnd()

	return result