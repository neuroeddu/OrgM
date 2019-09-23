'''
		OrgM: Organoid Size Measurer 			- ImageJ Macro written in  Python 
		
		Input		- Directory containing Organoid bright field images
		
		Output		- CSV file containing size and shape descriptors for each organoid image

		Written by: 						Eddie Cai and Rhalena Thomas - NeuroEDDU 
'''

# Import required packages

import os, sys, math, datetime
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.process import ImageProcessor
from ij.process import ImageConverter
from ij.gui import WaitForUserDialog
from ij.gui import GenericDialog
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer


# Set Threshold mode

thresholdMode = False

gd = GenericDialog("Set Threshold Mode")
gd.addChoice("Would you like to enable thresholding mode?", ["No, run the normal macro", "Yes, enable thresholding mode"], "No")
gd.showDialog()
if gd.getNextChoice() == "Yes, enable thresholding mode":
	thresholdMode = True


# Set watershed

watershedMode = False

gd = GenericDialog("Set Watershed Mode")
gd.addChoice("Would you like to enable watershedding?", ["No, do not watershed", "Yes, enable watershed"], "No")
gd.showDialog()
if gd.getNextChoice() == "Yes, enable watershed":
	watershedMode = True



# Set default thresholds:
#	round_threshold is the minimum roundness a roi must have to be considered an organoid for the isOrganoid column
#	area_threshold is the minimum area a roi must have to be considered an organoid for the isorganoid column
#	minimum_size is the minimum area to be considered an ROI

gd = GenericDialog("Other Thresholds.")
gd.addMessage("Ajust after you have determined if new thresholds are needed.")
gd.addStringField("Round threshold", "0.62")
gd.addStringField("Area Threshold", "50000")
gd.addStringField("Minimum Size", "3000")
gd.showDialog()

round_threshold = float(gd.getNextString())
area_threshold = float(gd.getNextString())
minimum_size = float(gd.getNextString())

#set pix_width and pix_height to real dimensions per pixel 

gd = GenericDialog("Dimension Options")
gd.addMessage("Conversion from pixles to uM :Evos 10X pixle width/height = 0.8777017 uM")
gd.addMessage("Conversion from pixles to uM :Evos 4X  pixle width/height = 2.1546047 uM")
gd.addMessage("Conversion from pixles to uM :Calculate for your objective and enter below")
gd.addStringField("Pixel Width:", "0.8777017")
gd.addStringField("Pixel Height:", "0.8777017")
gd.showDialog()

pix_width = gd.getNextString()
pix_height = gd.getNextString()



# Get input and output directories with GUI 

dc = DirectoryChooser("Choose an input directory")  
inputDirectory = dc.getDirectory() 

dc = DirectoryChooser("Choose an output directory")
outputDirectory = dc.getDirectory()

with open(outputDirectory + "output_"+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")+".csv", "w") as output:

# set the output column names for the csv sheet

	output.write("Subfolder, File Name,Feret,MinFeret,Average Feret,Area,Equivalent Circle Diameter, Ellipse Major, Ellipse Minor, Circularity,Roundness,Solidity, MeetsCriteria \n")
	subfolders = []

	# Finds subfolders in input directory

	for subfolder in os.listdir(inputDirectory):
		if os.path.isdir(inputDirectory + subfolder):
			subfolders.append(subfolder)

	# If there are no subfolders, runs on images in input directory instead

	if len(subfolders) == 0:
		subfolders = [""]

	for subfolder in subfolders:

		#Opens each image

		for filename in os.listdir(inputDirectory + subfolder): 
			imp = IJ.openImage(inputDirectory + subfolder + '/' + filename)	

			if imp:
				# 10X objective
				IJ.run(imp, "Properties...", "channels=1 slices=1 frames=1 unit=um pixel_width=" +str(pix_width)+ " pixel_height=" +str(pix_height)+" voxel_depth=25400.0508001")			# Change to a GUI option later?

				# Threshold, fills hole and watershed

				ic = ImageConverter(imp);
				ic.convertToGray8();
				IJ.setAutoThreshold(imp, "Default dark")

				if thresholdMode:
					imp.show()
					IJ.run("Threshold...")
					WaitForUserDialog("Title", "Adjust threshold").show()
				IJ.run(imp, "Convert to Mask", "")
				IJ.run(imp, "Invert", "")
				IJ.run(imp, "Fill Holes", "")
				
				if watershedMode:
					IJ.run(imp, "Watershed", "")



				#Measure particles 

				table = ResultsTable()
				roim = RoiManager(True)
				ParticleAnalyzer.setRoiManager(roim); 
				pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER | ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES, Measurements.AREA | Measurements.FERET | Measurements.CIRCULARITY | Measurements.SHAPE_DESCRIPTORS | Measurements.CENTROID | Measurements.ELLIPSE, table, minimum_size, 9999999999999999, 0.2, 1.0)
				pa.setHideOutputImage(True)
				pa.analyze(imp)

				index = -1
				maxArea = -1

				if thresholdMode:
					imp.show()
					#WaitForUserDialog("Title", "I want to see the ROI").show()


				# Check if Column even exists (in case it didn't measure anything)

				if table.getColumnIndex("Area") != -1:

						# Find the ROI with the largest area

					for i, area in enumerate(table.getColumn(table.getColumnIndex("Area"))):
						if area > maxArea:
							index = i

				

				# Writes everything in the output file
				if index != -1:

					diameter = 2* math.sqrt( float(table.getValue("Area", index)) / (2* math.pi)) 
					isOrganoid = table.getValue("Area", index) > area_threshold and table.getValue("Area", index) > round_threshold
					output.write(str(subfolder) + ',' + filename + ',' + str(table.getValue("Feret", index)) + ',' + str(table.getValue("MinFeret", index)) + ',' + str((table.getValue("MinFeret", index)+table.getValue("Feret", index))/2) + ','  + str(table.getValue("Area", index)) + ',' + str(diameter) + ',' + str(table.getValue("Major", index)) + ','+ str(table.getValue("Minor", index)) + ','+ str(table.getValue("Circ.", index)) + ',' +str(table.getValue("Round", index)) + ',' + str(table.getValue("Solidity", index)) + ','  + str(isOrganoid))
				else:
					output.write(str(subfolder) + ',' + filename + ",NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA")

				output.write('\n')
				imp.changes = False
				imp.close()

				roim.reset()
				roim.close()
				
# End of macro

cat = """

      \    /\           Macro completed!    
       )  ( ')   meow!
      (  /  )
       \(__)|"""

print(cat)

