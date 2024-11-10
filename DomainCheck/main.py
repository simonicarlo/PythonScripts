import whois
from itertools import combinations, permutations, product

# Function to check if a domain is available
def is_domain_available(domain):
    try:
        whois.whois(domain)
        return False
    except whois.parser.PywhoisError:
        return True
    except Exception as e:
        print(f"Error checking {domain}: {e}")
        return False

# Checks a list of domains and returns a list of available domains
def get_available_domains(domains):
    return [domain for domain in domains if is_domain_available(domain)]

# Function to generate all possible combinations of words
def get_combs(words):
    return [list(comb) for i in range(1, len(words) + 1) for comb in combinations(words, i)]

# Generates all possible combinations and permutaions of words and extensions
def generate_domain_names(words, extensions, separators=['-', '']):
    domains = []
    for comb in get_combs(words):
        for perm in permutations(comb):
            for sep in separators:
                domain_base = sep.join(perm)
                domains.extend([domain_base + ext for ext in extensions])
    # remove duplicates
    domains = list(set(domains))
    return domains

# Function to check domain availability
def check_domain_availability():
    words = [word.strip() for word in input("Enter domain words (comma-separated): ").split(',')]
    extensions = [ext.strip() for ext in input("Enter domain extensions (comma-separated, starting with dot): ").split(',')]
    domains = generate_domain_names(words, extensions)
    print(f"Testing domains: {domains}\n")

    available_domains = get_available_domains(domains)
    if available_domains:
        print("Available domains:")
        for domain in available_domains:
            print(domain)
        print(f'Total available domains: {len(available_domains)}\n')
        print("Unavailable domains:")
        for domain in set(domains) - set(available_domains):
            print(domain)
        print(f'Total unavailable domains: {len(set(domains) - set(available_domains))}\n')
    else:
        print("No available domains found.\n2")

# Function to check domain ownership
def check_domain_ownership():
    domain = input("Enter domain to check ownership: ").strip()
    try:
        domain_info = whois.whois(domain)
        print(f"{domain} is registered. Info:\n{domain_info}")
    except whois.parser.PywhoisError:
        print(f"{domain} is available.")
    except Exception as e:
        print(f"Error checking {domain}: {e}")

def main():

    print("\n--- WELCOME TO THE DOMAIN TESTING TOOL --- \n")

    # Select Mode
    while True:
        choice = input("Enter '1' for ownership check, '2' for availability check, or '0' to exit: ").strip()
        if choice == '1':
            check_domain_ownership()
        elif choice == '2':
            check_domain_availability()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")



if __name__ == '__main__':
    main()