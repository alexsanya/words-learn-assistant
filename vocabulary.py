import os
from pymongo import MongoClient
from dataclasses import dataclass
from collections import namedtuple
from config import DB_CONNECTION_STRING, DB_NAME, MEMORIZATION_TRESHOLD

@dataclass
class Record:
    _id: str
    word: str
    translation: str
    score: int

Word = namedtuple('Record', ['word', 'translation'])


client = MongoClient(DB_CONNECTION_STRING)

class Vocabulary:
    def __init__(self) -> None:
        self.db = client[DB_NAME]
    
    def push(self, item: Word) -> None:
        self.db.vocabulary.insert_one({"word": item.word, "translation": item.translation, "score": 0})
    
    def get_list(self, limit=-1) -> list[Record]:
        cursor = self.db.vocabulary.find(filter={"score": {"$lt": MEMORIZATION_TRESHOLD }}, limit=limit).sort("score")
        return [Record(_id=item["_id"], word=item["word"], translation=item["translation"], score=item["score"]) for item in cursor]
    
    def update_scores(self, ids: list[str]) -> None:
        self.db.vocabulary.update_many({"_id": {"$in": ids}}, {"$inc": {"score": 1}})

    def delete_words(self, ids: list[str]) -> None:
        self.db.vocabulary.delete_many({"_id": {"$in": ids}})

vocabulary = Vocabulary()