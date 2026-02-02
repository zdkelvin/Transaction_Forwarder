import singletonManager

from fastapi.responses import JSONResponse

class BaseResponseHandler:
    @staticmethod
    def apiMasterServerResponse(result: dict, task_id: str = None):
        success = result.get('success', False)
        code = result.get('code', '500')
        message = result.get('message', '')
        data = result.get('data', None)
        captcha_data = data.get('captcha_data', '') if data else ''
        cropped_image = data.get('cropped_image', '') if data else ''
        if singletonManager.DBManager().server_info_db.versionAtLeast('1.0.0'):
            return JSONResponse(
                status_code = int(code),
                content = {
                    "active_sessions" : 0,
                    "cpu_usage": 0,
                    "memory_usage": 0,
                    "storage_usage": 0,
                    "message" : message,
                    "status" : "Success" if success else "Failed",
                    "captchaData" : captcha_data,
                    "cropped_image" : cropped_image,
                }
            )
        else:
            return JSONResponse(
                status_code = int(code),
                content = {
                    "code": code,
                    "status": "Success" if success else "Failed",
                    "result": success,
                    "message": message,
                    "data": data
                }
            )
        
    @staticmethod
    def apiMasterServerError(code: str, message: str):
        if singletonManager.DBManager().server_info_db.versionAtLeast('1.0.0'):
            return JSONResponse(
                status_code = int(code),
                content={
                    "code": code,
                    "status": "Failed",
                    "result": False,
                    "message": message
                }
            )
        else:
            return JSONResponse(
                status_code = int(code),
                content = {
                    "status": "Failed",
                    "message": message,
                }
            )

    @staticmethod
    def apiResponse(result: dict, task_id: str = None):
        success = result.get('success', False)
        code = result.get('code', '500')
        message = result.get('message', '')
        data = result.get('data', None)
        return JSONResponse(
            status_code = int(code),
            content = {
                "code": code,
                "status": "Success" if success else "Failed",
                "result": success,
                "message": message,
                "data": data
            }
        )
    
    @staticmethod
    def apiError(code: str, message: str):
        return JSONResponse(
            status_code = int(code),
            content = {
                "status": "Failed",
                "message": message,
            }
        )