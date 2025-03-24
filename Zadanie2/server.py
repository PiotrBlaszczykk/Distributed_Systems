from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
from fastapi import Request


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def main_page():

    #bezużyteczny fakt dnia
    fact = await get_fact()

    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read().replace("{{ fact }}", fact)

    return HTMLResponse(content=html)


async def get_fact():

    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            fact_data_en = response.json()
            fact_text_en = fact_data_en.get("text", "Brak faktu")
        except Exception:
            fact_text_en = "Nie udało się pobrać faktu."

    # print("pobrany fakt dnia: " + fact_text_en)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(

                # pół-legalne API do google tłumacza
                "https://clients5.google.com/translate_a/t",
                params={
                    "client": "dict-chrome-ex",
                    "sl": "auto",
                    "tl": "pl",
                    "q": fact_text_en
                }
            )

            json_data = response.json()
            fact_pl = json_data[0][0]  # pierwszy element zawiera przetłumaczony tekst

            # print("STATUS ODPOWIEDZI:", response.status_code)
            # print("PRZETŁUMACZONY FAKT:", fact_pl)

        except Exception as e:
            print(f"coś poszło nie tak przy tłumaczeniu: {e}")
            fact_pl = "błąd"

    return fact_pl

@app.get("/translator", response_class=HTMLResponse)
async def get_translator_page():

    # bezużyteczny fakt dnia
    fact = await get_fact()

    with open("translator.html", "r", encoding="utf-8") as file:
        html = file.read().replace("{{ fact }}", fact)

    return HTMLResponse(content=html)


@app.get("/translated", response_class=HTMLResponse)
async def translate_text(request: Request, text: str, source_lang: str, target_lang: str):

    #zabezpieczanie API przed złośliwym uzytkownikiem które może kazać przetłumaczyć np milion znaków
    if len(text) > 1000:
        return HTMLResponse(content="Zbyt długi tekst do tłumaczenia", status_code=413)  # 413 Payload Too Large

    print("Próba tłumaczenia:", text)
    print("Z języka:", source_lang, "na:", target_lang)

    # bezużyteczny fakt dnia
    fact = await get_fact()

    async with httpx.AsyncClient() as client:
        try:

            response = await client.get(
                "https://clients5.google.com/translate_a/t",
                params={
                    "client": "dict-chrome-ex",
                    "sl": source_lang,
                    "tl": target_lang,
                    "q": text
                }
            )

            print("STATUS:", response.status_code)
            print("ODPOWIEDŹ:", response.text)

            json_data = response.json()

            """
                użyty endpoint is "lewy" i nieudokumentowany, więc czasem zwraca różne
                rzeczy w zależności, co my wyślemy. Czasem zwraca sam string
                np ["chicken"], a czasem liste [ [ "chicken", en ] ] tak więc żeby wszystko działo
                sprawdzamy tu 2 przypadki
            """
            try:
                if isinstance(json_data[0], list):
                    translated_text = json_data[0][0]

                elif isinstance(json_data[0], str):
                    translated_text = json_data[0]
                else:
                    translated_text = "zwrócono coś dziwnego"
            except Exception as e:
                print("Błąd przy odczycie json'a", e)
                translated_text = "błąd"


        except Exception as e:
            print(f"coś poszło nie tak przy tłumaczeniu: {e}")
            translated_text = "błąd"

    with open("translator_2.html", "r", encoding="utf-8") as file:
        html = file.read()
        html = html.replace("{{ original_text }}", text)
        html = html.replace("{{ translated_text }}", translated_text)
        html = html.replace("{{ fact }}", fact)

    return HTMLResponse(content=html)



#====================================================

@app.get("/currencies.html", response_class=HTMLResponse)
async def get_currencies_page():

    # bezużyteczny fakt dnia
    fact = await get_fact()

    with open("currencies.html", "r", encoding="utf-8") as file:
        html = file.read().replace("{{ fact }}", fact)

    return HTMLResponse(content=html)

@app.get("/exchange", response_class=HTMLResponse)
async def exchange_rates(base: str, target: str):


    supported_currencies = ["USD", "EUR", "PLN", "GBP", "CHF"]

    # walidacja walut od inputa
    if base.upper() not in supported_currencies or target.upper() not in supported_currencies:
        return HTMLResponse(
            content=f"<h2>Błąd: Nieobsługiwana waluta.</h2><p>Dozwolone waluty: {', '.join(supported_currencies)}</p>",
            status_code=400
        )

    # bezużyteczny fakt dnia
    fact = await get_fact()

    #pobieramy kurs z 3 różnych API i bierzemy średnią

    results = []

    #NBP
    url_nbp_base = f"https://api.nbp.pl/api/exchangerates/rates/A/{base}/?format=json"
    url_nbp_target = f"https://api.nbp.pl/api/exchangerates/rates/A/{target}/?format=json"

    """
        NBP pobiera tylko base walutę i zwraca kurs w PLN, tak więc
        więc żeby korzystając z tego API obliczać kursy walut trzeba zrobić
        dwa requesty a potem podzielić wyniki przez siebie 
    """

    async with httpx.AsyncClient() as client:
        try:
            response_base = await client.get(url_nbp_base)
            response_target = await client.get(url_nbp_target)

            base_to_pln = response_base.json()["rates"][0]["mid"]
            target_to_pln = response_target.json()["rates"][0]["mid"]

            rate_nbp = base_to_pln / target_to_pln
            print(f"Kurs {base} → {target} z NBP: {rate_nbp}")

            results.append(rate_nbp)

        except Exception as e:
            print(f"Błąd pobierania kursu z NBP: {e}")

    #Frankfurter
    url_frankfurter = f"https://api.frankfurter.dev/v1/latest?base={base}&symbols={target}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_frankfurter)
            data = response.json()
            rate = data["rates"][target]
            print(f"Kurs {base} → {target} z Frankfurtera: {rate}")

            results.append(rate)

        except Exception as e:
            print(f"Błąd pobierania kursu z Frankfurtera: {e}")


    # VatComply
    url_vatcomply = f"https://api.vatcomply.com/rates?base={base.upper()}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url_vatcomply)
            data = response.json()
            rate = data["rates"][target.upper()]
            print(f"Kurs {base} → {target} z Vatcomply: {rate}")

            results.append(rate)

        except Exception as e:
            print(f"Błąd pobierania kursu z Vatcomply: {e}")

    #results = []

    if len(results) == 0:
        final_rate = "błąd przy pobieraniu kursów"
    else:
        final_rate = sum(results) / len(results)


    with open("currencies_result.html", "r", encoding="utf-8") as file:
        html = file.read()
        html = html.replace("{{ base }}", base)
        html = html.replace("{{ target }}", target)
        html = html.replace("{{ avg_rate }}", str(final_rate))
        html = html.replace("{{ fact }}", fact)

    return HTMLResponse(content=html)
