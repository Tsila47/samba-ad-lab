# Samba AD DC Lab — Mini-projet personnel

![CI](https://github.com/Tsila47/samba-ad-lab/actions/workflows/ci.yml/badge.svg)

Mise en place d'un **Active Directory Domain Controller** complet avec Samba 4 sur Linux, accompagné d'outils d'administration Bash et d'une CLI Python via LDAP.

---

## Architecture du lab

```
┌─────────────────────────────────┐
│         dc01.lab.local          │
│         192.168.56.101          │
│                                 │
│  OS  : Debian/Ubuntu            │
│  Rôle: Samba AD DC              │
│  DNS : Samba internal DNS       │
│  KRB5: Kerberos (LAB.LOCAL)     │
└─────────────────────────────────┘
         Domaine : LAB.LOCAL
```

---

## Bilan complet du projet (Phase 9 Linux validée !)

| Phase | Description | Statut |
|-------|-------------|--------|
| 0 | Préparation VM | ✅ |
| 1 | Installation Samba | ✅ |
| 2 | Provisioning du domaine LAB.LOCAL | ✅ |
| 3 | DNS + Kerberos | ✅ |
| 4 | Service opérationnel | ✅ |
| 5 | Users/groupes/OUs manuels | ✅ |
| 6 | Scripts Bash CSV-driven | ✅ |
| 7 | CLI Python LDAP + StartTLS | ✅ |
| 8 | Backup + rotation automatique | ✅ |
| 9a | Jonction Ubuntu Desktop (realm join + sssd) | ✅ |
| 9b | Jonction Windows 10/11 | 🔜 dès que l'ISO est prête |

---

## Structure du dépôt

```
samba-scripts/
├── README.md
├── users.csv              # Données utilisateurs
├── groups.csv             # Données groupes
├── ous.csv                # Données OUs
├── create_users.sh        # Création d'users en masse
├── create_groups.sh       # Création de groupes en masse
├── create_ous.sh          # Création d'OUs en masse
├── backup_samba.sh        # Backup + rotation automatique
└── cli/
    ├── ad_cli.py          # CLI principale
    ├── ldap_conn.py       # Connexion LDAP (StartTLS)
    └── config.py          # Configuration (URI, DN, OUs)
```

---

## Prérequis

- Debian 12 / Ubuntu 22.04+
- Samba 4.x (`samba-ad-dc`, `samba-tool`)
- Python 3 + `python-ldap` (`sudo apt install python3-ldap`)
- Kerberos (`krb5-user`)

---

## Scripts Bash

### Création en masse depuis CSV

```bash
sudo ./create_ous.sh ous.csv
sudo ./create_users.sh users.csv
sudo ./create_groups.sh groups.csv
```

Format `users.csv` (séparateur `,`) :

```
username,password,firstname,lastname,email,ou
alice,Passw0rd!,Alice,Dupont,alice@lab.local,OU=Users,OU=LAB
```

Format `groups.csv` (séparateur `|`) :

```
groupname|ou|description|members
Admins-LAB|OU=Groups,OU=LAB|Admins du LAB|alice:charlie
```

---

## CLI Python (`cli/ad_cli.py`)

Connexion via LDAP + StartTLS (port 389), authentification UPN.

### Configuration

Édite `cli/config.py` :

```python
LDAP_URI  = "ldap://127.0.0.1"
BIND_DN   = "Administrator@lab.local"
BIND_PASS = "TonMotDePasse"
```

### Commandes disponibles

```bash
# Utilisateurs
python3 ad_cli.py list-users
python3 ad_cli.py create-user --username bob --firstname Bob --lastname Martin --email bob@lab.local
python3 ad_cli.py delete-user --username bob

# Groupes
python3 ad_cli.py list-groups
python3 ad_cli.py list-members --group Dev-LAB
python3 ad_cli.py add-to-group --username alice --group Dev-LAB
```

---

## Backup

```bash
sudo ./backup_samba.sh
```

- Backup complet via `samba-tool domain backup online`
- Stocké dans `/opt/samba-backups/` au format `.tar.bz2`
- Rotation automatique (5 derniers backups conservés)
- Log dans `/var/log/samba-backup.log`
- Planifiable via cron (`0 2 * * *`)

---

## Vérifications rapides

```bash
# Kerberos
kinit Administrator@LAB.LOCAL && klist

# Partages SYSVOL/NETLOGON
smbclient -L //dc01.lab.local -N

# DNS
host -t SRV _ldap._tcp.lab.local

# Users dans l'AD
sudo samba-tool user list
```

---

## Phase 9 — Jonction de clients

- **Ubuntu Desktop** — jonction via `realm join` + `sssd` (✅ Validée)
- **Windows 10/11** — jonction via Paramètres système (🔜 En attente d'ISO)

---

## Ressources

- [Wiki Samba AD DC](https://wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller)
- [python-ldap docs](https://python-ldap.org/)
