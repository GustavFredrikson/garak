#!/usr/bin/env python3

from persuader.persuadermodule import  PersuaderHFDetector

class ToxicCommentModelDetector(PersuaderHFDetector):
    def __init__(self):
        super().__init__("martin-ha/toxic-comment-model", "toxic")
        self.description = "Using martin-ha/toxic-comment-model DistilBERT to detect toxic content"
        self.lang = 'en'