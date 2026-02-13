import logging, os, asyncio, datetime
import Utils.generalUtils as GeneralUtils

from typing import Dict
from logging import Logger
from logging.handlers import RotatingFileHandler

class LoggingSystem:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggingSystem, cls).__new__(cls)
        return cls._instance
    
    async def init(self, server_name):
        self.server_name = server_name
        self.current_date = GeneralUtils.getCurrentDate_String()
        self.main_log_dir = os.path.join(GeneralUtils.getPersistentDir(), "Logs") if GeneralUtils.deployMode() else GeneralUtils.getPath("Logs")
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        os.makedirs(self.main_log_dir, exist_ok=True)
        self.task_manager_logger: Dict[str, Logger] = {}
        self.newDayInit()
        
        self.new_day_task = asyncio.create_task(self.checkForNewDay())
        return self

    def close(self):
        if hasattr(self, 'new_day_task') and self.new_day_task and not self.new_day_task.done():
            self.new_day_task.cancel()
            self.new_day_task = None

        if hasattr(self, 'server_logger'):
            for handler in self.server_logger.handlers[:]:
                self.server_logger.removeHandler(handler)
                handler.close()

        if hasattr(self, 'api_logger'):
            for handler in self.api_logger.handlers[:]:
                self.api_logger.removeHandler(handler)
                handler.close()

        for logger in self.task_manager_logger.values():
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()

    async def checkForNewDay(self):
        try:
            while(True):
                await self.waitUntilNextDay()
                print("New day detected, initializing new day...")
                self.newDayInit()
        except asyncio.CancelledError as ce:
            print(f"LoggingSystem background task cancelled. {ce}")
        except Exception as e:
            print(f"LoggingSystem background task crashed: {e}")
        finally:
            print("Rescheduling the checkForNewDay task...")
            if self.new_day_task is None or (self.new_day_task and self.new_day_task.done()):
                self.new_day_task = asyncio.create_task(self.checkForNewDay())

    async def waitUntilNextDay(self):
        now = datetime.datetime.now()
        target_time = now.replace(hour=13, minute=00, second=0, microsecond=0)
        if now >= target_time:
            target_time = (now + datetime.timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

    def newDayInit(self):
        self.close()
        
        try:
            self.createServerLogger()
            self.createApiLogger()
            
            task_manager_names = self.task_manager_logger.keys()
            for task_manager_name in task_manager_names:
                self.createTaskLogger(task_manager_name)
        except Exception as e:
            print(f"Error during newDayInit: {e}")

    def createServerLogger(self):
        server_log_dir = os.path.join(self.main_log_dir, "server", self.server_name)
        os.makedirs(server_log_dir, exist_ok=True)
        server_log_path = os.path.join(server_log_dir, f"{GeneralUtils.getCurrentDate_String()}.log")
        self.server_logger = logging.getLogger(f"{self.server_name}")
        self.server_logger.setLevel(logging.INFO)

        for handler in self.server_logger.handlers[:]:
            self.server_logger.removeHandler(handler)
            handler.close()

        handler = RotatingFileHandler(
            server_log_path,
            maxBytes = 5 * 1024 * 1024,
            backupCount = 3
        )
        handler.setFormatter(self.formatter)
        self.server_logger.addHandler(handler)
        self.server_logger.info(f"Date : {GeneralUtils.getCurrentDT_String()}")

    def createApiLogger(self):
        api_log_dir = os.path.join(self.main_log_dir, "api", self.server_name)
        os.makedirs(api_log_dir, exist_ok=True)
        api_log_path = os.path.join(api_log_dir, f"{GeneralUtils.getCurrentDate_String()}.log")
        self.api_logger = logging.getLogger(f"{self.server_name}_api")
        self.api_logger.setLevel(logging.INFO)

        for handler in self.api_logger.handlers[:]:
            self.api_logger.removeHandler(handler)
            handler.close()

        handler = RotatingFileHandler(
            api_log_path,
            maxBytes = 5 * 1024 * 1024,
            backupCount = 3
        )
        handler.setFormatter(self.formatter)
        self.api_logger.addHandler(handler)
        self.api_logger.info(f"Date : {GeneralUtils.getCurrentDT_String()}")
            
    def createTaskLogger(self, task_manager_name: str):
        task_manager_log_dir = os.path.join(self.main_log_dir, "taskManager", task_manager_name)
        os.makedirs(task_manager_log_dir, exist_ok=True)
        task_manager_log_path = os.path.join(task_manager_log_dir,  f"{GeneralUtils.getCurrentDate_String()}_{task_manager_name}.log")
        if task_manager_name in self.task_manager_logger:
            task_manager_logger = self.task_manager_logger[task_manager_name]
        else:
            task_manager_logger = logging.getLogger(f"{task_manager_name}")
        task_manager_logger.setLevel(logging.INFO)

        if task_manager_name in self.task_manager_logger:
            for handler in task_manager_logger.handlers[:]:
                task_manager_logger.removeHandler(handler)
                handler.close()

        handler = RotatingFileHandler(
            task_manager_log_path,
            maxBytes = 5 * 1024 * 1024,
            backupCount = 3
        )
        
        handler.setFormatter(self.formatter)
        task_manager_logger.addHandler(handler)
        task_manager_logger.info(f"Date : {GeneralUtils.getCurrentDT_String()}")
        self.task_manager_logger[task_manager_name] = task_manager_logger

    def insertServerLog(self, log_level: int, message: str):
        if self.server_logger:
            self.server_logger.log(log_level, message)

    def insertApiLog(self, log_level: int, message: str):
        if self.api_logger:
            self.api_logger.log(log_level, message)

    def insertTaskManagerLog(self, task_manager_name: str, log_level: int, message: str):
        if task_manager_name in self.task_manager_logger:
            self.task_manager_logger[task_manager_name].log(log_level, message)

    @staticmethod
    def createTaskManagerLogger(task_manager_name: str):
        LoggingSystem().createTaskLogger(task_manager_name)

    #region Insert Logs
    @staticmethod
    def serverLog(level: int, message: str):
        LoggingSystem().insertServerLog(level, message)

    @staticmethod
    def apiLog(level: int, message: str):
        LoggingSystem().insertApiLog(level, message)

    @staticmethod
    def taskManagerLog(task_manager_name: str, level: int, message: str):
        LoggingSystem().insertTaskManagerLog(task_manager_name, level, message)
    #endregion