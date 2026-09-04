# Deploy - Kassa

Zelfde opzet als ZettleToMoneyBird: Docker-container op een lokale poort op de
kiwi-main VPS (195.201.219.169), Caddy ervoor als reverse proxy met automatische HTTPS.

| | |
|---|---|
| URL | https://kassa.kiwi-ict.nl |
| Map op de server | `~/apps/kassa` |
| Container | `kassa`, poort **127.0.0.1:3004** (niet publiek) |
| Webserver | gunicorn (2 workers, 4 threads, `--preload`) |
| Gegevens | `~/apps/kassa/data/kassa.db` (SQLite) |

## Bijwerken na een codewijziging

Vanaf de projectmap op de pc:

```bash
tar --exclude='.venv' --exclude='data' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='.claude' -czf - . | ssh kiwi-main 'mkdir -p ~/apps/kassa && tar -xzf - -C ~/apps/kassa && cd ~/apps/kassa && docker compose up -d --build'
```

`data/` zit niet in de tar en is een volume: verkopen en voorraad blijven bij een deploy staan.

## Demodata opnieuw laden

De database wordt alleen geseed als hij leeg is. Opnieuw beginnen:

```bash
ssh kiwi-main 'cd ~/apps/kassa && docker compose down && rm -f data/kassa.db && docker compose up -d'
```

## Handige commando's

```bash
ssh kiwi-main 'cd ~/apps/kassa && docker compose logs -f --tail 50'
```

## Caddy

In `/etc/caddy/Caddyfile`:

```
kassa.kiwi-ict.nl {
    reverse_proxy localhost:3004
}
```

Na een wijziging: `sudo caddy validate --config /etc/caddy/Caddyfile` en `sudo systemctl reload caddy`.

## Let op

De POC heeft nog geen login. Iedereen die de URL kent kan de kassa bedienen en
`/admin` bekijken. Dat is bewust voor de demo; voor een echte winkel komt hier
authenticatie (zie TODO.md).
