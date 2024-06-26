import pandas as pd
from typing import Dict, List
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from model import DelayModel
import uvicorn


# Define app in FastAPI
app = FastAPI()

# Import model from DelayModel
model = DelayModel()

unique_opers = [
 'American Airlines',
 'Air Canada',
 'Air France',
 'Aeromexico',
 'Aerolineas Argentinas',
 'Austral',
 'Avianca',
 'Alitalia',
 'British Airways',
 'Copa Air',
 'Delta Air',
 'Gol Trans',
 'Iberia',
 'K.L.M.',
 'Qantas Airways',
 'United Airlines',
 'Grupo LATAM',
 'Sky Airline',
 'Latin American Wings',
 'Plus Ultra Lineas Aereas',
 'JetSmart SPA',
 'Oceanair Linhas Aereas',
 'Lacsa'
]

# Class to format flights data
class FlightInfo(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

class FlightsReq(BaseModel):
    flights: List[FlightInfo]

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(flight_req:FlightsReq, response:Response) -> dict:
    
    flight = flight_req.flights[0]
    
    # Validate input data
    if flight.OPERA not in unique_opers:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=400, detail='OPERA should be an airline operator')
    
    if flight.TIPOVUELO not in ['N', 'I']:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=400, detail="TIPOVUELO should be either 'N' or 'I'")

    if flight.MES not in list(range(1, 13)) or type(flight.MES) != int:
        response.status_code = status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=400, detail='MES should be an integer between 1 and 12')

    # Convert JSON to DataFrame
    flights_dict = flight.dict()
    
    # Get input data as df
    flights_df = pd.DataFrame([flights_dict])

    # Preprocess input data and predict
    flights_feats = model.preprocess(data=flights_df)
    y_pred = model.predict(features=flights_feats)
    
    return {'predict': y_pred}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port='8080')