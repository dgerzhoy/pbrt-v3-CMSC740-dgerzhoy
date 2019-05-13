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

def textureDots1D(texture,name,u,v,inside,outside):
    texture.append('Texture "{}" "spectrum" "dots"\n'.format(name))
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "rgb inside" [{} {} {}] "rgb outside" [{} {} {}]\n'.format(*inside,*outside))

def textureChecks1D(texture,name,u,v,tex1,tex2):
    texture.append('Texture "{}" "spectrum" "checkerboard"\n'.format(name))
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "rgb tex1" [{} {} {}] "rgb tex2" [{} {} {}]\n'.format(*tex1,*tex2))

#Use checkerboard to create solid color by setting colors equal
def textureColor1D(texture,name,u,v,color1,color2):
    color2 = color1
    texture.append('Texture "{}" "spectrum" "checkerboard"\n'.format(name))
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "rgb tex1" [{} {} {}] "rgb tex2" [{} {} {}]\n'.format(*color1,*color2))

#Textures with 1-2 colors
def texture1D(texture,name,UV=[4,8,16,32,64],color1=None,color2=None):
    if not color1:
        color1 = ( rand.random(), rand.random(), rand.random() )
    if not color2:
        color2 = ( rand.random(), rand.random(), rand.random() )
    
    textFunc = rand.choice([textureDots1D,textureChecks1D,textureColor1D])
    uv = rand.choice(UV)
    return textFunc(texture,name,uv,uv,color1,color2)

def textureDots2D(texture,name,u,v,tex1,tex2):
    texture.append('Texture "{}" "spectrum" "dots"\n'.format(name))
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "texture inside" "{}" "texture outside" "{}"\n'.format(tex1,tex2))

def textureChecks2D(texture,name,u,v,tex1,tex2):
    texture.append('Texture "{}" "spectrum" "checkerboard"\n'.format(name))
    texture.append('		"float uscale" [{}] "float vscale" [{}]\n'.format(u,v))
    texture.append('	   "texture tex1" "{}" "texture tex2" "{}"\n'.format(tex1,tex2))

def texureScale2D(texture,name,u,v,tex1,tex2):
    texture.append('Texture "{}" "spectrum" "scale"\n'.format(name))
    texture.append('	   "texture tex1" "{}" "texture tex2" "{}"\n'.format(tex1,tex2))

def textureMix2D(texture,name,u,v,tex1,tex2):
    texture.append('Texture "{}" "spectrum" "mix"\n'.format(name))
    texture.append('	   "texture tex1" "{}"  "texture tex2" "{}"\n'.format(tex1,tex2))

#Returns a 2D texture
def texture2D(texture,name,tex1,tex2,UV=[4,8,16,32,64]):
    
    textFunc = rand.choice([textureDots2D,textureChecks2D,texureScale2D,textureMix2D])
    uv = rand.choice(UV)
    textFunc(texture,name,uv,uv,tex1,tex2)


#Multi-dimentional texture
def textureMultiD(texture,name,depth=2,UV=[4,8,16,32,64]):
    if depth < 1:
        depth = 1
    
    if depth == 1:
        texture1D(texture,name,UV)
    else:
        name1 = name+'_d{}b1'.format(depth)
        textureMultiD(texture,name1,(depth-1),UV)
        name2 = name+'_d{}b2'.format(depth)
        textureMultiD(texture,name2,(depth-1),UV)
        texture2D(texture,name,name1,name2,UV)

def texture(T=[2,3,4,5],UV=[4,8,16,32,64]):
    tex = list()
    name = 'text'
    depth = rand.choice(T)
    textureMultiD(tex,name,depth,UV)
    
    material = rand.choice(['matte','plastic'])
    
    tex.append('Material "{}"\n'.format(material))
    tex.append('"texture Kd" "{}"\n'.format(name))

    return tex

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

def addFloor(f_lines,texture):
    f_lines.append('#floor \n')
    f_lines.append('AttributeBegin \n')
    [f_lines.append(t) for t in texture]
    f_lines.append('    Shape \"trianglemesh\" \"point P\" [ -1 0 -1 1 0 -1 1 0 1 -1 0 1 ] \n')
    f_lines.append('	\"integer indices\" [ 0 1 2 2 3 0] \n')
    f_lines.append('AttributeEnd \n\n')

def addSpotlight(s_lines):
    s_lines.append('#spotlight \n')
    s_lines.append('AttributeBegin \n')
    s_lines.append('CoordSysTransform \"camera\" \n')
    s_lines.append('LightSource \"point\" \"color I\" [ .01 .01 .01 ] \n')
    s_lines.append('AttributeEnd\n\n')


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
parser.add_argument('-S',"--Sizes",nargs='+',help="Sizes s1 s2 s3...",type=float, default=(.00625, .0125, .025, .05, .1))
parser.add_argument('-LX',"--Light_X_Range",nargs=3,help="X range for lights (start stop step)",type=float, default=(-.1, .1, .05))
parser.add_argument('-LY',"--Light_Y_Range",nargs=3,help="Y range for lights (start stop step)",type=float, default=(.3, .6, .1))
parser.add_argument('-LZ',"--Light_Z_Range",nargs=3,help="Z range for lights (start stop step)",type=float, default=(-.2, .2, .05))
#parser.add_argument("--Light_Sizes",nargs='+',help="Sizes for lights s1 s2 s3...",type=float, default=(.025, .05, .1))
parser.add_argument('-Sh',"--Shape",help="Shape mode: Ball Cube Both", default="both")
parser.add_argument('-rot',"--rotate",nargs=4,help="angle x-axis y-axis z-axis (in degrees 1/0 1/0 1/0", default=(360,1,0,0))
parser.add_argument('-t',"--texture_depths",nargs='+',help="Depths d1 d2 d3...",type=float, default=(1, 2, 3, 4, 5))
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
T = args.texture_depths

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

integrator_lines = list()
integratorPreamble(integrator_lines)
addSpotlight(integrator_lines)

up_samples = args.up_samples
down_samples = args.down_samples
up_line = "        \"integer pixelsamples\" [ {} ] \n".format(up_samples)
down_line = "        \"integer pixelsamples\" [ {} ] \n".format(down_samples)

shape_mode = args.Shape
if(shape_mode != 'ball' and shape_mode != 'cube' and shape_mode != 'both'):
    print("Shape mode incorrect\n")
    parser.print_usage()
    exit(-1)

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
        #create floor as ball config
        text = texture(T=T,UV=[64,128,256])
        addFloor(config,text)
        for b in range(nBalls):
            rand.shuffle(P)
            p = P.pop()
            s = rand.choice(S)
            #Balls.append((p,s))
            #addBall(config,b,p,s)
            text = texture(T=T)
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
        print("Adding File {}".format(file_name))
        fileList.append(file_name+"\n")
        fo = open(outpath+file_name+".pbrt","w")

        fo.writelines(base_lines)
        fo.writelines(depth_lines)
        fo.writelines(ball_config)
        fo.write("WorldEnd\n")
        fo.close()
     
    #Now create the Area light configs for each ball config
    for (b,ball_config) in enumerate(BallConfigs):
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
                print("[{}][{}]Adding File {}".format(b,l,file_name))
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
                print("[{}][{}]Adding File {}".format(b,l,file_name))
                fileList.append(file_name+"\n")

fo = open(outlistfile,"w")

fo.writelines(fileList)

fo.close()







