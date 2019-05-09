import os
import numpy as np
import math
import fileinput
import itertools as it
import argparse
import random as rand

def sharedPreamble(
        base_lines,
        eye=(0,0.25,0.25),
        lookat=(0,0,0),
        up=(0,1,0),
        scale=(-1,1,1),
        rotate=None,
        fov=90):
    base_lines.append('   Film "image" \n')
    base_lines.append('        "integer xresolution" [ 256 ]\n')
    base_lines.append('        "integer yresolution" [ 256 ] \n')
    base_lines.append('        "string filename" [ "generated.png" ] \n')
    base_lines.append('PixelFilter "box" \n')
    base_lines.append('LookAt 	{} {} {} \n'.format(*eye))
    base_lines.append('        {} {} {}\n'.format(*lookat))
    base_lines.append('        {} {} {}\n'.format(*up))
    base_lines.append('Scale {} {} {}\n'.format(*scale))
    if rotate:
        base_lines.append("Rotate {} {} {} {}\n".format(*rotate))
    base_lines.append('Camera "perspective" \n')
    base_lines.append('        "float fov" [ {} ] \n\n'.format(fov))

    base_lines.append('Sampler "halton"\n')



def addLight(lines,l,p,r=0.025,samps=1,power=128):
    lines.append("#Light {}\n".format(l))
    lines.append("\nAttributeBegin\n")
    lines.append("    AreaLightSource \"diffuse\"\n")
    lines.append("    \"integer nsamples\" [{} ] \n".format(samps))
    lines.append("    \"color L\" [{} {} {}]\n".format(power,power,power))
    lines.append("    Material \"matte\"  \"color Kd\"  [0.000000 0.000000 0.000000]\n")
    lines.append("    Translate {} {} {}\n".format(*p))
    lines.append("    Shape \"sphere\" \"float radius \" {}\n".format(r))
    lines.append("AttributeEnd\n\n")

def textureDots(u,v,inside,outside,material='matte'):
    texture = list()
    texture.append('Texture "text" "spectrum" "dots"\n')
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "rgb inside" [{} {} {}] "rgb outside" [{} {} {}]\n'.format(*inside,*outside))
    texture.append('Material "{}"\n'.format(material))
    texture.append('"texture Kd" "text"\n')
    return texture

def textureChecks(u,v,tex1,tex2,material='matte'):
    texture = list()
    texture.append('Texture "text" "spectrum" "checkerboard"\n')
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "rgb tex1" [{} {} {}] "rgb tex2" [{} {} {}]\n'.format(*tex1,*tex2))
    texture.append('Material "{}"\n'.format(material))
    texture.append('"texture Kd" "text"\n')
    return texture

#uv/color2 ignored for the interface
def textureColor(u,v,color,color2,material='matte'):
    texture = list()
    texture.append("	Material \"{}\"\n".format(material))
    texture.append("	\"rgb Kd\" [ {} {} {} ]\n".format(*color))
    return texture

def texture(color1=None,color2=None):
    if not color1:
        color1 = ( rand.random(), rand.random(), rand.random() )
    if not color2:
        color2 = ( rand.random(), rand.random(), rand.random() )
    material = rand.choice(['matte','plastic'])
    textFunc = rand.choice([textureDots,textureChecks,textureColor])
    uv = rand.choice([4,8,16,32,64])
    return textFunc(uv,uv,color1,color2,material)

def addBall(lines,b,p,s,texture):
    #print("Ball {} has coordinate {}  and size {}".format(b,p,s))
    lines.append("#Ball {}\n".format(b))
    lines.append("\nAttributeBegin\n")
    [lines.append(t) for t in texture]
    lines.append("  Translate {} {} {}\n".format(*p))
    lines.append("  Shape \"sphere\" \"float radius \" {}\n".format(s))
    lines.append("AttributeEnd\n\n")

def addCube(lines,c,p,s,texture):
    lines.append("#Cube {}\n".format(b))
    lines.append("\nAttributeBegin\n")
    [lines.append(t) for t in texture]
    lines.append("  Translate {} {} {}\n".format(*p))
    lines.append("  Shape \"trianglemesh\" \"point P\" [\n")
    lines.append("  {} -{} {}\n".format(s,s,s))
    lines.append("  {} -{} -{}\n".format(s,s,s))
    lines.append("  {} {} -{}\n".format(s,s,s))
    lines.append("  {} {} {}\n".format(s,s,s))
    lines.append("  -{} -{} {}\n".format(s,s,s))
    lines.append("  -{} -{} -{}\n".format(s,s,s))
    lines.append("  -{} {} -{}\n".format(s,s,s))
    lines.append("  -{} {} {} ]\n".format(s,s,s))
    lines.append('            	"integer indices" [ 4 0 3 4 3 7 0 1 2 0 2 3 1 5 6 1 6 2 5 4 7 5 7 6 7 3 2 7 2 6 0 5 1 0 4 5]\n')
    lines.append("AttributeEnd\n\n")

def depthPreamble(d_lines):
    d_lines.append("        \"integer pixelsamples\" [ {} ] \n".format(depthmap_samples))
    d_lines.append("Integrator \"depthmap\"\n")
    d_lines.append("#############################################\n")
    d_lines.append("WorldBegin\n\n")

def integratorPreamble(i_lines):
    i_lines.append("Integrator \"directlighting\"\n")
    i_lines.append("#############################################\n")
    i_lines.append("WorldBegin\n\n")

def addSharedWorld(s_lines):
    s_lines.append("\
#floor \n\
AttributeBegin \n\
    Material \"matte\" \n\
        \"rgb Kd\" [ 0.40000001 0.41999999 0.47999999 ] \n\
    Shape \"trianglemesh\" \"point P\" [ -1 0 -1 1 0 -1 1 0 1 -1 0 1 ] \n\
	\"integer indices\" [ 0 1 2 2 3 0] \n\
AttributeEnd \n\
\n\
#spotlight \n\
AttributeBegin \n\
CoordSysTransform \"camera\" \n\
LightSource \"point\" \"color I\" [ .01 .01 .01 ] \n\
AttributeEnd\n\n")


parser = argparse.ArgumentParser()
parser.add_argument("outpath",help="path for generated scene files")
parser.add_argument('-r',"--random_seed",help="Seed for random number generator",type=int, default=1)
parser.add_argument('-nB',"--nBalls",nargs='+',help="Number of Balls (list)",type=int, default=[3])
parser.add_argument('-nBA',"--nBall_Arrangements",help="Number of Ball Arrangements per nBalls",type=int, default=3)
parser.add_argument('-nL',"--nLights",nargs='+',help="Number of Lights (list)",type=int, default=[2])
parser.add_argument('-nLA',"--nLight_Arrangements",help="Number of Light Arrangements per nLights",type=int, default=3)
parser.add_argument('-u',"--up_samples",help="Sample Rate for Ground Truth",type=int, default=64)
parser.add_argument('-d',"--down_samples",help="Sample Rate for input",type=int, default=4)
parser.add_argument('-X',"--X_Range",nargs=3,help="X range (start stop step)",type=float, default=(-.1, .1, .05))
parser.add_argument('-Y',"--Y_Range",nargs=3,help="Y range (start stop step)",type=float, default=(.05, .2, .05))
parser.add_argument('-Z',"--Z_Range",nargs=3,help="Z range (start stop step)",type=float, default=(-.1, .1, .05))
parser.add_argument('-S',"--Sizes",nargs='+',help="Sizes s1 s2 s3...",type=float, default=(.00625, .0125, .025, .05))
parser.add_argument('-LX',"--Light_X_Range",nargs=3,help="X range for lights (start stop step)",type=float, default=(-.1, .1, .05))
parser.add_argument('-LY',"--Light_Y_Range",nargs=3,help="Y range for lights (start stop step)",type=float, default=(.3, .6, .1))
parser.add_argument('-LZ',"--Light_Z_Range",nargs=3,help="Z range for lights (start stop step)",type=float, default=(-.2, .2, .05))
#parser.add_argument("--Light_Sizes",nargs='+',help="Sizes for lights s1 s2 s3...",type=float, default=(.025, .05, .1))
parser.add_argument('-Sh',"--Shape",help="Shape mode: Ball Cube Both", default="both")
parser.add_argument('-rot',"--rotate",nargs=4,help="angle x-axis y-axis z-axis (in degrees 1/0 1/0 1/0", default=(360,1,0,0))
args = parser.parse_args()

outpath = args.outpath
outlistfile = outpath+"list.txt"

if not os.path.exists(outpath):
    os.mkdir(outpath)

base_lines = list()
sharedPreamble(base_lines,rotate=args.rotate)

seed = args.random_seed
rand.seed(seed)

S = args.Sizes

(X_Start, X_End, X_Step) = args.X_Range
(Y_Start, Y_End, Y_Step) = args.Y_Range
(Z_Start, Z_End, Z_Step) = args.Z_Range
X = np.arange(X_Start,X_End,X_Step,float)
Y = np.arange(Y_Start,Y_End,Y_Step,float)
Z = np.arange(Z_Start,Z_End,Z_Step,float)

(L_X_Start, L_X_End, L_X_Step) = args.Light_X_Range
(L_Y_Start, L_Y_End, L_Y_Step) = args.Light_Y_Range
(L_Z_Start, L_Z_End, L_Z_Step) = args.Light_Z_Range
LX = np.arange(L_X_Start,L_X_End,L_X_Step,float)
LY = np.arange(L_Y_Start,L_Y_End,L_Y_Step,float)
LZ = np.arange(L_Z_Start,L_Z_End,L_Z_Step,float)

#List of Possible Positions for balls and lights
P_ = list(it.product(X,Y,Z))
LP = list(it.product(LX,LY,LZ))

nBalls_List = args.nBalls
nBA = args.nBall_Arrangements

nLights_List = args.nLights
nLA = args.nLight_Arrangements

depthmap_samples = 32
depth_lines = list()
depthPreamble(depth_lines)
addSharedWorld(depth_lines)

integrator_lines = list()
integratorPreamble(integrator_lines)
addSharedWorld(integrator_lines)

up_samples = args.up_samples
down_samples = args.down_samples
up_line = "        \"integer pixelsamples\" [ {} ] \n".format(up_samples)
down_line = "        \"integer pixelsamples\" [ {} ] \n".format(down_samples)

shape_mode = args.Shape
if(shape_mode != 'ball' and shape_mode != 'cube' and shape_mode != 'both'):
    print("Shape mode incorrect\n")
    parser.print_usage()
    exit(-1)

textures = ["checkerboard","dots"]

fileList = list()
#For number of balls in scene
for nBalls in nBalls_List:
    #Empty list of Configs
    BallConfigs = list()
    #number of Arrangements
    for a in range(nBA):
        #Copy Position List
        P = list(P_)
        #Empty List of Balls for this Configuration
        config = list()
        for b in range(nBalls):
            rand.shuffle(P)
            p = P.pop()
            s = rand.choice(S)
            #Balls.append((p,s))
            #addBall(config,b,p,s)
            text = texture()
            if shape_mode == 'ball':
                addBall(config,b,p,s,text)
            elif shape_mode == 'cube':
                addCube(config,b,p,s,text)
            else:
                Shape = rand.choice([addBall,addCube])
                Shape(config,b,p,s,text)
        BallConfigs.append(config)

    #Now that I have a config saved, create depth map scenes each
    for (c,ball_config) in enumerate(BallConfigs):
        file_name = "{}B_C{}_depth.pbrt".format(nBalls,c)
        fileList.append(file_name+"\n")
        fo = open(outpath+file_name+".pbrt","w")

        fo.writelines(base_lines)
        fo.writelines(depth_lines)
        fo.writelines(ball_config)
        fo.write("WorldEnd\n")
        fo.close()
     
    #Now create the Area light configs for each ball config
    for ball_config in BallConfigs:
        for nLights in nLights_List:
            #nA = int(nLA / nLights)
            LightConfigs = list()
            for a in range(nLA):
                rand.seed(seed)
                light_config = list()
                coord_file = "{}L_C{}.txt".format(nLights,a)
                fo = open(outpath+coord_file,"w")

                for l in range(nLights):
                    p = rand.choice(LP)
                    r = .025
                    power = 128
                    addLight(light_config,l,p,r=r,power=power)
                    #               x  y  z  r  p
                    light_coords = "{} {} {} {} {}\n".format(*p,r,power)
                    fo.write(light_coords)
                LightConfigs.append(light_config)

                fo.close()

            for (b,ball_config) in enumerate(BallConfigs):
                for (l,light_config) in enumerate(LightConfigs):
                    #create pbrt file for ground truth
                    file_name = "{}B_C{}_{}L_C{}_truth".format(nBalls,b,nLights,l)
            
                    fo = open(outpath+file_name+".pbrt","w")
                    fo.writelines(base_lines)
                    fo.write(up_line)
                    fo.writelines(integrator_lines)
                    fo.writelines(ball_config)
                    fo.writelines(light_config)
                    fo.write("WorldEnd\n")
                    fo.close()
                    fileList.append(file_name+"\n")

                    #create pbrt file for input image
                    file_name = "{}B_C{}_{}L_C{}_input".format(nBalls,b,nLights,l)
                    fo = open(outpath+file_name+".pbrt","w")
                    fo.writelines(base_lines)
                    fo.write(down_line)
                    fo.writelines(integrator_lines)
                    fo.writelines(ball_config)
                    fo.writelines(light_config)
                    fo.write("WorldEnd\n")
                    fo.close()
                    fileList.append(file_name+"\n")

fo = open(outlistfile,"w")

fo.writelines(fileList)

fo.close()







