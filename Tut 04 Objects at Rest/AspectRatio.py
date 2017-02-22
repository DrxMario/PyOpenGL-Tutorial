# Mario Rosasco, 2016
# adapted from AspectRatio.cpp, Copyright (C) 2010-2012 by Jason L. McKesson
# This file is licensed under the MIT License.

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
from framework import *

# A 1-D array of 3 4-D vertices (X,Y,Z,W)
# Note that this must be a numpy array, since as of 
# 170111 support for lists has not been implemented.
vertexData = np.array(
    [0.25,  0.25, -1.25, 1.0,
	 0.25, -0.25, -1.25, 1.0,
	-0.25,  0.25, -1.25, 1.0,

	 0.25, -0.25, -1.25, 1.0,
	-0.25, -0.25, -1.25, 1.0,
	-0.25,  0.25, -1.25, 1.0,

	 0.25,  0.25, -2.75, 1.0,
	-0.25,  0.25, -2.75, 1.0,
	 0.25, -0.25, -2.75, 1.0,

	 0.25, -0.25, -2.75, 1.0,
	-0.25,  0.25, -2.75, 1.0,
	-0.25, -0.25, -2.75, 1.0,

	-0.25,  0.25, -1.25, 1.0,
	-0.25, -0.25, -1.25, 1.0,
	-0.25, -0.25, -2.75, 1.0,

	-0.25,  0.25, -1.25, 1.0,
	-0.25, -0.25, -2.75, 1.0,
	-0.25,  0.25, -2.75, 1.0,

	 0.25,  0.25, -1.25, 1.0,
	 0.25, -0.25, -2.75, 1.0,
	 0.25, -0.25, -1.25, 1.0,

	 0.25,  0.25, -1.25, 1.0,
	 0.25,  0.25, -2.75, 1.0,
	 0.25, -0.25, -2.75, 1.0,

	 0.25,  0.25, -2.75, 1.0,
	 0.25,  0.25, -1.25, 1.0,
	-0.25,  0.25, -1.25, 1.0,

	 0.25,  0.25, -2.75, 1.0,
	-0.25,  0.25, -1.25, 1.0,
	-0.25,  0.25, -2.75, 1.0,

	 0.25, -0.25, -2.75, 1.0,
	-0.25, -0.25, -1.25, 1.0,
	 0.25, -0.25, -1.25, 1.0,

	 0.25, -0.25, -2.75, 1.0,
	-0.25, -0.25, -2.75, 1.0,
	-0.25, -0.25, -1.25, 1.0,
    

	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,

	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,
	0.0, 0.0, 1.0, 1.0,

	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,

	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,
	0.8, 0.8, 0.8, 1.0,

	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,

	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,
	0.0, 1.0, 0.0, 1.0,

	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,

	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,
	0.5, 0.5, 0.0, 1.0,

	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,

	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,
	1.0, 0.0, 0.0, 1.0,

	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,

	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0,
	0.0, 1.0, 1.0, 1.0],
    dtype='float32'
)

vertexDim = 4
nVertices = 12*3

# Global variable to represent the compiled shader program, written in GLSL
theProgram = None

# Global variable to represent the buffer that will hold the position vectors
vertexBufferObject = None

# Global variables to store the location of the shader's uniform variables
offsetUniform = None
perspectiveMatrixUnif = None

# Global display variables
perspectiveMatrix = None
fFrustumScale = 1.0

# Set up the list of shaders, and call functions to compile them
def initializeProgram():
    shaderList = []
    
    shaderList.append(loadShader(GL_VERTEX_SHADER, "MatrixPerspective.vert"))
    shaderList.append(loadShader(GL_FRAGMENT_SHADER, "StandardColors.frag"))
    
    global theProgram 
    theProgram = createProgram(shaderList)
    
    for shader in shaderList:
        glDeleteShader(shader)
    
    global offsetUniform
    offsetUniform = glGetUniformLocation(theProgram, "offset")
    
    global perspectiveMatrixUnif
    perspectiveMatrixUnif = glGetUniformLocation(theProgram, "perspectiveMatrix")
    
    fzNear = 0.5
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
    global vertexBufferObject
    vertexBufferObject = glGenBuffers(1)
    
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    glBufferData( # PyOpenGL allows for the omission of the size parameter
        GL_ARRAY_BUFFER,
        vertexData,
        GL_STREAM_DRAW
    )
    glBindBuffer(GL_ARRAY_BUFFER, 0)

# Initialize the OpenGL environment
def init():
    initializeProgram()
    initializeVertexBuffer()
    glBindVertexArray(glGenVertexArrays(1))
    
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CW)
   
# Called to update the display. 
# Because we are using double-buffering, glutSwapBuffers is called at the end
# to write the rendered buffer to the display.
def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    
    glUseProgram(theProgram)
    
    glUniform2f(offsetUniform, 1.5, 0.5)
    
    glBindBuffer(GL_ARRAY_BUFFER, vertexBufferObject)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(0, vertexDim, GL_FLOAT, GL_FALSE, 0, None)
    # a ctype void pointer must be used to pass in the offset into the bound GL_ARRAY_BUFFER
     # also note that python's underlying float type is usally 64-bit, but
     # we have specified that our vertex array contains float32 data.
    colorOffset = c_void_p(vertexDim*nVertices*4)
    glVertexAttribPointer(1, vertexDim, GL_FLOAT, GL_FALSE, 0, colorOffset)
    
    glDrawArrays(GL_TRIANGLES, 0, nVertices)
    
    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)
    glUseProgram(0)
    
    glutSwapBuffers()
    glutPostRedisplay()

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
