#!/bin/bash
# Usage: sudo ./create_users.sh users.csv

CSV_FILE="${1:-users.csv}"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "Fichier introuvable : $CSV_FILE"
    exit 1
fi

# Ignore la première ligne (header)
tail -n +2 "$CSV_FILE" | while IFS=',' read -r username password firstname lastname email ou; do
    echo "Création de l'utilisateur : $username"
    samba-tool user create "$username" "$password" \
        --userou="$ou" \
        --given-name="$firstname" \
        --surname="$lastname" \
        --mail-address="$email" 2>&1

    if [[ $? -eq 0 ]]; then
        echo "  OK : $username créé"
    else
        echo "  ERREUR : $username non créé"
    fi
    echo "---"
done
