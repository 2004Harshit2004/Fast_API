from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pickle
from pydantic import BaseModel, Field, computed_field 
from typing import Annotated,Literal
import pandas as pd


# import ml model
with open("ml_model_endpoint\model.pkl",'rb') as f:
    model = pickle.load(f)

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

app=FastAPI()


# pydantic model to validate input data
class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description='Tell me your age')]
    weight: Annotated[float, Field(..., gt=0, description='Tell me your weight')]
    height: Annotated[float, Field(..., gt=0, description='Tell me your height in meters')]
    income_lpa: Annotated[int, Field(..., gt=0, description='Tell me your income in lpa')]
    smoker: Annotated[bool, Field(..., description='Tell me you smoke or not')]
    city: Annotated[str, Field(..., description='Tell me in which city you live')]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'], Field(..., description='Tell me your occupation')]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight/(self.height**2)
    
    @computed_field
    @property
    def age_group(self) ->str:
        if self.age<25:
            return "young"
        elif self.age<45:
            return "adult"
        elif self.age<60:
            return "middle_aged"
        else:
            return "senior"

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
            if self.smoker and self.bmi > 30:
                return "high"
            elif self.smoker or self.bmi > 27:
                return "medium"
            else:
                return "low"
            
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3


# endpoint
@app.post('/predict')
def predict(data: UserInput):
    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }])

    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code=200, content={'predicted_category':'prediction'})