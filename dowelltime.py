
import requests

from datetime import datetime

# import json

import json
# store the URL in url as
# parameter for urlopen

dowellclock_url = "https://100009.pythonanywhere.com/dowellclock"

dowellclock = requests.get(dowellclock_url).json()['t1']

print(dowellclock)


dd=datetime.now()
time=dd.strftime("%d:%m:%Y,%H:%M:%S")
url="https://100003.pythonanywhere.com/event_creation"
data={"platformcode":"FB" ,"citycode":"101","daycode":"0",
                "dbcode":"pfm" ,"ip_address":"192.168.0.41",
                "login_id":"lav","session_id":"new",
                "processcode":"1","regional_time":time,
                "dowell_time":time,"location":"22446576",
                "objectcode":"1","instancecode":"100051","context":"afdafa ",
                "document_id":"3004","rules":"some rules","status":"work"
                }


r=requests.post(url,json=data)

print("#"*30)
print(r.text)



