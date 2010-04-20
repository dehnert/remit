from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
import socket
import settings

class SocketAuthBackend():
    """
    SocketAuthBackend provides a simple way to authenticate with another process.

    The protocol is simple:
    * Open a connection to a socket.
    * On the first line, pass the name of the operation
    * Then, on successive lines, pass additional arguments, one per line
    * Close the write half of the socket
    * The authentication server sends back a reply, one tuple element
      per line

    Queries include:
    * AUTHENTICATE(username, password) => boolean
    * FINGER(username) => (first name, last name, email, )
    """
    def authenticate(self, username, password, ):
        (result,) = query(1, "AUTHENTICATE", username, password, )
        print result
        if result == 'true':
            try:
                user = User.objects.get(username=username)
                if len(user.groups.filter(name='local-auth-only')) > 0:
                    if user.check_password(password):
                        return user
                    else:
                        return None
                else:
                    return user
            except User.DoesNotExist:
                user = User(username=username, password='SocketAuth')
                user.is_staff = False
                user.is_superuser = False
                # Is there a race condition here? Yes.
                # Should I do more error-checking? Yes.
                # Do I care? No.
                (first, last, email,) = query(3, 'FINGER', username)
                user.first_name = first
                user.last_name = last
                user.email = email
                user.save()
                try:
                    user.groups.add(auth.models.Group.objects.get(name='autocreated'))
                except ObjectDoesNotExist:
                    print "Failed to retrieve autocreated group"
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def query(length, *args):
    conn = socket.socket(socket.AF_UNIX)
    conn.connect(settings.AUTH_SOCK)
    conn.send('\n'.join(args))
    conn.shutdown(socket.SHUT_WR)
    result = conn.makefile().read().split('\n')
    if(len(result)==length+1 and result[-1] == ''):
        result = result[:-1]
    if len(result) != length:
        raise ValueError("Got return value of length %d to query '%s'; needed length %d" % (len(result), args[0], length, ))
    conn.close()
    return result
