# Chaîne de Conservation - Procédure Complète - DFEPR

## Vue d'ensemble

La chaîne de conservation (Chain of Custody) est le système fondamental qui démontre
que les preuves numériques n'ont pas été modifiées, perdues ou compromises. C'est
un élément crucial pour l'admissibilité en cour.

## Principes Fondamentaux ACPO

### 1. Continuité Ininterrompue
La chaîne doit être complète de l'acquisition initiale jusqu'à la présentation devant le tribunal.

### 2. Documentation Exhaustive
Chaque transfert, chaque accès, chaque changement d'état doit être documenté.

### 3. Responsabilité Individuelle
Chaque personne manipulant les preuves est nommée et responsable.

### 4. Tracabilité Physique et Numérique
Suivi des preuves physiques ET des fichiers/images numériques.

## Structure de la Chaîne de Conservation

```
┌─────────────────────────────────────────┐
│   ACQUISITION INITIALE                  │
│ • Dispositif Source  • Date/Heure       │
│ • Acquéreur          • Hashes           │
│ • Signature          • Métadonnées      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   TRANSFERT 1                           │
│ • De: [Personne 1]  À: [Personne 2]    │
│ • Date/Heure        • Condition Code    │
│ • Signatures        • Observations      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   STOCKAGE SÉCURISÉ                     │
│ • Date d'entrée     • Conditions        │
│ • Emplacement       • Log d'accès       │
│ • Personne garante                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   ANALYSE 1                             │
│ • Date/Heure début  • Fin               │
│ • Analyste          • Outils utilisés   │
│ • Procédures        • Résultats         │
│ • Signature         • Observations      │
└──────────────┬──────────────────────────┘
               │
         [Cycles d'analyses]
               │
└──────────────▼──────────────────────────┐
│   LIBÉRATION / ARCHIVAGE                │
│ • Date de libération                    │
│ • État final des preuves                │
│ • Signature de release                  │
│ • Lieu d'archivage                      │
└─────────────────────────────────────────┘
```

## Documentation Requise

### 1. Formulaire d'Acquisition

```
FORMULAIRE D'ACQUISITION DE PREUVES NUMÉRIQUES

Case ID: _________________________
Evidence ID: _______________________

SOURCE PHYSIQUE:
  Description: _____________________
  Fabricant/Modèle: __________________
  Numéro de Série: ________________
  Capacité: ______________________
  État Physique: ____________________

ACQUISITION:
  Date: ________________________  Heure: ___________
  Dispositif Acquéreur: ________________
  Personne: ______________________
  Titre/Qualification: _______________
  
IMAGES CRÉÉES:
  Fichier: ________________________
  Taille: ________________________
  Localisation: ____________________
  
HASH VERIFICATION:
  MD5: ___________________________
  SHA-256: _________________________
  
SCELLÉ/CODE:
  Type de scellé: __________________
  Code: ________________________
  
SIGNATURE ACQUÉREUR:
  ____________________________  Date: __________
  
SIGNATURE SUPERVISEUR:
  ____________________________  Date: __________
```

### 2. Formulaire de Transfert

```
FORMULAIRE DE TRANSFERT DE PREUVE

Evidence ID: _______________________
Description: _______________________

TRANSFERT DE:
  Nom: __________________________
  Titre: _________________________
  Date/Heure: ________________

À:
  Nom: __________________________
  Titre: _________________________
  Date/Heure: ________________

ÉLÉMENTS TRANSFÉRÉS:
  [ ] Dispositif original
  [ ] Image(s) disque
  [ ] Hash files
  [ ] Métadonnées
  [ ] Rapports
  [ ] Autre: ________________________

CONDITION PHYSIQUE:
  Scellés intacts: [ ] Oui [ ] Non
  Scellé #: ________________________
  Observations: _______________________

VÉRIFICATION D'INTÉGRITÉ:
  Hashes vérifiés: [ ] Oui [ ] Non
  Résultat: [ ] PASS [ ] FAIL
  
SIGNATURES:
  Transférant: ___________________  Date: ________
  Recevant: ____________________  Date: ________

NOTES ADDITIONNELLES:
  _________________________________
  _________________________________
```

### 3. Formulaire de Stockage

```
FORMULAIRE DE STOCKAGE SÉCURISÉ

Case ID: _________________________
Evidence ID: _______________________

CONDITIONS DE STOCKAGE:
  Localisation exacte: _______________
  Armoire/Réseau: ___________________
  Température: _____ °C  Humidité: ____%
  
ACCÈS:
  Gardien désigné: __________________
  Horaires d'accès: __________________
  Accès restreint à: ________________
  
INSPECTION/VÉRIFICATION:
  Fréquence: ______________________
  Dernière: _____  Prochaine: _____
  
ÉVÉNEMENTS:
  Date/Heure | Événement | Personnel
  ___________|___________|___________
  
CODE/SCELLÉ:
  Type: __________________________
  Numéro: ________________________
  État actuel: [ ] Intact [ ] Endommagé [ ] Cassé
  
TRANSPORT:
  [ ] Jamais transporté
  [ ] Transporté le: ________________
  Raison: __________________________
  
Signature Gardien: _________________  Date: _______
```

### 4. Formulaire d'Analyse

```
FORMULAIRE D'ANALYSE FORENSE

Case ID: _________________________
Evidence ID: _______________________

ANALYSE #: ______  DATE: _______________

ANALYSTE:
  Nom: __________________________
  Titre: _________________________
  Qualifications: _____________________
  
DÉBUT:
  Date: _______  Heure: ________
  Image: ________________________
  État initial de l'image:
    [ ] Vérification PASS
    [ ] Vérification FAIL
    Hashes: [Document les hashes vérifiés]
  
PROCÉDURES:
  Outils utilisés:
    1. __________________________ Version: ____
    2. __________________________ Version: ____
    3. __________________________ Version: ____
    
  Paramètres:
    _________________________________
    _________________________________
    
  Méthodologie:
    _________________________________
    _________________________________
    
FIN:
  Date: _______  Heure: ________
  Durée totale: ____________________
  
RÉSULTATS:
  Découvertes principales:
    _________________________________
    _________________________________
    
  Fichiers créés:
    1. __________________________ Taille: _____
    2. __________________________ Taille: _____
    
  Hashes de fichiers créés:
    Fichier 1: ______________________
    Fichier 2: ______________________
    
SIGNATURE ANALYSTE:
  ____________________________  Date: __________
  
SIGNATURE SUPERVISEUR:
  ____________________________  Date: __________
  
OBSERVATIONS:
  _________________________________
  _________________________________
```

### 5. Formulaire de Libération

```
FORMULAIRE DE LIBÉRATION DE PREUVE

Case ID: _________________________
Evidence ID: _______________________

RAISON DE LIBÉRATION:
  [ ] Enquête terminée
  [ ] Procès terminé
  [ ] Destruction ordonnée
  [ ] Retour au propriétaire
  [ ] Autre: ________________________

ÉTAT FINAL:
  Dispositif original: [ ] Intact [ ] Modifié [ ] Détruit
  Images disque: [ ] Archivées [ ] Supprimées [ ] Transférées
  Rapports: [ ] Archive [ ] Remis au[ ] Destroyed
  
ARCHIVAGE (si applicable):
  Lieu d'archivage: __________________
  Format: __________________________
  Période de conservation: _____________
  
DESTRUCTION (si applicable):
  Date/Heure destruction: _____________
  Méthode: ________________________
  Témoin 1: _______________________
  Témoin 2: _______________________
  
RETOUR AU PROPRIÉTAIRE:
  Destinataire: _____________________
  Date de retour: __________________
  Méthode: ________________________
  Signature reçue: ___________________
  
SIGNATURE RESPONSABLE:
  ____________________________  Date: __________

APPROBATION SUPERVISEUR:
  ____________________________  Date: __________
```

## Procédure Pas à Pas

### Phase 1: Acquisition
1. Inspecter le dispositif source
2. Enregistrer tous les détails physiques
3. Créer l'image avec vérification d'intégrité
4. Calculer les hashes (MD5 + SHA256)
5. Compléter le formulaire d'acquisition
6. Signer par acquéreur et superviseur

### Phase 2: Transfert Initial
1. Remplir le formulaire de transfert
2. Vérifier l'intégrité avant transfert
3. Appliquer le code/scellé
4. Signatures des deux parties
5. Documenter les observations
6. Archiver le formulaire complété

### Phase 3: Stockage Sécurisé
1. Placer dans emplacement désigné
2. Enregistrer l'emplacement exact
3. Vérifier conditions de stockage
4. Effectuer inspections régulières
5. Tenir jour le log d'accès
6. Documenter tous les accès

### Phase 4: Analyses
Pour chaque analyse:
1. Vérifier l'intégrité de l'image
2. Compléter form d'analyse avec détails
3. Effectuer l'analyse documentée
4. Vérifier l'intégrité après
5. Créer hashes des fichiers générés
6. Signature analyste ET superviseur
7. Archiver le formulaire

### Phase 5: Énumération/Libération
1. Vérifier l'état final
2. Déterminer le sort des preuves
3. Compléter formulaire approprié
4. Obtenir approbations requises
5. Effectuer action (archivage/destruction/retour)
6. Témoins le cas échéant
7. Archiver documentation complète

## Gestion Électronique de la CoC

### Utiliser Python pour automatiser:

```python
from src.chain_of_custody import ChainOfCustody, CustodyAction

# Créer ou charger la CoC
coc = ChainOfCustody("CASE_2026_001", "EVIDENCE_001")

# Ajouter les entrées
coc.add_entry(
    action=CustodyAction.ACQUISITION,
    person_name="John Doe",
    person_title="Examiner",
    location="Lab",
    description="Disk imaging with ddrescue",
    items_affected=["/dev/sda"],
    signature="JD-2026040301"
)

# Générer le rapport
report = coc.generate_report()
print(report)

# Exporter pour soumission
coc.export_for_submission("EVIDENCE_001_coc_report.txt")
```

## Qualité Assurance

### Audit et Vérification

```bash
# Vérifier l'intégrité de la CoC
python3 << 'EOF'
from src.chain_of_custody import ChainOfCustody

coc = ChainOfCustody("CASE_ID", "coc_file.json")
history = coc.get_history()

print(f"Total entries: {len(history)}")
for i, entry in enumerate(history, 1):
    print(f"{i}. {entry['action']} by {entry['person_name']} on {entry['timestamp']}")
    
# Check gaps
if len(history) < 2:
    print("WARNING: Only one entry. May indicate incomplete CoC")
EOF
```

### Checklist Conformité ACPO

- [ ] Acquisition enregistrée avec signatures
- [ ] Tous les transferts documentés
- [ ] Chaque personnel nommé
- [ ] Toutes les dates/heures UTC
- [ ] Hashes vérifiés et documentés
- [ ] Scellés appropriés utilisés
- [ ] Stockage sécurisé vérifié
- [ ] Chaque analyse documentée
- [ ] Aucune interruption dans la chaîne
- [ ] Tous les formulaires archivés
- [ ] Superviseur a approuvé
- [ ] Prêt pour présentation en cour

## Problèmes Courants

### Chaîne Brisée
**Symptôme**: Gap dans la documentation ou accès non autorisé

**Solution**:
1. Documenter le gap clairement
2. Obtenir une déclaration écrite de l'équipe
3. Justifier la rupture
4. Évaluer l'impact sur les preuves
5. Consulter superviseur et conseil légal

### Hashes Non Concordants
**Symptôme**: Les hashes ne correspondent pas

**Solution**:
1. Recalculer les hashes
2. Vérifier les outils utilisés
3. Documenter la discrepance
4. Investiguer la cause
5. Signaler au superviseur

### Preuves Manquantes
**Symptôme**: Preuves enregistrées mais non localisées

**Solution**:
1. Arrêter immédiatement
2. Lancer investigation interne
3. Documenter tous les détails
4. Notifier supervision
5. Potentiellement reportable légalement

## Ressources

### Templates
- [Formulaires Word](docs/forms/)
- [Templates Python](src/chain_of_custody.py)

### Documentation ACPO
- ACPO Good Practice Guide v2012
- ISO/IEC 27037:2012
- NIST SP 800-86

###  Exemples de Cas
- [Example 1](docs/case_examples/case_001.md)
- [Example 2](docs/case_examples/case_002.md)

---

**Document Version:** 1.0
**Last Updated:** 2026-04-03
**ACPO Compliance:** Verified

Pour toutes questions: consult the lab supervisor
