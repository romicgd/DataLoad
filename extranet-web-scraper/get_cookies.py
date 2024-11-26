import json
import requests
import os

cookies_file_path = "cookies.json"
login_url = "https://www.sa.mcss.gov.on.ca/?password-protected=login"
password = os.getenv('PASSWORD')

login_data = {
    "password_protected_pwd": password 
}

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

def get_cookies_from_json():
    try:
        with open(cookies_file_path, "r") as file:
            cookies = json.load(file)
            return cookies
    except FileNotFoundError:
        return None

def save_cookies_to_json(cookies):
    with open(cookies_file_path, "w") as file:
        json.dump(cookies, file)

def authenticate_and_get_cookies():
    session = requests.Session()
    response = session.post(login_url, data=login_data, headers=headers)
    if response.status_code == 200:
        cookies = session.cookies.get_dict()

        required_cookies = {
            "sa": "odsp",
            "bid_1_password_protected_auth": cookies.get("bid_1_password_protected_auth"),
            "PHPSESSID": cookies.get("PHPSESSID")
        }

        if required_cookies["bid_1_password_protected_auth"] and required_cookies["PHPSESSID"]:
            save_cookies_to_json(required_cookies)
            return required_cookies
        else:
            print("Failed to retrieve the required cookies.")
            return None
    else:
        print(f"Failed to authenticate. Status code: {response.status_code}")
        return None

def get_valid_cookies():
    cookies = get_cookies_from_json()
    if cookies is None or "bid_1_password_protected_auth" not in cookies or not cookies["bid_1_password_protected_auth"] or "PHPSESSID" not in cookies or not cookies["PHPSESSID"]:
        print("Cookies not found or expired. Re-authenticating...")
        cookies = authenticate_and_get_cookies()
    return cookies

if __name__ == "__main__":
    if not os.path.exists(cookies_file_path):
        with open(cookies_file_path, "w") as file:
            json.dump({}, file)

    cookies = get_valid_cookies()
    print(cookies)
    if cookies:
        print("Successfully retrieved cookies:")
        print(cookies)
    else:
        print("Failed to retrieve cookies.")
