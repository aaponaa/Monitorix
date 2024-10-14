import re
import pandas as pd

# Charger le texte depuis le fichier
with open('texts/test.txt', 'r', encoding='utf-8') as file:
    text = file.read()
    print("Loaded text from test.txt")

# Diviser le texte en blocs correspondant à chaque décision
blocks = re.findall(r'(Par ordonnance du.*?)(?=Par ordonnance du|$)', text, flags=re.DOTALL)

data = []

for block in blocks:
    block = block.strip()
    if not block:
        continue  # Ignorer les blocs vides

    # Supprimer les sauts de ligne et les espaces multiples pour faciliter la correspondance
    block_clean = ' '.join(block.split())

    # Extraire les informations de la personne protégée
    protected_person_pattern = re.compile(
        r'(?P<name>[A-Z][A-Za-z\'\- ]+),\s*(?:né|née)(?: à [^,]+)?,?\s*le\s*(?P<birth_date>\d{1,2} \w+ \d{4}),\s*(?:domicilié|domiciliée) à\s*(?P<address>.*?)(?:,?\s*et résidant|,?\s*personne à protéger|,?\s*personne protégée|,)',
        flags=re.IGNORECASE)
    protected_person_match = protected_person_pattern.search(block_clean)

    # Gérer le cas où l'adresse est inconnue
    if not protected_person_match:
        protected_person_pattern = re.compile(
            r'(?P<name>[A-Z][A-Za-z\'\- ]+),\s*(?:né|née)(?: à [^,]+)?,?\s*le\s*(?P<birth_date>\d{1,2} \w+ \d{4}),\s*adresse inconnue',
            flags=re.IGNORECASE)
        protected_person_match = protected_person_pattern.search(block_clean)
        if protected_person_match:
            protected_person_address = 'Adresse inconnue'
            protected_person_name = protected_person_match.group('name').strip()
            protected_person_dob = protected_person_match.group('birth_date').strip()
        else:
            print("Informations de la personne protégée non trouvées dans le bloc :")
            print(block, "\n---")
            continue
    else:
        protected_person_address = protected_person_match.group('address').strip()
        protected_person_name = protected_person_match.group('name').strip()
        protected_person_dob = protected_person_match.group('birth_date').strip()

    # Extraire les informations de l'administrateur
    administrator_pattern = re.compile(
        r'(?P<name>[A-Z][A-Za-z\'\- ]+),\s*(?:avocat[e]?|Avocat[e]?|AVOCAT[E]?)?,?\s*(?:dont le cabinet (?:est|est établi|est situé|sis) à )?\s*(?P<address>.*?)(?:,?\s*a été désigné[e]? en qualité d’administrateur)',
        flags=re.IGNORECASE)
    administrator_match = administrator_pattern.search(block_clean)

    if administrator_match:
        administrator_name = administrator_match.group('name').strip()
        administrator_address = administrator_match.group('address').strip()
    else:
        print("Informations de l'administrateur non trouvées dans le bloc :")
        print(block[:200], "\n---")
        continue

    # Ajouter les données extraites à la liste
    data.append({
        'Protected Person Name': protected_person_name,
        'Protected Person Date of Birth': protected_person_dob,
        'Protected Person Address': protected_person_address,
        'Administrator Name': administrator_name,
        'Administrator Address': administrator_address,
    })

# Créer un DataFrame à partir des données
df = pd.DataFrame(data)

# Afficher le DataFrame
print("\nDataFrame output:")
print(df.to_markdown(index=False))
