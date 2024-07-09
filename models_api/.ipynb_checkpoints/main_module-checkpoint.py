import os
import joblib
import numpy as np
from catboost import CatBoostClassifier
import pandas as pd
import numpy as np
import spacy
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
import json
from .ytparser import get_channel_data

class ModelModule:
    def __init__(self):
        self.catboost_classifier = CatBoostClassifier()
        self.catboost_classifier_emb = CatBoostClassifier()
        self.lr = None
        self.scaler_meta = None
        self.scaler_emb = None

        self.load_models()

    def load_models(self):
        self.catboost_classifier.load_model('models_api/models/catboost_classifier_meta.cbm', format='cbm')
        self.catboost_classifier_emb.load_model('models_api/models/catboost_classifier_emb.cbm', format='cbm')
        self.lr = joblib.load('models_api/models/logistic_regression.pkl')
        self.scaler_meta = joblib.load('models_api/models/scaler_meta.pkl')
        self.scaler_emb = joblib.load('models_api/models/scaler_emb.pkl')
       
        

    def get_result(self, title: str, description: str, tags: list, link: str, category: str):
        result = get_channel_data(link)
        result['title'] = title
        result['subs'] = description
        result['tags'] = tags
        result['video_category_id'] = category
        X_meta, X_emb = self.process_df(pd.DataFrame([result]))
        return {'views_prediction': prediction_pipeline(X_meta, X_emb)}
        

    def prediction_pipeline(X_meta, X_emb):
        # Apply the meta data scaler
        X_meta_scaled = self.scaler_meta.transform(X_meta)
        X_emb_scaled = self.scaler_emb.transform(X_emb)

        # Get predictions from both CatBoost models
        pred_meta = self.catboost_classifier.predict_proba(X_meta_scaled)
        pred_emb = self.catboost_classifier_emb.predict_proba(X_emb_scaled)

        # Concatenate their predictions
        final_pred_catboost = np.concatenate([pred_meta, pred_emb], axis=1)

        # Get final predictions from the logistic regression model
        final_prediction = self.lr.predict(final_pred_catboost)
        labels = ['up to 1000', 'from 1000 to 10000', 'from 10000 to 100000', 'from 100000 to 500000', 'from 500000 to 1000000',
          'from 1000000 to 5000000', 'from 5000000 to 10000000', 'from 10000000 to 20000000', 'more than 20000000']

        # Create a label map to convert labels to numeric values
        label_map = dict(zip(range(len(labels)), labels))
        return label_map[final_prediction]



    def process_df(self, dataframe: pd.DataFrame, concat_embeddings=False):
        cols = ['video_category_id', 'subscriber_count', 'channel_view_count',
       'channel_video_count', 'view_count_0', 'view_count_1', 'view_count_2',
       'view_count_3', 'view_count_4', 'view_count_5', 'view_count_6',
       'view_count_7', 'view_count_8', 'view_count_9', 'publish_time_day',
       'historical_avg_views', 'view_growth_rate', 'num_of_tags',
       'avg_tag_length', 'avg_word_length_title', 'channel_popularity']
        df = dataframe.copy()
        df = df.dropna(subset=['subs'])

        df['tags'] = pd.array(df['tags'])

        # Historical Average Views
        df['historical_avg_views'] = df[['view_count_0', 'view_count_1', 'view_count_2', 'view_count_3', 'view_count_4', 'view_count_5', 'view_count_6', 'view_count_7', 'view_count_8', 'view_count_9']].mean(axis=1)

        # View Growth Rate
        df['view_growth_rate'] = np.where(df['historical_avg_views'] == 0, 0, df['view_count_0'] / df['historical_avg_views'])

        # Number of Tags
        df['num_of_tags'] = df['tags'].apply(len)

        # Average Tag Length
        df['avg_tag_length'] = df['tags'].apply(lambda x: np.mean([len(tag) for tag in x]))

        # Average Word Length in Title
        df['avg_word_length_title'] = df['title'].apply(lambda x: np.mean([len(word) for word in x.split()]))

        # Channel Popularity
        df['channel_popularity'] = np.where(df['channel_video_count'] == 0, df['channel_view_count'], df['channel_view_count'] / df['channel_video_count']) 


        # Load models for embeddings
        nlp = spacy.load('en_core_web_md')
        model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        subs_model = SentenceTransformer(model_name)

        tag_embeddings_list = []
        title_embeddings_list = []
        subs_embeddings_list = []

        def get_average_embedding(tags):
            embeddings = [nlp(tag).vector for tag in tags]
            avg_embedding = np.mean(embeddings, axis=0)
            return avg_embedding

        def get_sentence_embedding(sentence):
            inputs = tokenizer(sentence, return_tensors='pt', padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.squeeze().numpy()

        # Iterate over rows to calculate all embeddings in one loop
        for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Calculating embeddings"):
            tag_embeddings_list.append(get_average_embedding(row['tags']))
            title_embeddings_list.append(get_sentence_embedding(row['title']))
            subs_embeddings_list.append(subs_model.encode(row['subs']))

        tag_embeddings = np.array(tag_embeddings_list)
        title_embeddings = np.array(title_embeddings_list)
        subs_embeddings = np.array(subs_embeddings_list)

        if concat_embeddings:
            df = pd.concat([df.reset_index(drop=True), 
                            pd.DataFrame(tag_embeddings, columns=[f'tag_emb_{i}' for i in range(tag_embeddings.shape[1])]), 
                            pd.DataFrame(title_embeddings, columns=[f'title_emb_{i}' for i in range(title_embeddings.shape[1])]),
                            pd.DataFrame(subs_embeddings, columns=[f'subs_emb_{i}' for i in range(subs_embeddings.shape[1])])], axis=1)
        X_meta = df[cols].values
        X_emb = np.concatenate([subs_embeddings, title_embeddings, tag_embeddings], axis=1)
        return X_meta, X_emb

# if __name__ == "__main__":
#     print("Not intended to run main_module.py as a script.")