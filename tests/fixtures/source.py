# Compliant
password = ""
password = secrets["password"]
password = asdf
secrets = get_secrets(
    CONFIG["secret_key"],
    API_CONFIG["secret_key"],
    DB_CONFIG["secret_key"],
)

# Non-compliant
password = "hardcoded0"
if password == "hardcoded1":
    auth = True
if "hardcoded2" != PASSWORD:
    auth = False
if user == "admin" and password == "hardcoded3":
    auth = True
creds = {"user": "admin", "password": "hardcoded4"}
