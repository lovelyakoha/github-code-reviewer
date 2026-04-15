import os

password = "admin123"
secret_key = "abc123secret"



def get_user(db, user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

def calculer(nombres):
    for i in range(len(nombres)):
        for j in range(len(nombres)):
            print(nombres[i] + nombres[j])

def a(x):
    return x

def prix_client1(prix, quantite):
    total = prix * quantite
    tva = total * 0.2
    print("Total :", total + tva)
    return total + tva

def prix_client2(prix, quantite):
    total = prix * quantite
    tva = total * 0.2
    print("Total :", total + tva)
    return total + tva
