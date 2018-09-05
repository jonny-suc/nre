#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : word2vec_zh.py
# @Author: TW
# @Date  : 2018/3/20
# @Desc  :

import os

from keras.models import load_model

from tw_word2vec.bilstm_trainer_zh import BiLstmTrainer
from tw_word2vec.inputer import Inputer, Configuration, SentencesVector
from tw_word2vec.lstm_trainer_zh import LstmTrainer
from tw_word2vec.outputer import Outputer
import numpy as np
# from ltl_pytorch import ACNN_trainer
from tw_word2vec.bilstm_attention_trainer import BiLstmAttentionTrainer

class Trainer(object):
    def __init__(self, inputer: Inputer, testType) -> object:
        self.config = inputer.config
        self.inputer = inputer
        config = self.config
        if not os.path.exists(config.model_file_path):
            vector = self.inputer.vector
            print("句子向量矩阵的shape" + str(vector.sentence_vec.shape))
            print("位置向量矩阵的shape" + str(vector.position_vec.shape))
            print("词性向量矩阵的shape" + str(vector.pos_vec.shape))
            print("关系分类矩阵的shape" + str(vector.classifications_vec.shape))
            if testType == "CNN":
                pass
            self.modelTrainer = BiLstmAttentionTrainer(vector)
            self.model = self.train()
            self.model.save(config.model_file_path)
        self.model = load_model(config.model_file_path)

    def train(self):
        return self.modelTrainer.train()


    def predict(self, sentence_vector: SentencesVector):
        classVector = np.ones(sentence_vector.classifications_vec.shape)
        prop = self.model.predict(
            {'sequence_input': sentence_vector.embedded_sequences,
             "posi_input" : sentence_vector.position_vec,
             "typeInput" : classVector})
        return sentence_vector.prop2index(prop)


if __name__ == '__main__':
    config = Configuration(
        position_matrix_file_path="../data/posi_matrix.npy",
        word2vec_file_path="../data/needed_zh_word2vec.bin",
        POS_list_file_path="../data/military/pos_list.txt",
        types_file_path="../data/military/relations_zh.txt",
        corpus_file_path="../data/military/train_zh.txt",
        model_file_path="../data/model/re_military_zh_model.bilstm.hdf5",
    )
    inputer = Inputer(config)
    trainer = Trainer(inputer, BiLstmTrainer())
    outputer = Outputer(trainer)
    predict_texts = ["<loc>美国</loc>目前共有2级11艘航空母舰，包括企业级核动力航母1艘，尼米兹级核动力航母10<loc>艘，</loc>全部采用核动力发动机",
                     "<loc>美国</loc>经过多年航空母舰的发<loc>展，</loc>一直以来都是全球拥有最多、排水量和体积最大、舰载机搭载数量最多、作战效率最强大、而且全部使用核动力航空母舰的国家"]
    import json
    print(json.dumps(outputer.getDescription(predict_texts), ensure_ascii=False))
