# Specyfikacja Funkcjonalności: Aplikacja do Słuchania Krytycznego

## 1. Moduł Treningu Częstotliwości (solweż)

Ten moduł skupia się na rozpoznawaniu zmian w paśmie częstotliwości.

### Dostępne Tryby Treningu :
* **Tryb "Rozpoznaj Zmianę" (A/B)**
  * **Zasada:** Użytkownik ma przyciski przełączające płynnie między próbką referencyjną, a badaną (Zmienioną).
  * **Zadanie:** Wskazanie na siatce częstotliwości, w którym paśmie dokonano zmiany.
  * **Opcje:** Możliwość wyboru, czy aplikacja pyta tylko o pasmo (np. 1 kHz), czy również o to, czy nastąpiło wzmocnienie (Boost) czy redukcja (Cut).
* **Tryb "Dopasuj" (Matching EQ)**
  * **Zasada:** Użytkownik słyszy próbkę referencyjną (która ma nałożony ukryty filtr EQ) oraz próbkę "zerową" (płaską).
  * **Zadanie:** Użytkownik dostaje do dyspozycji interfejs korektora graficznego (wybór częstotliwości, podbicia/cięcia w dB i opcjonalnie dobroci Q). Musi "ukręcić" na próbce zerowej takie samo brzmienie, jakie ma referencja. 
  
  * **Ocena:** System porównuje ustawione przez użytkownika parametry z ukrytymi parametrami referencji.

### Zmienne Parametry:
* **Podział pasm:** 3 pasma (Łatwy), 10 pasm (Średni/ISO), 30 pasm (tercje, ale to już może być przesada) lub 3/5/10.
* **Skok Gain:** Subtelność zmian (np. od drastycznych +/- 12 dB, do bardzo trudnych +/- 3 dB). Wybór musi byc elastyczny np. tylko +12, -12/+12, tylko +9, -9/+9, albo adaptyacyjny - po kilku poprawnych odpowiedziach zmiany subtelniejsze, po niepoprawnej - zmiany mniej subtelne.
* **Szerokość filtra:** Szerokie dzwony łatwiejsze do wychwycenia vs wąskie filtry.

---

## 2. Moduł Treningu Głośności

Ten moduł uczy rozpoznawania różnic w ciśnieniu akustycznym.

### Dostępne Tryby Gry:
* **Tryb "Wykryj Różnicę" (A/B)**
  * **Zasada:** Przełączanie między próbką Referencyjną a Badaną.
  * **Zadanie:** Użytkownik musi wybrać z listy (lub wpisać), o ile decybeli różnią się próbki (np. -3 dB, +1.5 dB, ale również brak zmiany).
* **Tryb "Wyrównaj Poziom" (Matching)**
  * **Zasada:** Przełączanie między próbką A (głośniejszą/cichszą) i B.
  * **Zadanie:** Użytkownik za pomocą wirtualnego tłumika (fadera) musi zmienić głośność próbki B tak, aby brzmiała identycznie głośno jak A.
  * **Ocena:** Margines tolerancji (np. zaliczone, jeśli różnica wynosi mniej niż 0.5 dB, jeśli zaprojektujemy wybór liniowo, jeśli skokowo co 0.5dB to musi być dokładnie).

---

## 3. Silnik Audio i Interfejs (Frontend - JavaScript/Web Audio API)

* **Przetwarzanie w Czasie Rzeczywistym i Beztrzaskowe Przełączanie (Seamless A/B):** * Aplikacja pobiera tylko **jeden** plik źródłowy. Wszelkie zmiany (EQ, głośność) są aplikowane w czasie rzeczywistym za pomocą Web Audio API.
  * Sygnał jest rozdzielany na dwa równoległe kanały (Referencja i Badana). Użytkownik zmieniając parametry (np. szukając częstotliwości w trybie Matching) modyfikuje jedynie parametry cyfrowego filtra, a nie sam plik audio.  * **Eliminacja "klików":** Przełączanie między próbką A i B odbywa się poprzez operowanie dwoma węzłami głośności (`GainNode`). Zmiana z A na B to szybki, np. 5-milisekundowy crossfade, co zapobiega trzaskom.
* **Sterowanie Klawiaturą:**
  * W zależności od zadania, ważne, żeby była intuicyjna i opisana, może obejmować podstawowe funkcjonalności np. dla trybu matching czestotliowsci start/pauze i zmiane miedzy próbką badaną a referencyjną.
* **Pętla (Looping):** Automatyczne zapętlanie krótkich (np. 5-10 sekund) fragmentów audio, aby użytkownik mógł skupić się na zmianach.

---

## 4. Architektura i Backend (Django)

* **Biblioteka Próbek:**
  * Serwowanie plików bezstratnych (FLAC/WAV).
  * System tagowania próbek (Bębny, Bas, Wokal, Gitara, Pełny Mix). Różne instrumenty to inne wyzwania dla konkretnych pasm.
* **Zarządzanie Użytkownikiem:**
  * Logowanie i profile.
  * Zapisywanie postępów sesji (np. które pasma sprawiają największą trudność - zapis do bazy danych).
* **Dynamiczne Generowanie Zadań:**
  * Frontend wysyła żądanie do Django, a Django losuje próbkę, wybiera tryb gry i wysyła parametry (np. wybrane pasmo i wartość zmiany) do Frontendu, który lokalnie aplikuje te filtry. (Backend nie renderuje audio, jedynie zarządza logiką i weryfikuje odpowiedzi).