import string
import itertools
import random
class ManagerPassword:
    results = {
                'all_letters': string.ascii_letters, # All letters
                'upper_letters': string.ascii_uppercase, # Upper letters
                'lower_letters': string.ascii_lowercase, # Lower letters
                'digits': string.digits, # Digits
                'punctuation': string.punctuation, # Punctuation
                'printable': string.printable, # Printable
                'whitespace': string.whitespace, # Whitespace
            }


    @staticmethod
    def generate_pwd_list(dic, max_len):
        """
        description:Generate a password sequence of a specified length
        param {*} dic    Dictionary
        param {*} pwd_len    Maximum password length
        return {*} All possible passwords
        """
        k = itertools.product(dic, repeat=max_len)  # Iterator
        allkey = ("".join(i) for i in k)
        if max_len == 1:

            return list(allkey)
        return ManagerPassword.generate_pwd_list(dic, max_len - 1) + list(allkey)
    
    @staticmethod
    def random_pwd(pwd_len):
        """
        Randomly generate a password
        :param pwd_len: Password length
        :return: Random password
        """
        characters = ManagerPassword.results['all_letters'] + ManagerPassword.results['digits'] + ManagerPassword.results['punctuation']
        return ''.join(random.choice(characters) for _ in range(pwd_len))

    
