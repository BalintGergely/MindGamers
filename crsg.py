
from mglib.network.peer import *
from mglib.protocol.choices import *
from mglib.progress import filterAll, filterThenSlice

import time

import interface.steam as steam
import itertools

appSpaceModulus = 1600000
testsPerApp = 25

def soloMode(count : int):
	idspace = utils.shuffle(list(range(appSpaceModulus)))

	for k in filterThenSlice(idspace, steam.checkSteamAppExists, count):
		print(f"https://store.steampowered.com/app/{k}")


def crsgGame(peer : Peer | str, randomAppCount : int, secretAppIds : Set[int], security : int):

	def checkSteamAppExists(id):
		return id in secretAppIds or steam.checkSteamAppExists(id)

	secretAppIds = set(secretAppIds)

	if isinstance(peer,str):
		peer = SocketPeer(peer)
	
	basic.agreeOn(peer,"CRSG Game",randomAppCount,len(secretAppIds))

	peer.send(appSpaceModulus)
	peer.send(testsPerApp)

	peerAppSpaceModulus = peer.recv(int)
	peerTestsPerApp = peer.recv(int)

	usingAppSpaceModulus = max(peerAppSpaceModulus,appSpaceModulus)
	usingTestsPerApp = max(testsPerApp,peerTestsPerApp)

	print(f"Modulus {usingAppSpaceModulus} with TPA {usingTestsPerApp}")

	idspace = list(range(usingAppSpaceModulus))

	random.sharedShuffle(peer, idspace, security)

	totalAppsToChoose = len(secretAppIds) * 2 + randomAppCount

	print("Elimination round 1 Begin")

	k = secretChoice(peer,
		  len(idspace),
		  totalAppsToChoose * usingTestsPerApp,
		  set(idspace.index(id) for id in secretAppIds),
		  len(secretAppIds),
		  security)

	print("Elimination round 1 End")

	idspace = [idspace[i] for i in k]
	idspace.sort()
	cut = len(idspace) // 2

	random.sharedShuffle(peer, idspace, security)

	check = random.coinFlip(peer, security)

	if check:
		myTask = idspace[:cut]
		peerTask = idspace[cut:]
	else:
		myTask = idspace[cut:]
		peerTask = idspace[:cut]
	
	print("Filtering pass 1 of 2")
	
	myFoundApps = filterAll(myTask,checkSteamAppExists)

	peer.send(myFoundApps)
	peerFoundApps = peer.recv(list)

	assert all(k in peerTask for k in peerFoundApps)

	peerMissedApps = [k for k in peerTask if k not in peerFoundApps]
	myMissedApps = [k for k in myTask if k not in myFoundApps]
	
	print("Filtering pass 2 of 2")

	myFoundApps2 = filterAll(peerMissedApps,checkSteamAppExists)

	peer.send(myFoundApps2)
	peerFoundApps2 = peer.recv(list)

	assert all(k in myMissedApps for k in peerFoundApps2)

	idspace = list(set(myFoundApps + myFoundApps2 + peerFoundApps))

	idspace.sort()

	basic.agreeOn(peer,idspace)

	random.sharedShuffle(peer,idspace,security)

	print("Elimination round 2 Begin")

	k = secretChoice(
		peer,
		len(idspace),
		min(len(idspace),totalAppsToChoose),
		set(idspace.index(id) for id in secretAppIds),
		len(secretAppIds),
		security)
	
	print("Elimination round 2 End")
	
	finalAppIds = [idspace[i] for i in k]

	finalAppIds.sort()

	random.sharedShuffle(peer,finalAppIds,security)

	for k in finalAppIds:
		print(f"https://store.steampowered.com/app/{k}")

