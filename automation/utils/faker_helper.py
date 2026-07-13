# automation/utils/faker_helper.py
from faker import Faker
import random

fake = Faker("zh_CN")  # 中文数据


class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def random_name():
        """随机姓名"""
        return fake.name()

    @staticmethod
    def random_email():
        """随机邮箱"""
        return fake.email()

    @staticmethod
    def random_phone():
        """随机手机号"""
        return fake.phone_number()

    @staticmethod
    def random_address():
        """随机地址"""
        return fake.address()

    @staticmethod
    def random_company():
        """随机公司名"""
        return fake.company()

    @staticmethod
    def random_sentence():
        """随机句子"""
        return fake.sentence()

    @staticmethod
    def random_password(length=10):
        """随机密码"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def random_number(min=1, max=100):
        """随机数字"""
        return random.randint(min, max)

    @staticmethod
    def random_bool():
        """随机布尔值"""
        return random.choice([True, False])

    @staticmethod
    def random_choice(items):
        """随机选择"""
        return random.choice(items)


# 便捷函数
random_name = TestDataGenerator.random_name
random_email = TestDataGenerator.random_email
random_phone = TestDataGenerator.random_phone
random_password = TestDataGenerator.random_password
random_sentence = TestDataGenerator.random_sentence