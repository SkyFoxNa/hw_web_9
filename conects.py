from mongoengine import connect, disconnect


def connect_to_mongodb():
    disconnect()

    # Подключение к MongoDB
    connect(
        db = "hw_web_8",
        host = "mongodb+srv://user_goit_web:user_goit_web@mains-db.nfj7rrz.mongodb.net/?retryWrites=true&w=majority"
               "&appName=Mains-db",
    )


