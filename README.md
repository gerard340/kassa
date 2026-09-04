# Kassa (POC)

Kassasysteem voor een kleine supermarkt. Dit is de browser-POC: nog geen Android, geen echte pin, geen printer.

## Starten

    start.bat

of handmatig:

    python -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt
    .venv\Scripts\python app.py

- Kassa:  http://localhost:5050/
- Beheer: http://localhost:5050/admin  (voorproefje van het cloud-portaal)

Bij de eerste start wordt `data/kassa.db` aangemaakt en gevuld met demodata (62 producten, 8 categorieen
met subcategorieen, gegenereerde SVG-afbeeldingen in `static/img/products/`). Database weggooien = opnieuw seeden.

## Wat de POC laat zien

- Categorie-tegels -> producten van die categorie, subcategorieen als filter-chips ("Alles" + subs).
- Producten zonder categorie zijn NIET zichtbaar in de kassa, maar wel scanbaar (voorbeeld: Cadeaubon).
- Zoeken op naam of barcode.
- Scanner: een HID-scanner typt de EAN + Enter; de pagina vangt dat globaal af. Zonder scanner: paneel
  "Scanner-simulatie" rechtsonder.
- Bon met aantallen, statiegeld als aparte btw-vrije regel, btw-splitsing 9%/21%.
- NIX18-prompt bij een leeftijdsgebonden product (1x per bon).
- Gesimuleerde pinbetaling (terminal-animatie, altijd geslaagd), daarna de bon (afdrukbaar via Bon afdrukken).
- Verkoop wordt opgeslagen, voorraad wordt afgeboekt; zichtbaar in /admin.

## Structuur

    app.py              Flask-routes (pagina's + JSON-API)
    kassa/db.py         SQLite-schema (bedragen in centen, prijzen incl. btw, store_id voor multi-store)
    kassa/seed.py       demodata + SVG-generator
    templates/          kassa.html, admin.html, receipt.html
    static/js/kassa.js  kassalogica (geen framework)
    static/css/kassa.css
    TODO.md             open punten en besluiten

## API

    GET  /api/catalog                 winkel + categorieen (met subcategorieen) + zichtbare producten
    GET  /api/products/by-ean/<ean>   product op barcode (ook zonder categorie)
    POST /api/payments/pin            {amount_cents} -> gesimuleerde goedkeuring + referentie
    POST /api/sales                   {lines:[{product_id,qty}], payment:{method,ref}} -> bon; prijzen komen uit de DB
    GET  /api/sales/<id>              bon als JSON

## Pinprovider (nog te kiezen)

Cloud-terminal-API betekent: de kassa stuurt het bedrag via internet naar de provider, de terminal in de winkel
toont het, de kassa krijgt het resultaat terug. Daarvoor is een merchant-account bij die provider nodig
(op naam van de winkel: KvK, IBAN). Kandidaten: Mollie Terminal, Adyen Terminal API, CCV, SumUp. Zie TODO.md.
