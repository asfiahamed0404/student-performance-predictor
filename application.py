import os
import warnings

warnings.filterwarnings("ignore")

from flask import Flask, request, render_template, jsonify

from src.pipeline.predict_pipeline import CustomData, PredictionPipeline
from src.pipeline.train_pipeline import run_training_pipeline

application = Flask(__name__)
app = application


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predictdata", methods=["GET", "POST"])
def predict_datapoint():
    if request.method == "GET":
        return render_template("home.html")

    try:
        data = CustomData(
            gender=request.form.get("gender"),
            race_ethnicity=request.form.get("race_ethnicity"),
            parental_level_of_education=request.form.get("parental_level_of_education"),
            lunch=request.form.get("lunch"),
            test_preparation_course=request.form.get("test_preparation_course"),
            reading_score=float(request.form.get("reading_score", 0)),
            writing_score=float(request.form.get("writing_score", 0)),
        )
        pred_df = data.get_data_as_dataframe()

        predict_pipeline = PredictionPipeline()
        results = predict_pipeline.predict(pred_df)

        prediction_value = float(results[0])
        prediction_value = max(0.0, min(100.0, prediction_value))

        return render_template(
            "home.html",
            results=round(prediction_value, 2),
        )
    except (ValueError, TypeError) as ve:
        return render_template(
            "home.html",
            results=None,
            error="Please enter valid numeric scores between 0 and 100.",
        )
    except FileNotFoundError as fnf:
        return render_template(
            "home.html",
            results=None,
            error="Model artifacts not found. Please run /train first to generate them.",
        )
    except Exception as e:
        return render_template(
            "home.html",
            results=None,
            error=f"Something went wrong: {str(e)}",
        )


@app.route("/train", methods=["GET"])
def train():
    try:
        r2 = run_training_pipeline()
        return jsonify(
            {
                "status": "success",
                "message": "Training pipeline completed successfully.",
                "r2_score": r2,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    model_path = os.path.join("artifacts", "model.pkl")
    preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")
    return jsonify(
        {
            "status": "ok",
            "model_exists": os.path.exists(model_path),
            "preprocessor_exists": os.path.exists(preprocessor_path),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")