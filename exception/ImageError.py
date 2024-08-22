class ImageError(Exception):
    """이미지 조건을 불만족하는 경우"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message
