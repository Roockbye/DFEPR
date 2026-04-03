# FAQ - Foire Aux Questions - DFEPR

## Questions Générales

### Q: Qu'est-ce que le DFEPR?
**A:** DFEPR (Digital Forensics Evidence Preservation & Recovery Lab) est un laboratoire 
de forensique numérique open-source conforme aux directives ACPO (Association of Chief 
Police Officers). Il fournit les outils et procédures nécessaires pour acquérir des images 
disque, récupérer des fichiers supprimés, et générer des rapports admissibles en cour.

### Q: Quels outils open-source sont utilisés?
**A:** 
- **ddrescue**: Acquisition d'images disque
- **The Sleuth Kit**: Analyse de systèmes de fichiers
- **PhotoRec**: Récupération par signature
- **Scalpel**: Carving avancé
- **Python**: Automatisation et scripting
- **OpenSSL**: Vérification cryptographique

### Q: Le DFEPR est-il légalement acceptable?
**A:** Oui. Le DFEPR suit strictement les directives ACPO et est conforme aux normes 
ISO/IEC et NIST. Les preuves acquises avec DFEPR sont admissibles en cour si les procédures 
sont correctement suivies.

### Q: Dois-je utiliser tous les outils?
**A:** Non, mais vous devez documenter quels outils vous utilisez et pourquoi. DFEPR 
fournit une flexibilité tout en maintenant la conformité ACPO.

---

## Questions Techniques

### Q: Puis-je acquérir une image d'un téléphone?
**A:** DFEPR est conçu pour les disques durs et SSD. Pour les téléphones, vous devriez 
consulter des outils spécialisés comme:
- UFED (Cellebrite) pour iOS/Android
- Magnet AXIOM pour mobile
- Toujours documenter l'outil utilisé

### Q: Combien de temps prend une acquisition?
**A:** Cela dépend de la taille et de la vitesse du disque:
- 1TB via USB 3.0: ~1-2 heures
- 512GB SSD: ~30-45 minutes
- Pour estimation: utilisez `time ddrescue --probe`

### Q: Puis-je faire plusieurs analyses sur la même image?
**A:** Oui! L'image disque est votre "original" numérique. Vous pouvez en analyser 
plusieurs copies sans crainte de modification, tant que vous vérifiez les hashes régulièrement.

### Q: Quel write-blocker dois-je utiliser?
**A:** N'importe quel write-blocker certifié convient:
- Tableau T35es/T35eu
- Paraben BlueCheck
- Guidance Software WiebeTech
- Pourvu qu'il soit testé et documenté

### Q: Les fichiers chiffrés peuvent-ils être récupérés?
**A:** Non. Si les données sont chiffrées par le système d'exploitation ou l'application, 
la récupération n'est pas possible sans la clé. Cependant, les métadonnées et les fragments 
peuvent toujours fournir des indications.

---

## Questions sur la Chaîne de Conservation

### Q: Qui peut accéder aux preuves?
**A:** Uniquement les personnes nommées et autorisées. Chaque accès doit être documenté 
avec date, heure, raison et signature.

### Q: Que faire en cas de rupture de la chaîne de conservation?
**A:**
1. Documenter complètement la rupture
2. Évaluer l'impact sur l'admissibilité
3. Obtenir une déclaration du personnel impliqué
4. Notifier la supervision et le conseil légal
5. Potentiellement rendre les preuves inadmissibles

### Q: Combien de temps faut-il conserver les preuves?
**A:** Cela dépend des exigences légales locales, mais généralement:
- Pendant l'enquête: Maintenu en sécurité
- Pendant le procès: Jusqu'à verdict + appels
- Après: Selon les directives locales (souvent 2-5 ans)

### Q: Puis-je supprimer une image disque?
**A:** Seulement après:
1. Accord juridique écrit
2. Archivage d'une copie (si ordonnance)
3. Documentation de destruction (témoins)
4. Fermeture officielle du cas

---

## Questions sur la Récupération de Fichiers

### Q: PhotoRec ou Scalpel?
**A:**
- **PhotoRec**: Rapide, créé par le même auteur que Recuva, bon pour rapport d'images
- **Scalpel**: Plus granulaire, meilleure configuration, bon pour ciblage spécifique

Utilisez les deux pour comparaison.

### Q: Les fichiers récupérés sont-ils fiables?
**A:** Cela dépend:
- **Haute confiance**: Fichiers avec métadonnées intactes
- **Moyenne confiance**: Fichiers récupérés par signature
- **Faible confiance**: Fichiers fragmentés/corrompus

Toujours vérifier l'intégrité et tester les fichiers.

### Q: Combien de temps la récupération prend-elle?
**A:**
- PhotoRec sur 1TB: 4-8 heures
- Scalpel sur 1TB: 2-4 heures
- Utiliser des systèmes plus puissants pour accélérer

### Q: Puis-je récupérer des fichiers spécifiques?
**A:** Partiellement:
- Vous pouvez configurer Scalpel pour des types spécifiques
- Vous pouvez trier les résultats de PhotoRec
- Mais vous risquez de manquer des fichiers

Mieux: récupérer tous, puis analyser.

---

## Questions Procédurales

### Q: Dois-je toujours calculer MD5 ET SHA256?
**A:** Oui. ACPO et les normes recommandent deux hashes:
- **MD5**: Pour rapidité et compatibilité (bien qu'deprecated)
- **SHA256**: Pour sécurité cryptographique et révision juridique

Tous deux fournissent une protection contre manipulation.

### Q: Quel format pour les rapports?
**A:** Au choix, mais incluez toujours:
- Texte brut (lisible, imprimable)
- HTML (présentation, archivage)
- JSON (données structurées)

Les procureurs préfèrent souvent PDF/Word pour format présenté.

### Q: Dois-je être Expert judiciaire?
**A:** Cela dépend de la juridiction. DFEPR fournit:
- Procédures acceptées
- Documentation complète
- Certification appropriée

Vous devez comprendre chaque étape et pouvoir la justifier en cour.

### Q: Puis-je automatiser l'analyse?
**A:** Oui, avec DFEPR Python modules:
```python
from src.chain_of_custody import ChainOfCustody
from src.hash_verifier import HashVerifier

# Créer automatiquement les documents
coc = ChainOfCustody("CASE_ID", "EVIDENCE_ID")
verifier = HashVerifier("CASE_ID")
```

Mais documentez toujours les étapes automatisées.

---

## Questions de Conformité

### Q: Comment assurer la conformité ACPO?
**A:** Suivez les quatre principes:
1. **Principe 1**: Ne modifier JAMAIS les données originales
   - ✓ Utiliser write-blocker
   - ✓ Créer image disque
   - ✓ Vérifier hashes

2. **Principe 2**: Identifier tout personnel
   - ✓ Signer tous les formulaires
   - ✓ Documenter les qualifications
   - ✓ Enregistrer tous les accès

3. **Principe 3**: Documenter les procédures
   - ✓ Utiliser formulaires standardisés
   - ✓ Enregistrer la chaîne de conservation
   - ✓ Conserver tous les logs

4. **Principe 4**: Supervision responsable
   - ✓ Approuver par superviseur
   - ✓ Vérifier les résultats
   - ✓ Signer les rapports

### Q: Comment démontrer la conformité en cour?
**A:**
1. Présenter la chaîne de conservation complète
2. Montrer les vérifications de hash
3. Expliquer la méthodologie ACPO
4. Présenter les certifications personnelles
5. Fournir les logs détaillés

### Q: Qu'en cas de défi lors du procès?
**A:**
1. Rester calme et professionnel
2. Référencer les normes ACPO/NIST
3. Expliquer chaque étape
4. Produire la documentation de soutien
5. Ne pas improviser - vous connaissez votre procédure

---

## Questions de Ressources

### Q: Quel matériel est nécessaire?
**A:** Minimum:
- Ordinateur Linux ou compatible (8GB RAM min)
- Write-blocker USB
- Espace disque: 3x la taille de l'appareil analysé
- Disque dur externe pour archivage

Recommandé:
- Système dédié au laboratoire
- 32GB RAM pour accélération
- Stockage RAID pour redondance
- Disque externe chiffré pour preuves

### Q: Quel système d'exploitation?
**A:** 
- **Linux** (Ubuntu/Debian/Fedora): Recommandé, tous les outils natifs
- **macOS**: Les outils fonctionnent mais avec limitations
- **Windows**: Difficile, envisager dual-boot ou VM

Utilisez Linux dédié pour optimal.

### Q: Puis-je analyser des preuves de taille 5TB?
**A:** Théoriquement oui, pratiquement:
- Vous aurez besoin: ≥15TB d'espace libre
- Temps d'acquisition: 8-12 heures
- Temps de récupération: 20-40 heures
- Coût: Important en électricité et temps

Considérer le partitionnement ou la sélection.

### Q: Où puis-je obtenir de l'aide?
**A:**
- Documentation DFEPR: `docs/` directory
- Procédures: `docs/procedures/`
- Tests: `python3 tests/test_dfepr.py`
- Issues: Vérifier la documentation d'abord
- Superviseur: Pour questions conformité
- Conseil légal: Pour questions légales

---

## Questions Éthiques

### Q: Puis-je analyser des appareils personnels?
**A:** **Seulement** avec:
- Mandat juridique approprié
- Consentement écrit du propriétaire, OU
- Autorité légale établie

JAMAIS sans foundation légale.

### Q: Les données privées/confidentielles?
**A:** 
- Traiter confidentiel: Mots de passe, communications privées
- Documenter: Vous l'avez trouvé, ce qu'il contient
- Limiter l'accès: À le minimum nécessaire
- Rapporter: Les conclusions, pas les détails privés

Consulter éthique de laboratoire et conseil légal.

### Q: Que faire si je découvre un crime non connexe?
**A:**
1. Documenter la découverte
2. Notifier supervision immédiatement
3. Consulter conseil légal
4. Potentiellement rapporter aux autorités
5. Maintenir la chaîne de conservation

C'est un obligation morale et souvent légale.

---

## Ressources Supplémentaires

### Documentation Externe
- ACPO: https://www.acpo.police.uk/
- NIST SP 800-86: Digital Forensics 
- ISO/IEC 27037:2012: Digital Evidence

### Outils Additionnels
- Autopsy: Analyse graphique
- Volatility: Analyse mémoire
- FTK: Alternative commerciale
- Wireshark: Analyse réseau

### Formation
- GIAC GCIH: Certifications
- EnCE: Examinateurs certifiés
- SANS SEC504: Forensique avancée

---

## Pour Plus d'Aide

**Lab Manager**: Consultez votre superviseur
**Technical Issues**: Vérifier les logs avec `make logs`
**Procedure Questions**: Référencer la documentation dans `docs/`
**Test Coverage**: Lancer les tests avec `make test`

---

**Document Version**: 1.0
**Last Updated**: 2026-04-03
**ACPO Compliant**: Yes
