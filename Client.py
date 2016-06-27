import base64
import string
import random

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


def deobfuscate(cipher, key):

    cipher = base64.b64decode(cipher)
    cipher = cipher.decode('ascii')

    new_plain_text = []

    for plain_let, key_let in zip(cipher, key):
        new_let_num = ord(plain_let)-ord(key_let)

        if new_let_num < 0:
            new_let = chr(new_let_num+128)
        else:
            new_let = chr(new_let_num)

        if new_let == chr(0):
            break

        new_plain_text.append(new_let)

    return "".join(new_plain_text)


def print_with_key(msg, key):
    print(obfuscate(msg, key))
    print(key)


def generate_key():
        to_choose_from = string.ascii_letters+string.digits
        key = []
        for i in range(64):
            key.append(random.choice(to_choose_from))

        return "".join(key)


while True:
    action = input("Do you want to send (s) or receive (r) a message? ")

    if action == "s" or action == "send":
        msg_key = generate_key()
        name = input("What is your name? ")
        person1 = input("Who do you want to vote for/who is the first person you want to do your action to? (leave "
                        "blank if N/A) ")

        if person1 == "":
            print_with_key(name, msg_key)
        else:
            person2 = input("Who is the second person you want to do your action to? (leave blank if N/A) ")

            if person2 == "":
                print_with_key(name +"," + person1, msg_key)
            else:
                print_with_key(name +"," + person1 +"," + person2, msg_key)

    elif action == "r" or action == "receive":
        cipher_text = input("Enter obfuscated message: ")
        msg_key = input("Enter key: ")
        print(deobfuscate(cipher_text, msg_key))

    else:
        print("Invalid action!")
