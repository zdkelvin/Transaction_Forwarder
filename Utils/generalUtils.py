import datetime, hashlib, os, sys, pytz, aiofiles

from pathlib import Path

def getDirectoryPath():
    return os.path.join(os.path.dirname(__file__)).replace('\\', '/')

def getPath(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, path)

def getPersistentDir():
    if sys.platform == "win32":
        path = Path(os.environ.get("USERPROFILE", "C:/")) / "Documents"
    else:
        path = Path("/root")

    return os.path.join(path, "Transaction Forwarder")

def deployMode():
    return getattr(sys, 'frozen', False) or '__compiled__' in globals()

def getCurrentTimeZoneDT(country_code = "SG"):
    if country_code == 'AUS':
        timeZone = 'Australia/Sydney'
    else:
        timeZone = 'Asia/Singapore'
    timeZoneDT = pytz.timezone(timeZone)
    return datetime.datetime.now(timeZoneDT)

def getCurrentDT_String():
    timeZoneDT = getCurrentTimeZoneDT()
    dtNow = timeZoneDT.strftime('%d%m%Y_%H%M%S')
    return dtNow

def getCurrentDate_String():
    timeZoneDT = getCurrentTimeZoneDT()
    dtNow = timeZoneDT.strftime('%d%m%Y')
    return dtNow

def convertToTimestamp(dateTime: str, format: str) -> str:
    dt_object = datetime.datetime.strptime(dateTime, format)
    timestamp = dt_object.timestamp()
    return str(timestamp)
    
async def saveTextFile(filename, content):
    async with aiofiles.open(filename, 'w') as file:
        await file.write(content)
    
def parseDateTime(dateTime, country_code):
    timeZoneByCountry = {
        "AUS": "Australia/Sydney",
        "MY": "Asia/Kuala_Lumpur",
        "SG": "Asia/Singapore"
    }
    timeZone = timeZoneByCountry.get(country_code, "Asia/Singapore")
    return pytz.timezone(timeZone).localize(dateTime)

def hashSignature(signature: str) -> str:
    sha512 = hashlib.sha512()
    sha512.update(signature.encode('utf-8'))
    return sha512.hexdigest()