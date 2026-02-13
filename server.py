import asyncio, logging
import singletonManager

from contextlib import asynccontextmanager
from fastapi import FastAPI
from Routes.middleware import VerifyAppPairKeyMiddleware, VerifyAdminPairKeyMiddleware
from loggingSystem import LoggingSystem
from Routes.adminRoute import router as AdminRoute
from Routes.deviceRoute import router as DeviceRoute

@asynccontextmanager
async def lifespan(app: FastAPI):
    LoggingSystem()
    logger = await LoggingSystem().init('MasterServer')
    logger.insertServerLog(logging.INFO, 'Master server starting.')
    singletonManager.DBManager()
    await asyncio.sleep(3)
    singletonManager.AdminManager()
    singletonManager.DeviceManager()
    logger.insertServerLog(logging.INFO, 'Master server started.')
    yield
    LoggingSystem().close()
    logger.insertServerLog(logging.INFO, 'Master server shutting down.')

app = FastAPI(lifespan=lifespan)
app.add_middleware(VerifyAppPairKeyMiddleware)
app.add_middleware(VerifyAdminPairKeyMiddleware)

app.include_router(AdminRoute)
app.include_router(DeviceRoute)