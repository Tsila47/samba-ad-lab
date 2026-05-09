#!/bin/bash
# Usage: sudo ./create_groups.sh groups.csv

CSV_FILE="${1:-groups.csv}"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "Fichier introuvable : $CSV_FILE"
    exit 1
fi

tail -n +2 "$CSV_FILE" | while IFS='|' read -r groupname ou description members; do
    echo "Création du groupe : $groupname"
    samba-tool group add "$groupname" \
        --groupou="$ou" \
        --description="$description" 2>&1

    if [[ $? -eq 0 ]]; then
        echo "  OK : groupe $groupname créé"
    else
        echo "  ERREUR ou groupe déjà existant : $groupname"
    fi

    if [[ -n "$members" ]]; then
        IFS=':' read -ra member_list <<< "$members"
        for member in "${member_list[@]}"; do
            echo "  Ajout de $member dans $groupname"
            samba-tool group addmembers "$groupname" "$member" 2>&1 | grep -v "already exists"
        done
    fi
    echo "---"
done
