# Analiza stratnych transakcji INTC i MU

Analiza porównuje dwa stratne cykle z wcześniejszymi zyskownymi transakcjami na podstawie danych z `completed_trades.txt`. Uwzględnia 26 wcześniejszych zyskownych cykli oraz dwa stratne.

Wskaźniki przy zakupie pochodzą z pierwszego dnia kupna. Dla transakcji kupowanych przez kilka dni w pliku zapisany jest odczyt tylko z pierwszego dnia.

## Transakcje stratne

| Ticker i data kupna | Wynik brutto | Wartość kupna | RSI14 | Disparity14 | MACD Hist | ADX14 | Układ SMA20 > SMA50 > SMA200 |
|---|---:|---:|---:|---:|---:|---:|---|
| INTC, 2026-10-05–2026-10-08 | −$9,051.95 | $90,670.58 | 56.49 | 100.47% | −$0.04 | 24.89 | Tak |
| MU, 2026-10-09 | −$1,664.04 | $51,207.89 | 50.20 | 98.08% | −$6.32 | 13.35 | Tak |

## Porównanie z wcześniejszymi zyskownymi cyklami

Wśród 26 wcześniejszych zyskownych cykli RSI14 miał medianę 50.95 i zakres 37.12–76.10. Mediana Disparity14 wyniosła 98.68%, a 16 z 26 odczytów było poniżej 100%. MACD Hist był ujemny w 12 cyklach. Mediana ADX14 wyniosła 17.51. Układ SMA20 > SMA50 > SMA200 wystąpił w 12 cyklach.

### INTC

- RSI 56.49 i Disparity14 100.47% mieściły się w zakresach wcześniejszych zyskownych wejść na INTC.
- MACD Hist spadł z +1.34 przy zyskownym wejściu 2026-09-29 do −0.04 przy wejściu 2026-10-05. To wskazuje na osłabienie krótkoterminowego momentum, choć sam odczyt był bliski zera.
- ADX14 wyniósł 24.89, podobnie jak 24.33 przy poprzednim zyskownym wejściu. ADX opisuje siłę trendu, ale bez dodatkowych danych nie wskazuje jego kierunku.
- Wolumen wyniósł 81.3 mln, mniej niż przy czterech wcześniejszych zyskownych wejściach na INTC (88.7–181.1 mln). OBV spadł z 3.813 mld przy wejściu 2026-09-29 do 3.628 mld.
- Średnie SMA nadal układały się wzrostowo. Zatem ostrzeżenie wynikało raczej z osłabienia MACD i niższego wolumenu niż z układu średnich.

### MU

- Disparity14 wyniosło 98.08%, poniżej 100% i poniżej wszystkich sześciu wcześniejszych zyskownych wejść na MU (98.91–103.25%).
- RSI 50.20 mieściło się w typowym zakresie dla wcześniejszych zysków na MU (47.02–59.66), ale było niższe od ich mediany 52.59.
- MACD Hist wyniósł −6.32. Przy poprzednim zyskownym wejściu 2026-10-06 wynosił −1.22. W relacji do ATR14 te odczyty wynosiły odpowiednio około −13.7% i −2.8%, więc ujemne momentum było wyraźniejsze.
- OBV spadł z 1.387 mld przy wejściu 2026-10-06 do 1.368 mld. ADX14 wyniósł 13.35 i mieścił się w zakresie wcześniejszych zyskownych wejść na MU (10.38–18.57).
- Średnie SMA nadal układały się wzrostowo, ale kilka wskaźników krótkoterminowych pokazywało słabość jednocześnie.

## Wniosek i ograniczenia

Przy INTC sygnał osłabienia był subtelny: MACD Hist znalazł się tuż poniżej zera, a wolumen był niski w porównaniu z wcześniejszymi wejściami na ten ticker. Przy MU słabość była wyraźniejsza: Disparity14 spadło poniżej 100%, MACD Hist stał się mocniej ujemny, a OBV obniżyło się względem poprzedniego odczytu.

Wskaźniki opisują warunki w dniu rozpoczęcia kupna, ale nie dowodzą przyczyny późniejszej straty. Próbka obejmuje 28 cykli, więc porównania są orientacyjne. Surowych wartości MACD, ATR, wolumenu i OBV nie należy bezpośrednio porównywać między różnymi tickerami ze względu na ich różną skalę. Kwoty z pliku są brutto, bez prowizji.
