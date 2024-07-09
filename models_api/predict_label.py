import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from catboost import CatBoostClassifier
from sklearn.linear_model import LogisticRegression

# Load the models and scalers
scaler_meta = joblib.load('models/scaler_meta.joblib')
scaler_emb = joblib.load('models/scaler_emb.joblib')
catboost_classifier = joblib.load('models/catboost_classifier.joblib')
catboost_classifier_emb = joblib.load('catboost_classifier_emb.joblib')
lr = joblib.load('logistic_regression.joblib')

def prediction_pipeline(X_meta, X_emb):
    # Apply the meta data scaler
    X_meta_scaled = scaler_meta.transform(X_meta)

    # Apply the embeddings scaler
    X_emb = np.concatenate([subs_embeddings, title_embeddings, tag_embeddings], axis=1)
    X_emb_scaled = scaler_emb.transform(X_emb)

    # Get predictions from both CatBoost models
    pred_meta = catboost_classifier.predict_proba(X_meta_scaled)
    pred_emb = catboost_classifier_emb.predict_proba(X_emb_scaled)

    # Concatenate their predictions
    final_pred_catboost = np.concatenate([pred_meta, pred_emb], axis=1)

    # Get final predictions from the logistic regression model
    final_predictions = lr.predict(final_pred_catboost)
    
    return final_predictions

# Example usage
# X_meta, subs_embeddings, title_embeddings, tag_embeddings should be your new input data
# final_predictions = prediction_pipeline(X_meta, subs_embeddings, title_embeddings, tag_embeddings)
