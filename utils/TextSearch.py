import re
import os
import platform
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 한글 토큰화 도구
# windows, linux에 따라 경로를 다르게 지정하기

os_name = platform.system()
if os_name == 'Windows':
    os.environ["JAVA_HOME"] = "C:\\Program Files\\Java\\jdk-21\\bin"
elif os_name == 'Linux':
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-21-openjdk-amd64"

okt = Okt()


def preprocess_text(text):
    """
    텍스트를 전처리하고 토큰화합니다.

    Parameters:
        text (str): 입력 텍스트

    Returns:
        str: 전처리 및 토큰화된 텍스트
    """
    # 영문 소문자 변환 및 불필요한 문자 제거
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9가-힣\s]', '', text)

    # 한글과 영문을 각각 토큰화
    tokens = []
    tokens += okt.morphs(text)
    tokens += re.findall(r'\b\w+\b', text)  # 영문 및 숫자 토큰화

    return ' '.join(tokens)


class TextVectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None

    def fit_transform(self, documents):
        """
        문서를 벡터화합니다.

        Parameters:
            documents (list of str): 입력 문서 리스트

        Returns:
            sparse matrix: 벡터화된 문서 행렬
        """
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        return self.tfidf_matrix

    def transform(self, query):
        """
        쿼리를 벡터화합니다.

        Parameters:
            query (str): 입력 쿼리

        Returns:
            sparse matrix: 벡터화된 쿼리 행렬
        """
        return self.vectorizer.transform([query])

    def compute_similarity(self, query_vec):
        """
        쿼리와 문서들 간의 유사도를 계산합니다.

        Parameters:
            query_vec (sparse matrix): 벡터화된 쿼리

        Returns:
            numpy array: 문서와 쿼리 간의 유사도 배열
        """
        return cosine_similarity(query_vec, self.tfidf_matrix).flatten()


class SearchEngine:
    def __init__(self, documents):
        """
        검색 엔진을 초기화합니다.

        Parameters:
            documents (list of str): 검색 대상 문서 리스트
        """
        self.documents = documents
        self.vectorizer = TextVectorizer()
        preprocessed_docs = [preprocess_text(doc["content"]) for doc in documents]
        self.vectorizer.fit_transform(preprocessed_docs)

    def search(self, query):
        """
        쿼리에 대한 검색을 수행합니다.

        Parameters:
            query (str): 검색 쿼리

        Returns:
            list of tuples: 문서 인덱스와 유사도 스코어 리스트
        """
        query = preprocess_text(query)
        query_vec = self.vectorizer.transform(query)
        similarities = self.vectorizer.compute_similarity(query_vec)
        sorted_indices = similarities.argsort()[::-1]

        return [(index, similarities[index]) for index in sorted_indices]


#
# results = engine.search("고백")
# for index, score in results[:5]:
#     print(f"Document: {documents[index]}, Similarity Score: {score:.4f}")
