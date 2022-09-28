from pymongo import MongoClient
import gridfs
import ssl
import certifi
try:
    connection = MongoClient("mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())
    print("connected")
    print(connection.server_info())
except Exception:
    print("Unable to connect to the server.")
database = connection['client_data']
#database = connection['web_image_write']
fs = gridfs.GridFS(database)
i=0
c=fs.find()
print("{}".format(c))
# print(type(c))
z=database.fs.files.find()
for f in z:
    i=i+1
    print(f)
print(i)

i=0
# for f in c:
#     print(f.filename)
#     image_bytes=f.read()
#     x=f.filename+".jpg"
#     with open(x,"wb") as binary_file:
#         binary_file.write(image_bytes)
#     i=i+1
#for dwlwting images
for h in fs.find():
    x=h._id
    print(x)
    fs.delete(x)
print("images are deleted in db")
