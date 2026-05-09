#!/bin/bash
# Usage: sudo ./create_ous.sh ous.csv

CSV_FILE="${1:-ous.csv}"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "Fichier introuvable : $CSV_FILE"
    exit 1
fi

tail -n +2 "$CSV_FILE" | while IFS=',' read -r ou_dn; do
    echo "Création de l'OU : $ou_dn"
    samba-tool ou create "$ou_dn" 2>&1
    echo "---"
done
