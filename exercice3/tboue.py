from collections import deque
from itertools import permutations
ROUTES = {
    (1, 2): 14, (1, 3): 15, (1, 8): 17,
    (2, 3): 13, (2, 4): 14, (2, 5): 20, (2, 8): 21,
    (3, 4): 11, (3, 5): 21, (3, 6): 17, (3, 7): 9, (3, 8): 9,
    (4, 5): 11, (4, 6): 10, (4, 7): 8, (4, 8): 20,
    (5, 6): 15, (5, 7): 18,
    (6, 7): 9,
    (7, 8): 13,
}
DIST = {}
for (a, b), d in ROUTES.items():
    DIST[(a, b)] = d
    DIST[(b, a)] = d
SOLUTION_INITIALE = [1, 2, 3, 4, 5, 6, 7, 8, 1]
NB_ITERATIONS = 10
TAILLE_LISTE_TABOUE = 3
AFFICHER_VOISINS = True
def longueur(circuit):
    total = 0
    for a, b in zip(circuit, circuit[1:]):
        if (a, b) not in DIST:
            return None
        total += DIST[(a, b)]
    return total
def texte_circuit(circuit):
    return "-".join(map(str, circuit))
def texte_echange(m):
    return f"{m[0]}↔{m[1]}"
def voisins(circuit):
    """Retourne la liste des (échange, nouveau circuit, longueur) pour tous les échanges.
    La longueur vaut None si le circuit utilise une route inexistante."""
    resultat = []
    n = len(circuit)
    for i in range(1, n - 1):
        for j in range(i + 1, n - 1):
            nouveau = circuit[:]
            nouveau[i], nouveau[j] = nouveau[j], nouveau[i]
            echange = tuple(sorted((circuit[i], circuit[j])))   # 2↔3 = 3↔2
            resultat.append((echange, nouveau, longueur(nouveau)))
    return resultat
def recherche_taboue(depart, nb_iter=NB_ITERATIONS, taille_liste=TAILLE_LISTE_TABOUE,
                     verbose=AFFICHER_VOISINS):
    courant = depart[:]
    z_courant = longueur(courant)
    meilleur, z_meilleur = courant[:], z_courant

    liste_taboue = deque(maxlen=taille_liste)
    historique = [{"it": 0, "circuit": courant[:], "z": z_courant, "echange": None,
                   "meilleur": z_meilleur, "debut": [], "ajoute": None, "sort": None,
                   "liste_apres": []}]

    for it in range(1, nb_iter + 1):
        debut = list(liste_taboue)[::-1]
        evalues = []
        for echange, circuit, z in voisins(courant):
            if z is None:
                continue
            est_tabou = echange in liste_taboue
            aspiration = est_tabou and z < z_meilleur
            evalues.append({"echange": echange, "circuit": circuit, "z": z,
                            "tabou": est_tabou and not aspiration,
                            "aspiration": aspiration})

        evalues.sort(key=lambda v: v["z"])
        choix = next((v for v in evalues if not v["tabou"]), None)
        if choix is None:
            print(f"Itération {it} : tous les voisins sont interdits, arrêt.")
            break

        if verbose:
            print(f"\n--- Itération {it} --- circuit courant {texte_circuit(courant)} (Z = {z_courant}), "
                  f"liste taboue : {[texte_echange(m) for m in debut] or 'vide'}")
            for v in evalues:
                etat = ("INTERDIT" if v["tabou"] else
                        "ASPIRATION" if v["aspiration"] else "autorisé")
                marque = "  <== choisi" if v is choix else ""
                print(f"    {texte_echange(v['echange']):<6} {texte_circuit(v['circuit'])}  "
                      f"Z = {v['z']:<4} {etat}{marque}")
        courant, z_courant = choix["circuit"], choix["z"]
        sort = liste_taboue[0] if len(liste_taboue) == taille_liste else None
        liste_taboue.append(choix["echange"])
        if z_courant < z_meilleur:
            meilleur, z_meilleur = courant[:], z_courant

        historique.append({"it": it, "circuit": courant[:], "z": z_courant,
                           "echange": choix["echange"], "meilleur": z_meilleur,
                           "debut": debut, "ajoute": choix["echange"], "sort": sort,
                           "liste_apres": list(liste_taboue)[::-1]})

    return meilleur, z_meilleur, historique
def cases(liste):
    """Texte des 3 cases de la liste taboue (case 1 = la plus récente)."""
    textes = [texte_echange(m) for m in liste] + ["vide"] * (TAILLE_LISTE_TABOUE - len(liste))
    return " · ".join(textes)
def afficher_tableau_etapes(hist):
    print("\n=== TABLEAU DES ÉTAPES (circuit obtenu APRÈS chaque itération) ===")
    print(f"{'Itér.':<7}{'Circuit courant':<22}{'Coût':<7}{'Échange':<9}"
          f"{'Meilleur':<10}Liste taboue après l'itération (case 1 · 2 · 3)")
    print("-" * 100)
    for h in hist:
        ech = "-" if h["echange"] is None else texte_echange(h["echange"])
        print(f"{h['it']:<7}{texte_circuit(h['circuit']):<22}{h['z']:<7}{ech:<9}"
              f"{h['meilleur']:<10}{cases(h['liste_apres'])}")
def afficher_liste_taboue(hist):
    print("\n=== LISTE TABOUE À CHAQUE ITÉRATION ===")
    print(f"{'Itér.':<7}{'Liste au début (case 1 · 2 · 3)':<38}{'Ajouté':<9}Sort de la liste")
    print("-" * 70)
    for h in hist[1:]:
        sort = "-" if h["sort"] is None else texte_echange(h["sort"])
        print(f"{h['it']:<7}{cases(h['debut']):<38}{texte_echange(h['ajoute']):<9}{sort}")
def enumeration_complete():
    circuits = []
    for p in permutations(range(2, 9)):
        c = [1, *p, 1]
        z = longueur(c)
        if z is not None:
            circuits.append((z, c))
    circuits.sort()
    return circuits
if __name__ == "__main__":
    print(f"Circuit initial : {texte_circuit(SOLUTION_INITIALE)}, "
          f"Z = {longueur(SOLUTION_INITIALE)}")
    print(f"Itérations : {NB_ITERATIONS} | Liste taboue : {TAILLE_LISTE_TABOUE} cases")

    meilleur, z_meilleur, historique = recherche_taboue(SOLUTION_INITIALE)

    afficher_tableau_etapes(historique)
    afficher_liste_taboue(historique)

    print("\n=== RÉSULTAT DE LA RECHERCHE TABOUE ===")
    print(f"Meilleur circuit trouvé : {texte_circuit(meilleur)}")
    print(f"Longueur : {z_meilleur}")
