# Directives ACPO pour la Préservation des Preuves Numériques

## Vue d'ensemble

Les directives ACPO (Association of Chief Police Officers) définissent quatre principes fondamentaux pour la manipulation des preuves numériques. Ces principes garantissent l'intégrité, l'admissibilité en cour et la traçabilité complète des preuves.

## Les Quatre Principes Fondamentaux

### Principe 1: Pas de modification des données originales

**Énoncé**: Aucune action ne doit modifier les données originales ou les preuves de support.

**Applicabilité**:
- Si suppression/modification est inévitable, documenter complètement
- Justifier scientifiquement et légalement
- Maintenir une copie non modifiée

**Mise en œuvre**:
- Accès en lecture seule aux preuves originales
- Utiliser des blocs de lecture seule matériels
- Créer des images disque (clones) pour l'analyse
- Vérifier l'intégrité via empreintes cryptographiques

```
Données Originales (JAMAIS modifiées)
    ↓
Image Forense (Équivalent exact cryptographiquement)
    ↓
Copie de Travail (Pour analyse)
    ↓
Résultats
```

### Principe 2: Accès auditée et traçabil

**Énoncé**: Toute personne accédant aux preuves doit être clairement nommée, qualifiée et autorisée.

**Applicabilité**:
- Enregistrement de toute personne manipulant les preuves
- Qualifications et autorisations documentées
- Responsabilité individuelle identifiée

**Mise en œuvre**:
- Chaîne de conservation formelle
- Registres de laboratoire
- Signatures numériques des examinateurs
- Horodatage de toutes les actions

**Informations requises**:
- Nom et titre de la personne
- Date et heure de chaque accès
- Raison de l'accès
- Actions effectuées
- Signature ou validation

### Principe 3: Documentation Complète des Procédures

**Énoncé**: À chaque changement de possession des preuves, les procédures de transmission et de manutention doivent être documentées et acceptées.

**Applicabilité**:
- Transmission entre personnes
- Transmission entre localisations
- Changement d'état des preuves
- Modification de formats

**Mise en œuvre**:
- Formulaires de transmission signés
- Documentation des responsabilités
- Reçus et accusations
- Procédures de reprise de contact
- Logs détaillés des actions

**Documentation obligatoire**:
- Source des preuves
- Chemin complet de transmission
- Conditions de stockage
- Modificateurs et justifications
- État des scellés/certificats

### Principe 4: Responsabilité Organisationnelle

**Énoncé**: Un responsable de laboratoire doit être nommé qui possède une connaissance complète de tous les processus, outils et procédures impliqués.

**Applicabilité**:
- Supervision de tous les examens
- Responsabilité légale
- Validation des méthodes
- Garantie de qualité

**Mise en œuvre**:
- Nomination officielle d'un responsable
- Compétences et qualifications vérifiées
- Responsabilité des certifications
- Révision des procédures
- Validation des rapports

**Responsabilités**:
- Compétence technique
- Connaissance réglementaire
- Supervision de l'examen
- Responsabilité légale
- Documentation de l'autorisation

## Chaîne de Conservation

La chaîne de conservation est la documentation continue de la possession, du contrôle et de la manutention des preuves.

### Éléments essentiels

```
ACQUISITION
  ├─ Source identifiée
  ├─ Description des preuves
  ├─ Empreinte cryptographique
  └─ Signature de l'examinateur

TRANSFERT
  ├─ De: [Personne] [Date/Heure]
  ├─ À: [Personne] [Date/Heure]
  ├─ Description de l'objet
  ├─ Condition/État des scellés
  └─ Signatures des deux parties

STOCKAGE
  ├─ Localisation sécurisée
  ├─ Conditions (température, humidité)
  ├─ Accès restreint
  └─ Log d'accès

ANALYSE
  ├─ Date/Heure de début
  ├─ Examinateur et qualifications
  ├─ Outils et versions utilisés
  ├─ Procédures appliquées
  ├─ Résultats obtenus
  └─ Signature de l'examinateur
```

### Formulaire de Chaîne de Conservation

```
CHAÎNE DE CONSERVATION - FORMULAIRE STANDARD

Case ID: ________________
Evidence ID: ________________
Description: ________________
Original MD5: ________________
Original SHA256: ________________

ACQUISITION:
  Date: ________________  Heure: ________________
  Acquéreur: ________________  Titre: ________________
  Source: ________________
  Conditions: ________________
  Signature: ________________

[TRANSFERTS SUCCESSIFS]

TRANSFERT #1:
  De: ________________  Date/Heure: ________________
  À: ________________  Date/Heure: ________________
  Condition des scellés: ________________
  Signature De: ________________
  Signature À: ________________

[ANALYSES]

ANALYSE #1:
  Analyseur: ________________  Titre: ________________
  Date: ________________  Heure: ________________
  Durée: ________________
  Outils utilisés: ________________
  Actions effectuées: ________________
  Résultats: ________________
  Signature: ________________

```

## Standards Techniques

### Empreintes Cryptographiques

**Obligatoires**:
- MD5 (pour compatibilité et vérification rapide)
- SHA-256 (pour authenticité cryptographique)

**Utilisation**:
- Calculé sur données originales
- Recalculé sur chaque copie
- Correspondance requise pour validation
- Documenté dans rapport

**Format**:
```
Épreuve Originale:
  MD5: a1b2c3d4e5f6g7h8i9j0
  SHA256: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p

Image Copie:
  MD5: a1b2c3d4e5f6g7h8i9j0
  SHA256: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p

✓ Vérification: PASSÉE
```

### Outils Approuvés

**Acquisition**:
- dd (GNU ddutil)
- ddrescue (gestion d'erreurs)
- dc3dd (certificat de numérisation)

**Vérification**:
- md5sum / SHA256sum
- OpenSSL
- Tools.sleuthkit

**Récupération**:
- The Sleuth Kit (TSK)
- PhotoRec
- Scalpel
- Foremost

**Tous les outils doivent**:
- Être documentés et testés
- Avoir des versions connues
- Être configurés de manière cohérente
- Générer des logs vérifiables

## Procédures d'Identification et de Marquage

### Format des Identifiants

```
FORMAT: CASE_YYYY_NNNNNN_DD

CASE: Code d'affaire (p.ex.: THEFT, HOMICIDE)
YYYY: Année de l'affaire
NNNNNN: Numéro séquentiel
DD: Numéro d'épreuve

EXEMPLE: THEFT_2026_000001_01
```

### Marquage des Preuves

**Physique**:
- Étiquette apposée directement (si possible)
- Code à barres ou QR code
- Sac/conteneur identifié
- Signature du scellé

**Numérique**:
- Nommage cohérent des fichiers
- Métadonnées intégrées
- Tags de classification
- Horodatage UTC

## Conformité et Audit

### Vérifications internes

- Audit mensuel de la chaîne de conservation
- Vérification des empreintes cryptographiques
- Revue des procédures
- Test des outils
- Entrevues d'examinateurs

### Documentation à maintenir

- Journaux d'activités
- Tests de validité des outils
- Enregistrements de formation
- Procédures à jour
- Rapports d'audit
- Résolutions de non-conformité

### Rapport d'Audit

```markdown
## Audit de Conformité ACPO

Période: [Date début] à [Date fin]
Auditeur: [Nom] [Titre]

### Résultats

#### Principe 1: Protection des données originales
- Conformité: [✓/✗]
- Observations: ...
- Actions correctives: ...

#### Principe 2: Traçabilité des accès
- Conformité: [✓/✗]
- Observations: ...
- Actions correctives: ...

#### Principe 3: Documentation des procédures
- Conformité: [✓/✗]
- Observations: ...
- Actions correctives: ...

#### Principe 4: Responsabilité organisationnelle
- Conformité: [✓/✗]
- Observations: ...
- Actions correctives: ...

### Conclusion

[Résumé général de conformité]

Signé: ________________  Date: ________________
```

## Références

- ACPO (2012) - Good Practice Guide for Digital Evidence
- ENFSI (2015) - Best Practice Manual for Forensic Image Analysis
- ISO/IEC 27037:2012 - Guidelines for identification, collection, acquisition and preservation of digital evidence
- NIST SP 800-86 - Guide to Integrating Forensic Techniques into Incident Response

---

**Note**: Ces directives doivent être adaptées à la juridiction locale et aux exigences légales spécifiques.
