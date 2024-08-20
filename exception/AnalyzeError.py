class AnalyzeError(Exception):
    """ChatGPT의 이미지 해석에 문제가 있는 경우"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message
