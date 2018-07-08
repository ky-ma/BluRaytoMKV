#!/usr/bin/python
import os
import subprocess
import sys
import pdb
import time
import re
import operator
import shlex
import pexpect

#Scan:	Converted -	Completed Conversion of Disks					(Originals)
#	Merged - 	Contains mkvmerged subtitle, Transcoded Video and Audio		(Compressed)
#	Movies -	Contains Movies							(Moved)
#	Source - 	Contains NEW Rips						(New)
#	Transcoded - 	Contains x264 transcoded video					(Transcoded)
#

SOURCE = "PATH"
TRANSCODED = "PATH"
MERGED = "PATH"
CONVERTED = "PATH"
MOVIES = "PATH"
PERMISSIONS = "user:group"

#Compare the Transcoded Directory to Source and see if it's already Transcoded, and mark the Source respectively
#
#Compare the Merged Directory to Converted to make sure that the Transcode is finished
###
#rootdir = sys.argv[1]

reg_exp1 = r'(.+?)(.[^\.]*$)'					#Strip off .mkv extensions
reg_exp4 = r'(.+?)(.[^\.]*.[^\.]*.[^\.]*.[^\.]*$)'		#Strip off .x264.DTS.Sub.mkv extensions
reg_exp5 = r'BluRays\/(.+)'								#Capture Directory
convert = True


while convert == True:
	#Fix Permissions
	subprocess.Popen('find ' + SOURCE + ' -type f -name "*.mkv" -print0 | xargs -0 chmod 644', shell=True)
	subprocess.Popen('find ' + SOURCE + ' -type f -name "*.mkv" -print0 | xargs -0 chown ' + PERMISSIONS, shell=True)
	subprocess.Popen('find ' + MERGED + ' -type f -name "*.mkv" -print0 | xargs -0 chmod 644', shell=True)
	subprocess.Popen('find ' + MERGED + ' -type f -name "*.mkv" -print0 | xargs -0 chown ' + PERMISSIONS, shell=True)
	#Reset to default
	sourceFileList = []
	renameSourceFileList = []
	transcodedFileList = []
	mergedFileList = []
	convertedFileList = []
	statusFileList = []
	status = -1

	#print "-----SCAN SOURCE-----"
	for path, subFolders, files in os.walk(SOURCE):
		print ('Found directory: %s' % path)
		for file in files:
			sourceFileList.append({'name':os.path.join(file)[:-4], 'path':os.path.join(path), 'transcoded':'no'})
			#print  os.path.join(path) + " " + os.path.join(file)
	
	#print "-----SCAN TRANSCODED-----"
	for path, subFolders, files in os.walk(TRANSCODED):
	    for file in files:
	        transcodedFileList.append({'name':os.path.join(file)[:-9], 'path':os.path.join(path), 'merged':'no'})
#		print  os.path.join(path) + " " + os.path.join(file)

	#print "-----SCAN MERGED-----"
	for path, subFolders, files in os.walk(MERGED):
	    for file in files:
	        #mergedFileList.append({'name':os.path.join(file), 'path':os.path.join(path)})
	        mergedFileList.append({'name':re.findall(reg_exp4,(os.path.join(file)))[0][0], 'path':os.path.join(path), 'converted':'yes'})
#		print  os.path.join(path) + " " + os.path.join(file)

	#print "-----SCAN CONVERTED-----"
	for path, subFolders, files in os.walk(CONVERTED):
	    for file in files:
	        convertedFileList.append({'name':re.findall(reg_exp1,(os.path.join(file)))[0][0], 'path':os.path.join(path)})
#		print  os.path.join(path) + " " + os.path.join(file)

	#print "-----TRANSCODED-----"
	#Check to see if SOURCE exists in TRANSCODED\
	for source in sourceFileList:
		for transcoded in transcodedFileList:
			if source['name'] == transcoded['name']:
				source['transcoded'] = 'yes'

	#print "-----MERGED-----"
	#Check to see if TRANSCODED is in MERGED
	for transcoded in transcodedFileList:
		for merged in mergedFileList:
			if transcoded['name'] == merged['name']:
				transcoded['merged'] = 'yes'

#	print "-----CONVERTED-----"
	#Check to see if MERGED is in CONVERTED
	for merged in mergedFileList:
		for converted in convertedFileList:
			if merged['name'] == converted['name']:
				merged['converted'] = 'yes'

	#Sort the Dictionary lists
	sourceFileList.sort(key=operator.itemgetter('name'))
	transcodedFileList.sort(key=operator.itemgetter('name'))
	mergedFileList.sort(key=operator.itemgetter('name'))
	convertedFileList.sort(key=operator.itemgetter('name'))

	print "----Files to Transcode: %s" % len(sourceFileList)
	for source in sourceFileList:
		if source['transcoded'] == 'no':
			print '%-60s: Not Transcoded' % source['name']
		elif source['transcoded'] == 'yes':
			print '%-60s: Transcoded' % source['name']
	print "----Files Transcoded: %s" % len(transcodedFileList)
	for merged in transcodedFileList:
		if merged['merged'] == 'no':
			print '%-60s: Not Merged' % merged['name']
		elif merged['merged'] == 'yes':
			print '%-60s: Merged' % merged['name']
	print "----Files Merged: %s" % len(mergedFileList)
	for converted in mergedFileList:
		if converted['converted'] == 'no':
			print '%-60s: Not Converted' % converted['name']
		elif converted['converted'] == 'yes':
			print '%-60s: Converted' % converted['name']
	print "-----End of LIST-----"

	#Check to see if the SOURCE files were moved after MERGED Scan. If not, move SOURCE to CONVERTED
#	pdb.set_trace()
#	print "[DBG] Checking mergedFileList"
	for merged in mergedFileList:
		if merged['converted'] == 'no':
#			pdb.set_trace()
			#Find the path of the source file that matches that transcoded file
			for source in range(len(sourceFileList)):
				if sourceFileList[source]['name'] == merged['name']:
					move_cmd = 'mv "' +  sourceFileList[source]['path'] + '/' + sourceFileList[source]['name'] + ".mkv\" \"" + CONVERTED + sourceFileList[source]['name'] + '.mkv"'
					print "move_cmd is: %s" % move_cmd
#					pdb.set_trace()
					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + sourceFileList[source]['name'] + '"', shell=True)
					subprocess.Popen(move_cmd, shell=True)

#	pdb.set_trace()
	#Check if it's already merged and merge if it isn't
#	print "[DBG] Checking transcodedFileList"
	#import pdb
	#pdb.set_trace()
	for transcoded in transcodedFileList:
		if transcoded['merged'] == 'no':
			#Find the path of the source file that matches that transcoded file
			for source in range(len(sourceFileList)):
				print "Source: %s	Transcoded: %s" % (sourceFileList[source]['name'], transcoded['name'])
				if sourceFileList[source]['name'] == transcoded['name']:
					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Starting Merge:" "' + transcoded['name'] + '"', shell=True)
					mkvCheck_cmd = 'mkvmerge -i "' + sourceFileList[source]['path'] + '/'  + transcoded['name'] + '.mkv"'
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

					if status == 2 or status == 14 or status == 17:         #DTS 7.1
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
						merge_cmd = 'mkvmerge -o "' + MERGED + transcoded['name'] + '.x264.' + audioTrack1  + '.Sub.mkv" --title "' + transcoded['name'] + '.x264.' + audioTrack1 + '.Sub.mkv" --track-order 2:1,3:2,3:3,3:4 --no-chapters "' + TRANSCODED + transcoded['name'] + '.x264.mkv" --track-name 2:"' + audioTrack1 + '" --track-name 3:"' + audioTrack2 + '" -D "' + sourceFileList[source]['path'] + '/' + transcoded['name'] + '.mkv"'
					else:
						merge_cmd = 'mkvmerge -o "' + MERGED + transcoded['name'] + '.x264.' + audioTrack1  + '.Sub.mkv" --title "' + transcoded['name'] + '.x264.' + audioTrack1 + '.Sub.mkv" --track-order 2:1,3:2,3:3,3:4 --no-chapters "' + TRANSCODED + transcoded['name'] + '.x264.mkv" --track-name 2:"' + audioTrack1 + '" -D "' + sourceFileList[source]['path'] + '/' + transcoded['name'] + '.mkv"'
					move_cmd = 'mv "' +  sourceFileList[source]['path'] + '/' + sourceFileList[source]['name'] + ".mkv\" \"" + CONVERTED + sourceFileList[source]['name'] + '.mkv"'

					print "[DBG] merge_cmd is: %s" % merge_cmd
					#print "move_cmd is: %s" % move_cmd
					merge = pexpect.spawn(merge_cmd)
					merge.logfile = sys.stdout
					status = merge.expect([pexpect.TIMEOUT, pexpect.EOF], timeout = 14400)
					if status == 0:
						subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Merging Failed: Timed Out', shell=True)
					merge.close()

					subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Finished Merging:" "' + transcoded['name'] + '"', shell=True)
					subprocess.Popen(move_cmd, shell=True)
		else:
			#pdb.set_trace()
			move_cmd = 'mv "' +  transcoded['path'] + '/' + transcoded['name'] + "\".* " + CONVERTED + '/Transcoded/'
			print "move_cmd is: %s" % move_cmd
			#pdb.set_trace()
			subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Moving to Completed:" "' + transcoded['name'] + '"', shell=True)
			subprocess.Popen(move_cmd, shell=True)

	#Fix Permissions before another loop of Transcoding
	subprocess.Popen('find ' + SOURCE + ' -type f -name "*.mkv" -print0 | xargs -0 chmod 644', shell=True)
	subprocess.Popen('find ' + SOURCE + ' -type f -name "*.mkv" -print0 | xargs -0 chown ' + PERMISSIONS, shell=True)
	subprocess.Popen('find ' + MERGED + ' -type f -name "*.mkv" -print0 | xargs -0 chmod 644', shell=True)
	subprocess.Popen('find ' + MERGED + ' -type f -name "*.mkv" -print0 | xargs -0 chown ' + PERMISSIONS, shell=True)

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


	#One last check after of unmerged transcoded files before pausing to stop the wait before merging
	unmergedFileCount = 0
	for transcoded in transcodedFileList:
		if transcoded['merged'] == 'no':
			unmergedFileCount = unmergedFileCount + 1
	if unmergedFileCount == 0:
		pauseTime = 3600
		subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Completed, Waiting for 60 minutes"', shell=True)
		time.sleep(pauseTime)
	else:
		pauseTime = 300
		subprocess.Popen('echo "[$(date +%b\ %d\ %Y:\ %H:%M:%S)] Waiting for 5 minutes"', shell=True)
		time.sleep(pauseTime)
