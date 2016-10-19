__author__ = 'Jason'
import base64,random,string

# generate a random password for encrypt the sql statement.
g_pswd =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

def encode(clear):
    global g_pswd
    key = g_pswd
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(enc):
    global g_pswd
    key = g_pswd
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


