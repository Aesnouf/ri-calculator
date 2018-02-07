# DISTRI BY THE POURCENTAGE RI EXPRESS

# NETTOYE

# TEST THE ORDER OF TREATMENT: sum of the correlation index


# cette fonction est déjà présente je crois...

def orthonormation_meth(v, cols):
    deleted = 0
    # normation of the first column
    v[cols[0]] = v[cols[0]] / np.linalg.norm(v[cols[0]])

    # j is a cursor that will pass every columns (category). The loop is stop by the total number of category in the method
    j = 0
    while j < v.shape[1]:
        # i is a cursor that will pass every columns from 0 to j (j not included)
        # f is a cursor that is equal to i if column norm is not equal to zero
        i = 0
        f = 0
        while i < j and i == f:

            # calcul of the orthogonal projection of j on each i and substraction of the projection from j
            v[cols[j]] = v[cols[j]] - v[cols[i]] * (
            float(sum(v[cols[i]] * v[cols[j]])) / float(sum(v[cols[i]] * v[cols[i]])))
            if (np.linalg.norm(v[cols[j]]) == 0):
                # if after the projection, the j columns became null, it is droped (i.e it is linearly dependant with
                # the other columns)
                v.drop(v.columns[j], inplace=True, axis=1)
                cols.remove(cols[j])
                i = i
                # then f become different of i and the while loop ends
                f += 1
                deleted += 1
            else:
                # the non null columns j is normed and the second while loop keeps going
                v[cols[j]] = v[cols[j]] / (np.linalg.norm(v[cols[j]]))
                i += 1
                f += 1
        j += 1

    return (v, deleted)




# c'est le dataframe qui va être écrasé au fur et à mesure pour obtenir les RIs orthogonalisés
cos_2_final = np.square(cat_process_cosinus_default.loc[:, process].copy(deep=True))

# cat est la liste des catégories. elle doit être dispo dans un autre dataframe du package
cat = cat_process_cosinus_default.index

# process: liste de procedé à étudier un par un. ça correspond doit au nom 'LCIS' dans RI calculator

for process_to_study in process:

    # emission process est simplement le dataframe des flux elementaire dtandardisés
    emission_process = pd.DataFrame(emission_normed_normal_normed.loc[:, process_to_study])

    # et donc ici c'est une copie de toutes les catégories de toutes les méthodes
    meth_to_ortho = meth_normed_normal_normed.copy(deep=True)

    # meth_name_to_shart va correspondre à 'METHODS_NAMES' sauf que faire toutes les méthodes peut prendre un peu de temps...
    # La boucle sur les méthodes est peut être à mettre au dessus, avant la boucle sur les procédés... peut-être
    for methods in meth_name_to_shart:

        # extraction des catégories appartenant à la méthode étudiée
        to_extract = [s for s in cat if methods in s]

        # test_2 : matrice des correlation entre categories
        test = meth_normed_normal_normed.loc[:, to_extract].copy(deep=True)

        test_2 = pd.DataFrame(index=to_extract, columns=to_extract)

        for j in range(0, test_2.shape[0]):
            for i in range(0, j + 1):
                test_2.iloc[j, i] = abs(test.iloc[:, i] * test.iloc[:, j]).sum()
                test_2.iloc[i, j] = abs(test.iloc[:, i] * test.iloc[:, j]).sum()

        # Classement des catégories en fonction de leur corrélation. Celle qui est la plus corrélée avec les autres sera traitée en premier
        test_2 = test_2.loc[
            test_2.sum().sort_values(ascending=False).index, test_2.sum().sort_values(ascending=False).index].copy(
            deep=True)

        cat_ordered = test_2.index

        # test_33 va ordoner les catégories en fonction du nombre de catégorie avec lesquelle elle a des corrélations
        # test_4 est identique mais les catégories e sont pas ordonnées
        # ces lignes ne sont pas forcement interessante
        test_33 = test_2.copy(deep=True)
        test_33[test_33 != 0] = 1
        test_4 = test_33.copy(deep=True)
        test_33 = test_33.loc[
            test_33.sum().sort_values(ascending=False).index, test_33.sum().sort_values(ascending=False).index].copy(
            deep=True)

        # cat_ordered=test_33.index

        # meth_to_ortho va être écrasé à chaque boucle effectué sur les catégories ordonnées
        meth_to_ortho = meth_normed_normal_normed.loc[:, to_extract].copy(deep=True)

        # On calcul de nouveau le RI des catégories.... déjà fait dans RI calculator donc c'est à récupérer
        # dans un autre dataframe...

        threshold = 0
        (cos_2_origin, analysis, cos_above, cos_above_1, select, analysis_median) = similarity_cosinus(meth_to_ortho,
                                                                                                       emission_process,
                                                                                                       threshold)

        # C'est sur les carrés des RI que les sommes et soustraction sont valables
        cos_2_origin = np.square(cos_2_origin).copy(deep=True)

        # création d'un dataframe qui sera rempli au fur et à mesure avec les catégories orthogonalisées par rapport
        # à celles déjà présentes dans ce tableau
        cat_orthonormed = pd.DataFrame(meth_normed_normal_normed.loc[:, cat_ordered[0]])

        for i in range(0, len(to_extract) - 1):
            # Les 6 prochaines lignes de code sont peut être un peu sales...
            # du genre il y a de la redondance et des objets en double

            # on selectionne la catégorie à orthogonaliser grâce à cat_ordered
            meth_to_ortho = meth_to_ortho.loc[:, cat_ordered[i + 1:]]

            # On ajoute cette catégories à celle déjà orthogonalisé
            meth_to_ortho = pd.DataFrame.join(cat_orthonormed, meth_to_ortho, how='outer')

            # On orthonorme cette catégories en utilisant la fonction
            meth_orthonormed, cat_del = orthonormation_meth(meth_to_ortho, meth_to_ortho.columns)

            # On récupère la catégorie orthogonalisée actuellement en cours de traitement par la boucle
            meth_to_ortho = meth_orthonormed.loc[:, cat_ordered[i + 1:]]

            # On calcul le cosinus avec la fonction de calcul des RI par catégorie
            (cos_ortho, analysis, cos_above, cos_above_1, select, analysis_median) = similarity_cosinus(meth_to_ortho,
                                                                                                        emission_process,
                                                                                                        threshold)

            # On ajoute à cat_orthonormed la catégorie orthogonalisée actuellement en cours de traitement par la boucle
            cat_orthonormed = pd.DataFrame.join(cat_orthonormed,
                                                pd.DataFrame(meth_orthonormed.loc[:, cat_ordered[i + 1]]), how='outer')

            cos_ortho = np.square(cos_ortho)

            # On calcule la différence entre RI ortho et RI origine
            to_distribute = cos_ortho.loc[cat_ordered[i + 1], process_to_study] - cos_2_origin.loc[
                cat_ordered[i + 1], process_to_study]

            # extraction des catégories sur lesquelles la différence entre RI doit être partagée
            test_3 = np.square(test_2.loc[:, :].copy(deep=True))
            cat_to_update = test_3.loc[:, cat_ordered[i + 1]] != 0

            # On extrait les RI des catégories qui sont corrélées à la catégories en cours
            distri_factor = cos_2_origin.loc[cat_to_update, :].copy(deep=True)

            # On reparti la différence en fonction de la valeur des RI origine
            cos_2_final.loc[cat_to_update[cat_to_update].index, process_to_study] += to_distribute * (
            (distri_factor / ((distri_factor).sum(axis=0))).loc[cat_to_update, process_to_study])


            # cat_orthonormed_all_per_process[process.index(process_to_study)][1]=pd.DataFrame.join(cat_orthonormed_all_per_process[process.index(process_to_study)][1],cat_orthonormed,how='outer')

# On prend la racine carré des RIs orthogonalisés
cos_2_final = pd.DataFrame(np.sqrt(cos_2_final), index=cos_2_final.index, columns=cos_2_final.columns)
