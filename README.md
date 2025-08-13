
## ToolStatix

Projekt prototypowy służący do określania **żywotności**, **przebiegu** oraz innych **parametrów narzędzi** za pomocą **analizy pomiarów natężenia prądu**.

Obrabiarka (maszyna CNC), chcąc utrzymać stabilne obroty narzędzia (RPM) pod wpływem obciążenia wywołanego przez obrabiany materiał, zwiększa pobór prądu. Po przekroczeniu określonego progu (threshold), program rozpoczyna zbieranie danych do pamięci, które na końcu cyklu są zapisywane do bazy danych. Można również dodać powiązane parametry, takie jak przepływ chłodziwa, prędkości posuwu i inne, które również zostaną zapisane do bazy po zakończeniu cyklu.

Dodatkowo należy określić I/O sygnał wymiany narzędzia (zakończeniu pracy narzędzia), to pozwoli automatycznie wygenerować raport.


## 🎯 Cel projektu

- Zbieranie statystyk pracy narzędzi obróbki CNC.
- Automatyczny raport przebiegu oraz innych powiązanych parametrów.


## ⚙️ Główne funkcje

- Odczyt danych o natężeniu prądu w czasie rzeczywistym
- Analiza i przetwarzanie sygnału
- Zbieranie danych i archiwizacja danych do bazy
- Generowanie raportu przebiegu narzędzia i parametrów pracy


## 🖼️ Schemat działania

1. Ustalenie maszyn i źródła danych
2. Dodanie głównego adresu (main_tag) i progu (threshold) jako sygnał to rozpoczęcia zbierania i zakończenia zbierania danych oraz ich zapisu
3. Dodanie adresów powiązanych parametrów (related_tags) jeżeli są potrzebne.
4. Start śledzenia wartości prądu
5. Po przekroczeniu threshold program zapisuje wartości do pamięci podręcznej.
6. Po spadku wartości prądu poniżej threshold, zostaje zapisana do bazy danych statystyka przebiegu: min, max, średnia, czas pracy. 


## Ważne uwagi

### 06.08.2025

- Projek powstał w celu nauki i treningu
- Aktualnie dostępny *driver to OPCUA
Oznacza to że maszyna / obrabiarka musi mieć zmierzoną wartość prądu i zapisaną na sterowniku, bądź w innych możliwym miejscu do pobrania przez serwer OPC
Oznacza to że potrzebny jest już skonfigurowany serwer OPC oraz dostępna zmierzona wartość prądu.
- Możliwe rozbudowanie o sygnały analogowe, oraz drivery MODBUS RTU, MODBUS TCP, MQTT.

### ✅ TODO
- dodanie obsługi sygnału do wymiany narzędzia 
- usunięcie z bazy danych rekordów zużytego narzędzia - Raport OK 

### *

**Driver** - określa sposób / biblioteki do zbierania danych np. MODBUS / OPCUA / MQTT

## How to run

1) Start MariaDB docker container (first download image) on port 3306

2) open /ToolStatix/backend and create venv

```
python -m venv venv
```
3) run script to work on venv

Powershell
```
./venv/scripts/activate
```

4) install requirements.txt

```
pip install requirements.txt
```

5) create /backend/.env file

**Don't change FIRST_LOGIN_ROOT_PASS**
```
FIRST_LOGIN_ROOT_PASS=password
ROOT_PASSWORD=
DB_ADMIN_PASSWORD=
DB_USER_PASSWORD=
```

6) run python script /backend/db_init.py - to initialize db tables and users

```
cd core

python db_init.py

```
7) run API in development

```
fastapi dev main.py
```