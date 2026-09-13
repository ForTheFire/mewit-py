#!/usr/bin/env python3
import socket
import psutil
import os
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

from utils import *


prefix = ".mew"


def main():
	parser = parserDefiner()
	args = parser.parse_args()
	if args.comando == "init":
		init()
	if args.comando == "add":
		add(args.files)
	if args.comando == "rm":
		rm(args.files)
	if args.comando == "commit":
		commit(args.message)
	if args.comando == "log":
		log()
	if args.comando == "status":
		status()
	if args.comando == "checkout":
		checkout(args.checkoutCommit)
	if args.comando == "autosave-start":
		autosaveStart()
	if args.comando == "autosave-stop":
		autosaveStop()
	if args.comando == "autosave-status":
		autosaveStatus()
	


def parserDefiner():
	parser = argparse.ArgumentParser(description="mewit")
	mewit = parser.add_subparsers(title="mewit", description="mew", dest="comando")
	mewit.add_parser('init', help="initiate your repository")
	add = mewit.add_parser('add', help="add to commit some files IDK, ima cat")
	add.add_argument("files", type=str, nargs="+")
	rm = mewit.add_parser('rm', help="remove some files to not commit still, ima cat")
	rm.add_argument("files", type=str, nargs="+")
	commit = mewit.add_parser('commit', help="commit your crimes :D")
	commit.add_argument("message", type=str, nargs="?")
	mewit.add_parser('log', help="bruh... i mean... you dont know what wood is?")
	mewit.add_parser('status', help="bruh... i mean... you dont know what wood is?")
	checkout = mewit.add_parser('checkout', help="revert to a commit")
	checkout.add_argument('checkoutCommit', type=str, nargs=1)
	mewit.add_parser('autosave-start', help="yeah, ima cool cat, do you want autosave evry 20 raws")
	mewit.add_parser('autosave-stop', help="you can also stop the autosave :)")
	mewit.add_parser('autosave-status', help="check if autosave is runnin")
	
	return parser


def init():
	objTypes = ["blobs", "commits", "trees"]
	
	if os.path.exists(prefix):
		print("How many times you want to prr???")
	else:
		refPath = "refs/heads"
		os.makedirs(prefix + "/objects")
		for type in objTypes:
			os.mkdir(prefix + "/objects/" + type)
		os.makedirs(os.path.join(".mew/", refPath))
		with open(prefix + "/HEAD", 'w') as f:
			f.write("ref: " + refPath + "/main")
		print("prrr (cat is ready to *mew*)")


def add(filesToCheck):
	files = []
	for f in filesToCheck:
		if os.path.isdir(f):
			for file in isDir(f):
				files.append(file)
		else: 
			files.append(f)
	print("Files saved in the box: ")
	print(files)
	
	filesToSave = []
	
	for i in files:
		if os.path.exists(i):
			i = normalize_path(i)
			filesToSave.append(i)
		else:
			print()
			print("Error: cat... file not found: ", i)
			print()

	# Old tree dict
	treeDict = {}
	currentTree = None
	try: 
		with open(prefix+"/INDEX",'r') as index:
			currentTree = index.read()
	except FileNotFoundError:
		print("no tre")
	if currentTree:
		with open(prefix + "/objects/trees/" + currentTree) as f:
			lines = f.readlines()
			hashAndBlobs = []
			for line in lines:
				hashAndBlobs.append(line.rstrip().split(" ", 1))
			for file in hashAndBlobs:
				if os.path.exists(file[1]):
					treeDict[file[1]] = file[0] # File: Hash
	
	# Blob
	for i, f in enumerate(filesToSave):
		try: 
			with open(f, "r") as fileToRead:
				content = fileToRead.read()
				fileHash = hashCalc(content)
				if f in treeDict:
					if treeDict[f] == fileHash:
						print("no difference in: " + f)
						treeDict[f] = fileHash
						continue
				print(f + ": " + fileHash)
				treeDict[f] = fileHash
				with open(prefix + "/objects/blobs/" + fileHash, 'w') as hashFile:
					hashFile.write(content)
				
		except FileNotFoundError:
			print("You didnt INIT ad repo (tip: mewit init)")
			return 1

	# Tree
	treeFileData = ""
	for percorso, fileHash in treeDict.items():
		treeFileData += fileHash + " " + percorso + "\n"
	treeHash = hashCalc(treeFileData)
	with open(prefix + "/objects/trees/" + treeHash, 'w') as treeFile:
		treeFile.write(treeFileData)
	with open(prefix + "/INDEX", 'w') as f:
		f.write(treeHash)


def commit(message=None):
	if not message:
		message = "none"
	add([])
	commitData = ""
	with open(prefix+"/INDEX",'r') as index:
		tree = index.read()
	with open(prefix + "/HEAD", 'r') as head: 
		branch = head.readline().rstrip().removeprefix("ref: ")
	if not os.path.exists(prefix + "/" + branch):
		commitData = "tree " + tree + "\n\n\n" # 3 riga sempre vuota, si legge dalla 4 
		if message:
			commitData += message+ "\n"
		print(commitData)
		with open(prefix + "/objects/commits/" + hashCalc(commitData), 'w') as b: 
			b.write(commitData)
		with open(prefix + "/" + branch, 'w') as b: 
			b.write(hashCalc(commitData))
		
	else:
		print("esiste, " + tree)
		with open(prefix + "/" + branch, "r") as b: 
			parent = b.read()
			commitData = "tree " + tree + "\n"
			commitData += "parent " + parent + "\n\n"
			if message:
				commitData += message + "\n"
		with open(prefix + "/" + branch, "w") as b: 
			b.write(hashCalc(commitData))
		with open(prefix + "/objects/commits/" + hashCalc(commitData), 'w') as b: 
			b.write(commitData)

def log():
	if not os.path.exists(prefix):
		print("You didnt INIT ad repo (tip: mewit init)")
		return
	with open(prefix + "/HEAD", 'r') as head: 
		branch = head.readline().rstrip().removeprefix("ref: ")
	try: 
		with open(prefix + "/" + branch, "r") as b: 
			current = b.read()
	except FileNotFoundError:
		print("No commit")
		return
	print("Smaller the number, latest the commit")
	print()
	cN = 0
	toCheck = current
	while toCheck != "":
		print(cN, "| Commit "+ toCheck + ": ")
		with open(prefix + "/objects/commits/" + toCheck) as f:
			content = f.readlines()
			tree = content[0].rstrip()
			toCheck = content[1].rstrip().removeprefix("parent ")
			message = content[3].rstrip()
			print(tree, ", parent " + toCheck, ", message " + message)
		if toCheck != "": 
			print("               ↑                   ")

def status():
	if not os.path.exists(prefix):
		print("You didnt INIT ad repo (tip: mewit init)")
		return
	
	with open(prefix + "/HEAD", 'r') as head: 
		branch = head.readline().rstrip().removeprefix("ref: ")
	try: 
		with open(prefix + "/" + branch, "r") as b:
			current = b.read()
	except FileNotFoundError:
		print("No commit")
		return
	currentTree = retrieveTree(current)
	
	if not currentTree:
		print("Commit somethin before •w•")
		return
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
				if hashCalc(f.read()) != fileHash:
					print(directory + ": has been mewdified")
				else:
					print(directory + ": is safe")
	print()
	try: 
		with open(prefix+"/INDEX",'r') as index:
			lastTree = index.read()
	except FileNotFoundError:
		print("How did you get here, you committed without adding ANYTHIN!?!??")
		return
	if lastTree == currentTree:
		print("You are OK to go")
	else:
		print("You forgot to commit, remember before leaving the session")

def checkout(commitNum):
	if not os.path.exists(prefix):
		print("You didnt INIT ad repo (tip: mewit init)")
		return

	if not os.path.exists(".acf/"):
		os.makedirs(".acf/")

	structure = isDir(".")

	currentDir = []
	for f in structure:
		currentDir.append(normalize_path(f))

	try:
		tree = retrieveTree(commitNum[0])
	except FileNotFoundError:
		print("Commit doesnt exists")
		return

	treeDict = {}
	with open(prefix + "/objects/trees/" + tree) as f:
		folders = os.listdir(".acf")
		num = 0
		
		for name in folders:
			try:
				if num<int(name.removeprefix("checkout")):
					num = int(name.removeprefix("checkout"))
			except ValueError:
				pass
		for file in currentDir:
			destination = os.path.join(".acf/checkout" + str(num+1), file)
			os.makedirs(os.path.dirname(destination), exist_ok=True)
			os.rename(file, destination)

		ignored = {".mew", ".acf"}

		for path in list(Path("./").rglob("*")):
			if any(part in ignored for part in path.parts):
				continue

			if os.path.isdir(path):
				shutil.rmtree(path)
			else:
				os.remove(path)


		lines = f.readlines()

		for line in lines:
			fileHash, path = line.rstrip().split(" ", 1)
			treeDict[path] = fileHash

	with open(prefix + "/HEAD", 'r') as head: 
		branch = head.readline().rstrip().removeprefix("ref: ")
	with open(prefix + "/" + branch, "w") as reference:
		reference.write(commitNum[0])

	for path, hashNum in treeDict.items():
		dirPart = os.path.dirname(path)
		if dirPart:
			os.makedirs(dirPart, exist_ok=True)
		with open(path, "w") as file:
			file.write(readBlob(hashNum))

def rm(rmFiles):
	files = []
	for f in rmFiles:
		if os.path.isdir(f):
			for file in isDir(f):
				files.append(file)

		else: 
			files.append(f)
	print("Files saved in the box: ")
	print(files)
	
	filesToSave = []
	for i in files:
		if os.path.exists(i):
			i = normalize_path(i)
			filesToSave.append(i)
		else:
			print()
			print("Error: cat... file not found: ", i)
			print()

	# Old tree dict
	treeDict = {}
	currentTree = None
	try: 
		with open(prefix+"/INDEX",'r') as index:
			currentTree = index.read()
	except FileNotFoundError:
		print("no tre")
	if currentTree:
		with open(prefix + "/objects/trees/" + currentTree) as f:
			lines = f.readlines()
			hashAndBlobs = []
			for line in lines:
				hashAndBlobs.append(line.rstrip().split(" ", 1))
			for file in hashAndBlobs:
				if os.path.exists(file[1]):
					treeDict[file[1]] = file[0] # File: Hash
	
	# Blob
	for i, f in enumerate(filesToSave):
		if f in treeDict:
			treeDict.pop(f)
			print(treeDict, f)

	# Tree
	treeFileData = ""
	for percorso, fileHash in treeDict.items():
		treeFileData += fileHash + " " + percorso + "\n"
	treeHash = hashCalc(treeFileData)
	with open(prefix + "/objects/trees/" + treeHash, 'w') as treeFile:
		treeFile.write(treeFileData)
	with open(prefix + "/INDEX", 'w') as f:
		f.write(treeHash)

def autosaveStart():
		if not os.path.exists(prefix):
				print("You didnt INIT ad repo (tip: mewit init)")
				return

		pidPath = prefix + "/autosave.pid"

		# Controlla se è già in esecuzione
		if os.path.exists(pidPath):
				try:
						with open(pidPath, "r") as f:
								pid = int(f.read())
						if psutil.pid_exists(pid):
								p = psutil.Process(pid)
								if "python" in p.name().lower():
										print("Autosave già in esecuzione (PID " + str(pid) + ")")
										return
				except (ValueError, psutil.NoSuchProcess):
						pass

		cartella_script = os.path.dirname(os.path.abspath(__file__))
		percorso_worker = os.path.join(cartella_script, "worker.py")

		process = subprocess.Popen(
				[sys.executable, percorso_worker],
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL
		)

		with open(pidPath, "w") as f:
				f.write(str(process.pid))

		print("Autosave avviato, PID:", process.pid)

def autosaveStop():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(("localhost", 9999))
		s.sendall("stop".encode())
		s.close()
		print("Autosave fermato")
	except ConnectionRefusedError:
		print("L'autosave non è in esecuzione")
	
	pidPath = prefix + "/autosave.pid"
	if os.path.exists(pidPath):
		os.remove(pidPath)

def autosaveStatus():
	pidPath = prefix + "/autosave.pid"
	if os.path.exists(pidPath):
		try:
			with open(pidPath, "r") as f:
				pid = int(f.read())
			if psutil.pid_exists(pid) and "python" in psutil.Process(pid).name().lower():
				print("In esecuzione")
				return
		except (ValueError, psutil.NoSuchProcess):
			pass
	print("Non in esecuzione")
main()
