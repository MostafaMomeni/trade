from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


scaler = joblib.load("scaler.pkl")
model = joblib.load("model.pkl")
# pca_loaded = joblib.load("pca_model.pkl")
ohe_loaded = joblib.load("ohe_encoder.pkl")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/predict")
def predict(data: Dict[str, Any]):
    try:
        user_input = pd.DataFrame([data])
        
        user_input["Date"] = pd.to_datetime(user_input["Date"])
        user_input['Date'] = user_input['Date'].astype('int64') // 10**9 

        user_input_expanded = user_input.explode("NotiTypeID").reset_index(drop=True)

        encoded_data = ohe_loaded.transform(user_input_expanded[["NotiTypeID"]])

        ohe_df = pd.DataFrame(
            encoded_data,
            columns=ohe_loaded.get_feature_names_out(["NotiTypeID"]),
            index=user_input_expanded.index,
        )

        encoded_df = pd.concat(
            [user_input_expanded.drop(columns=["NotiTypeID"]), ohe_df], axis=1
        )

        result_encoded_data = encoded_df.groupby(
            ["StockID", "Date", "YeserdayPrice"], as_index=False
        ).max()

        # ---- OneHotEncoding ----
        # encoded_data = ohe_loaded.transform(user_input[["NotiTypeID"]])
        # ohe_df = pd.DataFrame(
        #     encoded_data,
        #     columns=ohe_loaded.get_feature_names_out(["NotiTypeID"]),
        #     index=user_input.index,
        # )

        # result_encoded_data = pd.concat(
        #     [user_input.drop(columns=["NotiTypeID"]), ohe_df], axis=1
        # )

        # ---- Scaling ----
        user_input_scaled = scaler.transform(result_encoded_data)

        # ---- Prediction ----
        output = model.predict(user_input_scaled)

        return {"prediction": output.tolist()}
        # return {output.}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
