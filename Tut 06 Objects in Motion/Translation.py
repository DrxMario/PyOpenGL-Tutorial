# Mario Rosasco, 2016
# adapted from Translation.cpp, Copyright (C) 2010-2012 by Jason L. McKesson
# This file is licensed under the MIT License.

from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
from framework import *
from math import tan, cos, sin

# A 1-D array of 3 4-D vertices (X,Y,Z,W)
# Note that this must be a numpy array, since as of 
# 170111 support for lists has not been implemented.
vertexData = np.array([
    +1.0, +1.0, +1.0,
	-1.0, -1.0, +1.0,
	-1.0, +1.0, -1.0,
	+1.0, -1.0, -1.0,

	-1.0, -1.0, -1.0,
	+1.0, +1.0, -1.0,
	+1.0, -1.0, +1.0,
	-1.0, +1.0, +1.0,

    # GREEN_COLOR
	0.0, 1.0, 0.0, 1.0,
    # BLUE_COLOR
	0.0, 0.0, 1.0, 1.0,
    # RED_COLOR
	1.0, 0.0, 0.0, 1.0,
    # BROWN_COLOR
	0.5, 0.5, 0.0, 1.0,
	
    # GREEN_COLOR
	0.0, 1.0, 0.0, 1.0,
    # BLUE_COLOR
	0.0, 0.0, 1.0, 1.0,
    # RED_COLOR
	1.0, 0.0, 0.0, 1.0,
    # BROWN_COLOR
	0.5, 0.5, 0.0, 1.0],
    dtype='float32'
)

indexData = np.array([
    0, 1, 2,
	1, 0, 3,
	2, 3, 0,
	3, 2, 1,

	5, 4, 6,
	4, 5, 7,
	7, 6, 4,
	6, 7, 5], 
    dtype='uint16')

vertexDim = 3
colorDim = 4
nVertices = 8

# Helper function to calculate the frustum scale. 
# Accepts a field of view (in degrees) and returns the scale factor
def calcFrustumScale(fFovDeg):
    degToRad = 3.14159 * 2.0 / 360.0
    fFovRad = fFovDeg * degToRad
    return 1.0 / tan(fFovRad / 2.0)

# Global variable to represent the compiled shader program, written in GLSL
theProgram = None

# Global variable to represent the buffer that will hold the position vectors
vertexBufferObject = None
# Global variables to hold vertex array objects
vao = None
# Global variable to hold the position index buffer object
indexBufferObject = None

# Global variables to store the location of the shader's uniform variables
modelToCameraMatrixUnif = None
cameraToClipMatrixUnif = None

# Global display variables
cameraToClipMatrix = np.zeros((4,4), dtype='float32')
fFrustumScale = calcFrustumScale(45.0)

# Set up the list of shaders, and call functions to compile them
def initializeProgram():
    shaderList = []
    
    shaderList.append(loadShader(GL_VERTEX_SHADER, "PosColorLocalTransform.vert"))
    shaderList.append(loadShader(GL_FRAGMENT_SHADER, "ColorPassthrough.frag"))
    
    global theProgram 
    theProgram = createProgram(shaderList)
    
    for shader in shaderList:
        glDeleteShader(shader)
    
    global modelToCameraMatrixUnif, cameraToClipMatrixUnif
    modelToCameraMatrixUnif = glGetUniformLocation(theProgram, "modelToCameraMatrix")
    cameraToClipMatrixUnif = glGetUniformLocation(theProgram, "cameraToClipMatrix")
    
    fzNear = 1.0
    fzFar = 45.0
    
    global cameraToClipMatrix
    # Note that this and the transformation matrix below are both
    # ROW-MAJOR ordered. Thus, it is necessary to pass a transpose
    # of the matrix to the glUniform assignment function.
    cameraToClipMatrix[0][0] = fFrustumScale
    cameraToClipMatrix[1][1] = fFrustumScale
    cameraToClipMatrix[2][2] = (fzFar + fzNear) / (fzNear - fzFar)
    cameraToClipMatrix[2][3] = -1.0
    cameraToClipMatrix[3][2] = (2 * fzFar * fzNear) / (fzNear - fzFar)
    
    glUseProgram(theProgram)
    glUniformMatrix4fv(cameraToClipMatrixUnif, 1, GL_FALSE, cameraToClipMatrix.transpose())
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
    
# Helper functions to return various types of transformation arrays
def stationaryOffset(fElapsedTime):
    newTransform = np.identity(4, dtype='float32')
    newTransform[2][3] = -20
    return newTransform
    
def ovalOffset(fElapsedTime):
    fLoopDuration = 3.0
    fScale = 3.14159 * 2.0 / fLoopDuration
    
    fCurrTimeThroughLoop = fElapsedTime % fLoopDuration
    
    newTransform = np.identity(4, dtype='float32')
    newTransform[0][3] = cos(fCurrTimeThroughLoop * fScale) * 4.0
    newTransform[1][3] = sin(fCurrTimeThroughLoop * fScale) * 6.0
    newTransform[2][3] = -20
    return newTransform
        
def bottomCircleOffset(fElapsedTime):
    fLoopDuration = 12.0
    fScale = 3.14159 * 2.0 / fLoopDuration
    
    fCurrTimeThroughLoop = fElapsedTime % fLoopDuration
    
    newTransform = np.identity(4, dtype='float32')
    newTransform[0][3] = cos(fCurrTimeThroughLoop * fScale) * 4.0
    newTransform[1][3] = -3.5
    newTransform[2][3] = sin(fCurrTimeThroughLoop * fScale) * 5.0 - 20.0
    return newTransform
        
# A list of the helper offset functions.
# Note that this does not require a structure def in python.
# Each function is written to return the complete transform matrix.
g_instanceList =[
    stationaryOffset,
    ovalOffset,
    bottomCircleOffset]
        
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
    
    fElapsedTime = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    for func in g_instanceList:
        transformMatrix = func(fElapsedTime)
        
        glUniformMatrix4fv(modelToCameraMatrixUnif, 1, GL_FALSE, transformMatrix.transpose())
        glDrawElements(GL_TRIANGLES, len(indexData), GL_UNSIGNED_SHORT, None)
    
    glBindVertexArray(0)
    glUseProgram(0)
    
    glutSwapBuffers()
    glutPostRedisplay()

# keyboard input handler: exits the program if 'esc' is pressed
def keyboard(key, x, y):

    # ord() is needed to get the keycode
    keyval = ord(key)
    if keyval == 27: 
        glutLeaveMainLoop()
        return
            
# Called whenever the window's size changes (including once when the program starts)
def reshape(w, h):
    global cameraToClipMatrix
    cameraToClipMatrix[0][0] = fFrustumScale * (h / float(w))
    cameraToClipMatrix[1][1] = fFrustumScale

    glUseProgram(theProgram)
    glUniformMatrix4fv(cameraToClipMatrixUnif, 1, GL_FALSE, cameraToClipMatrix.transpose())
    glUseProgram(0)
    
    glViewport(0, 0, w, h)
    
# The main function
def main():
    glutInit()
    displayMode = GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH | GLUT_STENCIL;
    glutInitDisplayMode (displayMode)
    
    glutInitContextVersion(3,3)
    glutInitContextProfile(GLUT_CORE_PROFILE)
    
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
