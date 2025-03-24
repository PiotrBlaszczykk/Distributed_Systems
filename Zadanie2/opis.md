# REST API – Systemy Rozproszone Zadanie 2

## Opis projektu
Aplikacja webowa stworzona przy użyciu FastAPI, udostępniająca dwa główne zasoby:
- **Tłumaczenie tekstu** (z wykorzystaniem "półlegalnego" API Google Translate),
- **Wymiana walut** (z wykorzystaniem danych z 3 różnych API: NBP, Frankfurter, Vatcomply).

Dodatkowo serwis wzbogacony o "bezużyteczny fakt dnia" pobierany z publicznego API i tłumaczony na język polski
za pomocą kolejnego API.

---

## Zgodność z REST (wg prezentacji slajd 21)

1. **Zasoby**: `/translated`, `/exchange`, `/translator`, `/currencies.html`, `/`.
2. **Relacje między zasobami**: formularze i linki między stronami HTML.
3. **URLe**: Przejrzyste, RESTowe, np. `/exchange?base=USD&target=PLN`
4. **Metody HTTP**: Wszystkie zasoby dostępne poprzez metodę `GET` (pobieranie danych).
5. **Reprezentacja zasobów**: odpowiedzi to strony HTML generowane dynamicznie na podstawie zapytań do API i logiki lokalnej.
6. **Serwer**: uruchamiany przez `uvicorn`, niezależnie od IDE.
7. **Testowanie**: możliwe poprzez przeglądarkę, SwaggerUI (`/docs`) oraz Postmana.

---

## Endpointy

### `GET /`
- **Opis:** Strona główna z bezużytecznym faktem dnia oraz przyciskiem do tłumacza i konwertera walut.
- **Odpowiedź:** HTML (`index.html`) – fakt dnia tłumaczony automatycznie.

### `GET /translator`
- **Opis:** Formularz tłumaczenia tekstu.
- **Odpowiedź:** HTML z formularzem

### `GET /translated`
- **Opis:** Przetwarza dane z formularza tłumaczenia.
- **Parametry:**
  - `text`: tekst do przetłumaczenia (maks. 1000 znaków)
  - `source_lang`: język źródłowy (np. `en`)
  - `target_lang`: język docelowy (np. `pl`)
- **Odpowiedź:** HTML ze stroną z wynikiem tłumaczenia i nowym faktem dnia
- **Zabezpieczenia:** Limit znaków wejściowych, fallback dla niepoprawnych języków

### `GET /currencies.html`
- **Opis:** Formularz wyboru waluty bazowej i docelowej
- **Odpowiedź:** HTML z formularzem oraz bezużytecznym faktem dnia

### `GET /exchange`
- **Opis:** Zwraca średni kurs wymiany z 3 różnych źródeł
- **Parametry:**
  - `base`: waluta bazowa (np. `USD`)
  - `target`: waluta docelowa (np. `PLN`)
- **Obsługiwane waluty:** `USD`, `EUR`, `PLN`, `GBP`, `CHF`
- **Odpowiedź:** HTML ze średnią kursu i przetłumaczonym faktem dnia
- **Zabezpieczenia:** Walidacja walut (błąd 400 dla nieobsługiwanych)

---

## Wykorzystywane publiczne API

### Bezużyteczny Fakt Dnia
- **Źródło:** https://uselessfacts.jsph.pl/?ref=public_apis&utm_medium=website
- **Tłumaczenie:** Google Translate endpoint (https://clients5.google.com/translate_a/t)

### Kursy walut
- **NBP API:** https://api.nbp.pl/en.html?ref=public_apis&utm_medium=website
- **Frankfurter:** https://frankfurter.dev/?ref=public_apis&utm_medium=website
- **Vatcomply:** https://www.vatcomply.com/documentation?ref=public_apis&utm_medium=website

---


## Elementy bezpieczeństwa
- Walidacja długości tekstu tłumaczenia (`max 1000 znaków`)
- Walidacja listy dostępnych walut
- Zabezpieczenie przed błędami z API – fallbacki i komunikaty w HTML

---

## Asynchroniczność
- Wszystkie zapytania do API (NBP, Translate, Frankfurter, Vatcomply) wykonywane asynchronicznie za pomocą `httpx.AsyncClient`

---

## Deployment
- Uruchamiane lokalnie przez `uvicorn` (`uvicorn server:app --reload`)
- Możliwość przeniesienia do środowiska produkcyjnego lub chmurowego (opcjonalnie)

---

## Podsumowanie
Zadanie spełnia wszystkie wymagania:
- REST API zgodne ze standardem,
- różne źródła danych,
- przetwarzanie i logika po stronie serwera,
- HTML jako forma odpowiedzi,
- obsługa błędów i walidacja,
- pełna dokumentacja + możliwość testowania.


