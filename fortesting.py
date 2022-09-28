from datetime import datetime
import os
import cv2
print("---")
y=datetime.now()
print(y)
x=datetime.now().isoformat().replace(":","-")
print(x)

file_size=os.path.getsize("1.jpg")
x=file_size
print("file size is :",x,"bytes")
image = cv2.imread("1.jpg")
y=image.shape
print(y)
if image.all():
    print("----")
    print("done")
else:
    print("helo")