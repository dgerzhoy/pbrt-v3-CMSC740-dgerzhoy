GENERATOR SCRIPT:

usage: sceneGenerator.py [-h] [-r RANDOM_SEED] [-nB NBALLS [NBALLS ...]]
                         [-nBA NBALL_ARRANGEMENTS] [-nL NLIGHTS [NLIGHTS ...]]
                         [-nLA NLIGHT_ARRANGEMENTS] [-u UP_SAMPLES]
                         [-d DOWN_SAMPLES] [-X X_RANGE X_RANGE X_RANGE]
                         [-Y Y_RANGE Y_RANGE Y_RANGE]
                         [-Z Z_RANGE Z_RANGE Z_RANGE] [-S SIZES [SIZES ...]]
                         [-LX LIGHT_X_RANGE LIGHT_X_RANGE LIGHT_X_RANGE]
                         [-LY LIGHT_Y_RANGE LIGHT_Y_RANGE LIGHT_Y_RANGE]
                         [-LZ LIGHT_Z_RANGE LIGHT_Z_RANGE LIGHT_Z_RANGE]
                         outpath
						 
The scene generator generates scenes out of balls placed 
randomly on discrete grid points and area lights placed
randomly on another discrete grid.

The default values place the lights above the view of the camera.

The pbrt files for ground truth, input, and depthmap are output 
in list.txt in the directory specified.
The depthmap is applicable for all ball count/configurations regardless
of light configuration.


The script also generates a file for each light configuration <nLights>L_C<configNum>
which contains information about each light: Position, Size, Power						 

example in the scene directory generated with command (on Windows from scenes\generated directory:

	python ..\..\generator\sceneGenerator\sceneGenerator.py .\example\ -nB 2 3 -nBA 2 -nL 1 2 -nLA 2

		This means you generate scenes with 2 balls and 3 balls (-nB 2 3) with 2 arrangements each (-nBA)
		with 1 light and 2 lights (-nL 1 2) with 2 arrangements each (-nLA)

to rotate around x axis (for background shadows) add -rot 90 1 0 0
	python ..\..\generator\sceneGenerator\sceneGenerator.py .\example\ -nB 2 3 -nBA 2 -nL 1 2 -nLA 2 -rot 90 1 0 0 

you can change the random seed with -r <seed>

RUN SCRIPT:
	
usage: sceneRunner.py [-h] pbrt path

positional arguments:
  pbrt        pbrt executable
  path        path with file list and scenes

optional arguments:
  -h, --help  show this help message and exit
  
 
 Simple script to render each scene file in list.
 
 python sceneRunner.py <path to scenes>