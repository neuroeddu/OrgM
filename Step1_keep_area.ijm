// Written by Vince Soubannier & Eddie Cai
// Adjusted by Rhalena Thomas
//  
//Step 1 cut the bad parts out the the image and make a folder with the tiff to input into a batch



function action(input, output, filename)
{	
		open(input + filename);

		

		// keep
			// This will cut away the selected area and make it white

		run("Select All");
		setTool("freehand");

		waitForUser( "Pause","Please isolate manually the region to KEEP. \n Or press OK to keep the whole image. \n  \n Press OK when you are done");
		setBackgroundColor(255, 255, 255);
		
		run("Clear Outside");
		saveAs(filename, output + filename + "_cut.TIF");


		
	    close();



}


input = getDirectory("Choose Input Directory");

output = getDirectory("Choose Output Directory");

list = getFileList(input);
for (i = 0; i < list.length; i++)
{

		if (endsWith(list[i], ".TIF")) {
			action(input, output, list[i]);	
		}

}


waitForUser("Finished!", "Analysis Complete!");
