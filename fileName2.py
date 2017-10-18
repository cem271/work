# A very specific utility to be used at work.
# Essentially, goes through a directory of images and/or videos
# with very specific naming conventions. Each file has a specific
# ID number. This code extracts those numbers and creates a CSV
# file as an output. Speeds up the reporting process.



import os
import csv

with open ('fileName.csv', 'wb') as gettyIDs:
	writer = csv.writer(gettyIDs)
	
	for filename in os.listdir("."): 									# For each item in the target directory, get the filenames as a String.
		print filename 													# Debug code to show that the filename is correctly taken.
		if filename.startswith(".") or filename.startswith("fileName"): # Accounting for the fact that MacOSX adds a .DS_Store file to folders								
			print "Oh!"													# And the fact that the code itself is in the folder.
			continue
		else:
			gettyIndex = filename.index("GettyImages")					#Each filename has the word 'GettyImages' in them. Anything before that
			print gettyIndex											#is irrelevant. We call that the GettyIndex.
			workingName = filename[gettyIndex:]							#We remove everything before the GettyIndex and create a workingName.
			indexIn = workingName.index("-")							#There's always a - after GettyIndex. The ID we need is between the -
			if "_" not in workingName and ".jpg" in workingName:		#and a _. Sometimes, there is no _, so we account for that trouble
				indexOut = workingName.index(".jpg")					#by treating the file extension as the last few bits in the filename.
				result = workingName[indexIn+1:indexOut]				#The result is anything between indexIn+1 and indexOut.
				writer.writerow([result])								#We print that into the console for debugging and also write it in a
				print result											#.csv file.
				continue
			elif "_" not in workingName and ".mov" in workingName:
				indexOut = workingName.index(".mov")
				result = workingName[indexIn+1:indexOut]
				writer.writerow([result])
				print result
				continue	
			elif "_" not in workingName and ".mp4" in workingName:
				indexOut = workingName.index(".mp4")
				result = workingName[indexIn+1:indexOut]
				writer.writerow([result])
				print result
				continue
			elif "_" in workingName and "full" not in workingName and "medium" not in workingName and "master" not in workingName and "super" not in workingName and "large" not in workingName and "high" not in workingName:
				indexOut = workingName.index(".")
				result = workingName[indexIn+1:indexOut]
				writer.writerow([result])
				print result
				continue		
			indexOut = workingName.index("_")
			result = workingName[indexIn+1:indexOut]
			writer.writerow([result])
			print result


