import requests


def extract_app_id(url: str) -> str | None:
    parts = url.split("/")
    if "app" not in parts:
        return None

    try:
        index = parts.index("app")
        return parts[index + 1]
    except:
        return None


def get_price(app_id: str):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=IN"

    response = requests.get(url, timeout=10)
    data = response.json()

    if not data[str(app_id)]["success"]:
        return None

    info = data[str(app_id)]["data"]

    name = info["name"]

    if "price_overview" not in info:
        return name, "Free or unavailable"

    price_data = info["price_overview"]

    price = price_data["final"] / 100  # convert paise to rupees

    return name, f"₹{price}"