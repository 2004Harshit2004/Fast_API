from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of patient',examples=['P001','P002'])]
    name: Annotated[str, Field(..., description='Name of the patient', examples=['Harshit Goswami'])]
    city: Annotated[str, Field(...,description='city of patient')]
    age: Annotated[int, Field(..., gt=0, lt=100, description='Age of patient')]
    gender: Annotated[Literal['Male', 'Female', 'other'], Field(...,description='Gender of Patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of Patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi<18.5:
            return 'Underweight'
        elif self.bmi<30:
            return 'Normal'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):

    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['Male', 'Female', 'other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open('patients.json') as f:
        data = json.load(f)
        return data
    
def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)


@app.get("/")
def hello():
    return {"message":"Patient Management System API"}

@app.get("/about")
def about():
    return {"message":"An API system for patient record management"}

@app.get("/view")
def view():
    data=load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str = Path(..., description="patient id", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by:str = Query(...,description='Sort on the basis of height, weight or bmi'), order:str = Query('asc',description='order in desc or asc order')):

    valid_fields= ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select from asc or desc')

    data= load_data()

    sort_order= True if order=='desc' else False
    
    sorted_data= sorted(data.values(), key=lambda x:x.get(  sort_by,0),reverse=sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data from db
    data = load_data()

    # check if patient is already in db
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exist')

    # add new patient
    data[patient.id] = patient.model_dump(exclude=[id])

    # save it into json file
    save_data(data)

    return JSONResponse(status_code=201, content={'messge': 'Patient created successfully'})


@app.put('/edit/{patient_id}')
def upadate_patient(patient_id: str, patient_update:PatientUpdate):

    # load data from db
    data = load_data()

    # check patient is present or not
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]
    upadate_patient_info = patient_update.model_dump(exclude_unset=True)

    for key,value in upadate_patient_info.items():
        existing_patient_info[key]=value

    # existing_patient_info -> pydantic_obj to update value of bmi and verdict
    existing_patient_info['id'] = patient_id
    pydantic_obj=Patient(**existing_patient_info)

    # pydantic_obj -> existing_patient_info(dict) to update it in data
    existing_patient_info = pydantic_obj.model_dump(exclude=['id'])
    
    # save data
    data[patient_id] = existing_patient_info
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    # check patient is in db or not
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    

    # delete patient
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient deleted'})