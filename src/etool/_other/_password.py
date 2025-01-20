import string
import itertools
import random
class PasswordManager:
    results = {
                'all_letters': string.ascii_letters, # 所有字母
                'upper_letters': string.ascii_uppercase, # 大写字母
                'lower_letters': string.ascii_lowercase, # 小写字母
                'digits': string.digits, # 数字
                'punctuation': string.punctuation, # 标点符号
                'printable': string.printable, # 可打印字符
                'whitespace': string.whitespace, # 空白字符
            }
    def __init__(self):
        pass

    def generate_pwd_list(self, dic, max_len):
        """
        description:生成指定长度的密码序列
        param {*} dic   字典
        param {*} pwd_len   最大密码长度
        return {*} 所有可能的密码
        """
        k = itertools.product(dic, repeat=max_len)  # 迭代器
        allkey = ("".join(i) for i in k)
        if max_len == 1:
            return list(allkey)
        return self.generate_pwd_list(dic, max_len - 1) + list(allkey)
    
    def random_pwd(self, pwd_len):
        """
        随机生成密码
        :param pwd_len: 密码长度
        :return: 随机密码
        """
        characters = self.results['all_letters'] + self.results['digits'] + self.results['punctuation']
        return ''.join(random.choice(characters) for _ in range(pwd_len))
    
if __name__ == '__main__':
    print(PasswordManager().random_pwd(8))