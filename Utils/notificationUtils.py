import re

from decimal import Decimal
from datetime import datetime

def getBankCodeByNotification(app_name, title):
    if app_name == "PB QR":
        return "PBB"
    elif (app_name == "DBS digibank" or (app_name == "Gmail" and title == "DBS digibank")):
        return "DBS"
    elif (app_name == "MariBank" or (app_name == "Gmail" and title == "MariBank")):
        return "Maribank"
    elif (app_name == "GXS Bank" or (app_name == "Gmail" and title == "GXS")):
        return "GXS"
    elif app_name == "TNG eWallet":
        return "TNG"
    elif app_name == "Karnataka Bank":
        return "KARB"
    elif app_name == "City Union Bank":
        return "CUB"
    elif app_name == "IDBI Bank":
        return "IDBI"
    else:
        return None

def getBankCodeByAppName(app_name):
    if app_name == "PB QR":
        return "PBB"
    elif app_name == "DBS digibank":
        return "DBS"
    elif app_name == "MariBank":
        return "Maribank"
    elif app_name == "GXS Bank":
        return "GXS"
    elif app_name == "TNG eWallet":
        return "TNG"
    elif app_name == "Karnataka Bank":
        return "KARB"
    elif app_name == "City Union Bank":
        return "CUB"
    elif app_name == "IDBI Bank":
        return "IDBI"
    else:
        return None
    
def getBankExternalAppName(bank_code):
    if bank_code == "KARB":
        return "Messages"
    elif bank_code == "CUB":
        return "Messages"
    elif bank_code == "IDBI":
        return "Messages"
    elif bank_code == "Maribank":
        return "Gmail"
    elif bank_code == "GXS":
        return "Gmail"
    elif bank_code == "DBS":
        return "Gmail"
    else:
        return ""
    
def parseNotification(title, content, timestamp, bank_code):
    if bank_code == "GXS":
        return parseGXSNotification(title, content, timestamp)
    elif bank_code == "Maribank":
        return parseMariBankNotification(title, content, timestamp)
    elif bank_code == "DBS":
        return parseDBSNotification(title, content, timestamp)
    else:
        return None
    
def jsonableNotification(notification_data):
    jsonable_data = notification_data.copy()
    if 'amount' in jsonable_data and isinstance(jsonable_data['amount'], Decimal):
        jsonable_data['amount'] = str(jsonable_data['amount'])
    if 'received_dt' in jsonable_data and isinstance(jsonable_data['received_dt'], datetime):
        jsonable_data['received_dt'] = jsonable_data['received_dt'].isoformat()
    return jsonable_data

def parseGXSNotification(title: str, content: str, timestamp: str):
    match_titles = ["You've been paid", "GXS"]
    if not any(match_title in title for match_title in match_titles):
        return None
    
    if "GXS" in title:
        notification_type = "Gmail Notification"
    else:
        notification_type = "GXS App Notification"

    message = content.replace("\n", " ").strip()
    if notification_type == "Gmail Notification":
        amount_pattern = r"You received S\$([\d,]+(?:\.\d{1,2})?) in"
        sender_pattern = r"from ([A-Z ]+) on"
        receiver_pattern = r"ending with (\d{4}) from"
        datetime_pattern = r"on (\d{1,2} \w+ \d{4}, \d{1,2}:\d{2}[AP]M) via"

        amount_match = re.search(amount_pattern, message, re.IGNORECASE)
        sender_match = re.search(sender_pattern, message, re.IGNORECASE)
        receiver_match = re.search(receiver_pattern, message, re.IGNORECASE)
        datetime_match = re.search(datetime_pattern, message, re.IGNORECASE)

        try:
            amount = getAmount(amount_match.group(0)) if amount_match else 0
            sender = sender_match.group(1).strip() if sender_match else ''
            receiver = receiver_match.group(1) if receiver_match else ''
            received_dt = datetime_match.group(1) if datetime_match else ""
            received_dt = datetime.strptime(received_dt, "%d %B %Y, %I:%M%p") if received_dt else None
            return {
                "amount": amount,
                "sender": sender,
                "receiver": receiver,
                "received_dt": received_dt
            }
        except:
            return None
    else:
        amount_pattern = r"S\$([\d,]+(?:\.\d{1,2})?)"

        amount_match = re.search(amount_pattern, message, re.IGNORECASE)

        try:
            amount = getAmount(amount_match.group(0)) if amount_match else 0
            received_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
            return {
                "amount": amount,
                "sender": "",
                "receiver": "",
                "received_dt": received_dt
            }
        except:
            return None

def parseMariBankNotification(title: str, content: str, timestamp: str):
    match_titles = ["You have an incoming PayNow transfer", "MariBank"]
    if not any(match_title in title for match_title in match_titles):
        return None
    
    if "MariBank" in title:
        notification_type = "Gmail Notification"
    else:
        notification_type = "Maribank App Notification"

    message = content.replace("\n", " ").strip()

    if notification_type == "Gmail Notification":
        amount_pattern = r"Amount: S\$([\d,]+(?:\.\d{1,2})?)"
        sender_pattern = r"From:\s([A-Za-z ]+)(?=\sIf)"
        receiver_pattern = r"Account ending (\d{4})"
        datetime_pattern = r"Transaction Time: (\d{1,2} \w{3} \d{4} \d{2}:\d{2})"
    else:
        amount_pattern = r"S\$([\d,]+(?:\.\d{1,2})?)"
        sender_pattern = r"^([A-Z ]+?) has sent you"
        receiver_pattern = r"ending (\d{4})"
        datetime_pattern = r"on (\d{1,2} \w{3} \d{4} \d{2}:\d{2})"

    amount_match = re.search(amount_pattern, message, re.IGNORECASE)
    sender_match = re.search(sender_pattern, message, re.IGNORECASE)
    receiver_match = re.search(receiver_pattern, message, re.IGNORECASE)
    datetime_match = re.search(datetime_pattern, message, re.IGNORECASE)

    try:
        amount = getAmount(amount_match.group(0)) if amount_match else 0
        sender = sender_match.group(1).strip() if sender_match else ''
        receiver = receiver_match.group(1) if receiver_match else ''
        received_dt = datetime_match.group(1) if datetime_match else ""
        received_dt = datetime.strptime(received_dt, "%d %b %Y %H:%M") if received_dt else None
        return {
            "amount": amount,
            "sender": sender,
            "receiver": receiver,
            "received_dt": received_dt
        }
    except:
        return None

def parseDBSNotification(title: str, content: str, timestamp: str):
    match_titles = ["DBS digibank"]
    if not any(match_title in title for match_title in match_titles):
        return None
    
    if "DBS digibank" in title:
        notification_type = "Gmail Notification"
    else:
        notification_type = "DBS App Notification"

    message = content.replace("\n", " ").strip()
        
    if notification_type == "Gmail Notification":
        amount_pattern = r"You received SGD ([\d,]+(?:\.\d{1,2})?) from"
        sender_pattern = r"from ([A-Z ]+) to"
        receiver_pattern = r"A/C ending (\d{4}) on"
        datetime_pattern = r"on (\d{1,2} \w{3} \d{2,4} \d{2}:\d{2}) ?([A-Z]{3})?"

        amount_match = re.search(amount_pattern, message, re.IGNORECASE)
        sender_match = re.search(sender_pattern, message, re.IGNORECASE)
        receiver_match = re.search(receiver_pattern, message, re.IGNORECASE)
        datetime_match = re.search(datetime_pattern, message, re.IGNORECASE)

        try:
            amount = getAmount(amount_match.group(0)) if amount_match else 0
            sender = sender_match.group(1).strip() if sender_match else ''
            receiver = receiver_match.group(1) if receiver_match else ''
            received_dt = datetime_match.group(1) if datetime_match else ""
            if received_dt:
                now = datetime.now()
                received_dt = datetime.strptime(f"{received_dt} {now.year}", "%d %b %H:%M %Y")
            return {
                "amount": amount,
                "sender": sender,
                "receiver": receiver,
                "received_dt": received_dt
            }
        except:
            return None
    else:
        amount_pattern = r"SGD\s?([\d.]+)"
        sender_pattern = r"from\s+([A-Z ]{3,})(?=\s+on)"
        datetime_pattern = r"on (\d{1,2} \w{3} \d{1,2}:\d{2})"

        amount_match = re.search(amount_pattern, message, re.IGNORECASE)
        sender_match = re.search(sender_pattern, message, re.IGNORECASE)
        datetime_match = re.search(datetime_pattern, message, re.IGNORECASE)

        try:
            amount = getAmount(amount_match.group(0)) if amount_match else 0
            sender = sender_match.group(1).strip() if sender_match else ''
            received_dt = datetime_match.group(1) if datetime_match else ""
            year = datetime.now().year
            received_dt = datetime.strptime(f"{received_dt} {year}", "%d %b %H:%M %Y") if received_dt else None
            return {
                "amount": amount,
                "sender": sender,
                "received_dt": received_dt
            }
        except:
            return None

def getAmount(amount_text: str):
    if not amount_text:
        return Decimal(0)
    
    amount_text = re.sub(r'(\d)\s+\.(\d{2})', r'\1.\2', amount_text)
    amount_text = re.sub(r'[^\d,.\-+]', '', amount_text)
    pattern = r'[+-]?\d+(?:,\d{3})*(?:\.\d+)?'
    match = re.search(pattern, amount_text)

    if match:
        amount = match.group(0).replace(",", "")
        try:
            return Decimal(amount)
        except Exception:
            pass

    return Decimal(0)