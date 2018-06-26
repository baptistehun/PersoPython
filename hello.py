def mini(tableau):
    """
    :param tableau: liste
    :return: le minimum
    """
    min = tableau[0]
    for i in range(len(tableau)):
        if min > tableau[i]:
            min = tableau[i]
    return min


def maxi(tableau):
    """
    :param tableau: liste
    :return: le maximum
    """
    max = tableau[0]
    for i in range(len(tableau)):
        if max < tableau[i]:
            max = tableau[i]
    return max


def somme(tableau):
    """
    :param tableau: liste
    :return: la somme de la liste
    """
    sommeloc = 0
    for i in range(len(tableau)):
        sommeloc += tableau[i]
    return sommeloc


def average(tableau):
    """
    :param tableau: liste
    :return: la valeur moyenne de la liste
    """
    averageloc = somme(tableau) / len(tableau)
    return averageloc


def isPrime(n):
    """
    :param n: entier
    :return: Boolean, True for prime number, False for !prime number
    """
    b = True
    if n < 2:
        b = False
    else:
        for i in range(2, n):
            if n % i == 0:
                b = False
    return b


def getPrimeNumber(tableau):
    """
    :param tableau: liste d'entier
    :return: liste des entier premiers
    """
    tableauLoc = []
    for i in range(len(tableau)):
        if isPrime(tableau[i]):
            tableauLoc.append(tableau[i])
    return tableauLoc


def factorielle(n):
    """
    :param n: entier
    :return: la factorielle de n
    """
    if n < 2:
        return 1
    else:
        n = n * factorielle(n - 1)
    return n


def inverse(tableau):
    """
    :param tableau: liste
    :return: une nouvelle liste inverse de celle d'entrée
    """
    tableauloc = []
    n = len(tableau) - 1
    for i in range(n+1):
        tableauloc.append(tableau[n-i])
    return tableauloc


def inverse2(tableau):
    """
    :param tableau: liste
    :return: la liste d'entrée inversée
    """
    n = len(tableau) - 1
    for i in range(n+1):
        tableau.append(tableau[n-i])
    for i in range(n+1):
        tableau.remove(tableau[0])
    return tableau

if __name__ == '__main__':
    table = [1, 2, 3, 5, 7, 8, 9, 11, 5]
    print(somme(table))
    print(getPrimeNumber(table))
    print(inverse(table))
    print(table)
    print(inverse2(table))
    print(table)
