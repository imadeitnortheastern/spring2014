import os, crypt

def create(name, password):
    enc_pass = crypt.crypt(password, "22")   
    return os.system('useradd -p {} -s /bin/bash -d /home/{} -m {}'.format(enc_pass, name, name))


