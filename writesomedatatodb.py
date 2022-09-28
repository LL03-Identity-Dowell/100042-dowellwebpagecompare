from pymongo import MongoClient
import ssl
import certifi
try:
    #connection = MongoClient("mongodb+srv://qruser:qr1234@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())
    connection = MongoClient("mongodb+srv://qruser:qr_12345@cluster0.n2ih9.mongodb.net/DB_IMAGE?retryWrites=true&w=majority",ssl_cert_reqs=ssl.CERT_REQUIRED, ssl_ca_certs=certifi.where())

    print("connected")

    #print(connection.server_info())
except Exception:
    print("Unable to connect to the server.")
database = connection['client_data']

collection =database.socialmedia_form
x="oceans"
cont=" As wild harvests decrease and per capita seafood consumption increases, aquaculture should have an important role. For example, the U.S. imports 60% of its seafood, which contributes to its trade imbalance. Aquaculture can help by providing jobs as well as food products for domestic consumption and for export."
# delete data in db
# cursor=collection.find()
# for record in cursor :
#     collection.delete_one(record)

testing={
     "email":"abc",
     "name" :"Eshwar",
     "Topic":x,
     "Topic_description":cont

    }


#record1=collection.insert_one(testing)
cursor=collection.find()
for record in cursor :
    print(record)

v='Eshwar'

for record in collection.find({'name' :v}):
    y=record['email']
    print(y)


