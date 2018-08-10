#!/usr/bin/python
import os, shutil, subprocess, pexpect, sys, time, re
import pdb

SOURCE = "/share/MakeMKV/BluRays/"
TRANSCODED = "/share/MakeMKV/Transcoded/"
MERGED = "/share/MakeMKV/Merged/"
CONVERTED = "/share/MakeMKV/Converted/"
CONVERTEDTRANSCODED = CONVERTED + "Transcoded/"
MOVIES = "/share/Movies/"
PERMISSIONS = "user:group"
TEMPPATH = "/share/MakeMKV/tmp/"

reg_exp1 = r'(.+?)(.[^\.]*$)'					#Strip off .mkv extensions
reg_exp4 = r'(.+?)(.[^\.]*.[^\.]*.[^\.]*.[^\.]*$)'		#Strip off .x264.DTS.Sub.mkv extensions
reg_exp5 = r'BluRays\/(.+)'								#Capture Directory
convert = True

sourceRenameList = []
sourceFileList = []
renameSourceFileList = []
transcodedFileList = []
mergedFileList = []
convertedFileList = []
statusFileList = []
status = -1

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
		print(movieDirFile)
		try:
			os.mkdir(movieDir, 0755)
		except:
			print 'Movie Directory Exists'
		#shutil.copyfile(tempSource, movieDirFile)
		#shutil.copyfile(tempConverted, movieDirFileTranscoded)
#print "-----SCAN SOURCE-----"
#Scannong the source and setting these new files to not transcoded
def scanSource():
	for path, subFolders, files in os.walk(SOURCE):
		#print ('Found directory: %s' % path)
		for file in files:
			sourceFileList.append({'name':os.path.join(file)[:-4], 'path':os.path.join(path), 'transcoded':'no'})
			print 'Movie Found: %s' % os.path.join(path) + os.path.join(file)

#print "-----SCAN TRANSCODED-----"
#Scanning the transcoded folder, files in here have been transcoded bot not merged into the new MKV
def scanTranscoded():
	for path, subFolders, files in os.walk(TRANSCODED):
		for file in files:
			transcodedFileList.append({'name':os.path.join(file)[:-9], 'path':os.path.join(path), 'merged':'no'})
#		print  os.path.join(path) + " " + os.path.join(file)
	#print "-----TRANSCODED-----"
	#Check to see if SOURCE exists in TRANSCODED\
	for source in sourceFileList:
		for transcoded in transcodedFileList:
			if source['name'] == transcoded['name']:
				source['transcoded'] = 'yes'

#print "-----SCAN MERGED-----"
#Scanning the Merged folder, files in here have been merged from the Transcoded video into the new MKV
def scanMerged():
	for path, subFolders, files in os.walk(MERGED):
		for file in files:
			#mergedFileList.append({'name':os.path.join(file), 'path':os.path.join(path)})
			mergedFileList.append({'name':re.findall(reg_exp4,(os.path.join(file)))[0][0], 'path':os.path.join(path), 'converted':'yes'})
#		print  os.path.join(path) + " " + os.path.join(file)
	#print "-----MERGED-----"
	#Check to see if TRANSCODED is in MERGED
	for transcoded in transcodedFileList:
		for merged in mergedFileList:
			if transcoded['name'] == merged['name']:
				transcoded['merged'] = 'yes'

#print "-----SCAN CONVERTED-----"
#Scanning the converted folder, Source and Transcoded files are moved here after the merge
def scanConverted():
	for path, subFolders, files in os.walk(CONVERTED):
		for file in files:
			convertedFileList.append({'name':re.findall(reg_exp1,(os.path.join(file)))[0][0], 'path':os.path.join(path)})
#		print  os.path.join(path) + " " + os.path.join(file)
#	print "-----CONVERTED-----"
	#Check to see if MERGED is in CONVERTED
	for merged in mergedFileList:
		for converted in convertedFileList:
			if merged['name'] == converted['name']:
				merged['converted'] = 'yes'

def renameBluRays():
	global renameSourceFileList
	renameSourceFileList = []
	for folder, subs, files in os.walk(SOURCE):
		for filename in files:
			sourceRenameList.append({'fileName':os.path.join(filename)[:-4], 'filePath':os.path.join(folder), 'renamed':'no'})

	#Moving and auto renaming files under the sub directoryies to match the directory name
	for rename in sourceRenameList:
		if rename['renamed'] == 'no':
			if rename['filePath'] == SOURCE:
				print 'Do not need to rename file: %s' % rename['fileName']
			else:
				filePath = rename['filePath']
				fileNameOnly = filePath.replace(SOURCE,'') + '.mkv'
				print 'Will RENAME this file: %s --->>> %s' % (rename['fileName'], fileNameOnly)
				move_cmd = 'mv ' + rename['filePath'] + '/' + rename['fileName'] + '.mkv ' + SOURCE + fileNameOnly
				print "[DBG] move_cmd is: %s" % move_cmd
				rmdir_cmd = 'rmdir ' + filePath
				print "[DBG] rmdir_cmd is: %s" % rmdir_cmd
				subprocess.Popen(move_cmd, shell=True)
				subprocess.Popen(rmdir_cmd, shell=True)

def checkFiles():
#Check to see if the SOURCE files were moved after MERGED Scan. If not, move SOURCE to CONVERTED
#	pdb.set_trace()
	for merged in mergedFileList:
		for source in sourceFileList:
			if merged['name'] == source['name']:
				print '[DBG] Moving Source: %s to Converted.' % source['name']
				#Find the path of the source file that matches that transcoded file
				move_cmd = 'mv ' + source['path'] + source['name'] + '.mkv ' + CONVERTED + source['name'] + '.mkv'
				#print "[DBG] CHECKFILESTATUS move_cmd is: %s" % move_cmd
				#pdb.set_trace()
				subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + source['name'] + '"', shell=True)
				subprocess.Popen(move_cmd, shell=True)
				time.sleep(2)
		for transcoded in transcodedFileList:
			if merged['name'] == transcoded['name']:
				print '[DBG] Moving Transcoded: %s to Converted/Transcoded.' % transcoded['name']
				move_cmd = 'mv ' +  transcoded['path'] + transcoded['name'] + '.x264.mkv ' + CONVERTEDTRANSCODED
				#print "[DBG] CHECKFILESTATUS move_cmd is: %s" % move_cmd
				#pdb.set_trace()
				subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + transcoded['name'] + '"', shell=True)
				subprocess.Popen(move_cmd, shell=True)
				time.sleep(2)

def checkTranscodedFiles():
#Check to see if the SOURCE files were moved after MERGED Scan. If not, move SOURCE to CONVERTED
#	pdb.set_trace()
#	print "[DBG] Checking mergedFileList"
	for transcoded in transcodedFileList:
		if transcoded['merged'] == 'no':
			print '[DBG] Moving Transcoded: %s to Converted/Transcoded.' % transcoded['name']
			#Find the path of the source file that matches that transcoded file
			move_cmd = 'mv ' + transcoded['path'] + transcoded['name'] + '.x264.mkv ' + CONVERETDTRANSCODED + transcoded['name'] + '.x264.mkv'
			#print "[DBG] CheckTranscodedFiles move_cmd is: %s" % move_cmd
			pdb.set_trace()
			subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + transcoded['name'] + '"', shell=True)
			subprocess.Popen(move_cmd, shell=True)
			time.sleep(2)

def initList():
	global sourceRenameList
	global sourceFileList
	global transcodedFileList
	global mergedFileList
	global convertedFileList
	global statusFileList
	sourceRenameList = []
	sourceFileList = []
	transcodedFileList = []
	mergedFileList = []
	convertedFileList = []
	statusFileList = []

	scanSource()
	scanTranscoded()
	scanMerged()
	scanConverted()

#createSources()

while convert == True:
	renameBluRays()
	initList()					#Create the Initial list of files, because it will change after finishing the queue. 
	checkFiles()
	initList()					#Rescan List after the file moves
	#checkTranscodedFiles()		#Move Transcoded Files that don't line up with any merged files.
	#initList()					#Rescan List after the file moves
#	pdb.set_trace()

#Sort the Dictionary lists
	sourceFileList.sort()
	transcodedFileList.sort()
	mergedFileList.sort()
	convertedFileList.sort()
#	sourceFileList.sort(key=operator.itemgetter('name'))
#	transcodedFileList.sort(key=operator.itemgetter('name'))
#	mergedFileList.sort(key=operator.itemgetter('name'))
#	convertedFileList.sort(key=operator.itemgetter('name'))

	print "----		%s Movies in the Source Directory" % len(sourceFileList)
	for source in sourceFileList:
			print '%-60s' % source['name']
	print "----		%s Movie Files Transcoded" % len(transcodedFileList)
	for merged in transcodedFileList:
			print '%-60s' % merged['name']
	print "----		%s Movies Finished and Merged" % len(mergedFileList)
	for converted in mergedFileList:
			print '%-60s' % converted['name']
	print "-----End of LIST-----"

#One last check after of unmerged transcoded files before pausing to stop the wait before merging
	unmergedFileCount = 0
	for transcoded in transcodedFileList:
		if transcoded['merged'] == 'no':
			unmergedFileCount = unmergedFileCount + 1
	print "[DBG] Unmerged File Count is: %s" % unmergedFileCount

	#pdb.set_trace()

	for transcoded in transcodedFileList:
		if transcoded['merged'] == 'no':
			#Find the path of the source file that matches that transcoded file
			for source in range(len(sourceFileList)):
				if sourceFileList[source]['name'] == transcoded['name']:
					print "Source: %s	Transcoded: %s" % (sourceFileList[source]['name'], transcoded['name'])
					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Starting Merge:" "' + transcoded['name'] + '"', shell=True)
					mkvCheck_cmd = 'mkvmerge -i "' + sourceFileList[source]['path'] + transcoded['name'] + '.mkv"'
					print "[DBG] Command is: %s" % mkvCheck_cmd
					mkvCheck = pexpect.spawn(mkvCheck_cmd)
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
						print "[DBG] ERROR returned Status of mkvCheck is: %s" % status
						mkvCheck.close()
					elif status == 2 or status == 14 or status == 17:         #DTS 7.1
						print "Audio is DTS-True Surround"
						audioTrack1 = "DTS-TrueHD"
					elif status == 3:	                		#DTS-MA
						print "Audio is DTS-MA"
						audioTrack1 = "DTS-MA"
						audioTrack2 = "DTS 3/2+1"
					elif status == 4 or status == 13 or status == 16:	#DTS
						print "Audio is DTS"
						audioTrack1 = "DTS"
					elif status == 5 or status == 6:	                #TrueHD
						print "Audio is TrueHD"
						audioTrack1 = "TrueHD"
						audioTrack2 = "AC3 3/2+1"
					elif status == 7 or status == 8 or status == 22 or status == 23:	#AC3
						print "Audio is AC3"
						audioTrack1 = "AC3"
					elif status == 9:	                		#DTS-MA
						print "Audio is DTS-MA"
						audioTrack1 = "DTS-MA"
						audioTrack2 = "DTS 3/2+1"
					elif status == 10:			                #PCM
						print "Audio is PCM"
						audioTrack1 = "PCM"
						audioTrack2 = ""
					elif status == 11:	                		#Surround
						print "Audio is 5.1"
						audioTrack1 = "Surround.5.1"
					elif status == 12:			                #Spanish Lossless
						print "Audio is DTS-MA"
						audioTrack1 = "DTS-MA"
					elif status == 13:		                	#ACM
						print "Audio is ACM"
						audioTrack1 = "ACM"
					elif status == 14 or status == 18 or status == 19 or status == 21:      #Surround
						print "Audio is 5.1"
						audioTrack1 = "Surround.5.1"
					elif status == 20:					 #Atmos
						print "TrueHD Atmos"
						audioTrack1 = "TrueHD.Atmos"

					print "[DBG] Status is: %s" % status

					#mkvmerge -o <outputfile> <file with x264> <file with audio/subtitle>

					if status == 3 or status == 5 or status == 7:
						merge_cmd = 'mkvmerge -o "' + MERGED + transcoded['name'] + '.x264.' + audioTrack1  + '.Sub.mkv" --title "' + transcoded['name'] + '.x264.' + audioTrack1 + '.Sub.mkv" --track-order 2:1,3:2,3:3,3:4 --no-chapters "' + TRANSCODED + transcoded['name'] + '.x264.mkv" --track-name 2:"' + audioTrack1 + '" --track-name 3:"' + audioTrack2 + '" -D "' + sourceFileList[source]['path'] + transcoded['name'] + '.mkv"'
					else:
						merge_cmd = 'mkvmerge -o "' + MERGED + transcoded['name'] + '.x264.' + audioTrack1  + '.Sub.mkv" --title "' + transcoded['name'] + '.x264.' + audioTrack1 + '.Sub.mkv" --track-order 2:1,3:2,3:3,3:4 --no-chapters "' + TRANSCODED + transcoded['name'] + '.x264.mkv" --track-name 2:"' + audioTrack1 + '" -D "' + sourceFileList[source]['path'] + transcoded['name'] + '.mkv"'
					print "[DBG] merge_cmd is: %s" % merge_cmd
					#print "move_cmd is: %s" % move_cmd
					merge = pexpect.spawn(merge_cmd)
					merge.logfile = sys.stdout
					status = merge.expect([pexpect.TIMEOUT, pexpect.EOF], timeout = 14400)
					if status == 0:
						subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Merging Failed: Timed Out', shell=True)
					merge.close()
					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished Merging:" "' + transcoded['name'] + '"', shell=True)

#Check if it's already transcoded
	for source in sourceFileList:
		if source['transcoded'] == 'no':
			process = subprocess.Popen('ps -ef | egrep "HandBrakeCLI" | grep -v grep', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout = process.communicate()[0]
			process.wait()
			if stdout == '':
				subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Starting Transcode:" "' + source['name'] + '"', shell=True)
				encoding_cmd = 'HandBrakeCLI -i "' + source['path'] + source['name'] + '.mkv" -o "' + TRANSCODED+source['name'] + '.x264.mkv"  -e x264 -q 20.0 -a none -f mkv --detelecine --decomb --loose-anamorphic -m -x b-adapt=2:rc-lookahead=50'
				print "Encoding CMD: %s" % encoding_cmd
				#import pdb
				#pdb.set_trace()
				#args = shlex.split(encoding_cmd)
				handbrake = pexpect.spawn(encoding_cmd)
				#pdb.set_trace()
				handbrake.logfile = sys.stdout
				status = handbrake.expect ([pexpect.TIMEOUT, pexpect.EOF, 'HandBrake has exited.'], timeout = 32400)
				if status == 0:
					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Transcoding Timed Out:" "' + source['name'] + '"', shell=True)
				elif status == 1:
					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Transcoding End of File:" "' + source['name'] + '"', shell=True)
				elif status == 2:
					handbrake.close()
				subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished Transcoding:" "' + source['name'] + '"', shell=True)
			else:
				subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Found another instance of HandBrake running, pausing 5 minutes..."', shell=True)
				time.sleep(300)
	else:	#Nothing to do, so wait
		subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished with Transcoding: Stopping"', shell=True)
		#aconvert = False
		#break
		#print "Waiting for %s minutes" % str(pauseTime/60)

	if unmergedFileCount == 0:
#Reset to default
#Rescan everything again after moving the files.
		pauseTime = 3600
		subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Completed, Waiting for 60 minutes"', shell=True)
		#pdb.set_trace()
		time.sleep(pauseTime)
