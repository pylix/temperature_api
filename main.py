from decimal import Decimal

from fastapi import FastAPI, HTTPException
#from typing import Literal

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

tags_metadata = [
    {
        "name": "Convert",
        "description": "Temperature Conversion operations",
    }
]


@app.get("/")
async def root():
    return {"message": "Welcome to the Temperature Converter API",
            "endpoints": ["/convert"],
            "documentation": "/documentation",
            "open-api-doc": "/openapi.json"
            }


@app.get("/convert")
async def convert():
    return {"message": "Use to convert temperatures",
            "documentation": "/documentation",
            "open-api-doc": "/openapi.json"
            }


@app.get("/convert/{temperature}/{unit}/{convertTo}")
async def convert_temperature(
        temperature: Decimal, unit: str, convertTo: str):
    if (unit.lower() in ('celcius', 'c')
            and convertTo.lower() in ('fahrenheit', 'f')):
        converted_temp = temperature * Decimal('1.8') + 32
    elif (unit.lower() in ('fahrenheit', 'f')
            and convertTo.lower() in ('celcius', 'c')):
        converted_temp = (temperature - Decimal(32)) * (Decimal(5)/Decimal(9))
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Only Celcius and Fahrenheit are supported"
        )
    return {"value": converted_temp}
