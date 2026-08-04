import os
import sys

import pandas as pd

from src.exception import CustomException
from src.utils import load_object

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(ARTIFACTS_DIR, "preprocessor.pkl")


class PredictionPipeline:
    def __init__(self, model_path: str = MODEL_PATH, preprocessor_path: str = PREPROCESSOR_PATH):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path

    def predict(self, features):
        try:
            if not os.path.exists(self.model_path) or not os.path.exists(self.preprocessor_path):
                raise FileNotFoundError(
                    f"Model artifacts not found. Expected at '{self.model_path}' "
                    f"and '{self.preprocessor_path}'. artifacts/model.pkl and "
                    "artifacts/preprocessor.pkl must be included in the deployment."
                )

            model = load_object(file_path=self.model_path)
            preprocessor = load_object(file_path=self.preprocessor_path)

            data_scaled = preprocessor.transform(features)
            preds = model.predict(data_scaled)
            return preds
        except Exception as e:
            raise CustomException(e, sys)


class CustomData:
    def __init__(
        self,
        gender: str,
        race_ethnicity: str,
        parental_level_of_education: str,
        lunch: str,
        test_preparation_course: str,
        reading_score: float,
        writing_score: float,
    ):
        self.gender = gender
        self.race_ethnicity = race_ethnicity
        self.parental_level_of_education = parental_level_of_education
        self.lunch = lunch
        self.test_preparation_course = test_preparation_course
        self.reading_score = reading_score
        self.writing_score = writing_score

    def get_data_as_dataframe(self):
        try:
            if not (0 <= float(self.reading_score) <= 100):
                raise ValueError("reading_score must be between 0 and 100.")
            if not (0 <= float(self.writing_score) <= 100):
                raise ValueError("writing_score must be between 0 and 100.")

            custom_data_input_dict = {
                "gender": [self.gender],
                "race_ethnicity": [self.race_ethnicity],
                "parental_level_of_education": [self.parental_level_of_education],
                "lunch": [self.lunch],
                "test_preparation_course": [self.test_preparation_course],
                "reading_score": [float(self.reading_score)],
                "writing_score": [float(self.writing_score)],
            }
            return pd.DataFrame(custom_data_input_dict)
        except Exception as e:
            raise CustomException(e, sys)
