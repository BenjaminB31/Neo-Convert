import os
from collections import defaultdict
import re

# Fonction pour extraire les noms de VLAN
def extract_vlan_names(config):
    vlan_names = {}
    lines = config.splitlines()
    current_vlan = None

    for line in lines:
        words = line.split()
        if len(words) > 1:
            if words[0] == 'vlan':
                current_vlan = words[1]
            elif words[0] == 'name' and current_vlan:
                vlan_names[current_vlan] = words[1][1:-1]  # Exclure les guillemets

    return vlan_names

# Chemin du fichier actuel
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'vlan.txt')

# Lecture du contenu du fichier
with open(file_path, 'r') as file:
    text = file.read()

# Utilisation de la fonction pour extraire les noms de VLAN
vlan_names = extract_vlan_names(text)

# Dictionnaire pour stocker les VLAN par interface
vlan_table = defaultdict(list)

# Pattern pour identifier les interfaces et les VLAN
interface_pattern = re.compile(r'interface (Te\d+/\d+/\d+|port-channel \d+)')
vlan_pattern = re.compile(r'switchport trunk allowed vlan (\S+)')
access_vlan_pattern = re.compile(r'switchport access vlan (\d+)')

current_interface = None

# Parcours du texte ligne par ligne
for line in text.splitlines():
    interface_match = interface_pattern.match(line)
    vlan_match = vlan_pattern.match(line)
    access_vlan_match = access_vlan_pattern.match(line)
    
    if interface_match:
        current_interface = interface_match.group(1)
    elif vlan_match and current_interface:
        vlans = vlan_match.group(1).split(',')
        vlan_table[current_interface].extend(vlans)
    elif access_vlan_match and current_interface:
        vlan = access_vlan_match.group(1)
        vlan_table[current_interface].append((vlan, 'access'))

# Création d'un dictionnaire inversé pour les VLAN
vlan_interfaces = defaultdict(list)
for interface, vlans in vlan_table.items():
    for vlan_info in vlans:
        if isinstance(vlan_info, tuple):
            vlan, mode = vlan_info
            if mode == 'access':
                vlan_interfaces[vlan].append((interface.replace('Te1/', ''), 'untagged'))
        else:
            if '-' in vlan_info:
                start, end = map(int, vlan_info.split('-'))
                for v in range(start, end + 1):
                    vlan_interfaces[str(v)].append((interface.replace('Te1/', ''), 'tagged'))
            else:
                vlan_interfaces[vlan_info].append((interface.replace('Te1/', ''), 'tagged'))

# Écriture dans un fichier
output_file_path = os.path.join(current_directory, 'result.txt')
with open(output_file_path, 'w') as output_file:
    for vlan, interfaces in sorted(vlan_interfaces.items(), key=lambda x: int(x[0])):
        output_file.write(f"Interface Vlan {vlan}\n")
        vlan_name = vlan_names.get(vlan)
        if vlan_name:
            output_file.write(f"  Name \"{vlan_name}\"\n")
        for interface, mode in interfaces:
            if mode == 'tagged':
                if "port-channel" in interface:
                    output_file.write(f"  Tagged {interface}\n")
                else:
                    output_file.write(f"  Tagged TenGigabitEthernet {interface}\n")
            else:
                output_file.write(f"  Untagged TenGigabitEthernet {interface}\n")
        
        output_file.write('\n')  # Ajout d'une ligne vide après chaque VLAN

    print(f"Les résultats ont été écrits dans {output_file_path}")
