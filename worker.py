import shutil
from datetime import datetime
import time
from utils import *
import os
import threading
import socket

totaleDifferenza = 0
oldState = {}
deve_fermarsi = False


def ascoltaStop():
	global deve_fermarsi
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost", 9999))
	s.listen(1)
	while not deve_fermarsi:
		conn, addr = s.accept()
		messaggio = conn.recv(1024).decode()
		conn.close()
		if messaggio == "stop":
			deve_fermarsi = True
	s.close()


t = threading.Thread(target=ascoltaStop)
t.start()

while not deve_fermarsi:
	time.sleep(10)
	state = {}

	if not os.path.exists(prefix):
		print("You didnt INIT ad repo (tip: mewit init)")
		exit()

	if not os.path.exists(prefix + "/autosave"):
		os.makedirs(prefix + "/autosave")

	with open(prefix + "/HEAD", "r") as head:
		branch = head.readline().rstrip().removeprefix("ref: ")

	try:
		with open(prefix + "/" + branch, "r") as b:
			current = b.read()
	except FileNotFoundError:
		print("No commit")
		exit()

	currentTree = retrieveTree(current)
	if not currentTree:
		print("Commit somethin before •w•")
		exit()

	with open(prefix + "/objects/trees/" + currentTree) as f:
		lines = f.readlines()
		hashAndBlobs = []
		for line in lines:
			hashAndBlobs.append(line.rstrip().split(" ", 1))

	for fileHash, directory in hashAndBlobs:
		if not os.path.exists(directory):
			print("cancellato: " + directory)
		else:
			with open(directory) as f:
				righe = f.readlines()
				state[directory] = len(righe)
				if directory in oldState:
					totaleDifferenza += abs(len(righe) - oldState[directory])

	oldState = state

	print("Totale differenza accumulata:", totaleDifferenza)

	if totaleDifferenza >= 20:
		timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		saveDir = prefix + "/autosave/" + timestamp
		os.makedirs(saveDir)

		for fileHash, directory in hashAndBlobs:
			if os.path.exists(directory):
				destinazione = os.path.join(saveDir, directory)
				os.makedirs(os.path.dirname(destinazione), exist_ok=True)
				shutil.copy(directory, destinazione)

		print("SCATTA L'AUTOSAVE!")
		totaleDifferenza = 0
