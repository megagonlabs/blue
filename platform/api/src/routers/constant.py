from fastapi.responses import JSONResponse

NOT_ALPHA_NUMERIC_UNDERSCORE_STRING_RESPONSE = JSONResponse(status_code=400, content={"message": "Name can only contain alpha-numeric characters and underscores."})
