# Compliant
password = ""
password = secrets["password"]
password = asdf
if 1 == 1:
    auth = True
secrets = get_secrets(
    CONFIG["secret_key"],
    API_CONFIG["secret_key"],
    DB_CONFIG["secret_key"],
)
os.getenv("PASSWORD")
os.getenv("PASSWORD", "")
getenv("PASSWORD", "")
os.environ.get("pwd", "")
environ.get("pwd", "")
format_password = "prefix_{}".format(dynamic_value1)
format_password = "prefix_{0}".format(dynamic_value2)
format_password = f"prefix_{dynamic_value3}"
login(password="")

# Non-compliant
password = "hardcoded0"
if password == f"hardcoded1":
    auth = True
if "{}".format("hardcoded2") != PASSWORD:
    auth = False
if user == "admin" and password == "hardcoded3":
    auth = True
creds = {"user": "admin", "password": "hardcoded4"}
os.getenv("PASSWORD", "hardcoded5")
getenv("PASSWORD", "hardcoded6")
os.environ.get("pwd", "hardcoded7")
environ.get("pwd", "hardcoded8")
format_password = "prefix_{hardcoded9}"
login(password="hardcoded10")
