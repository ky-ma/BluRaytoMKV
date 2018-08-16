#!/usr/bin/python3
import os, shutil, subprocess, pexpect, sys, time, re, operator
import operator
import pdb

MAINPATH = '/share/MakeMKV/'
USER_PERMISSION = 'name'
GROUP_PERMISSION = 'users'
STORAGE = [
		{'freeSpace' : None, 'share' : '/share/3000gb-1', 'path' : '/Movies/', 'media': 'BluRay'},
		{'freeSpace' : None, 'share' : '/share/3000gb-2', 'path' : '/Movies/1080P/', 'media': 'BluRay'},
		{'freeSpace' : None, 'share' : '/share/4000gb-2', 'path' : '/Movies/', 'media': 'BluRay'},
		{'freeSpace' : None, 'share' : '/share/4000gb-3', 'path' : '/Movies/', 'media': 'BluRay'},
		{'freeSpace' : None, 'share' : '/share/4000gb-4', 'path' : '/Movies/', 'media': 'BluRay'},
		{'freeSpace' : None, 'share' : '/share/4000gb-4', 'path' : '/MoviesDVD/', 'media': 'DVD'}
		]

SOURCE = MAINPATH + 'BluRays/'
TRANSCODED = MAINPATH + 'Transcoded/'
MERGED = MAINPATH + 'Merged/'
CONVERTED = MAINPATH + 'Converted/'
CONVERTEDTRANSCODED = CONVERTED + "Transcoded/"
TEMPPATH = MAINPATH + 'tmp/'

reg_exp1 = r'(.+)\.mkv+'					#Strip off .mkv extensions
reg_exp2 = r'(.+)\.x264.+'					#Strip off .x264.DTS.Sub.mkv extensions

convert = True

sourceRenameList = []
sourceFileList = []
transcodedFileList = []
mergedFileList = []
convertedFileList = []

#-------------------Start of Test Section------------------------------
#Script to create test names to debug this script
movieList = [
			"The.Visitor.2007.DVD",
			"Blade.2011.BluRay",
			"Stop.Loss.2008.DVD",
			"Maze.Runner.The.Death.Cure.2018.BluRay",
			"Bad.Boys.1995.BluRay",
			"Wanted.2008.DVD",
			"Life.on.the.Line.2016",
			"Blade.of.the.Immortal.2017.BluRay",
			"House.of.Flying.Daggers.2004.BluRay",
			"Transformers.Prime.Darkness.Rising.2011.DVD"
			]
tempSource = TEMPPATH + 'Test.mkv'
tempConverted = TEMPPATH + 'Test.x264.mkv'

def createSources():
	for movie in movieList:
		movieDir = SOURCE + movie
		movieDirFile = movieDir + '/' + movie + '.mkv'
		movieDirFileTranscoded = TRANSCODED + movie + '.x264.mkv'
		#print "[DBG] move_cmd is: %s" % movieDirFile
		try:
			os.mkdir(movieDir, 0o755)
		except:
			print ('[INFO] Movie Directory Exists')
		#shutil.copyfile(tempSource, movieDirFile)
		#shutil.copyfile(tempConverted, movieDirFileTranscoded)a
#-------------------End of Test Section------------------------------

def checkFileSize():
	global sourceFileList    
	for source in sourceFileList:
		for key in source:		#Look for the fileSize Key then check filesize at the first scan
			if key == 'path':
				path = source[key]
			if key == 'fileSize':
				#print '[DBG] %-20s FileSize %20d Bytes' % (source['name'], source[key])
				fileSizeUpdateCheck = source[key]
			if key == 'name':
				fileName = source[key]
		#pdb.set_trace()
		time.sleep(2)
		fileSizeUpdateCheckDiff = os.stat(path + '/' + fileName + '.mkv').st_size
		while fileSizeUpdateCheck != fileSizeUpdateCheckDiff:
			fileSizeUpdateCheck = os.stat(path + '/' + fileName + '.mkv').st_size
			time.sleep(5)
			fileSizeUpdateCheckDiff = os.stat(path + '/' + fileName + '.mkv').st_size
			#print 'FileSize Previous %s Bytes' % fileSizeUpdateCheck
			print('[DBG] %20s			FileSize %6d: MegaBytes' % (source['name'], fileSizeUpdateCheckDiff/1000000))
	#pdb.set_trace()

#Scannong the source and setting these new files to not transcoded
def scanSource():
	global sourceFileList
	sourceFileList = []
	for path, subFolders, files in os.walk(SOURCE):
		#print ('[DBG] Found directory: %s' % path)
		for file in files:
			try:
				sourceFileList.append({'name':re.findall(reg_exp1, (os.path.join(file)))[0], 'path':os.path.join(path), 'transcoded':'no', 'fileSize':os.stat(path + '/' + os.path.join(file)).st_size})
			except:
				pdb.set_trace()
			#print 'Movie Found: %s' % os.path.join(path) + os.path.join(file)

#Scanning the transcoded folder, files in here have been transcoded bot not merged into the new MKV
def scanTranscoded():
	global transcodedFileList
	transcodedFileList = []
	for path, subFolders, files in os.walk(TRANSCODED):
		for file in files:
			transcodedFileList.append({'name':re.findall(reg_exp2, (os.path.join(file)))[0], 'path':os.path.join(path), 'merged':'no'})
#		print  os.path.join(path) + " " + os.path.join(file)
	#Check to see if SOURCE exists in TRANSCODED\
	for source in sourceFileList:
		for transcoded in transcodedFileList:
			if source['name'] == transcoded['name']:
				source['transcoded'] = 'yes'

#Scanning the Merged folder, files in here have been merged from the Transcoded video into the new MKV
def scanMerged():
	global mergedFileList
	mergedFileList = []
	for path, subFolders, files in os.walk(MERGED):
		for file in files:
			#mergedFileList.append({'name':os.path.join(file), 'path':os.path.join(path)})
			#pdb.set_trace()
			mergedFileList.append({'name':re.findall(reg_exp2,(os.path.join(file)))[0], 'path':os.path.join(path), 'converted':'yes'})
#		print  os.path.join(path) + " " + os.path.join(file)
	#Check to see if TRANSCODED is in MERGED
	for transcoded in transcodedFileList:
		for merged in mergedFileList:
			if transcoded['name'] == merged['name']:
				transcoded['merged'] = 'yes'

#Scanning the converted folder, Source and Transcoded files are moved here after the merge
def scanConverted():
	global convertedFileList
	convertedFileList = []
	for path, subFolders, files in os.walk(CONVERTED):
		for file in files:
			convertedFileList.append({'name':re.findall(reg_exp1,(os.path.join(file)))[0], 'path':os.path.join(path)})
#		print  os.path.join(path) + " " + os.path.join(file)
	#Check to see if MERGED is in CONVERTED
	for merged in mergedFileList:
		for converted in convertedFileList:
			if merged['name'] == converted['name']:
				merged['converted'] = 'yes'

def renameBluRays():
	global sourceRenameList
	sourceRenameList = []
	for folder, subs, files in os.walk(SOURCE):
		for filename in files:
			sourceRenameList.append({'fileName':os.path.join(filename)[:-4], 'filePath':os.path.join(folder), 'renamed':'no'})

	#Moving and auto renaming files under the sub directoryies to match the directory name
	for rename in sourceRenameList:
		if rename['renamed'] == 'no':
			if rename['filePath'] != SOURCE:
				filePath = rename['filePath']
				fileNameOnly = filePath.replace(SOURCE,'') + '.mkv'
				print ('[DBG] Will RENAME this file: %s --->>> %s' % (rename['fileName'], fileNameOnly))
				move_cmd = 'mv "' + rename['filePath'] + '/' + rename['fileName'] + '.mkv" ' + SOURCE + fileNameOnly
				print ('[DBG] move_cmd is: %s' % move_cmd)
				rmdir_cmd = 'rmdir ' + filePath
				print ('[DBG] rmdir_cmd is: %s' % rmdir_cmd)
				subprocess.Popen(move_cmd, shell=True)
				time.sleep(2)
				subprocess.Popen(rmdir_cmd, shell=True)

def checkFiles():
#Check to see if the SOURCE files were moved after MERGED Scan. If not, move SOURCE to CONVERTED
	updatePermissions(MERGED, USER_PERMISSION, GROUP_PERMISSION)
	for merged in mergedFileList:
		for source in sourceFileList:
			#pdb.set_trace()
			if merged['name'] == source['name']:
				print ('[DBG] Moving Source: %s to Converted.' % source['name'])
				#Find the path of the source file that matches that transcoded file
				subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + source['name'] + '"', shell=True)
				shutil.move(source['path'] + source['name'] + '.mkv', CONVERTED + source['name'] + '.mkv')
		for transcoded in transcodedFileList:
			if merged['name'] == transcoded['name']:
				print ('[DBG] Moving Transcoded: %s to Converted/Transcoded.' % transcoded['name'])
				subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + transcoded['name'] + '"', shell=True)
				shutil.move(transcoded['path'] + transcoded['name'] + '.x264.mkv', CONVERTEDTRANSCODED)

def updatePermissions(folder, user, group):
	#scanning to get entire file name
	for path, subFolders, files in os.walk(folder):
		for file in files:
			shutil.chown(os.path.join(path) + os.path.join(file), user, group)
			os.chmod(os.path.join(path) + os.path.join(file), 0o644)

def moveMergedFiles(storage):
	mergedFileList = []
	for shares in storage:
		share = os.statvfs(shares['share'])
		#pdb.set_trace()
		shares['freeSpace'] = share.f_bsize * share.f_bavail/1024/1024/1024
	storage.sort(key=operator.itemgetter('freeSpace'), reverse=True)
	#Sort in reverse
	for shares in storage:
		print('FreeSpace on %s is: %s' % (shares['share'], shares['freeSpace']))
	#Rescan to get full file name without stripping the mkv
	for path, subFolders, files in os.walk(MERGED):
		for file in files:
			#pdb.set_trace()
			mergedFileList.append({'name':os.path.join(file), 'path':os.path.join(path)})
	for shares in storage:
		if shares['media'] == 'DVD':
			dvdPath = shares['share'] + shares['path']
			break
	for shares in storage:
		if shares['media'] == 'BluRay':
			blurayPath = shares['share'] + shares['path']
			break
	for merged in mergedFileList:
		if (re.search('.+(DVD).+', merged['name'])) == 'DVD':
			print('[DBG] Move Command: %s  %s' % (merged['path'] + merged['name'], dvdPath))
		#	pdb.set_trace()
			shutil.move(merged['path'] + merged['name'], dvdPath)
			shutil.chown(dvdPath + merged['name'], USER_PERMISSION, GROUP_PERMISSION)
			os.chmod(dvdPath + merged['name'], 0o644)
		else:
			print('[DBG] Move Command: %s  %s' % (merged['path'] + merged['name'], blurayPath))
		#	pdb.set_trace()
			shutil.move(merged['path'] + merged['name'], blurayPath)
			shutil.chown(blurayPath + merged['name'], USER_PERMISSION, GROUP_PERMISSION)
			os.chmod(blurayPath + merged['name'], 0o644)

def initList():
	scanSource()
	scanTranscoded()
	scanMerged()
	scanConverted()

#createSources()		#Create the Test Area before the main loop

while convert == True:
	print ('[INFO] Scanning Files')
	scanSource()
	checkFileSize()
	renameBluRays()
	initList()					#Create the Initial list of files, because it will change after finishing the queue. 
	checkFiles()
	initList()					#Rescan List after the file moves
	#initList()					#Rescan List after the file moves
#	pdb.set_trace()
	#initList()					#Rescan List after the file moves
	#pdb.set_trace()

#Sort the Dictionary lists
	sourceFileList.sort(key=operator.itemgetter('name'))
	transcodedFileList.sort(key=operator.itemgetter('name'))
	mergedFileList.sort(key=operator.itemgetter('name'))
	convertedFileList.sort(key=operator.itemgetter('name'))
#	sourceFileList.sort(key=operator.itemgetter('name'))
#	transcodedFileList.sort(key=operator.itemgetter('name'))
#	mergedFileList.sort(key=operator.itemgetter('name'))
#	convertedFileList.sort(key=operator.itemgetter('name'))
	print ('----		%d Movies in the Source Directory' % len(sourceFileList))
	for source in sourceFileList:
			print ('%-60s' % source['name'])
	print ('----		%d Movie Files Transcoded' % len(transcodedFileList))
	for merged in transcodedFileList:
			print ('%-60s' % merged['name'])
	print ('----		%d Movies Finished and Merged' % len(mergedFileList))
	for converted in mergedFileList:
			print ('%-60s' % converted['name'])
	print ('-----End of LIST-----')

	if (sourceFileList == []) and (transcodedFileList == [] and mergedFileList != []):
		moveMergedFiles(STORAGE)
#	pdb.set_trace()

	for transcoded in transcodedFileList:
		if transcoded['merged'] == 'no':
			#Find the path of the source file that matches that transcoded file
			for source in range(len(sourceFileList)):
				if sourceFileList[source]['name'] == transcoded['name']:
					print ('[DBG] Source: %s	Transcoded: %s' % (sourceFileList[source]['name'], transcoded['name']))
					subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Starting Merge:" "' + transcoded['name'] + '"', shell=True)
					mkvCheck_cmd = 'mkvmerge -i "' + sourceFileList[source]['path'] + transcoded['name'] + '.mkv"'
					print ('[DBG] Command is: %s' % mkvCheck_cmd)
					mkvCheck = pexpect.spawn(mkvCheck_cmd, encoding='utf-8')
					mkvCheck.logfile = sys.stdout
					status = mkvCheck.expect ([
						pexpect.TIMEOUT,														#0
						pexpect.EOF,															#1
						'Track ID 2: audio \(A_DTS\) \[language:eng track_name:Surround 7.1',	#2
						'Track ID 2: audio \(A_DTS\) \[language:eng track_name:Lossless',		#3
						'Track ID 2: audio \(A_DTS\) \[language:eng track_name:3\/2+1',			#4
						'Track ID 2: audio \(A_TRUEHD\)',										#5
						'Track ID 1: audio \(TrueHD\)', 										#6
						'Track ID 2: audio \(A_AC3\)',											#7
						'Track ID 1: audio \(AC3/EAC3\)',										#8
						'Track ID 2: audio \(A_DTS\) \[language:chi track_name:Lossless',		#9
						'Track ID 2: audio \(A_PCM/INT/LIT\)',									#10
						'Track ID 2: audio \(A_DTS\) \[language:eng track_name:Surround 5.1',	#11
						'Track ID 2: audio \(A_DTS\) \[language:spa track_name:Lossless',		#12
						'Track ID 2: audio \(A_MS/ACM\) \[language:eng track_name:Surround',	#13
						'Track ID 2: audio \(A_DTS\) \[language:chi track_name:Surround',		#14
						'Track ID 2: audio \(A_DTS\)',											#15
						'Track ID 1: audio \(DTS\)',											#16
                        'Track ID 1: audio \(DTS-HD Master Audio\)',                            #17
						'Track ID 1: audio \(A_MS/ACM\)',                                       #18
						'Track ID 2: audio \(AC-3\/E-AC-3\)',                                   #19
						'Track ID 1: audio \(TrueHD Atmos\)',									#20
						'Track ID 1: audio \(DTS-ES\)',                                         #21
						'Track ID 1: audio \(AC-3/E-AC-3\)',									#22
						'Track ID 1: audio \(AC-3\)'											#23
						], timeout = 10)
					if status == 0:
						print ("[DBG] ERROR returned Status of mkvCheck is: %s" % status)
					elif status == 2 or status == 14 or status == 17:         #DTS 7.1
						print ("Audio is DTS-True Surround")
						audioTrack1 = "DTS-TrueHD"
					elif status == 3:	                		#DTS-MA
						print ("Audio is DTS-MA")
						audioTrack1 = "DTS-MA"
						audioTrack2 = "DTS 3/2+1"
					elif status == 4 or status == 13 or status == 16:	#DTS
						print ("Audio is DTS")
						audioTrack1 = "DTS"
					elif status == 5 or status == 6:	                #TrueHD
						print ("Audio is TrueHD")
						audioTrack1 = "TrueHD"
						audioTrack2 = "AC3 3/2+1"
					elif status == 7 or status == 8 or status == 22 or status == 23:	#AC3
						print ("Audio is AC3")
						audioTrack1 = "AC3"
					elif status == 9:	                		#DTS-MA
						print ("Audio is DTS-MA")
						audioTrack1 = "DTS-MA"
						audioTrack2 = "DTS 3/2+1"
					elif status == 10:			                #PCM
						print ("Audio is PCM")
						audioTrack1 = "PCM"
						audioTrack2 = ""
					elif status == 11:	                		#Surround
						print ("Audio is 5.1")
						audioTrack1 = "Surround.5.1"
					elif status == 12:			                #Spanish Lossless
						print ("Audio is DTS-MA")
						audioTrack1 = "DTS-MA"
					elif status == 13:		                	#ACM
						print ("Audio is ACM")
						audioTrack1 = "ACM"
					elif status == 14 or status == 18 or status == 19 or status == 21:      #Surround
						print ("Audio is 5.1")
						audioTrack1 = "Surround.5.1"
					elif status == 20:					 #Atmos
						print ("TrueHD Atmos")
						audioTrack1 = "TrueHD.Atmos"

					mkvCheck.close()
					print ('[DBG] Status is: %s' % status)

					#mkvmerge -o <outputfile> <file with x264> <file with audio/subtitle>

					if status == 3 or status == 5 or status == 7:
						merge_cmd = 'mkvmerge -o "' + MERGED + transcoded['name'] + '.x264.' + audioTrack1  + '.Sub.mkv" --title "' + transcoded['name'] + '.x264.' + audioTrack1 + '.Sub.mkv" --track-order 2:1,3:2,3:3,3:4 --no-chapters "' + TRANSCODED + transcoded['name'] + '.x264.mkv" --track-name 2:"' + audioTrack1 + '" --track-name 3:"' + audioTrack2 + '" -D "' + sourceFileList[source]['path'] + transcoded['name'] + '.mkv"'
					else:
						merge_cmd = 'mkvmerge -o "' + MERGED + transcoded['name'] + '.x264.' + audioTrack1  + '.Sub.mkv" --title "' + transcoded['name'] + '.x264.' + audioTrack1 + '.Sub.mkv" --track-order 2:1,3:2,3:3,3:4 --no-chapters "' + TRANSCODED + transcoded['name'] + '.x264.mkv" --track-name 2:"' + audioTrack1 + '" -D "' + sourceFileList[source]['path'] + transcoded['name'] + '.mkv"'
					print ('[DBG] merge_cmd is: %s' % merge_cmd)
					#print '[DBG] move_cmd is: %s' % move_cmd
					merge = pexpect.spawn(merge_cmd, encoding='utf-8')
					merge.logfile = sys.stdout
					status = merge.expect([pexpect.TIMEOUT, pexpect.EOF], timeout = 14400)
					if status == 0:
						subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Merging Failed: Timed Out', shell=True)
					merge.close()
					subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished Merging:" "' + transcoded['name'] + '"', shell=True)
					#pdb.set_trace()

#Check if it's already transcoded
	for source in sourceFileList:
		if source['transcoded'] == 'no':
			process = subprocess.Popen('ps -ef | egrep "HandBrakeCLI" | grep -v grep', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout = process.communicate()[0]
			process.wait()
			if stdout == b'':
				subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Starting Transcode:" "' + source['name'] + '"', shell=True)
				encoding_cmd = 'HandBrakeCLI -i "' + source['path'] + source['name'] + '.mkv" -o "' + TRANSCODED+source['name'] + '.x264.mkv"  -e x264 -q 20.0 -a none -f mkv --detelecine --decomb --loose-anamorphic -m -x b-adapt=2:rc-lookahead=50'
				print ('[DBG] Encoding CMD: %s' % encoding_cmd)
				#pdb.set_trace()
				#args = shlex.split(encoding_cmd)
				handbrake = pexpect.spawn(encoding_cmd, encoding='utf-8')
				#pdb.set_trace()
				handbrake.logfile = sys.stdout
				status = handbrake.expect ([pexpect.TIMEOUT, pexpect.EOF, 'HandBrake has exited.'], timeout = 32400)
				if status == 0:
					subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Transcoding Timed Out:" "' + source['name'] + '"', shell=True)
				elif status == 1:
					subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Transcoding End of File:" "' + source['name'] + '"', shell=True)
				elif status == 2:
					handbrake.close()
				subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished Transcoding:" "' + source['name'] + '"', shell=True)
			else:
				subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Found another instance of HandBrake running, pausing 5 minutes..."', shell=True)
				time.sleep(10)
		else:	#Nothing to do, so wait
			subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished with Transcoding: Stopping"', shell=True)
			#print 'Waiting for %s minutes' % str(pauseTime/60)

	if (sourceFileList == []) and (transcodedFileList == []):
		pauseTime = 60
		subprocess.Popen('echo "[INFO][$(date +%b\ %d\ %Y:\ %H:%M:%S)] All files Completed, Waiting for 60s"', shell=True)
		time.sleep(pauseTime)
