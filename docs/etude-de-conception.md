# Étude de conception — [nom du projet]

Groupe : Mohamed Saifeddine/Sara Hajdaoui/Marwa Khabarate/Ilyass Edhoum · Version : [brouillon / finale] · Date : [jj/mm/aaaa]

## 1. Contexte et utilisateurs
- Utilisateur principal (un rôle précis) :

## 2. Problème et décision
- Décision que l'utilisateur prend avec le système :
- Fréquence :
- Coût d'une erreur, et pour qui :

## 3. Approche par sous-problème
| Sous-problème | Approche (règles / ML / DL / LLM / RAG) | Pourquoi pas une approche plus simple |
|---|---|---|

## 4. Données
| Jeu de données | Source et licence | Volume | Données personnelles ? |
|---|---|---|---|

## 5. Métriques, baseline et critères d'acceptation
- Baseline et son score :
- Métrique principale, et pourquoi :
- Critères d'acceptation (métrique, nombre, jeu de données, condition) :

## 6. Architecture prévue
## 7. Choix technologiques
## 8. Risques, éthique, confidentialité
## 9. Limites et hors périmètre
(.venv) ➜  projet_a_completer python -m pytest                                      
============================================================================ test session starts ============================================================================
platform darwin -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/omisse1/Downloads/projet_a_completer
configfile: pytest.ini
testpaths: tests
collected 8 items                                                                                                                                                           

tests/test_data.py ...                                                                                                                                                [ 37%]
tests/test_models.py ..                                                                                                                                               [ 62%]
tests/test_train.py ...                                                                                                                                               [100%]

============================================================================= 8 passed in 2.89s =============================================================================
(.venv) ➜  projet_a_completer python -m monprojet.train                                            
                       accuracy  recall  precision     f1
arbre_decision            0.839   0.597      0.538  0.566
regression_logistique     0.889   0.574      0.737  0.645
foret_aleatoire           0.873   0.545      0.671  0.602
baseline                  0.824   0.000      0.000  0.000

CANTINE AI
(.venv) ➜  projet_a_completer python -m pytest
========================================================================= test session starts =========================================================================
platform darwin -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/omisse1/Downloads/projet_a_completer
configfile: pytest.ini
testpaths: tests
collected 8 items                                                                                                                                                     

tests/test_data.py ...                                                                                                                                          [ 37%]
tests/test_models.py ..                                                                                                                                         [ 62%]
tests/test_train.py ...                                                                                                                                         [100%]

========================================================================== 8 passed in 1.19s ==========================================================================
(.venv) ➜  projet_a_completer python -m monprojet.train
                        mae    rmse     r2
regression_lineaire  22.239  28.170  0.883
foret_aleatoire      31.845  41.540  0.746
arbre_decision       46.000  59.710  0.475
baseline             70.271  88.416 -0.151