import string
import itertools
class ScreateManager:
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

if __name__ == '__main__':
    print(ScreateManager().generate_pwd_list(ScreateManager.results['all_letters'] + ScreateManager.results['digits'], 2))