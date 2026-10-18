from collections import deque
from itertools import product
COUTS = [[5, 3, 4],
         [6, 7, 2]]
STOCKS = [8, 9]
DEMANDES = [4, 5, 8]
NOMS_M = ["M1", "M2", "M3"]
SOLUTION_INITIALE = (4, 3, 1)
NB_ITERATIONS = 10
TAILLE_LISTE_TABOUE = 3
def deduire_d2(x1):
    """Livraisons de D2 : ce que D1 ne livre pas."""
    return tuple(d - a for d, a in zip(DEMANDES, x1))
def cout_total(x1):
    """Fonction objectif Z."""
    x2 = deduire_d2(x1)
    return (sum(c * a for c, a in zip(COUTS[0], x1))
            + sum(c * a for c, a in zip(COUTS[1], x2)))
def est_realisable(x1):
    """Vérifie les contraintes : x >= 0, demandes, stocks de D1 et D2."""
    x2 = deduire_d2(x1)
    return (all(0 <= a <= d for a, d in zip(x1, DEMANDES))
            and sum(x1) <= STOCKS[0]
            and sum(x2) <= STOCKS[1])
def texte_mouvement(m):
    k, j = m
    return f"1 container de {NOMS_M[k]} vers {NOMS_M[j]}"
def voisins(x1):
    """Liste des (mouvement, solution voisine) réalisables."""
    resultat = []
    for k in range(3):
        for j in range(3):
            if k == j:
                continue
            nouveau = list(x1)
            nouveau[k] -= 1          # D1 livre 1 de moins à Mk
            nouveau[j] += 1          # D1 livre 1 de plus à Mj
            nouveau = tuple(nouveau)
            if est_realisable(nouveau):
                resultat.append(((k, j), nouveau))
    return resultat
def recherche_taboue(depart, nb_iter=NB_ITERATIONS, taille_liste=TAILLE_LISTE_TABOUE):
    courante = tuple(depart)
    z_courant = cout_total(courante)
    meilleure, z_meilleur = courante, z_courant
    liste_taboue = deque(maxlen=taille_liste)

    historique = [{"it": 0, "sol": courante, "z": z_courant, "best": z_meilleur,
                   "mouvement": "-", "interdits": []}]

    for it in range(1, nb_iter + 1):
        interdits = list(liste_taboue)
        choix, z_choix = None, float("inf")
        for mvt, sol in voisins(courante):
            z = cout_total(sol)
            est_tabou = mvt in interdits
            aspiration = z < z_meilleur
            if est_tabou and not aspiration:
                continue
            if z < z_choix:
                choix, z_choix = (mvt, sol), z

        if choix is None:
            print(f"Itération {it} : aucun voisin admissible, arrêt.")
            break
        (k, j), courante = choix
        z_courant = z_choix
        liste_taboue.append((j, k))
        if z_courant < z_meilleur:
            meilleure, z_meilleur = courante, z_courant

        historique.append({"it": it, "sol": courante, "z": z_courant, "best": z_meilleur,
                           "mouvement": texte_mouvement((k, j)),
                           "interdits": [texte_mouvement(m) for m in liste_taboue]})

    return meilleure, z_meilleur, historique
def afficher_historique(historique):
    print(f"{'Étape':<10}{'D1 (M1,M2,M3)':<16}{'Coût courant':<14}{'Meilleur coût':<15}"
          f"Mouvement effectué")
    print("-" * 90)
    for h in historique:
        nom = "Initiale" if h["it"] == 0 else f"Iter. {h['it']}"
        print(f"{nom:<10}{str(h['sol']):<16}{h['z']:<14}{h['best']:<15}{h['mouvement']}")
def afficher_liste_taboue(historique):
    print("\nListe taboue après chaque itération (mouvements interdits, le plus récent en dernier) :")
    for h in historique[1:]:
        print(f"  Iter. {h['it']:<3}: " + " | ".join(h["interdits"]))
def afficher_matrice(x1):
    x2 = deduire_d2(x1)
    print("\nMatrice des livraisons :")
    print(f"{'':<5}{'M1':>5}{'M2':>5}{'M3':>5}{'Total':>8}")
    print(f"{'D1':<5}{x1[0]:>5}{x1[1]:>5}{x1[2]:>5}{sum(x1):>8}")
    print(f"{'D2':<5}{x2[0]:>5}{x2[1]:>5}{x2[2]:>5}{sum(x2):>8}")
    print(f"Coût total Z = {cout_total(x1)}")
def enumeration_complete():
    """Énumère toutes les solutions réalisables (29 ici) et les trie par coût."""
    solutions = [(cout_total(x1), x1)
                 for x1 in product(*(range(d + 1) for d in DEMANDES))
                 if est_realisable(x1)]
    solutions.sort()
    return solutions
def verification_plne():
    """Résolution exacte du PLNE avec un solveur Branch and Bound (scipy), si disponible."""
    try:
        import numpy as np
        from scipy.optimize import milp, LinearConstraint, Bounds
    except ImportError:
        print("scipy non installé : vérification PLNE ignorée (pip install scipy).")
        return None

    c = np.array(COUTS[0] + COUTS[1], dtype=float)
    A_stock = [[1, 1, 1, 0, 0, 0],
               [0, 0, 0, 1, 1, 1]]
    A_dem = [[1, 0, 0, 1, 0, 0],
             [0, 1, 0, 0, 1, 0],
             [0, 0, 1, 0, 0, 1]]
    contraintes = [LinearConstraint(A_stock, -np.inf, STOCKS),
                   LinearConstraint(A_dem, DEMANDES, DEMANDES)]
    res = milp(c, constraints=contraintes, integrality=np.ones(6),
               bounds=Bounds(0, np.inf))
    x = [int(round(v)) for v in res.x]
    return x, int(round(res.fun))
if __name__ == "__main__":
    print(f"Solution initiale : D1 = {SOLUTION_INITIALE}, D2 = {deduire_d2(SOLUTION_INITIALE)}, "
          f"Z = {cout_total(SOLUTION_INITIALE)}")
    print(f"Itérations : {NB_ITERATIONS} | Liste taboue : {TAILLE_LISTE_TABOUE} cases\n")

    meilleure, z_meilleur, historique = recherche_taboue(SOLUTION_INITIALE)

    afficher_historique(historique)
    afficher_liste_taboue(historique)
    print("\n=== Meilleure solution trouvée par la recherche taboue ===")
    afficher_matrice(meilleure)
    solutions = enumeration_complete()
    z_opt, x_opt = solutions[0]
    print("\n=== Vérification par énumération complète ===")
    print(f"Nombre de solutions réalisables : {len(solutions)}")
    print(f"Optimum exact : D1 = {x_opt}, Z = {z_opt}")
    if z_meilleur == z_opt:
        print("La recherche taboue a trouvé la bonne solution.")