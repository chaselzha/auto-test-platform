# automation/utils/data_factory.py
from faker import Faker
import random
import string

fake = Faker("zh_CN")


class TestDataFactory:
    """测试数据工厂"""

    @staticmethod
    def generate_user():
        """生成用户数据"""
        return {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(length=12),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "company": fake.company(),
            "name": fake.name()
        }

    @staticmethod
    def generate_search_data():
        """生成搜索测试数据"""
        keywords = [
            "pytest", "selenium", "python", "自动化测试",
            "Jenkins", "Docker", "人工智能", "GitHub",
            "API测试", "性能测试", "安全测试"
        ]
        return {
            "keyword": random.choice(keywords),
            "expected": random.choice(keywords),
        }

    @staticmethod
    def generate_login_data():
        """生成登录测试数据"""
        return {
            "username": fake.user_name() + str(random.randint(1, 999)),
            "password": fake.password(length=10),
            "email": fake.email()
        }

    @staticmethod
    def generate_form_data():
        """生成表单测试数据"""
        return {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "message": fake.sentence(nb_words=20),
            "subject": fake.sentence(nb_words=5)
        }

    @staticmethod
    def generate_random_string(length=10):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def generate_random_number(min_val=1, max_val=100):
        """生成随机数字"""
        return random.randint(min_val, max_val)

    @staticmethod
    def generate_random_choice(items):
        """从列表中随机选择"""
        return random.choice(items)


# 便捷函数
generate_user = TestDataFactory.generate_user
generate_search_data = TestDataFactory.generate_search_data
generate_login_data = TestDataFactory.generate_login_data
generate_form_data = TestDataFactory.generate_form_data
generate_random_string = TestDataFactory.generate_random_string
generate_random_number = TestDataFactory.generate_random_number