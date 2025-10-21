
# x = int(input("Entrez une valeur :"))
# y = int(input("Entrez une deuxieme valeur :"))

# def add_func(x, y):
#     z = x + y 
#     return z

#mon_calcul = add_func(x, y)
#print(mon_calcul)


# if x == y:
#     print("Valeurs identiques, entrez deux valeurs differentes.")
# elif x > y:
#     print(x)
# else:
#     print(y)


# my_var = "bonjour "
# #print(my_var *3)

# for char in my_var:
#      print(char)





# test = int(my_var)
# print(test)

# print(chr(97))
# print(chr(118))

mot_de_passe = input("Veuillez entrer votre mot de passe: ")

def verif_mdp(mot_de_passe):
    if mot_de_passe.islower():
        print("Votre mot de passe doit contenir au moins une majuscule.")
    elif mot_de_passe < 8:
        print("Votre mot de passe doit contenir au moins huit caracteres.")
    elif "!#@/" not in mot_de_passe:
        print("Votre mot de passe doit contenir au moins huit caracteres.")
    else: 
        print("Mot de passe correct.")

verif_mdp(mot_de_passe)
