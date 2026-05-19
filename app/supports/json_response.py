from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class JSONResponseHandler:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        return JSONResponse(
            content=jsonable_encoder({"status": "success", "message": message, "data": data}),
            status_code=status_code,
        )

    @staticmethod
    def success_list(data=None, label="data", message=None, status_code=200):
        items = data or []
        response_message = message if items else f"Belum ada data {label}"
        return JSONResponseHandler.success(
            data=items,
            message=response_message or f"Data {label} berhasil diambil",
            status_code=status_code,
        )

    @staticmethod
    def success_items(data, items=None, label="data", message=None, status_code=200):
        item_list = items if items is not None else data.get("items", [])
        response_message = message if item_list else f"Belum ada data {label}"
        return JSONResponseHandler.success(
            data=data,
            message=response_message or f"Data {label} berhasil diambil",
            status_code=status_code,
        )

    @staticmethod
    def error(message="Error", data=None, status_code=400):
        return JSONResponse(
            content=jsonable_encoder({"status": "error", "message": message, "data": data}),
            status_code=status_code,
        )
