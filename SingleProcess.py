#!/usr/bin/env python
# coding: Latin-1
#	Configurable variables
debug         = False
interval      = 0.01
screenWidth   = 800
screenHeight  = 480
imageWidth    = 240 #	Needs to be at least half of the screenWidth
imageHeight   = 180 #	Needs to be at least half of the screenHeight
imagePath     = "SavedImages/"
#	Variables defined using above configurable variables
displayWidth  = imageWidth * 2
displayHeight = imageHeight * 2
imageX        = (screenWidth - displayWidth) / 2
imageY        = 20
#	Start program
print("======================================")
print("Running Test One for MikeyBorg")
print("======================================")
print("Importing Libraries")
#   Import libraries
from Classes import PicoBorgRev3 as PicoBorgRev
import pygame
import pygame.camera
from time import strftime, gmtime
print("Imported Libraries")
print("Setting up reverse")
#   set-up reverse
PBR = PicoBorgRev.PicoBorgRev()
PBR.Init()
#   If no board is found, look for it
if not PBR.foundChip:
	boards = PicoBorgRev.ScanForPicoBorgReverse()
	if len(boards) == 0:
		print('No boards found :(')
	else:
		print("No board at address %02X, but found:" % (PBR.i2cAddress))
		for board in boards:
			print("	%02X (%d)" (board, board))
		print("To change the board, add PBR.i2cAddress = 0x%02X" % (boards[0]))
		sys.exit()
#	enable communications failsafe
print("Enabling communications failsafe")
PBR.ResetEpo()
print("Setting movement settings")
#	Power Settings
voltageIn = 12.0
voltageOut = 6.0
#	setup power limits
if voltageOut > voltageIn:
	maxPower = 1.0
else:
	maxPower = voltageOut / float(voltageIn)
#	Variables for motor speeds
leftMotors  = 0
rightMotors = 0
#	Setup pygame and key states
print("Initialising key states")
global hadEvent
global moveUp
global moveDown
global moveLeft
global moveRight
global moveQuit
global showCam
global saveImage
global speedMultiplier
hadEvent        = True
moveUp          = False
moveDown        = False
moveLeft        = False
moveRight       = False
moveQuit        = False
showCam         = True
saveImage       = False
speedMultiplier = 1
#	Set the colours
black      = pygame.Color(0, 0, 0)
messageBar = pygame.Color(119, 136, 153)
background = pygame.Color(211, 211, 211)
print("Initialising screen")
pygame.init()
pygame.display.set_caption("Press [ESC] to quit")
screen = pygame.display.set_mode([screenWidth, screenHeight])
screen.fill(background)
#	Font initialisation
monospaceFont = pygame.font.SysFont("monospace", 15)
#	Draw 'border' around the image
pygame.draw.rect(screen, black, (imageX - 5, imageY - 5, displayWidth + 10, displayHeight + 10))
#	Draw message bar
pygame.draw.rect(screen, messageBar, (imageX - 5, imageY + 5 + displayHeight, displayWidth + 10, 20))
print("Initialising camera")
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", [imageWidth, imageHeight], "RGM")
cam.start()
image = cam.get_image()
print("Defining functions")
#	Function to handle events
def PygameHandler(events):
	#	Variables accessible outside this function
	global hadEvent
	global moveUp
	global moveDown
	global moveLeft
	global moveRight
	global moveQuit
	global showCam
	global saveImage
	global speedMultiplier
	#	Handle each event individually
	for event in events:
		#	If ESC pressed, quit
		if event.type == pygame.QUIT:
			hadEvent = True
			moveQuit = True
		#	Else check if this is a key press
		elif event.type == pygame.KEYDOWN:
			hadEvent = True
			if event.key == pygame.K_w:
				moveUp = True
			elif event.key == pygame.K_s:
				moveDown = True
			elif event.key == pygame.K_a:
				moveLeft = True
			elif event.key == pygame.K_d:
				moveRight = True
			elif event.key == pygame.K_ESCAPE:
				moveQuit = True
			elif event.key == pygame.K_LSHIFT:
				speedMultiplier = 0.5
		#	Else check if this is a key release
		elif event.type == pygame.KEYUP:
			hadEvent = True
			if event.key == pygame.K_w:
				moveUp = False
			elif event.key == pygame.K_s:
				moveDown = False
			elif event.key == pygame.K_a:
				moveLeft = False
			elif event.key == pygame.K_d:
				moveRight = False
			elif event.key == pygame.K_r:
				if showCam:
					cam.stop()
					showCam = False
				else:
					cam.start()
					image = cam.get_image()
					showCam = True
			elif event.key == pygame.K_LSHIFT:
				speedMultiplier = 1
			elif event.key == pygame.K_SPACE:
				saveImage = True
#	Setting speeds
def SetSpeed(driveLeft, driveRight):
	global speedMultiplier
	PBR.SetMotor1(driveRight * maxPower * speedMultiplier)
	PBR.SetMotor2(-driveLeft * maxPower * speedMultiplier)
#	Displaying a message
def DisplayMessage(message):
	message = monospaceFont.render(message, 1, black)
	screen.blit(message, (imageX, imageY + 10 + displayHeight))
#	Initialization done, so say so
print("======================================")
print("Initialisation complete, awaiting input")
print("Press [ESC] to quit")
print("======================================")
try:
	#	Loop forevermore, unless ESC pressed
	while True:
		#	Camera stuff
		#       If image is ready, use it
		if showCam and cam.query_image():
			image = cam.get_image()
			image = pygame.transform.scale(image, [displayWidth, displayHeight])
			#       Set image as background
			screen.blit(image, [imageX, imageY])
			if saveImage:
				filename = imagePath + strftime("%Y%m%d-%H%M%S", gmtime()) + ".jpg"
				pygame.image.save(cam.get_image(), filename)
				DisplayMessage("Saved picture to " + filename)
		else:
			saveImage = False
		pygame.display.update()
		#	Get the currently pressed keys
		PygameHandler(pygame.event.get())
		#	If something has changed since last iteration, do something
		if hadEvent:
			hadEvent = False
			#	If ESC was clicked
			if moveQuit:
				print("[ESC] clicked, terminating program")
				break
			#	If going forwards
			elif moveUp:
				#	If also going left
				if moveLeft == True and moveRight == False:
					SetSpeed(0.2, 1.0)
				#	If also going right
				elif moveLeft == False and moveRight == True:
					SetSpeed(1.0, 0.2)
				#	If just going forward
				else:
					SetSpeed(1.0, 1.0)
			#	If going backwards
			elif moveDown:
				#	If also going left
				if moveLeft == True and moveRight == False:
					SetSpeed(-1, -0.2)
				#	If also going right
				elif moveLeft == False and moveRight == True:
					SetSpeed(-0.2, -1)
				#	If just going backwards
				else:
					SetSpeed(-1, -1)
			#	If going left
			elif moveLeft:
				#	Turn left, if not also going right
				if moveRight == False:
					SetSpeed(-1.0, 1.0)
			#	If going right
			elif moveRight:
				SetSpeed(1.0, -1.0)
			else:
				PBR.MotorsOff()
		#	Wait for the interval
		#time.sleep(interval)
	#	Stop the motors
	PBR.MotorsOff()
#	CTRL+C pressed, so quit
except KeyboardInterrupt:
	PBR.MotorsOff()
print("Program Finished")
print("======================================")