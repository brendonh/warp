import getpass

from warp.common import avatar
from warp.runtime import config, avatar_store

def _getPassword():
    password = getpass.getpass().strip()

    if not password:
        print "You must give a password."
        return _getPassword()

    password2 = getpass.getpass("Password again: ").strip()

    if password != password2:
        print "Password's didn't match"
        return _getPassword()

    return password


def addUser():
    email = raw_input("Email: ").decode("utf-8").strip()
    if not email:
        print "You must give an email address."
        return addUser()

    password = _getPassword().decode("utf-8")

    hasher = config.get('hashPassword')
    if hasher is not None:
        password = hasher(password)

    roleNames = raw_input("Roles (space-separated):").split()

    av = avatar.Avatar()
    av.email = email
    av.password = password

    avatar_store.add(av)

    for (position, roleName) in enumerate(roleNames):
        role = avatar.AvatarRole()
        role.avatar = av
        role.role_name = roleName
        role.position = position
        avatar_store.add(role)

    avatar_store.commit()

    
    
    
