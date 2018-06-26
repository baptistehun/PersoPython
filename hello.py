def mini(tableau):
    mini = tableau[0]
    for i in range(len(tableau)):
        if mini > tableau[i]:
            mini = tableau[i]
    return mini

if __name__ == '__main__':
    print(mini([1, 2, 3, 4, 5, 6, 7, 8, 9]))
