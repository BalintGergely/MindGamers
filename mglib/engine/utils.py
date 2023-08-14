
import mglib.engine.numbers as numbers
from typing import List,Iterable,Tuple

def shuffleSeq(count : int):
	return (numbers.randomBelow(k) for k in range(2,count + 1))

def performSwaps(perm : List,s : Iterable[Tuple[int,int]]):
	for (a,b) in s:
		x = perm[a]
		y = perm[b]
		perm[a] = y
		perm[b] = x
	return perm

def shufflingSwaps(count : int):
	return zip(range(1,count),shuffleSeq(count))

def shuffle(perm : List):
	return performSwaps(perm, shufflingSwaps(len(perm)))