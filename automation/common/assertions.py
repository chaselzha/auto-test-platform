# automation/common/assertions.py
import allure
from utils.logger import logger


class Assertions:
    """统一断言类"""

    @staticmethod
    def assert_equals(actual, expected, message=None):
        """断言相等"""
        msg = message or f"期望值: {expected}, 实际值: {actual}"
        with allure.step(f"断言: {msg}"):
            assert actual == expected, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_not_equals(actual, expected, message=None):
        """断言不相等"""
        msg = message or f"实际值不应该等于: {expected}"
        with allure.step(f"断言: {msg}"):
            assert actual != expected, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_true(condition, message=None):
        """断言为 True"""
        msg = message or "条件应该为 True"
        with allure.step(f"断言: {msg}"):
            assert condition, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_false(condition, message=None):
        """断言为 False"""
        msg = message or "条件应该为 False"
        with allure.step(f"断言: {msg}"):
            assert not condition, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_in(element, container, message=None):
        """断言元素在容器中"""
        msg = message or f"'{element}' 应该在 '{container}' 中"
        with allure.step(f"断言: {msg}"):
            assert element in container, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_not_in(element, container, message=None):
        """断言元素不在容器中"""
        msg = message or f"'{element}' 不应该在 '{container}' 中"
        with allure.step(f"断言: {msg}"):
            assert element not in container, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_greater(actual, expected, message=None):
        """断言 actual > expected"""
        msg = message or f"实际值 {actual} 应该大于 {expected}"
        with allure.step(f"断言: {msg}"):
            assert actual > expected, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_less(actual, expected, message=None):
        """断言 actual < expected"""
        msg = message or f"实际值 {actual} 应该小于 {expected}"
        with allure.step(f"断言: {msg}"):
            assert actual < expected, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_contains(actual, expected, message=None):
        """断言 actual 包含 expected"""
        msg = message or f"'{actual}' 应该包含 '{expected}'"
        with allure.step(f"断言: {msg}"):
            assert expected in actual, msg
            logger.debug(f"✅ 断言通过: {msg}")

    @staticmethod
    def assert_not_contains(actual, expected, message=None):
        """断言 actual 不包含 expected"""
        msg = message or f"'{actual}' 不应该包含 '{expected}'"
        with allure.step(f"断言: {msg}"):
            assert expected not in actual, msg
            logger.debug(f"✅ 断言通过: {msg}")


# 便捷函数
assert_equals = Assertions.assert_equals
assert_true = Assertions.assert_true
assert_false = Assertions.assert_false
assert_in = Assertions.assert_in
assert_contains = Assertions.assert_contains