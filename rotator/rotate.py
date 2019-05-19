import numpy as np
import math
import fileinput
import itertools as it
import argparse

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta degrees.
    """
    theta = np.deg2rad(theta)
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])



parser = argparse.ArgumentParser()
parser.add_argument("path",help="path to files")
parser.add_argument("basefile",help="base name of the file")
parser.add_argument("--down", type=int, default=8, help="downsample rate")
parser.add_argument("--up", type=int, default=512, help="upsample rate for ground truth")
parser.add_argument("--step", type=int, default=90, help="stepping for rotation")
parser.add_argument("--axes", default="z", help="[xyz] axes for rotation (no separators)")
args = parser.parse_args()

axes_str = list(args.axes)# args.axes.split(',')
ax_dict = { 'x' : [1,0,0], 'y' : [0,1,0], 'z' : [0,0,1] }
axes = [ ax_dict[a] for a in axes_str ]

angles = list(range(0,360,args.step))

down = args.down
up = args.up

print("path:",args.path)
print("basefile:",args.basefile)
print("downsample rate:",down)
print("upsample (ground truth) rate:",up)
print("Angular step:",args.step)
print("Rotational Axes:",axes_str)


path = args.path
basefile = args.basefile

ext=".pbrt"

b = open(path+basefile+ext,"r")

lines = b.readlines()

b.close()

lightCount = 0
findNextTranslate = False
transPoints = []

for n,line in enumerate(lines):
    for s in line.split():
        if s == "AreaLightSource":
            lightCount += 1
            findNextTranslate = True
            #print("Line {} has AreaLightSource".format(n))
        if findNextTranslate and s == "Translate":
            #append to list
            transPoints.append(n)
            findNextTranslate = False
        if s == "pixelsamples\"":
            psLine = n
            print("Found pixelsamples line at",psLine)
    
print("{} lights found with translations @{}".format(lightCount, transPoints))

allTranslations = []
for l,n in enumerate(transPoints):
    #tuple(translation string, label)
    translations = []
    line = lines[n].split()
    line=line[1:]
    
    v = np.fromiter(line,float)
    print("v: ",v)

    for a,axis in enumerate(axes):
        for theta in angles:
            label="_l{}_{}ax_{}deg".format(l,axes_str[a],theta)
            vr = np.dot(rotation_matrix(axis, theta), v)

            translations.append(("    Translate "+" ".join(map(str,vr))+"\n",label))
    
    allTranslations.append(translations)


#[print(t) for n,l in allTranslations for t in l]

combos = list(it.product(*allTranslations))

#print(len(list(combos)))
#[ print(c) for c in combos ]

fileFile = open(basefile+"_fileList.txt","w")

for (sampLabel,sampleRate) in [ ("_down",down), ("_truth",up) ]:
    lines[psLine]    = "        \"integer pixelsamples\" [ {} ]\n".format(sampleRate)
    for c in combos:
        name = path+basefile
        for lightNum,(translation,label) in enumerate(c):
            lineNum = transPoints[lightNum]
            #print("lightNum {} @ line {} | {} | label : {}".format(lightNum,lineNum,translation,label))
            name += label
            lines[lineNum] = translation
        name+=sampLabel+ext
        f = open(name,"w")
        for line in lines:
            f.write(line)
        f.close()
        fileFile.write(name+"\n")

fileFile.close()
    
