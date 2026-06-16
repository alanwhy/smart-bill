"""自定义异常定义"""


class SmartBillException(Exception):
    """基础异常类"""

    def __init__(self, code: int, message: str, detail: str = None):
        self.code = code
        self.message = message
        self.detail = detail or message
        super().__init__(self.detail)


class ValidationError(SmartBillException):
    """数据验证错误"""

    def __init__(self, message: str, detail: str = None):
        super().__init__(400, message, detail)


class FileError(SmartBillException):
    """文件处理错误"""

    def __init__(self, message: str, detail: str = None):
        super().__init__(400, message, detail)


class QwenAPIError(SmartBillException):
    """Qwen API 调用错误"""

    def __init__(self, message: str, detail: str = None):
        super().__init__(500, message, detail)


class DatabaseError(SmartBillException):
    """数据库操作错误"""

    def __init__(self, message: str, detail: str = None):
        super().__init__(500, message, detail)


class ResourceNotFoundError(SmartBillException):
    """资源未找到"""

    def __init__(self, resource_type: str, resource_id):
        message = f"{resource_type} not found"
        detail = f"{resource_type} with id {resource_id} not found"
        super().__init__(404, message, detail)
