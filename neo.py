import os
from collections import defaultdict
import re

# Chemin du fichier actuel
current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'vlan.txt')

# Lecture du contenu du fichier
with open(file_path, 'r') as file:
    text = file.read()

# Dictionnaire pour stocker les VLAN par interface
vlan_table = defaultdict(list)

# Pattern pour identifier les interfaces et les VLAN
interface_pattern = re.compile(r'interface (Te\d+/\d+/\d+|port-channel \d+)')
vlan_pattern = re.compile(r'switchport trunk allowed vlan (\S+)')

current_interface = None

# Parcours du texte ligne par ligne
for line in text.splitlines():
    interface_match = interface_pattern.match(line)
    vlan_match = vlan_pattern.match(line)
    
    if interface_match:
        current_interface = interface_match.group(1)
    elif vlan_match and current_interface:
        vlans = vlan_match.group(1).split(',')
        vlan_table[current_interface].extend(vlans)

# Création d'un dictionnaire inversé pour les VLAN
vlan_interfaces = defaultdict(list)
for interface, vlans in vlan_table.items():
    for vlan in vlans:
        if '-' in vlan:
            start, end = map(int, vlan.split('-'))
            for v in range(start, end + 1):
                vlan_interfaces[str(v)].append(interface.replace('Te1/', ''))
        else:
            vlan_interfaces[vlan].append(interface.replace('Te1/', ''))

# Écriture dans un fichier
output_file_path = os.path.join(current_directory, 'result.txt')
with open(output_file_path, 'w') as output_file:
    for vlan, interfaces in sorted(vlan_interfaces.items(), key=lambda x: int(x[0])):
        output_file.write(f"Interface Vlan {vlan}\n")
        for interface in interfaces:
            if "port-channel" in interface:
                output_file.write(f"  Tagged {interface}\n")
            else:
                output_file.write(f"  Tagged TenGigabitEthernet {interface}\n")
        output_file.write('\n')  # Ajout d'une ligne vide après chaque VLAN

    print(f"Les résultats ont été écrits dans {output_file_path}")
