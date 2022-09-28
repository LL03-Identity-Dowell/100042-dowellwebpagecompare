from pymongo import MongoClient
import gridfs
import ssl
import certifi
connection = MongoClient("mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())

try:
    connection = MongoClient("mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())
    print("connected")
    #print(connection.server_info())
except Exception:
    print("Unable to connect to the server.")
# Connect to the Database where the images will be stored.
database = connection['client_data']
#database = connection['web_image_write']
# #Create an object of GridFs for the above database.
fs = gridfs.GridFS(database)
i=0
x=fs.find()
print(x)

for f in x:

     print(f.filename)
i=0
for f in fs.find():
    print(f.filename)
    image_bytes=f.read()
    print(str(image_bytes))
    # x=str(i)+".jpg"
    # with open(x,"wb") as binary_file:
    #     binary_file.write(image_bytes)
    i=i+1

print(i)