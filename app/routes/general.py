#vérifier que les appels sont les bons
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import or_
from app.app import app, db
from ..models.gares import Gares, Lignes
from ..models.formulaires import Recherche
import json
from ..models.formulaires import Recherche
from ..utils.transformations import nettoyage_string_to_int, clean_arg
from sqlalchemy.sql import text

@app.route("/")
@app.route("/home")
def home():
    return render_template('pages/index.html')

def getGeoJSON(query) :
    geoJSONfeatures= []
    for gare in query:
        lignes = [[ligne.id,ligne.label] for ligne in gare.lignes]
        geojsonFeature = {
            "type": "Feature",
            "properties": {
                "id":gare.codeunique,
                "name": gare.nom_long,
                "label":gare.label,
                "geoPoint":gare.coordonnees[0].geoPoint.split(', '),
                "lignes": lignes
            },
            "geometry": json.loads(gare.coordonnees[0].geoShape)
        }
        geoJSONfeatures.append(geojsonFeature)
    return {"type" : "FeatureCollection", "features":geoJSONfeatures}
    
@app.route("/carte")
def carte():
    return render_template('pages/carte.html', donnees=getGeoJSON(Gares.query.all()))

# @app.route("/gares")
# def gares():
#     dictGares = {}
#     for gare in Gares.query.order_by(Gares.label).all():
#         first = gare.label[0]
#         if first in dictGares.keys():
#             dictGares[first].append([gare.codeunique,gare.label])
#         else:
#             dictGares[first]=[[gare.codeunique,gare.label],]
#     return render_template('pages/gares.html', donnees=dictGares)

@app.route("/gares/<int:page>")
def gares(page):
    resultat = Gares.query.order_by(Gares.label).paginate(page=page, per_page=int(app.config["GARES_PER_PAGE"]))
    return render_template('pages/gares.html', pagination=resultat)

@app.route("/lignes")
def lignes():
    dictLignes = {}
    for ligne in Lignes.query.order_by(Lignes.label).all():
        first = ligne.label[0]
        if first in dictLignes.keys():
            dictLignes[first].append([ligne.id,ligne.label])
        else:
            dictLignes[first]=[[ligne.id,ligne.label],]
    return render_template('pages/lignes.html', donnees=dictLignes)

@app.route("/gare/<string:codeunique>")
def gare(codeunique):
    return render_template('pages/gare.html', id=codeunique, donnees=getGeoJSON([Gares.query.get(codeunique),]))

@app.route("/ligne/<string:id>")
def ligne(id):
    resultat = Lignes.query.get(id)
    return render_template('pages/ligne.html', id=id, resultat = resultat, donnees = getGeoJSON(resultat.lignes))

#manque route recherche
@app.route("/recherche", methods=['GET', 'POST'])
@app.route("/recherche/<int:page>", methods=['GET', 'POST'])
def recherche(page=1):
    form = Recherche() 

    
    # initialisation des données de retour dans le cas où il n'y ait pas de requête
    donnees = []

    try:
        if form.validate_on_submit():
            # récupération des éventuels arguments de l'URL qui seraient le signe de l'envoi d'un formulaire
            nom_gare =  clean_arg(request.form.get("nom_gare", None))
            nom_ligne =  clean_arg(request.form.get("ligne", None))

            # si l'un des champs de recherche a une valeur, alors cela veut dire que le formulaire a été rempli et qu'il faut lancer une recherche 
            # dans les données
            if nom_gare or nom_ligne:
                # initialisation de la recherche; en fonction de la présence ou nom d'un filtre côté utilisateur, nous effectuerons des filtres SQLAlchemy,
                # ce qui signifie que nous pouvons jouer ici plusieurs filtres d'affilée
                query_results = Gares.query

                if nom_gare:
                    query_results = query_results.filter(Gares.nom_long.ilike("%"+nom_gare.lower()+"%"))
                
                if ligne:
                    resource = db.session.execute("""select codeunique from gares 
                        inner join lignes on lignes.id = gares.codeunique and lignes.label  == '"""+nom_ligne+"""'
                        """).fetchall()
                    query_results = query_results.filter(Lignes.id.in_([l.id for l in lignes] ))
                
                
                
                donnees = query_results.order_by(Gares.name).paginate(page=page, per_page=app.config["GARES_PER_PAGE"])

                # renvoi des filtres de recherche pour préremplissage du formulaire
                form.nom_gare.data = nom_gare
                form.nom_ligne.data = nom_ligne
            flash("La recherche a été effectuée avec succès", "info")
    except Exception as e:
        flash("La recherche a rencontré une erreur "+ str(e), "info")

    return render_template("pages/resultats_recherche.html", 
            sous_titre= "Recherche" , 
            donnees=donnees,
            form=form)

@app.route("/autocompletion")
@app.route("/autocompletion/<string:chaine>")
def autocompletion(chaine=None):
    try: 
        query_results = Gare.query

        if chaine:
            query_results = query_results.filter(Gare.name.ilike("%"+chaine.lower()+"%"))
        
        donnees = [r.name for r in query_results.order_by(Gare.name).all()]
    except Exception as e:
        print(e)
        donnees = []
    return donnees