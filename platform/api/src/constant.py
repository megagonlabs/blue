from blue.platform import Platform
from fastapi.responses import JSONResponse
from blue.properties import EMAIL_DOMAIN_WHITE_LIST, PROPERTIES

EMAIL_DOMAIN_ADDRESS_REGEXP = r"@((\w+?\.)+\w+)"
END_OF_EVENT_SIGNAL = 'END_OF_EVENT_SIGNAL'

platform_id = PROPERTIES["platform.name"]
p = Platform(id=platform_id, properties=PROPERTIES)
allowed_domains = EMAIL_DOMAIN_WHITE_LIST.split(",")

# responses
RESPONSE_501 = JSONResponse(status_code=501, content={"message": "The server lacks the ability to fulfill the request."})
