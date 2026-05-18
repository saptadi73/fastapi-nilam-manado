from fastapi.responses import JSONResponse

class JSONResponseHandler:
    @staticmethod
    def success(data=None, message="Success"):
        return JSONResponse(content={"status": "success", "message": message, "data": data})

    @staticmethod
    def error(message="Error", data=None):
        return JSONResponse(content={"status": "error", "message": message, "data": data}, status_code=400)
