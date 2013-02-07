from pyglet.gl import *
from pyglet.window import key
import random
from collections import deque
import math
import time
from Shader import Shader
from euclid import *

## instead of grabbing the last point and deleting blocks 
#at the end point position we should test all the points for intersection



window = pyglet.window.Window(1000,500)

shader = Shader([''' 
   
  
varying vec4 worldCoord;
    void main()
    {

worldCoord = gl_ModelViewProjectionMatrix * gl_Vertex;    
gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;

gl_TexCoord[0] = gl_MultiTexCoord0;
    }

 '''], ['''

varying vec4 worldCoord;
uniform sampler2D tex0;
void main() 
{
   vec2 c = gl_TexCoord[0].xy;
   vec2 ws = worldCoord.xy;
   vec2 ws2 = vec2(ws.x,ws.y*.7);

   vec3 current = texture2D(tex0,ws2).rgb;
  
   current = vec3(current.r,current.g,current.b);
   gl_FragColor = vec4(current,1.0);

}
'''])

def initTexture(filename):
    img = pyglet.image.load(filename)
    textureIDs = (pyglet.gl.GLuint * 1) ()
    glGenTextures(1,textureIDs)
    textureID = textureIDs[0]
    imgdata = img.get_data('RGB',256*3)
    print 'generating texture', textureID, 'from ', filename
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 256, 256,
                 0, GL_RGB, GL_UNSIGNED_BYTE, imgdata)
    glBindTexture(GL_TEXTURE_2D, 0)
    return textureID


class Sprite:
    def __init__(self, width, height, xpos, ypos, color, texture):
        self.width = width
        self.aimoffset = 40
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.color = color
        self.texture = texture
        self.aimpoints =[]
        self.aimcolors = [0,0,0] * 100
    def draw(self,terrain,heights):
        glColor3f(self.color[0],self.color[1],self.color[2])
        if self.texture != 0: glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glPushMatrix()
        glTranslatef(self.xpos, self.ypos, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(0,0)
        glVertex2f(-self.width/2.0, -self.height/2.0)
        glTexCoord2f(1,0)
        glVertex2f(self.width/2.0, -self.height/2.0)
        glTexCoord2f(1,1)
        glVertex2f(self.width/2.0, self.height/2.0)
        glTexCoord2f(0,1)
        glVertex2f(-self.width/2.0, self.height/2.0)
        glEnd()
        glPopMatrix()
        self.aim(terrain,heights,self.aimoffset)
        pyglet.graphics.draw(len(self.aimpoints)/2,pyglet.gl.GL_LINES,('v2f',(self.aimpoints)),('c3b',(self.aimcolors)))
        if self.texture != 0: glDisable(GL_TEXTURE_2D)

    def update(self,terrain):
            # move the tank to the highest position in the current x column of the terrain
            for j in range(0,280,20):
                if terrain[self.xpos/20][j/20] == 0:
                    self.ypos = j
                    print j
                    break
    def aim(self,terrain,heights,aimoffset):
        # define a new set of points, use quadratic forumula
        # to get 100 points between tank and the point to shoot towards
        #(which is the highest block in some x column)
        self.aimpoints = []                
        for t in range(100):
            ap = self.quadratic(t/100.0,Vector2(self.xpos,self.ypos),Vector2(self.xpos+aimoffset,heights[(self.xpos+aimoffset)/20]-10),Vector2(self.xpos+20+aimoffset,self.ypos+100))
            self.aimpoints.append(ap.x)
            self.aimpoints.append(ap.y)
            #append these points to the points array for this position

    def quadratic(self,t,start,end,center):
        return (math.pow(1-t,2) * start +2*t*(1-t)*center + math.pow(t,2)*end)

    def shoot(self,terrain,heights):
        terrain[(self.xpos/20)+(self.aimoffset/20)][(heights[((self.xpos+self.aimoffset)/20)]/20)-1] =0
        heights[(self.xpos+self.aimoffset)/20] -= 20
        #

#this class is blocks mapped with a shader
class TerrainBlock:
    def __init__(self, width, height, xpos, ypos, color):
        self.xpos = xpos
        self.ypos = ypos
        self.color = color
        x = width/2.0
        y = height/2.0
        
        self.vlist = pyglet.graphics.vertex_list(4, ('v2f', [-x,-y, x,-y, -x,y, x,y]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
    
    ##put the block in the correct spot
    def draw(self):
        glPushMatrix()
        glTranslatef(self.xpos, self.ypos, 0)
        glColor3f(self.color[0],self.color[1],self.color[2])
        self.vlist.draw(GL_TRIANGLE_STRIP)
      	glPopMatrix()

@window.event
def on_draw():
    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)
 
    shader.bind()
    texture = pyglet.image.load("kitten2.png").get_texture()
    
    #for o in quadlist:
        #o.draw()

    for i in range(0,800,20):
        for j in range(0,280,20):
            x =quadtable[i/20][j/20] 
            
            if quadtable[i/20][j/20] != 0:
                    x.draw()    

    shader.unbind()
    sprite1.draw(quadtable,quad_y_list)

@window.event
def on_key_press(key,modifiers):
    global objects
    if key == pyglet.window.key.LEFT:
        sprite1.xpos -= 20
        sprite1.update(quadtable)
    elif key == pyglet.window.key.RIGHT:
        sprite1.xpos += 20
        sprite1.update(quadtable)
    elif key == pyglet.window.key.ENTER:
        sprite1.shoot(quadtable,quad_y_list)    
    elif key == pyglet.window.key.D:
        sprite1.aimoffset += 40
        #update the aim so that it aims 2 blocks to the right
    elif key == pyglet.window.key.A:
        sprite1.aimoffset -= 40




# generate our datastructure to actually hold the blocks
quadtable = [[0 for i in range(100)] for j in range(100)]
#data structure to hold the height of each column
quad_y_list = [0 for i in range(100)]
#iterate x positions by 20
for i in range(0,800,20):
    #generate y positions ranging randomly from 0 - 2xx
	for j in range(0,int(random.gauss(200-(.2*i),25-(.17*i))),20):
        #create a new terrain block at the positions in pixel coords so not scaled down by 20
		currentsquare = TerrainBlock(19,19,i,j,(1,1,1))
        #add to the quad table at scaled down by 20 positions
		quadtable[i/20][j/20] = currentsquare
# get the highest block in each column
for i in range(0,800,20):
    for j in range(0,280,20):
                print quadtable[i/20][j/20]        
                if quadtable[i/20][j/20] == 0: #if the position of a block inside table is 0, then theres no block there
                    quad_y_list[i/20] = j # so set the height of that column to the height in raw numbers
                    break

sprite1 = Sprite(20,20,500,300,(1,1,1),initTexture("tank.png"))
sprite1.update(quadtable)


pyglet.app.run()