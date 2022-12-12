#!/usr/bin/python3

import sys, json


def importJson(ifile):
	f = open("DINOMSSG","wb")
	fj = open(ifile,"r")
	aj = fj.read()
	j = json.JSONDecoder().decode(aj)

	a = 1

	startPos = len(j.keys()) * 2
	# print("start pos:",startPos)

	offsetChars = startPos
	newCharCount = 0

	pos = startPos

	offsets = [startPos]

	# pos += 3

	for x in j.keys():
		# print(x)
		# print("header at, string at", pos,end='')
		pos += 1
		# print(' ', pos)
		for d in j[x]['data']:
			if 'x' in j[x]['data'][d].keys():
				# print("pos before, len, after:",pos,3,end='')
				pos += 3
				# print(' ',pos)
			# print("pos before, len, after:",pos,len(j[x]['data'][d]['string']),end='')
			pos += len(j[x]['data'][d]['string'])
			# print(' ',pos)
		pos += 2
		offsets.append(pos)

	offsets = offsets[:-1]
	# print(offsets)
	# print(len(offsets))

	for x in offsets:
		f.write(int.to_bytes(x, length=2, byteorder="little"))

	for x in j.keys():
		headerlen=0
		for d in j[x]['data']:
			if 'x' in j[x]['data'][d].keys():
				headerlen += 3
			headerlen += len(j[x]['data'][d]['string'])
		headerlen += 1
		f.write(int.to_bytes(headerlen, length=2,byteorder='little'))

		for d in j[x]['data']:
			if 'x' in j[x]['data'][d].keys():
				f.write(int.to_bytes(200, length=1,byteorder='little'))
				f.write(int.to_bytes(j[x]['data'][d]['x'], length=1,byteorder='little'))
				f.write(int.to_bytes(j[x]['data'][d]['y'], length=1,byteorder='little'))
			for s in j[x]['data'][d]['string']:
				f.write(int.to_bytes(ord(s), length=1,byteorder='little'))
		f.write(int.to_bytes(38, length=1,byteorder='little'))

	fj.close()
	f.close()

def exportJson(ofile):
	j = {}

	f = open("DINOMSSG", "rb")

	a = f.read()
	f.close()

	firstStringStart = int.from_bytes(a[:2],byteorder="little")

	offsetArraySize = int(firstStringStart / 2) - 1
	# print(offsetArraySize)

	offsetArray = [firstStringStart]
	strings = []
	specialStrings = []

	x = 0
	i = 2

	while x < offsetArraySize:
		offsetArray.append(int.from_bytes(a[i:i+2],byteorder="little"))
		i = i + 2
		x = x + 1

	# pos = offsetArray[0]
	i=0
	addoffset = 0
	special = False

	for t in offsetArray:
		if a[t] == 38 and i!=41:
			start = t + 3
		else:
			start = t + 2

		objlen = 0
		

		while start+objlen < len(a) and a[start+objlen] != 38 and objlen < 1500:
			if a[start+objlen] == 200:
				objlen += 3
				continue
			objlen += 1

		if objlen >= 1500:
			print("Error finding string end for offset", t, a[start:start+objlen])
		else:
			if objlen > 0:
				# print(i,"offset, length, start, end",t,objlen,start,start+objlen)
				strings.append(a[start:start+objlen])
			else:
				print("Error loading string at offset",t,"objlen",objlen)
		i = i + 1

	# print(strings[0])

	slist = strings
	i = 0

	pos = firstStringStart

	while i < len(slist):
		j[i] = {}
		# j[i]['offset'] = pos
	
		pos = pos + 2

		# j[i]['data'] = str(slist[i])
		j[i]['data'] = {}
		p=0
		dataindex = 0
		while p < len(slist[i]):

			if not (dataindex in j[i]['data'].keys()):
				j[i]['data'][dataindex] = {}
				j[i]['data'][dataindex]["string"] = ""

			if slist[i][p] == 200:
				dataindex += 1
				j[i]['data'][dataindex] = {}
				j[i]['data'][dataindex]["x"] = slist[i][p+1]
				j[i]['data'][dataindex]["y"] = slist[i][p+2]
				j[i]['data'][dataindex]["string"] = ""
				pos += 3
				p += 3

			if slist[i][p] >= 32 and slist[i][p] < 128:
				j[i]['data'][dataindex]["string"] += chr(slist[i][p])
			else:
				j[i]['data'][dataindex]["string"] += hex(slist[i][p])
			pos += 1
			p=p+1
		pos = pos + 2
		i = i + 1

	f = open(ofile, "w")
	f.write(json.JSONEncoder().encode(j))
	f.close()

def usage():
	print("Usage:")
	print("edit-dinossg < -e [file name] | -i [file name] >")
	print("")
	print("Utility to help modifying the DINOMSSG data file")
	print("")
	print("")
	print("-e | -export [file name] - Export DINOMSSG to json file")
	print("\t\t\tfile name is an optional argument, if not provided")
	print("\t\t\twill default to DINOMSSG.json")
	print("")
	print("-i | -import [file name] - Import json file and save to DINOMSSG")
	print("\t\t\tfile name is an optional argument, if not provided")
	print("\t\t\twill default to DINOMSSG.json")

i = 0

for arg in sys.argv:
	if arg == "-e" or arg == "-export":
		outFile = "DINOMSSG.json"
		if i+1 < len(sys.argv):
			outFile = sys.argv[i+1]
		exportJson(outFile)
		exit()

	if arg == "-i" or arg == "-import":
		inFile = "DINOMSSG.json"
		if i+1 < len(sys.argv):
			inFile = sys.argv[i+1]
		importJson(inFile)
		exit()

	i = i + 1

usage()