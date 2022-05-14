from decimal import Decimal
from enum import Enum

from fastapi import FastAPI, HTTPException
import ray
from ray import serve

description = (
    "Welcome the the temperature" 
    " API! Operations like conversion are supported"
)

app = FastAPI(
    title="TemperatureAPI",
    description=description,
    version="0.0.1",
    docs_url="/documentation",
    redoc_url=None
)

ray.init(address="auto", namespace="temperature-api")
serve.start(detached=True)

tags_metadata = [
    {
        "name": "Convert",
        "description": "Temperature Conversion operations",
    }
]


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Temperature Converter API",
        "endpoints": ["/convert"],
        "documentation": "/documentation",
        "open-api-doc": "/openapi.json"
    }


@app.get("/convert")
async def convert():
    return {
        "message": "This endpoint is Used to convert temperatures",
        "documentation": "/documentation",
        "open-api-doc": "/openapi.json"
    }


class TempEnum(str, Enum):
    celsius = 'celsius'
    fahrenheit = 'fahrenheit'
    C = 'C'
    F = 'F'
    Celsius = 'Celsius'
    Fahrenheit = 'Fahrenheit'


@app.get("/convert/{temperature}/{unit}/{convertTo}")
async def convert_temperature(
        temperature: Decimal,
        unit: TempEnum, convertTo: TempEnum):
    if unit.lower() in ('fahrenheit', 'f') and temperature < Decimal(-459.67):
        raise HTTPException(
            status_code=400,
            detail=f"Values lower than absolute zero are not allowed"
        )
    elif unit.lower() in ('celsius', 'c') and temperature < Decimal(-273.15):
        raise HTTPException(
            status_code=400,
            detail=f"Values lower than absolute zero are not allowed"
        )
    elif (unit.lower() in ('celsius', 'c')
            and convertTo.lower() in ('fahrenheit', 'f')):
        converted_temp = Decimal(temperature * Decimal('1.8') + 32)
    elif (unit.lower() in ('fahrenheit', 'f')
            and convertTo.lower() in ('celsius', 'c')):
        converted_temp = Decimal(temperature - Decimal(32)) * (Decimal(5)/Decimal(9))
    else:
        # this code block should only be reached when the same unit appears twice
        raise HTTPException(
            status_code=400,
            detail=f"Nothing to convert because unit and convertTo are the unit"
        )
    return {"value": converted_temp}


@serve.deployment(route_prefix="/")
@serve.ingress(app)
class FastAPIWrapper:
    pass


FastAPIWrapper.deploy()
