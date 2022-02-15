import os
import platform

print('in getscrpath')

def get_scrpath():
    home_dir = os.environ.get("HOME").split('/')[:3]
    user_home = '{0}/{1}/{2}/'.format(homedir[0], homedir[1], homedir[2])

    if platform.system() == 'Darwin':
        return os.path.join(user_home,
                            'OneDrive/scripts3/maya/hh_autorig/')
    elif platform.system() == 'Windows':
        return os.path.join(user_home, 'OneDrive/scripts3/maya/hh_autorig/').replace('/', '\\')
