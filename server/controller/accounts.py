import fnmatch

def list_accounts(users_dict: dict, wildcard: str = "*"):
    """
    Lists all accounts in the accounts dictionary.
    """
    accounts = [user.username for user in users_dict.values() if user.active]
    if wildcard:
        print("Wildcard:", wildcard, "Accounts:", accounts)
        accounts = fnmatch.filter(accounts, wildcard)
    return accounts

def delete_account(users_dict: dict, uid: str):
    """
    Marks a user as inactive in the accounts dictionary.
    """

    print("Setting user as inactive in users_dict", uid)
    # Set user as inactive in users_dict
    users_dict[uid].active = False
    return True # success