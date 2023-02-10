# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 11:11:03 2021

@author: nadee
"""

import flask
from flask.globals import session
from flask.helpers import url_for
from flask import Flask, render_template, Response,send_file
import cv2
from app import app
from flask import render_template
from flask import request 
from flask import redirect, url_for , globals
from datetime import timedelta
import sqlite3
import random
import json
import re



from email_validator import validate_email, EmailNotValidError
import requests
import pdfplumber
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(minutes=3)


import csv
import re
import PyPDF3 as PyPDF2
import random as r
import smtplib
from email.message import EmailMessage
import ssl


#Envoie un mail à partir de l'adresse mail de notre site: ici docnect@hotmail.com
def send_mail(login,password):
    msg = EmailMessage()    
    msg["From"] = "docnects@gmail.com"
    msg["To"] = login
    msg["Subject"] = "Confirmation d'inscription"
    msg.set_content( "Bonjour, \n \n Votre inscription à Doc'nect a bien été prise en compte. \n \n Veuillez trouvez ci-dessous vos identifiants de connexion: \n Login: " + login + "\n" + " Code d'authentification: "+ password + "\n \n Vous pouvez dès à présent vous connecter à l'aide de ces idenifiants en les indiquant dans la rubrique '1ère connexion' dans le lien suivant: https://serveur-test-its.herokuapp.com/ \n \n \n Doc'nect")
    
    s = smtplib.SMTP("smtp.gmail.com",587)
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login('docnects@gmail.com', 'fohawtkofbmktrsu')
    
    s.sendmail("docnects@gmail.com", login, msg.as_string())

    s.quit()

#Envoi un mot de passe aléatoire contenant des chiffres et des lettres minuscules/majuscules 
def random_password(compt):
    pswd=""
    for i in range (compt):
        smin="abcdefghijklmnopqrstuvwxyz" #alphabet en minuscules
        smaj= smin.upper() #alpahabet en majuscules
        
        charmin= r.choice(smin) #lettre minuscule aléatoire
        charmaj= r.choice(smaj) #lettre majuscule aléatoire
        
        charnb= str(r.randint(0,9)) #chiffre entre 0 et 9 aléatoire
       
        #on s'assure qu'il y ait au moins une caractère minuscule, majuscule et un nombre en les affectant aux trois premières positions
        if(i==0):
            pswd+= charmin
        elif(i==1):
            pswd+= charmaj
        elif(i==2):
            pswd+= charnb
        else:    
            #on crée un string composé de la lettre minuscule, majuscule et le chiffre trouvés
            srandom= charmin + charmaj + charnb
            # puis on choisit aléatoirement parmi les 3 caractères celui qui correspondra au ième caractère du mot de passe
            carac=r.choice(srandom)   
            #on ajoute le caractère au mot de passe
            pswd+=carac                       
            
    #on mélange le mot de passe à nouveau pour que le login soit bien aléatoire au niveau des positions
    final= "".join(r.sample(pswd,compt)) 
    print("Votre mot de passe est: ", final)
    return final



#Fonction analyse de pdf et de la valeur de créatinine
def extract_creatinine_value(path):
    # Ouvrir le fichier pdf
    pdf_reader = PyPDF2.PdfFileReader(path)
    
    # Initialiser une variable pour stocker le contenu de toutes les pages
    contents = ''
    
    # Boucle sur toutes les pages du fichier pdf
    for page_num in range(pdf_reader.numPages):
        # Ajouter le contenu de la page actuelle à la variable 'contents'
        contents += pdf_reader.getPage(page_num).extractText()
    
    # Rechercher les valeurs de la molécule 'Creatinine' en utilisant une expression régulière qui capture chacune des valeurs
    creatinine_match = re.search(r'Creatinine\s*(\d+)\s*(\d+)\s*-\s*(\d+)\s*umol/L', contents)
    
    # Retourner les valeurs trouvées ou None si aucune valeur n'a été trouvée
    return creatinine_match.groups() if creatinine_match else None

def getCreatinine(path):#pdf_file est le chemin du fichier
    # Générer un nombre aléatoire compris entre 1 et 15
    #random_num = random.randint(1, 15)
    
    # Construire le nom du fichier pdf choisi
    
    #pdf_file = f'C:/Users/Anita/Downloads/BLOOD_TEST_PDF_CSV 2/BLOOD_TEST_PDF_CSV/blood{random_num}.pdf'
    
    # Extraire les valeurs de la molécule 'Creatinine'
    creatinine_values = extract_creatinine_value(path)
    
    # Si une valeur a été trouvée, l'exporter dans un fichier csv
    if creatinine_values:
        measured_value, min_value, max_value = [int(value) for value in creatinine_values]
        alert = ''
        if measured_value < min_value or measured_value > max_value:
            alert = 'ALERT : Votre taux est anormale, veuillez en parler à votre médecin'
        with open('creatinine_values.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Measured Value', 'Minimum Value', 'Maximum Value', 'Alert'])
            writer.writerow([measured_value, min_value, max_value, alert])
        #print(f'Creatinine values {creatinine_values} exported to creatinine_values.csv with alert "{alert}"')
        a="Votre taux de creatinine est " + str(measured_value) + " il doit etre compris entre " + str(min_value) + " et " + str(max_value) + " " + str(alert)
        return(a)
    else:
        return 'No Creatinine values found in pdf file'


    
@app.route('/first', methods = ['POST', 'GET'])
def first():
    return render_template('firstConnexion.html', title='Bienvenue')

@app.route('/firstConnexion', methods = ['POST', 'GET'])
def firstConnexion():
    if request.method == 'POST' and 'Se connecter' in request.form:
                    
        login = request.form['login']
        password = request.form['password']
        with sqlite3.connect("projet_api.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * from auth WHERE login=?;", [str(login)])
            con.commit()
            rows = cur.fetchall();
            datauser={"id": rows[0][0], "login": rows[0][1], "password":rows[0][2], "statut":rows[0][3], "first":rows[0][4]}
            if password == rows[0][2]:
                print("password ok")
                print(datauser["first"])
                print(datauser["statut"])

                if datauser["first"]==1 :
                    print("reset password")
                    return render_template('reset.html', title='Bienvenue', utilisateur= datauser)
                else:
                    print("reconnect")
                    return redirect(url_for("index"))


@app.route('/reset', methods = ['POST', 'GET'])
def reset():
    #1ère connexion
    if request.method == 'POST' and 'reset' in request.form:
        login = request.form['login']
        password = request.form['password']
        passwordok = request.form['passwordok']
        
        if password == passwordok:
            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                sql = "UPDATE auth SET first=0, password=? WHERE login=?;"
                value=(password, login)
                cur.execute(sql,value)
                #cur.execute("UPDATE auth SET first=0 password=? WHERE login=?;", (password, str(login)))
                con.commit()
            con.close()
            return redirect(url_for("index"))

                

     

@app.route('/connexion', methods = ['POST', 'GET'])
def postConnexion():

    if request.method == 'POST' and 'Se connecter' in request.form:
        login = request.form['login']
        password = request.form['password']
        session['user'] = login
        
    else:

    #Retour à la page précédente donc le même utilisateur
        login = session['user']
         #On récupère le mot de passe de l'utilisateur avec le login de l'utilisateur connecté    
        with sqlite3.connect("projet_api.db") as con:
            cur = con.cursor()
            cur.execute("SELECT password from auth WHERE login=?;", [str(login)])
            con.commit()
            rows = cur.fetchall();
            if rows:
                print(rows)
                password= rows[0][0]

         
    #On récupère les données de l'utilisateur avec le login saisi    
    with sqlite3.connect("projet_api.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * from auth WHERE login=?;", [str(login)])
        con.commit()
        rows = cur.fetchall();
        print (rows)
        datauser={"id": rows[0][0], "login": rows[0][1], "password":rows[0][2], "statut":rows[0][3], "first":rows[0][4]}
        
        print(rows)
        id= int(rows[0][0])
        print(id)
        #S'il existe, on récupère les données dans un dictionnaire
        if id:
            
            #Si le statut de l'utilisateur connecté est un patient
            if datauser['statut']=='patient':
                print("Patient")
                with sqlite3.connect("projet_api.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT * from Patient WHERE identifier=?;", [id])
                    con.commit()
                    rows = cur.fetchall();
                
                if rows:
                    user={"id":id, "nom" : rows[0][1], "mail":rows[0][2], "gender": rows[0][3], "date":rows[0][4],"address":rows[0][5],"generalPracticioner":rows[0][6], "tel":rows[0][7]};
                    
                    #Le bouton submit du fichier patient.html permettra de se déconnecter
                    a={"type":"Deconnexion"}
                    
    
                        #Si le mot de passe saisi correspond bien à celui enregistré dans la base de données
                    if datauser['password']== password and datauser['first']==0:
                            
                        with sqlite3.connect("projet_api.db") as con:
                            cur = con.cursor()
                            cur.execute("SELECT  Practitioner.name, Practitioner.specialite, Practitioner.disponibilite from Practitioner")
                            con.commit()
                            dataSet=cur.fetchall()
                            fields=cur.description
                                    
                            #On récupère sous forme de liste les données de l'ensemble des médecins disponibles
                            if dataSet:
                                i=0
                                j=0
                                result={}
                                resultSet={}
                                for data in dataSet:
                                    i=0
                                    for field in fields:
                                            if i<data.__len__():
                                                    result[field[0]]=str(data[i])
                                                    i+=1
                                    resultSet[j] = result.copy()
                                    j+=1
                                #On envoie en paramètre cette liste pour pouvoir l'afficher dans le fichier patient.html
                    
                                #return render_template('accueil.html')
                                return render_template('patient.html', title='Bienvenue', utilisateur=user, datauser=datauser,medecins=resultSet,action=a)
           
                    else:
                        return render_template('erreur.html')

                 #L'utilisateur est l'admin   
            elif datauser['statut']=='admin':
                #Si le mot de passe saisi correspond bien à celui enregistré dans la base de données
                if datauser['password']== password:
                    
                    #On récupère la liste des medecins 
                    with sqlite3.connect("projet_api.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT auth.identifier, Practitioner.name, auth.statut FROM auth INNER JOIN Practitioner ON auth.identifier=Practitioner.identifier WHERE auth.statut='medecin';")
                        con.commit()
                        dataSet=cur.fetchall()
                        fields=cur.description
                        print(dataSet)
                        #On récupère sous forme de liste les données de l'ensemble des patients
                        if dataSet:
                            i=0
                            j=0
                            result={}
                            resultSetMedecin={}
                            for data in dataSet:
                                i=0
                                for field in fields:
                                        if i<data.__len__():
                                                result[field[0]]=str(data[i])
                                                i+=1
                                resultSetMedecin[j] = result.copy()
                                j+=1
                                
                    #Puis on récupère la liste des patients 
                    with sqlite3.connect("projet_api.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT auth.identifier, Patient.name, auth.statut FROM auth INNER JOIN Patient ON auth.identifier=Patient.identifier WHERE auth.statut='patient';")
                        con.commit()
                        dataSet=cur.fetchall()
                        fields=cur.description
                        print(dataSet)
                        #On récupère sous forme de liste les données de l'ensemble des patients
                        if dataSet:
                            i=0
                            j=0
                            result={}
                            resultSetPatient={}
                            for data in dataSet:
                                i=0
                                for field in fields:
                                        if i<data.__len__():
                                                result[field[0]]=str(data[i])
                                                i+=1
                                resultSetPatient[j] = result.copy()
                                j+=1                                
                                
                                
                                
                            #On envoie en paramètre la liste des patients et des médecin pour pouvoir l'afficher dans le fichier admin.html
                            return render_template('admin.html', title='Bienvenue', datauser=datauser, medecins=resultSetMedecin, patients=resultSetPatient)
    
                    con.close()     
                
            #L'utilisateur est un medecin                    
            else:
                #Si le mot de passe saisi correspond bien à celui enregistré dans la base de données
                if datauser['password']== password:
                    with sqlite3.connect("projet_api.db") as con:
                        cur = con.cursor()
                        cur.execute("SELECT * from Practitioner WHERE identifier=?;", [id])
                        con.commit()
                        rows = cur.fetchall();
                    
                    if rows:
                        user={"id":id, "nom" : rows[0][1], "mail":rows[0][2], "gender": rows[0][3], "date":rows[0][4],"address":rows[0][5], "tel":rows[0][6]};
                        
                        #Le bouton submit du fichier action.html permettra de se déconnecter
                        a={"type":"Deconnexion"}
    
                        
                         #Puis on récupère la liste des patients 
                        with sqlite3.connect("projet_api.db") as con:
                            cur = con.cursor()
                            cur.execute("SELECT auth.identifier, Patient.name FROM auth INNER JOIN Patient ON auth.identifier=Patient.identifier WHERE auth.statut='patient';")
                            con.commit()
                            dataSet=cur.fetchall()
                            fields=cur.description
                            print(dataSet)
                            #On récupère sous forme de liste les données de l'ensemble des patients
                            if dataSet:
                                i=0
                                j=0
                                result={}
                                resultSetPatient={}
                                for data in dataSet:
                                    i=0
                                    for field in fields:
                                            if i<data.__len__():
                                                    result[field[0]]=str(data[i])
                                                    i+=1
                                    resultSetPatient[j] = result.copy()
                                    j+=1                                
                                    
                                
                                
                            #On envoie en paramètre la liste des patients et des médecin pour pouvoir l'afficher dans le fichier admin.html
                            return render_template('medecin.html', title='Bienvenue', utilisateur=user, datauser=datauser, patients=resultSetPatient)
        
                        con.close()   
        else:
            #Sinon message d'erreur
            return render_template('erreur.html', title='Erreur')

@app.route('/preinscription', methods = ['POST', 'GET'])
def preInscription():
    if "Ajouter un patient" in request.form:
        #Le bouton submit du fichier permettra de se déconnecter
        a={"type":"Retourner"}       
        return render_template('register.html', title='Inscription', action=a)

@app.route('/preinscriptionMedecin', methods = ['POST', 'GET'])
def preInscriptionMedecin():
    if "Ajouter un medecin" in request.form:
        #Le bouton submit du fichier permettra de se déconnecter
        a={"type":"Retourner"}
        return render_template('registerMedecin.html', title='Inscription', action=a)

@app.route('/inscription', methods = ['POST','GET'])
def postInscription():
    error=''
    print("hi")
    if request.method == 'POST':
        #Le bouton submit du fichier permettra de se déconnecter
        a={"type":"Retourner"}     
        print("hi2")
        gender= request.form['gender']
        print(gender)
        login= request.form['mail']
        print(login)
        password=random_password(10)
        nom= request.form['nom']
        print(nom)
        date= request.form['date']
        print(date)
        tel= request.form['tel']
        print(tel)
        address= request.form['address']
        print(address)
        first=1
        
        a={"type":"Retourner"}
        session["user"]=login
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', login):
            error = 'L`adresse mail est invalide !'
        else:
            error = 'valide!'
            
        with sqlite3.connect("projet_api.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO auth(login,password,statut,first) VALUES (?,?,'patient',?)", (login,password,first))
            con.commit()
            print("Inscription réalisée avec succès dans auth")
            error="Inscription réalisée avec succès dans auth"
            cur.execute("SELECT * from auth WHERE login=?;", [login])
            rows = cur.fetchall();
            if rows:
                user={"id":rows[0][0], "login" : rows[0][1], "password":rows[0][2], "statut": rows[0][3], "first":rows[0][4]};
                identifier=user["id"]
                cur.execute("INSERT INTO Patient(identifier,name,telecom,gender,birthDate,address,generalPractitioner,num) VALUES (?,?,?,?,?,?,'0',?)", (identifier,nom,login,gender,date,address,tel))
                con.commit()
                print("Inscription réalisée avec succès dans patients")
        con.close()    
        send_mail(login,password)
        return render_template('register.html', title='Ajouter un patient',action=a)
    
    
    
@app.route('/inscriptionMedecin', methods = ['POST','GET'])
def postInscriptionMedecin():
    error=''
    if request.method == 'POST':
        #Le bouton submit du fichier permettra de se déconnecter
        a={"type":"Retourner"}     
        gender= request.form['gender']
        print(gender)
        login= request.form['mail']
        print(login)
        password=random_password(10)
        nom= request.form['nom']
        print(nom)
        date= request.form['date']
        print(date)
        tel= request.form['tel']
        print(tel)
        address= request.form['address']
        print(address)
        first=1
        
        a={"type":"Deconnexion"}
        session["user"]=login
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', login):
            error = 'L`adresse mail est invalide !'
        else:
            error = 'valide!'
            
        with sqlite3.connect("projet_api.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO auth(login,password,statut,first) VALUES (?,?,'medecin',?)", (login,password,first))
            con.commit()
            print("Inscription réalisée avec succès dans auth")
            error="Inscription réalisée avec succès dans auth"
            cur.execute("SELECT * from auth WHERE login=?;", [login])
            rows = cur.fetchall();
            if rows:
                user={"id":rows[0][0], "login" : rows[0][1], "password":rows[0][2], "statut": rows[0][3], "first":rows[0][4]};
                identifier=user["id"]
                cur.execute("INSERT INTO Practitioner(identifier,name,telecom,gender,birthDate,address,num) VALUES (?,?,?,?,?,?,?)", (identifier,nom,login,gender,date,address,tel))
                con.commit()
                print("Inscription réalisée avec succès dans practitioner")
        con.close()    
        send_mail(login,password)
        return render_template('registerMedecin.html', title='Ajouter un medecin',action=a)        
   
        
   
@app.route('/detailsMedecin', methods = ['POST', 'GET'])
def detailsMedecin():
    #Selon l'id récupéré dans le formulaire, on affiche les détails du patient correspondant
    for i in range(0,100):
        if str(i) in request.form:

            a={"type":"Retourner"}

            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                cur.execute("SELECT identifier, name, telecom, birthDate, address, num FROM Patient WHERE identifier=?;", [str(i)])
                con.commit()
                rows = cur.fetchall();
                
                if rows:
                    user={"id":rows[0][0], "nom" : rows[0][1], "mail":rows[0][2], "date": rows[0][3], "address":rows[0][4], "tel":rows[0][5]};
                    return render_template('infopatient.html', title='Bienvenue', utilisateur=user, action=a)
    #L'identifiant n'existe pas donc message d'erreur
                else:
                    return render_template('erreur2.html', title='Erreur')
    if request.method == 'POST':
        
        
        #Si l'utilisateur a appuyer sur le bouton rechercher            
        if 'recherche' in request.form:     
            #On récupère l'identifiant saisi
            id= request.form['recherche']
            
            a={"type":"Retourner"}

            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                cur.execute("SELECT identifier, name, telecom, birthDate, address, num FROM Patient WHERE identifier=?;", [str(id)])
                con.commit()
                rows = cur.fetchall();
                
                if rows:
                    user={"id":rows[0][0], "nom" : rows[0][1], "mail":rows[0][2], "date": rows[0][3], "address":rows[0][4], "tel":rows[0][5]};
                    return render_template('infopatient.html', title='Bienvenue', utilisateur=user, action=a)
    #L'identifiant n'existe pas donc message d'erreur
                else:
                    return render_template('erreur2.html', title='Erreur')
                        


@app.route('/details', methods = ['POST', 'GET'])
def details():
    #Selon l'id récupéré dans le formulaire, on affiche les détails du patient correspondant
    for i in range(0,100):
        if str(i) in request.form:
             with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                cur.execute("SELECT auth.statut from auth WHERE identifier=?;", [str(i)])
                con.commit()
                rows = cur.fetchall();
                print(rows)
                #S'il y a un résultat correspondant à cet id dans la base
                if rows:
                    a={"type":"Retourner"}
                    statut= rows[0][0]
                    print(statut)
                    if statut == "patient":
                        with sqlite3.connect("projet_api.db") as con:
                            cur = con.cursor()
                            cur.execute("SELECT identifier, name, telecom, birthDate, address, num FROM Patient WHERE identifier=?;", [str(i)])
                            con.commit()
                            rows = cur.fetchall();
                            
                            if rows:
                                user={"id":rows[0][0], "nom" : rows[0][1], "mail":rows[0][2], "date": rows[0][3], "address":rows[0][4], "tel":rows[0][5]};
                                return render_template('infopatient.html', title='Bienvenue', utilisateur=user, action=a)
                #L'identifiant n'existe pas donc message d'erreur
                            else:
                                return render_template('erreur2.html', title='Erreur')
                            
                    elif statut == "medecin":
                        with sqlite3.connect("projet_api.db") as con:
                            cur = con.cursor()
                            cur.execute("SELECT identifier, name, telecom, birthDate, address, num FROM Practitioner WHERE identifier=?;", [str(i)])
                            con.commit()
                            rows = cur.fetchall();
                            
                            if rows:
                                user={"id":rows[0][0], "nom" : rows[0][1], "mail":rows[0][2], "date": rows[0][3], "address":rows[0][4], "tel":rows[0][5]};
                                return render_template('infomedecin.html', title='Bienvenue', utilisateur=user, action=a)
                #L'identifiant n'existe pas donc message d'erreur
                            else:
                                return render_template('erreur2.html', title='Erreur')                        

            

    if request.method == 'POST':
        
        
        #Si l'utilisateur a appuyer sur le bouton rechercher            
        if 'recherche' in request.form:     
            #On récupère l'identifiant saisi
            id= request.form['recherche']
            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                cur.execute("SELECT auth.statut from auth WHERE identifier=?;", [str(id)])
                con.commit()
                rows = cur.fetchall();
                print(rows)
                #S'il y a un résultat correspondant à cet id dans la base
                if rows:
                    a={"type":"Retourner"}
                    statut= rows[0][0]
                    print(statut)
                    if statut == "patient":
                        with sqlite3.connect("projet_api.db") as con:
                            cur = con.cursor()
                            cur.execute("SELECT identifier, name, telecom, birthDate, address, num FROM Patient WHERE identifier=?;", [str(id)])
                            con.commit()
                            rows = cur.fetchall();
                            
                            if rows:
                                user={"id":rows[0][0], "nom" : rows[0][1], "mail":rows[0][2], "date": rows[0][3], "address":rows[0][4], "tel":rows[0][5]};
                                return render_template('infopatient.html', title='Bienvenue', utilisateur=user, action=a)
                #L'identifiant n'existe pas donc message d'erreur
                            else:
                                return render_template('erreur2.html', title='Erreur')
                            
                    elif statut == "medecin":
                        with sqlite3.connect("projet_api.db") as con:
                            cur = con.cursor()
                            cur.execute("SELECT identifier, name, telecom, birthDate, address, num FROM Practitioner WHERE identifier=?;", [str(id)])
                            con.commit()
                            rows = cur.fetchall();
                            
                            if rows:
                                user={"id":rows[0][0], "nom" : rows[0][1], "mail":rows[0][2], "date": rows[0][3], "address":rows[0][4], "tel":rows[0][5]};
                                return render_template('infomedecin.html', title='Bienvenue', utilisateur=user, action=a)
                #L'identifiant n'existe pas donc message d'erreur
                            else:
                                return render_template('erreur2.html', title='Erreur')                        

            
        
                
@app.route('/info', methods = ['POST', 'GET'])
def info():
      if request.method == 'POST':
    
        if 'Mon espace' in request.form:
            #On récupère les informations actuelles
            nom= request.form['nom']
            address= request.form['address']
            date= request.form['date']
            mail= request.form['mail']
            tel= request.form['tel']   
            id= request.form["id"]
            user={"id":id, "nom" : nom, "address":address, "date": date, "mail":mail,"tel":tel};
            a={"type":"Retourner"}
            return render_template('info.html', title='Mes informations', utilisateur=user, action=a)
    

@app.route('/modifier', methods = ['POST', 'GET'])
def modifierinfo():

  if request.method == 'POST':
        
        
        #Si l'utilisateur a appuyer sur le bouton modifier            
        if 'Modifier' in request.form:     
            #On récupère les informations modifiées
            nom= request.form['nom']
            mail= request.form['mail']

            address= request.form['address']
            date= request.form['date']
            tel= request.form['tel']   
            id= request.form["id"]
            ident=int(id)
            print(ident)
            
            a={"type":"Retourner"}

            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                sql = "UPDATE Patient SET name = ?, telecom = ?, birthDate = ?, address = ?, num = ?  WHERE identifier = ?"
                value=(nom,mail,date,address,tel,ident)
                cur.execute(sql,value)
                con.commit()
                rows = cur.fetchall();
                print(rows)
                
                print("Table modifiée avec succès")
                
                user={"id":ident, "nom" : nom, "address":address, "date": date, "mail":mail,"tel":tel}
                print(user)
                return render_template('info.html', title='Bienvenue', utilisateur=user, action=a)
                con.close()

                #L'identifiant n'existe pas donc message d'erreur
        else:
            return render_template('erreur2.html', title='Erreur')

@app.route('/chatbot', methods = ['POST', 'GET'])
def chatbot():
    a={"type":"Retourner"}
    return render_template('chatbot.html', title='Erreur',action=a)


@app.route('/contact', methods = ['POST', 'GET'])
def contact():
    a={"type":"Retourner"}
    return render_template('contact.html', title='Contact',action=a)

@app.route('/documents', methods = ['POST', 'GET'])
def documents():
    a={"type":"Retourner"}
    return render_template('document.html', title='Documents', action=a)

@app.route('/sendDocument', methods = ['POST', 'GET'])
def sendDocument():
    if request.method == 'GET':
        #path= request.form['file']
        a={"type":"Retourner"}
        path=request.args.get("file")
        print(path)
        res=getCreatinine(path)
        message={"msg":res}
        print(res)
        return render_template('post_document.html', msg=message, action=a )




@app.route('/recherche', methods = ['POST', 'GET'])
def recherche():
    
    if request.method == 'POST':

        nom= request.form['nom']
        mail= request.form['mail']
        address= request.form['address']
        date= request.form['date']
        tel= request.form['tel']   
        id= request.form["id"]
        ident=int(id)
        mot= request.form["mot"]
        print(mot)
        user={"id":ident, "nom" : nom, "address":address, "date": date, "mail":mail,"tel":tel}

        if mot=="":    
            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                cur.execute("SELECT  Practitioner.identifier, Practitioner.name, Practitioner.specialite, Practitioner.disponibilite  from Practitioner")
                con.commit()
                rows = cur.fetchall();
                
                print(rows)
                print(len(rows))
                
                if rows:
                    a={"type":"Retourner"}
                    return render_template('post_recherche.html', title='Bienvenue', medecins=rows, utilisateur=user, action=a)
                    con.close()
                
        else:
            with sqlite3.connect("projet_api.db") as con:
                cur = con.cursor()
                cur.execute("SELECT Practitioner.identifier, Practitioner.name, Practitioner.specialite, Practitioner.disponibilite from Practitioner WHERE name=? or specialite=?;", [mot, mot])
                con.commit()
                rows = cur.fetchall();
                
                print(rows)
                print(len(rows))
                
                #S'il y a un résultat correspondant à cet id dans la base
                if rows:
                    a={"type":"Retourner"}
                    return render_template('post_recherche.html', title='Bienvenue', medecins=rows, utilisateur=user, action=a)
                    con.close()
                else:
                    return render_template('erreurrecherche.html', title='Erreur Recherche')

@app.route('/rdv', methods = ['POST','GET'])
def rdv():
    if request.method == 'POST':
        id=int(request.form['id'])
        print(id)
        a={"type":"Retourner"}
        return render_template('rdv.html', title='Bienvenue', action=a)
    
    


@app.route('/deconnexion', methods = ['POST','GET'])
def logout():
    if request.method == 'POST':
        
        #On récupère l'action saisi dans le formulaire: soit se deconnecter soit retourner à la page précédente
        action=request.form['action']
        
        #Si deconnexion
        if action=="Deconnexion":
            #On efface les données enregistrés dans la session et donc el login de l'utilisateur
            session.clear()
            if 'user' in session:
                 session.pop("user", None)
            #On retourne à la page d'auhentification
            return redirect(url_for("index"))
        else:
            #On retourne à la page précédente soit la liste de patients du médecin
            return redirect(url_for("postConnexion"))
            

@app.route('/',methods = ['POST', 'GET'])
def index():
    if request.method == 'POST' or 'GET':
        #Page d'authentification
        return render_template('index.html', title='Teledoc')

