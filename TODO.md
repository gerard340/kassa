# Kassa - TODO / open punten

Status-legenda: [ ] open  [~] deels in POC  [x] klaar

## Supermarkt-specifieke functies (bepalen mee de omvang)
- [~] Statiegeld: apart bedrag op de bon, btw-vrij. (POC: statiegeld per product als aparte regel; inname van statiegeldbonnen van de emballage-automaat nog niet)
- [~] Leeftijdscontrole (NIX18) bij alcohol: verplichte prompt op de kassa. (POC: eenvoudige ja/nee-prompt bij het toevoegen van een leeftijdsgebonden product)
- [ ] Weegschaal-barcodes (prefix 20-29 met ingebed gewicht of prijs) als er een weegschaal in de versafdeling staat.
- [ ] Acties: 2 voor 1, procent korting, tijdelijke prijs.
- [ ] Dagafsluiting (Z-rapport). Kastelling, kasverschil en wisselgeld-opname vervallen (geen contant geld), maar een dagrapport per pin-terminal blijft nodig.
- [ ] Retouren en bon annuleren met logging. (Kassiers met pincode-login vervallen: scan/pin only, geen kassalade.)
- [ ] Bewaarplicht: alle bonnen 7 jaar bewaren. NL kent geen fiscale zwarte doos zoals Belgie, dus geen gecertificeerde printer nodig. Bon moet wel btw-splitsing, KvK en bedrijfsnaam tonen.
- [ ] Koppeling met de boekhouding (Moneybird?) voor de dagomzet.

## Nog te beantwoorden vragen
- [ ] Vraag 3: Is er een weegschaal in de winkel? Wordt statiegeld ingenomen via een automaat of handmatig?
- [ ] Vraag 4: Wordt er alcohol verkocht? (bepaalt NIX18-prompt en 21% btw op alcohol)
- [ ] Vraag 5: Hoeveel artikelen ongeveer, en bestaat er al een productlijst (Excel, van de groothandel)?
- [ ] Vraag 7: Moeten inkooporders en leveringen van de groothandel in het systeem, of alleen "voorraad bijboeken"?
- [ ] Vraag 9: Klantenkaart, spaarsysteem of kassabon per e-mail gewenst?
- [ ] Vraag 12: Budget voor hardware (tablet, scanner, printer, terminal) - nog te bespreken.
- [ ] Pinprovider kiezen en account openen (Mollie of Adyen, zie README). Testomgeving aanvragen.

## Besloten
- [x] Pin via cloud-terminal-API (geen native SDK).
- [x] Platform: Android-tablet, kassa-app als device owner in Lock Task Mode.
- [x] Geen kassiers, geen contant geld, geen kassalade: scan/pin only.
- [x] Beheer: zowel op afstand (Gerard) als door de winkelier zelf -> portaal moet simpel zijn.
- [x] Eerst 1 winkel, later mogelijk meer: datamodel heeft vanaf dag 1 een store_id. Inloggen hoeft niet in de demo.
- [x] Naast scannen ook producten toevoegen via categorie-tegels op het scherm.
- [x] Product is alleen zichtbaar in de kassa als het in een categorie zit. Subcategorieen zijn optioneel en werken als filter binnen de gekozen categorie.

## Techniek (na de POC)
- [ ] Offline-first: lokale opslag op de tablet + synchronisatiewachtrij naar de cloud.
- [ ] Android-schil (Kotlin of Capacitor) met Lock Task Mode / device owner.
- [ ] Bonprinter ESC/POS over LAN (poort 9100), bijv. Epson TM-m30III of Star mC-Print3.
- [ ] Scanner: 2D-scanner in HID-modus (USB of Bluetooth).
- [ ] Echte pinkoppeling (Mollie Terminal API of Adyen Terminal API) inclusief storing/terugval en dagrapport.
- [ ] Cloudportaal: rapporten, voorraad bijwerken, Excel-import/export van producten en voorraad, categoriebeheer.
- [ ] Multi-store: store-selectie, per-winkel prijzen/voorraad, inloggen en rollen.
- [ ] Beeldbeheer producten (echte afbeeldingen uploaden in het portaal).
