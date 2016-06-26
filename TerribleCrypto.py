import base64


def obfuscate(plain_text, key):
    if len(plain_text) <= len(key):
        plain_text += chr(0) * (len(key) - len(plain_text))
    else:
        print("Too short")
        raise KeyboardInterrupt

    new_cipher_text = []

    for plain_let, key_let in zip(plain_text, key):
        new_let_num = ord(plain_let)+ord(key_let)
        
        if new_let_num > 127:
            new_let = chr(new_let_num-128)
        else:
            new_let = chr(new_let_num)

        new_cipher_text.append(new_let)

    cipher = "".join(new_cipher_text)
    cipher = cipher.encode('ascii')

    cipher_b64 = base64.b64encode(cipher)
    return cipher_b64.decode('ascii')


def deobfuscate(plain_text, key):

    plain_text = base64.b64decode(plain_text)
    plain_text = plain_text.decode('ascii')

    new_plain_text = []

    for plain_let, key_let in zip(plain_text, key):
        new_let_num = ord(plain_let)-ord(key_let)
        
        if new_let_num < 0:
            new_let = chr(new_let_num+128)
        else:
            new_let = chr(new_let_num)
            
        if new_let == chr(0):
            break

        new_plain_text.append(new_let)

    return "".join(new_plain_text)
