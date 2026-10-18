import math
import random
MATRICE = [
    #  V1    V2    V3    V4    V5    V6    V7    V8
    [0,    14,   15,   None, None, None, None, 17],     # ville 1
    [14,   0,    13,   14,   20,   None, None, 21],     # ville 2
    [15,   13,   0,    11,   21,   17,   9,    9],      # ville 3
    [None, 14,   11,   0,    11,   10,   8,    20],     # ville 4
    [None, 20,   21,   11,   0,    15,   18,   None],   # ville 5
    [None, None, 17,   10,   15,   0,    9,    None],   # ville 6
    [None, None, 9,    8,    18,   9,    0,    13],     # ville 7
    [17,   21,   9,    20,   None, None, 13,   0],      # ville 8
]
CIRCUIT_INITIAL = [1, 2, 5, 4, 6, 7, 3, 8, 1]
T0 = 10
PAS = 2
NB_ITERATIONS = 5
R_FIXE = 0.5
GRAINE = 42
ECHANGES_IMPOSES = None
def verifier_matrice(matrice):
    n = len(matrice)
    avertissements = []
    if any(len(ligne) != n for ligne in matrice):
        raise ValueError("La matrice doit être carrée.")
    for i in range(n):
        for j in range(i + 1, n):
            if matrice[i][j] != matrice[j][i]:
                avertissements.append(f"Asymétrie entre les villes {i + 1} et {j + 1} : "
                                      f"{matrice[i][j]} / {matrice[j][i]}")
    return avertissements
def verifier_circuit(circuit, matrice):
    n = len(matrice)
    if circuit[0] != 1 or circuit[-1] != 1:
        return False, "le circuit doit commencer et finir par la ville 1"
    if sorted(circuit[:-1]) != list(range(1, n + 1)):
        return False, "chaque ville doit être visitée exactement une fois"
    for a, b in zip(circuit, circuit[1:]):
        if matrice[a - 1][b - 1] is None:
            return False, f"liaison interdite entre les villes {a} et {b}"
    return True, "ok"
def calculer_cout(circuit, matrice):
    valide, message = verifier_circuit(circuit, matrice)
    if not valide:
        raise ValueError(f"Circuit irréalisable : {message}")
    return sum(matrice[a - 1][b - 1] for a, b in zip(circuit, circuit[1:]))
def texte_circuit(circuit):
    return "-".join(map(str, circuit))
def generer_voisin(circuit, matrice, rng, echange_impose=None):
    n = len(circuit)
    if echange_impose is not None:
        a, b = echange_impose
        candidat = [b if v == a else a if v == b else v for v in circuit]
        valide, message = verifier_circuit(candidat, matrice)
        if not valide:
            raise ValueError(f"L'échange imposé {a}↔{b} est irréalisable : {message}")
        return candidat, (a, b), 0
    positions = [(i, j) for i in range(1, n - 1) for j in range(i + 1, n - 1)]
    rng.shuffle(positions)
    rejets = 0
    for i, j in positions:
        candidat = circuit[:]
        candidat[i], candidat[j] = candidat[j], candidat[i]
        valide, _ = verifier_circuit(candidat, matrice)
        if valide:
            return candidat, tuple(sorted((circuit[i], circuit[j]))), rejets
        rejets += 1
    return None, None, rejets
def recuit_simule(matrice, circuit_initial, t0=T0, pas=PAS, nb_iter=NB_ITERATIONS,
                  r=R_FIXE, graine=GRAINE, echanges_imposes=ECHANGES_IMPOSES):
    valide, message = verifier_circuit(circuit_initial, matrice)
    if not valide:
        return {"erreur": f"Le circuit initial n'est pas réalisable : {message}."}
    t_derniere = t0 - pas * (nb_iter - 1)
    if t_derniere <= 0:
        return {"erreur": f"La température deviendrait nulle ou négative ({t_derniere}) "
                          f"à l'itération {nb_iter} : réduire le pas ou le nombre d'itérations."}
    if echanges_imposes is not None and len(echanges_imposes) < nb_iter:
        return {"erreur": "La liste ECHANGES_IMPOSES doit contenir un échange par itération."}

    rng = random.Random(graine)

    # --- Initialisation ---
    courant = circuit_initial[:]
    cout_courant = calculer_cout(courant, matrice)
    meilleur, cout_meilleur = courant[:], cout_courant
    lignes = []
    T = t0
    for k in range(1, nb_iter + 1):
        impose = echanges_imposes[k - 1] if echanges_imposes else None
        try:
            candidat, echange, rejets = generer_voisin(courant, matrice, rng, impose)
        except ValueError as erreur:                        # échange imposé irréalisable
            return {"erreur": f"Itération {k} : {erreur}", "lignes": lignes,
                    "circuit_initial": circuit_initial[:],
                    "cout_initial": calculer_cout(circuit_initial, matrice)}
        if candidat is None:
            return {"erreur": f"Itération {k} : aucun voisin réalisable (toutes les liaisons "
                              f"possibles sont interdites). Arrêt après {k - 1} itération(s).",
                    "lignes": lignes}

        cout_candidat = calculer_cout(candidat, matrice)
        delta = cout_candidat - cout_courant                # ΔC = C_candidat - C_courant

        if delta <= 0:                                      # cas 1 : amélioration ou égalité
            proba, accepte = None, True
        else:                                               # cas 2 : candidat moins bon
            proba = math.exp(-delta / T)                    # P = exp(-ΔC / T)
            accepte = r < proba                             # accepté si r < P

        if accepte:                                         # le candidat devient la solution courante
            courant, cout_courant = candidat, cout_candidat
            if cout_courant < cout_meilleur:                # mise à jour de la meilleure solution
                meilleur, cout_meilleur = courant[:], cout_courant

        lignes.append({"it": k, "T": T, "echange": echange, "rejets": rejets,
                       "candidat": candidat, "cout_candidat": cout_candidat,
                       "delta": delta, "proba": proba, "r": r, "accepte": accepte,
                       "courant": courant[:], "cout_courant": cout_courant,
                       "cout_meilleur": cout_meilleur})
        T -= pas                                            # T(k+1) = T(k) - 2

    return {"circuit_initial": circuit_initial[:],
            "cout_initial": calculer_cout(circuit_initial, matrice),
            "lignes": lignes, "meilleur": meilleur, "cout_meilleur": cout_meilleur}
def afficher_matrice(matrice):
    n = len(matrice)
    print("Matrice des coûts (— = liaison interdite) :")
    print("      " + "".join(f"{'V' + str(j + 1):>5}" for j in range(n)))
    for i in range(n):
        cases = "".join(f"{'—' if v is None else v:>5}" for v in matrice[i])
        print(f"  V{i + 1}  {cases}")
def afficher_resultats(res):
    if "erreur" in res:
        print("\n!!! " + res["erreur"])
        if not res.get("lignes"):
            return
    lignes = res["lignes"]
    if "circuit_initial" in res:
        print(f"\nCircuit initial : {texte_circuit(res['circuit_initial'])}  "
              f"(coût = {res['cout_initial']})")

    for l in lignes:
        print(f"\n--- Itération {l['it']} ---")
        print(f"Température T          : {l['T']}")
        print(f"Échange de villes      : {l['echange'][0]}↔{l['echange'][1]}"
              f"  ({l['rejets']} candidat(s) irréalisable(s) rejeté(s) avant)")
        print(f"Chemin candidat        : {texte_circuit(l['candidat'])}")
        print(f"Coût du candidat       : {l['cout_candidat']}")
        print(f"ΔC                     : {l['delta']:+d}")
        if l["proba"] is None:
            print("Probabilité P          : non nécessaire (ΔC <= 0)")
        else:
            print(f"Probabilité P          : exp(-{l['delta']}/{l['T']}) = {l['proba']:.4f}")
        print(f"Valeur r               : {l['r']}")
        if l["proba"] is None:
            decision = "ACCEPTÉ (ΔC <= 0)"
        elif l["accepte"]:
            decision = f"ACCEPTÉ (r = {l['r']} < P = {l['proba']:.4f})"
        else:
            decision = f"REJETÉ (r = {l['r']} >= P = {l['proba']:.4f})"
        print(f"Décision               : {decision}")
        print(f"Chemin courant après   : {texte_circuit(l['courant'])} (coût {l['cout_courant']})")
        print(f"Meilleur coût trouvé   : {l['cout_meilleur']}")

    # --- Tableau récapitulatif (facile à copier dans un rapport) ---
    print("\n=== TABLEAU RÉCAPITULATIF ===")
    entete = (f"{'Itér.':<6}{'T':<4}{'Chemin candidat':<20}{'Coût':<6}{'ΔC':<5}"
              f"{'P':<8}{'r':<5}{'Décision':<10}{'Chemin courant':<20}{'Coût courant':<14}"
              f"{'Meilleur':<9}")
    print(entete)
    print("-" * len(entete))
    print(f"{'0':<6}{'-':<4}{'-':<20}{'-':<6}{'-':<5}{'-':<8}{'-':<5}{'-':<10}"
          f"{texte_circuit(res['circuit_initial']):<20}{res['cout_initial']:<14}"
          f"{res['cout_initial']:<9}")
    for l in lignes:
        p = "-" if l["proba"] is None else f"{l['proba']:.3f}"
        print(f"{l['it']:<6}{l['T']:<4}{texte_circuit(l['candidat']):<20}{l['cout_candidat']:<6}"
              f"{l['delta']:<+5d}{p:<8}{l['r']:<5}{'Accepté' if l['accepte'] else 'Rejeté':<10}"
              f"{texte_circuit(l['courant']):<20}{l['cout_courant']:<14}{l['cout_meilleur']:<9}")

    # --- Résultat final ---
    if "meilleur" in res:
        print("\n=== RÉSULTAT FINAL ===")
        print(f"Meilleur circuit obtenu : {texte_circuit(res['meilleur'])}")
        print(f"Coût total              : {res['cout_meilleur']}")
if __name__ == "__main__":
    afficher_matrice(MATRICE)
    for avertissement in verifier_matrice(MATRICE):
        print("Attention :", avertissement)

    print(f"\nParamètres : T0 = {T0}, pas = -{PAS}, {NB_ITERATIONS} itérations, "
          f"r = {R_FIXE}, graine = {GRAINE}")
    print(f"Températures : {[T0 - PAS * k for k in range(NB_ITERATIONS)]}")

    resultats = recuit_simule(MATRICE, CIRCUIT_INITIAL)
    afficher_resultats(resultats)