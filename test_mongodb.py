from pymongo import MongoClient
uri = "mongodb+srv://tiwaritejas313_db_user:Admin123@cluster0.v5k0oiv.mongodb.net/"
client = MongoClient(uri)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()

except Exception as e:
    raise Exception(
        "The following error occurred: ", e)