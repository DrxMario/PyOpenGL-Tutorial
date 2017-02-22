# Mario Rosasco, 2016
# adapted from DepthBuffer.cpp, Copyright (C) 2010-2012 by Jason L. McKesson
# This file is licensed under the MIT License.

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
from framework import *
from itertools import chain

# Set some global constants. Naming scheme is unchanged to maintain
# analogy to the C++ code. Note that because of the lack of #define macros
# in python, the color values were input manually
RIGHT_EXTENT  = 0.8
LEFT_EXTENT = -RIGHT_EXTENT
TOP_EXTENT = 0.20
MIDDLE_EXTENT = 0.0
BOTTOM_EXTENT = -TOP_EXTENT
FRONT_EXTENT = -1.25
REAR_EXTENT = -1.75

# A 1-D array of 3 4-D vertices (X,Y,Z,W)
# Note that this must be a numpy array, since as of 
# 170111 support for lists has not been implemented.
vertexData = np.array([
    #Object 1 positions
	LEFT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	LEFT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,

	LEFT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,
	LEFT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	LEFT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	LEFT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	LEFT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	RIGHT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	RIGHT_EXTENT,	MIDDLE_EXTENT,	FRONT_EXTENT,
	RIGHT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	LEFT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,
	LEFT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	RIGHT_EXTENT,	TOP_EXTENT,		REAR_EXTENT,
	RIGHT_EXTENT,	BOTTOM_EXTENT,	REAR_EXTENT,

	#Object 2 positions
	TOP_EXTENT,		RIGHT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	RIGHT_EXTENT,	FRONT_EXTENT,
	MIDDLE_EXTENT,	LEFT_EXTENT,	FRONT_EXTENT,
	TOP_EXTENT,		LEFT_EXTENT,	REAR_EXTENT,

	BOTTOM_EXTENT,	RIGHT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	RIGHT_EXTENT,	FRONT_EXTENT,
	MIDDLE_EXTENT,	LEFT_EXTENT,	FRONT_EXTENT,
	BOTTOM_EXTENT,	LEFT_EXTENT,	REAR_EXTENT,

	TOP_EXTENT,		RIGHT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	RIGHT_EXTENT,	FRONT_EXTENT,
	BOTTOM_EXTENT,	RIGHT_EXTENT,	REAR_EXTENT,
					
	TOP_EXTENT,		LEFT_EXTENT,	REAR_EXTENT,
	MIDDLE_EXTENT,	LEFT_EXTENT,	FRONT_EXTENT,
	BOTTOM_EXTENT,	LEFT_EXTENT,	REAR_EXTENT,
					
	BOTTOM_EXTENT,	RIGHT_EXTENT,	REAR_EXTENT,
	TOP_EXTENT,		RIGHT_EXTENT,	REAR_EXTENT,
	TOP_EXTENT,		LEFT_EXTENT,	REAR_EXTENT,
	BOTTOM_EXTENT,	LEFT_EXTENT,	REAR_EXTENT,

	#Object 1 colors
    # GREEN_COLOR
	0.75, 0.75, 1.0, 1.0,
	0.75, 0.75, 1.0, 1.0,
	0.75, 0.75, 1.0, 1.0,
	0.75, 0.75, 1.0, 1.0,

    # BLUE_COLOR
	0.0, 0.5, 0.0, 1.0,
	0.0, 0.5, 0.0, 1.0,
	0.0, 0.5, 0.0, 1.0,
	0.0, 0.5, 0.0, 1.0,

    # RED_COLOR
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,

    # GREY_COLOR
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,

    # BROWN_COLOR
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,

	#Object 2 colors
    # RED_COLOR
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,

    # BROWN_COLOR
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,

    # BLUE_COLOR
	0.0, 0.5, 0.0, 1.0,
	0.0, 0.5, 0.0, 1.0,
	0.0, 0.5, 0.0, 1.0,

    # GREEN_COLOR
	0.75, 0.75, 1.0, 1.0,
	0.75, 0.75, 1.0, 1.0,
	0.75, 0.75, 1.0, 1.0,

    # GREY_COLOR
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0],
    dtype='float32'
).flatten() # flatten the array into 1D

indexData = np.array(
    [0, 2, 1,
	3, 2, 0,

	4, 5, 6,
	6, 7, 4,

	8, 9, 10,
	11, 13, 12,

	14, 16, 15,
	17, 16, 14], 
    dtype='uint16')

vertexDim = 3
colorDim = 4
nVertices = 12*3

# Global variable to represent the compiled shader program, written in GLSL
theProgram = None

# Global variable to represent the buffer that will hold the position vectors
vertexBufferObject = None
# Global variables to hold vertex array objects
vao = None
# Global variable to hold the position index buffer object
indexBufferObject = None

# Global variables to store the location of the shader's uniform variables
offsetUniform = None
perspectiveMatrixUnif = None

# Global display variables
perspectiveMatrix = None
fFrustumScale = 1.0

# Set up the list of shaders, and call functions to compile them
def initializeProgram():
    shaderList = []
    
    shaderList.append(loadShader(GL_VERTEX_SHADER, "Standard.vert"))
    shaderList.append(loadShader(GL_FRAGMENT_SHADER, "Standard.frag"))
    
    global theProgram 
    theProgram = createProgram(shaderList)
    
    for shader in shaderList:
        glDeleteShader(shader)
    
    global offsetUniform
    offsetUniform = glGetUniformLocation(theProgram, "offset")
    
    global perspectiveMatrixUnif
    perspectiveMatrixUnif = glGetUniformLocation(theProgram, "perspectiveMatrix")
    
    fzNear = 1.0
    fzFar = 3.0
    
    global perspectiveMatrix
    perspectiveMatrix = np.zeros(16, dtype='float32') # note type
    perspectiveMatrix[0] = fFrustumScale
    perspectiveMatrix[5] = fFrustumScale
    perspectiveMatrix[10] = (fzFar + fzNear) / (fzNear - fzFar)
    perspectiveMatrix[14] = (2 * fzFar * fzNear) / (fzNear - fzFar)
    perspectiveMatrix[11] = -1.0
    
    glUseProgram(theProgram)
    glUniformMatrix4fv(perspectiveMatrixUnif, 1, GL_FALSE, perspectiveMatrix)
    glUseProgram(0)

# Set up the vertex buffer that will store our vertex coordinates for OpenGL's access
def initializeVertexBuffer():
    global vertexBufferObject, indexBufferObject
    vertexBufferObject = glGenBuffers(1)
    
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    glBufferData( # PyOpenGL allows for the omission of the size parameter
        GL_ARRAY_BUFFER,
        vertexData,
        GL_STATIC_DRAW
    )
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    indexBufferObject = glGenBuffers(1)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER,
        indexData,
        GL_STATIC_DRAW
    )
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

# Initialize the OpenGL environment
def init():
    initializeProgram()
    initializeVertexBuffer()
    
    global vao
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    sizeOfFloat = 4 # all our arrays are dtype='float32'
    colorDataOffset = c_void_p(vertexDim * nVertices * sizeOfFloat)
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(0, vertexDim, GL_FLOAT, GL_FALSE, 0, None)
    glVertexAttribPointer(1, colorDim, GL_FLOAT, GL_FALSE, 0, colorDataOffset)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
    
    glBindVertexArray(0)
    
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)
    
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDepthFunc(GL_LEQUAL)
    glDepthRange(0.0, 1.0)
   
# Called to update the display. 
# Because we are using double-buffering, glutSwapBuffers is called at the end
# to write the rendered buffer to the display.
def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glUseProgram(theProgram)
    
    glBindVertexArray(vao)
    
    glUniform3f(offsetUniform, 0.0,0.0,0.0)
    glDrawElements(GL_TRIANGLES, len(indexData), GL_UNSIGNED_SHORT, None)

    glUniform3f(offsetUniform, 0.0,0.0,-1.0)
    glDrawElementsBaseVertex(GL_TRIANGLES, len(indexData), GL_UNSIGNED_SHORT, None, nVertices/2)
    
    glBindVertexArray(0)
    glUseProgram(0)
    
    glutSwapBuffers()

# keyboard input handler: exits the program if 'esc' is pressed
def keyboard(key, x, y):
    if ord(key) == 27: # ord() is needed to get the keycode
        glutLeaveMainLoop()
        return    
        
# Called whenever the window's size changes (including once when the program starts)
def reshape(w, h):
    global perspectiveMatrix
    perspectiveMatrix[0] = fFrustumScale / (w / float(h))
    perspectiveMatrix[5] = fFrustumScale
    
    glUseProgram(theProgram)
    glUniformMatrix4fv(perspectiveMatrixUnif, 1, GL_FALSE, perspectiveMatrix)
    glUseProgram(0)
    
    glViewport(0, 0, w, h)
    
# The main function
def main():
    glutInit()
    displayMode = GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH | GLUT_STENCIL;
    glutInitDisplayMode (displayMode)
    
    width = 500;
    height = 500;
    glutInitWindowSize (width, height)
    
    glutInitWindowPosition (300, 200)
    
    window = glutCreateWindow("Tutorial Window")
    
    init()
    glutDisplayFunc(display) 
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    
    glutMainLoop();

if __name__ == '__main__':
    main()
