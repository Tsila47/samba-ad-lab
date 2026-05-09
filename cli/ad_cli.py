#!/usr/bin/env python3
"""CLI de gestion Samba AD - python-ldap"""

import argparse
import ldap
import ldap.modlist as modlist
from ldap_conn import get_connection
from config import LDAP_BASE, OU_USERS, OU_GROUPS

def list_users(args):
    conn = get_connection()
    results = conn.search_s(OU_USERS, ldap.SCOPE_SUBTREE,
        "(objectClass=user)", ["cn", "mail", "sAMAccountName"])
    print(f"\n{'Username':<20} {'Nom complet':<30} {'Email'}")
    print("-" * 65)
    for dn, attrs in results:
        sam  = attrs.get("sAMAccountName", [b""])[0].decode()
        cn   = attrs.get("cn",             [b""])[0].decode()
        mail = attrs.get("mail",           [b"N/A"])[0].decode()
        print(f"{sam:<20} {cn:<30} {mail}")
    conn.unbind_s()

def create_user(args):
    conn = get_connection()
    dn = f"CN={args.firstname} {args.lastname},{OU_USERS}"
    attrs = {
        "objectClass":       [b"top", b"person", b"organizationalPerson", b"user"],
        "cn":                [f"{args.firstname} {args.lastname}".encode()],
        "sAMAccountName":    [args.username.encode()],
        "givenName":         [args.firstname.encode()],
        "sn":                [args.lastname.encode()],
        "userPrincipalName": [f"{args.username}@lab.local".encode()],
    }
    if args.email:
        attrs["mail"] = [args.email.encode()]
    try:
        conn.add_s(dn, modlist.addModlist(attrs))
        print(f"OK : utilisateur '{args.username}' créé.")
    except ldap.ALREADY_EXISTS:
        print(f"ERREUR : '{args.username}' existe déjà.")
    except Exception as e:
        print(f"ERREUR : {e}")
    conn.unbind_s()

def delete_user(args):
    conn = get_connection()
    results = conn.search_s(OU_USERS, ldap.SCOPE_SUBTREE,
        f"(sAMAccountName={args.username})", ["dn"])
    if not results:
        print(f"ERREUR : '{args.username}' introuvable.")
        conn.unbind_s()
        return
    conn.delete_s(results[0][0])
    print(f"OK : utilisateur '{args.username}' supprimé.")
    conn.unbind_s()

def list_groups(args):
    conn = get_connection()
    results = conn.search_s(OU_GROUPS, ldap.SCOPE_SUBTREE,
        "(objectClass=group)", ["cn", "description"])
    print(f"\n{'Groupe':<25} {'Description'}")
    print("-" * 55)
    for dn, attrs in results:
        cn   = attrs.get("cn",          [b""])[0].decode()
        desc = attrs.get("description", [b"N/A"])[0].decode()
        print(f"{cn:<25} {desc}")
    conn.unbind_s()

def list_members(args):
    conn = get_connection()
    results = conn.search_s(OU_GROUPS, ldap.SCOPE_SUBTREE,
        f"(cn={args.group})", ["member"])
    if not results:
        print(f"ERREUR : groupe '{args.group}' introuvable.")
        conn.unbind_s()
        return
    members = results[0][1].get("member", [])
    print(f"\nMembres de '{args.group}' ({len(members)}) :")
    print("-" * 40)
    for m in members:
        dn_str = m.decode()
        cn = dn_str.split(",")[0].replace("CN=", "")
        print(f"  - {cn}")
    conn.unbind_s()

def add_to_group(args):
    conn = get_connection()
    u = conn.search_s(OU_USERS, ldap.SCOPE_SUBTREE,
        f"(sAMAccountName={args.username})", ["dn"])
    if not u:
        print(f"ERREUR : utilisateur '{args.username}' introuvable.")
        conn.unbind_s()
        return
    g = conn.search_s(OU_GROUPS, ldap.SCOPE_SUBTREE,
        f"(cn={args.group})", ["dn"])
    if not g:
        print(f"ERREUR : groupe '{args.group}' introuvable.")
        conn.unbind_s()
        return
    try:
        conn.modify_s(g[0][0], [(ldap.MOD_ADD, "member", [u[0][0].encode()])])
        print(f"OK : '{args.username}' ajouté dans '{args.group}'.")
    except ldap.TYPE_OR_VALUE_EXISTS:
        print(f"INFO : '{args.username}' est déjà membre de '{args.group}'.")
    except Exception as e:
        print(f"ERREUR : {e}")
    conn.unbind_s()

def main():
    parser = argparse.ArgumentParser(description="CLI de gestion Samba AD")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-users",  help="Lister les utilisateurs")
    sub.add_parser("list-groups", help="Lister les groupes")

    p_cu = sub.add_parser("create-user", help="Créer un utilisateur")
    p_cu.add_argument("--username",  required=True)
    p_cu.add_argument("--firstname", required=True)
    p_cu.add_argument("--lastname",  required=True)
    p_cu.add_argument("--email",     default=None)

    p_du = sub.add_parser("delete-user", help="Supprimer un utilisateur")
    p_du.add_argument("--username", required=True)

    p_lm = sub.add_parser("list-members", help="Lister les membres d'un groupe")
    p_lm.add_argument("--group", required=True)

    p_ag = sub.add_parser("add-to-group", help="Ajouter un user dans un groupe")
    p_ag.add_argument("--username", required=True)
    p_ag.add_argument("--group",    required=True)

    args = parser.parse_args()
    {
        "list-users":   list_users,
        "list-groups":  list_groups,
        "create-user":  create_user,
        "delete-user":  delete_user,
        "list-members": list_members,
        "add-to-group": add_to_group,
    }[args.command](args)

if __name__ == "__main__":
    main()
