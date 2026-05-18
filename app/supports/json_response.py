from fastapi.responses import JSONResponse


class JSONResponseHandler:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        return JSONResponse(
            content={"status": "success", "message": message, "data": data},
            status_code=status_code,
        )

    @staticmethod
    def error(message="Error", data=None, status_code=400):
        return JSONResponse(
            content={"status": "error", "message": message, "data": data},
            status_code=status_code,
        )
