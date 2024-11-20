# text = "via domen"
# input_value = "CLIO FULL HYBRID E-TECH 140 CV 5 PORTE ZEN (DAL 2020/06)"

# print(len(text), len(input_value), len(input_value.split()))

# input_value = " ".join(input_value.split()[:2])
# print(
#     input_value[:8],
# )  # Output: "VIA domencio"

import requests


def correct_address_here(address):
    try:
        api_key = "LqvfPKMOJP52av8VdogYVsxf5pJL8Kv4w39CkUjESCc"
        # address = "{residenzaCivico}, {residenzaIndirizzoVia} {residenzaIndirizzo}, {residenzaComune}, {residenzaProvincia}"
        url = f"https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={api_key}"
        response = requests.get(url).json()

        if "items" in response and response["items"]:
            data = response["items"][0]["address"]
            street = data["street"]
            parts = street.split(maxsplit=1)
            via = parts[0]  # First part is "via"
            street_name = (
                parts[1] if len(parts) > 1 else ""
            )  # The rest is the street name
            # Dictionary of common typos and corrections
            typo_corrections = {
                "domencio": "domenico",
                "pietrarsa": "pietrarse",
                # Add more common typos as needed
            }

            # Replace known typos in the street
            for typo, correction in typo_corrections.items():
                street_name = street_name.lower().replace(typo, correction)
            return {
                "residenzaProvincia": data["countyCode"],
                "residenzaComune": data["city"],
                "residenzaIndirizzoVia": via,
                "residenzaIndirizzo": street_name,
                "residenzaCivico": data["houseNumber"],
            }
            # return response["items"][0]["address"]["label"]
        else:
            raise ValueError("Address not found")
    except:
        return address


# Example usage
# address = "184, VIA domenciona fontana, NAPOLI, NA"
address = "75, VIA PIETRARSE, POZZUOLI, NA"
# address = "Oloyede Layout Road, Modakeke, Nigeria"
corrected_address = correct_address_here(address)
print(f"address: {address}, Corrected Address:", corrected_address)
