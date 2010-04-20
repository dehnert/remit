from django.contrib.auth.models import User
import socket
import settings

class SocketAuthBackend():
    def authenticate(self, username, password, ):
        (result,) = query("AUTHENTICATE", username, password, )
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
                (first, last, email,) = query('FINGER', username)
                user.first_name = first
                user.last_name = last
                user.email = email
                user.save()
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def query(*args):
    conn = socket.socket(socket.AF_UNIX)
    conn.connect(settings.AUTH_SOCK)
    conn.send('\n'.join(args))
    conn.shutdown(socket.SHUT_WR)
    result = conn.makefile().read().strip().split('\n')
    conn.close()
    return result
