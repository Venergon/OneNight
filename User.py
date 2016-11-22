import cgi, cgitb, glob, os
import data_modification
from constants import *

class User:
    def __init__(self, zid, me, suspended = False):
        self.suspended = suspended
        self.me = me
        #Open the file with all the data
        with open("{}/{}/user.txt".format(DATA_DIRECTORY, zid), encoding="UTF-8") as f:
            text = f.read()
        #Get each of the fields of the user and store them
        fields = data_modification.string_to_dict(text)

        self.fields = fields

        self.load_from_dict(self.fields)

    def set_me(self, me):
        # If now logged in, set the value of me
        # Where 'me' is the person who's logged in
        self.me = me


    def load_from_dict(self, fields):
        #Need to do this for each item so that they are now part of the object
        self.zid = fields.get("zid", "")
        self.password = fields.get("password", "")
            

    def __str__(self):
        # Should never come up in actual running, just useful for debugging
        return "[User {} (zid {})]".format(self.name, self.zid)


    def add_token(self, token):
        # Add in the token that the logged in person has
        self.token = token

    def __eq__(self, other):
        # Since usernames are unique, this should be the only thing that's needed to check
        # As well, if we are changing some details about the user we still want the old and new version 
        # To be considered the same person
        return type(other) == User and self.zid == other.zid

    # Save the data to the profile file
    def save(self):
        to_save = []
        to_save.append("zid="+self.zid)
        to_save.append("password="+self.password)
        with open("{}/{}/user.txt".format(DATA_DIRECTORY, self.zid), "w", encoding="UTF-8") as f:
            f.write("\n".join(to_save))

