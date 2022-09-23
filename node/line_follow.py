#!/usr/bin/env python3

from __future__ import print_function
import roslib
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist



class image_converter:

  def __init__(self):
    self.image_pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 1)

    self.move = Twist()
    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("/rrbot/camera1/image_raw",Image,self.callback)

  def callback(self,data):
    try:
      cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)

    #Pipeline: Grayscale, convert to color, blur image, convert to a binary map, convert to greyscale (mainly binary map)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    gblur = cv2.GaussianBlur(gray, (5,5), 0)
    ret,binary = cv2.threshold(gblur,127,255, cv2.THRESH_BINARY_INV)
    finalgrey = binary
        

    M = cv2.moments(finalgrey)
    cX = int(M["m10"]/M["m00"])
    cY = int(M["m01"]/M["m00"])
    
    #Draw a circle at the center of mass coordinates
    final = cv2.circle(cv_image,(cX,cY),15,(255,0,0),cv2.FILLED)
    
    if(cX < 350 and cY > 200):
        self.move.linear.x = 0
        self.move.angular.z = 1
        self.image_pub.publish(self.move)
    elif(cX > 450 and cY > 200):
        self.move.linear.x = 0
        self.move.angular.z = -1
        self.image_pub.publish(self.move)
    else:
        self.move.linear.x = 1.5
        self.move.angular.z = 0
        self.image_pub.publish(self.move)
    
    #print(cX, cY)


    cv2.imshow("Image window", final)
    cv2.waitKey(3)

def main(args):
    rospy.init_node('image_converter', anonymous=True)
    ic = image_converter()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
