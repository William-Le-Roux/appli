from app.app import app, db

gares_lignes = db.Table(
    "gares_lignes",
    db.Column('gareid', db.Integer, db.ForeignKey('gares.codeunique'), primary_key=True),
    db.Column('ligneid', db.Integer, db.ForeignKey('lignes.id'), primary_key=True)
)

class Gares(db.Model):
    __tablename__ = "gares"

    codeunique	= db.Column(db.Integer, primary_key=True )
    nom_long = db.Column(db.String(100))
    label = db.Column(db.String(100))
    id_ref_lda = db.Column(db.Integer)
    nom_lda	= db.Column(db.String(100))
    id_ref_zdl = db.Column(db.Integer)
    nom_zdl = db.Column(db.String(100))
    idrefliga= db.Column(db.String(100))
    idrefligc= db.Column(db.String(100))

    # propriétés de relation
    coordonnees = db.relationship(
        'Coordonnees', 
        backref='geom', 
        lazy=True
    )

    lignes = db.relationship(
      'Lignes', 
      secondary=gares_lignes, 
      backref="lignes"
  )

class Coordonnees(db.Model):
    __tablename__ = "coordonnees"
    
    codeunique	= db.Column(db.Integer, db.ForeignKey('gares.codeunique'), primary_key=True)
    geoPoint = db.Column(db.String(200))
    geoShape = db.Column(db.String(200))
    x = db.Column(db.String(50))
    y = db.Column(db.String(50))

class Lignes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))