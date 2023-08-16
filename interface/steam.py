
from http.client import HTTPResponse
import urllib.request as r
import re

class NoRedirect(r.HTTPRedirectHandler):
	def __init__(self) -> None:
		super().__init__()
	def redirect_request(self, req, fp, code, msg, headers, newurl):
		return None

class NoError(r.HTTPErrorProcessor):
	def __init__(self) -> None:
		super().__init__()
	def http_response(self, request, response):
		return response
	def https_response(self, request, response):
		return response

opener = r.build_opener(NoRedirect,NoError)

storefrontRedirect = re.compile(r".*/store.steampowered.com/$")
redirectToExisting = re.compile(r".*/store.steampowered.com/app/(.*)$")

def checkSteamAppExists(id : int):
	with opener.open(r.Request(f"https://store.steampowered.com/app/{id}")) as response:
		if response.code == 200:
			return True
		if response.code == 302:
			location = response.getheader("Location")
			if storefrontRedirect.fullmatch(location):
				return False # App doesn't exist. Steam redirects to home page.
			if redirectToExisting.fullmatch(location):
				return True # Steam redirects to a different app.
		print(f"Unknown response code: {response.code} for id {id}")
		return False

xmlEntityRef = {"lt":"<","gt":">","amp":"&","apos":"'","quot":"\""}
xmlEntityPattern = re.compile(r"&(\w+);")

def removeXMLEntityRefs(name : str):
	return xmlEntityPattern.subn(lambda m : xmlEntityRef[m[1]], name)[0]

appnamePattern = re.compile(r".*?<div\s[^<]*?(?<=\s)id=['\"]appHubAppName['\"][^<]*?>([^<]+)</div\s*>")

def tryFindSteamAppName(id : int):
	try:
		with opener.open(r.Request(f"https://store.steampowered.com/app/{id}")) as response:
			if response.code == 200:
				data = response.read()
				data = data.decode()
				m = appnamePattern.search(data)
				return removeXMLEntityRefs(m[1])
			if response.code == 302:
				location = response.getheader("Location")
				if storefrontRedirect.fullmatch(location):
					return ""
				rematch = redirectToExisting.fullmatch(location)
				if rematch:
					return tryFindSteamAppName(rematch[1])
			print(f"Unknown response code: {response.code} for id {id}")
			return ""
	except:
		return ""
