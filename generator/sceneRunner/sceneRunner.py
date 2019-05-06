
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("pbrt",help="pbrt executable")
parser.add_argument("path",help="path with file list and scenes")

#parser.add_argument('-m',"--Mode",help="Run Mode: \n\t\'list\' -- read from file list in directory\n\t\'custom\' -- Run Subsets of generated files", default='list')
#parser.add_argument('-nB',"--nBalls",nargs='+',help="Number of Balls (list)",type=int, default=[3])
#parser.add_argument('-nBA',"--nBall_Arrangements",help="Number of Ball Arrangements per nBalls",type=int, default=3)
#parser.add_argument('-nL',"--nLights",nargs='+',help="Number of Lights (list)",type=int, default=[2])
#parser.add_argument('-nLA',"--nLight_Arrangements",help="Number of Light Arrangements per nLights",type=int, default=3)
args = parser.parse_args()

pbrt = args.pbrt
path = args.path

file = path+"list.txt"
f = open(file,"r")

scenes = f.readlines()

for i,scene in enumerate(scenes):
    scene = scene.strip()
    scene = path+scene
    #print("./pbrt {} --outfile {}.png".format(scene,scene))
    print("Rendering scene {} out of {}".format(i+1,len(scenes)))
    os.system("{} {}.pbrt --outfile {}.png".format(pbrt,scene,scene))