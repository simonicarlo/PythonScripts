import whois


def is_domain_available(domain):
    try:
        whois.whois(domain)
        return False
    except:
        return True

def get_available_domains(domains):
    available = []
    for domain in domains:
        if is_domain_available(domain):
            available.append(domain)
    return available


def get_domain_info(domain):
    try:
        get_info = whois.whois(domain)
        print(f"{domain} is Registered")
        print(get_info)
    except:
        print(f"{domain} is Available")


def get_combs(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in get_combs(a[1:]):
        cs += [c, c + [a[0]]]
    return cs


def get_permuts(lst):
    if len(lst) == 0:
        return []
    if len(lst) == 1:
        return [lst]
    l = []

    for i in range(len(lst)):
        m = lst[i]
        remLst = lst[:i] + lst[i + 1:]

        for p in get_permuts(remLst):
            l.append([m] + p)

    return l


def make_domains(words, extensions):
    domains = []
    permutations = []

    combinations = get_combs(words)
    for comb in combinations:
        permutations += get_permuts(comb)

    for permutationList in permutations:
        permutation = ""
        for perm in permutationList:
            permutation += perm
        for extension in extensions:
            domains.append(permutation + extension)
    return domains

def availabilityTest(words, extensions):

    while (True):
        consoleInput = input("Would you like to get console input for the domains? ['y' 'n']: ")
        if (consoleInput == 'y'):
            words = list((map(str.strip, input("Please enter the words your domain should contain separated by a comma: ").split(','))))
            extensions = list((map(str.strip, input(
                "Please enter the extensions your domain can have separated by a comma and led by a dot: ").split(','))))
            break
        elif (consoleInput == 'n'):
            break
        else:
            print("Please enter either 'y' for 'yes' or 'n' for 'no' !")

    # Creating the domains

    domains = make_domains(words, extensions)

    print(f"Testing the following domains: {domains} \n")

    # Testing the domains

    availableDomains = get_available_domains(domains)
    unavailableDomains = [x for x in domains if x not in availableDomains]

    if (len(availableDomains) == 0):
        print("None of the tested domains appear to be available")
    else:
        print("The following domains are potentially available:")
        for domain in availableDomains:
            print(domain)

    while (True):
        printUnavailable = input("\nWould you like to print the unavailable domains aswell? [y / n]: ")

        if (printUnavailable == 'y'):
            print("\nThe following domains appear to be unavailable:")
            for domain in unavailableDomains:
                print(domain)
            break
        elif (printUnavailable == 'n'):
            break
        else:
            print("Please enter either 'y' for 'yes' or 'n' for 'no' !")

def ownerTest(domain):

    if (domain != ""):
        get_domain_info(domain)
    else:
        domain = input("Which domain would you like to test: ")
        get_domain_info(domain)

    while (True):
        again = input("\nWould you like to test another domain? [y / n]: ")

        if (again == 'y'):
            domain = input("\nWhich domain would you like to test: ")
            get_domain_info(domain)
        elif (again == 'n'):
            break
        else:
            print("Please enter either 'y' for 'yes' or 'n' for 'no' !")


def main():

    print("\n--- WELCOME TO THE DOMAIN TESTING TOOL --- \n")

    # Specifying the domains

    domain = ""
    words = ['ai', 'safety']
    extensions = ['.com', '.ch']


    # Select Mode

    while(True):
        print("What would you like to do?")
        print("If you would like to see who owns a certain domain enter '1'.")
        print("If you would like to check if certain domains are available enter '2'.")
        option = input("Input: ")

        if((option == 1) or (option == '1')):
            ownerTest(domain)
            break
        elif((option == 2) or (option == '2')):
            availabilityTest(words, extensions)
            break
        else:
            print("Please enter a valid option!")


    print("\n \n --- GOODBYE ---")





if __name__ == '__main__':
    main()