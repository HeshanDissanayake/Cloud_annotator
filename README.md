# Cloud Annotator
This is a program that is used to annotate a image dataset which has all sky images. This has the following functionalities.
* Annotate a pixel in a image that is either cloud/thin coud/sky/sun.
* Export cropped images which are in a specific dimention. The center of that cropped image represent the selected pixel for annotating.
* Ability to annotate multiple images in one session.
* Shows previouse annotations that are done in earlier sessions.

# pre requisites
* Open CV 
```bash
pip3 install opencv-python
```

* Numpy
```bash
pip3 install numpy
```

* PyAutoGUI
```bash
pip3 install PyAutoGUI
```

* keyboard
```bash
pip3 install keyboard
```

# Before running 
make sure that a directory called `images` has to be created at the root directory with the images that will be annotated inside that directory

# Run the program
```bash
python3 anotator.py
```

# GUI

<img src="http://url/image.png" height="60" width="60" >

The image that is currently selected out of all images in the `images` directory, will we shown in the GUI preview. The cropped images view in the right top shows the image patch that will be extracted if that specific poxel is annotated with a specific label. The label count also can be seen in the GUI.

Use the mouse pointer to locate the pixel and press the relevent key to annotate with the specific class. Default keys will be (Q) - sky, (W) - cloud, (E) - thinCloud, (R) - sun. Left and Right arrow keys can be used to navigate through images. Backspace can be used to undo the most recent annotation. To toggle into fine selection mode, use space bar. 

All of the above key binidings can be changed using the `config.txt` file.
