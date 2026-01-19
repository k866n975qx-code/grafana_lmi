# LMI Grafana Upgrade / Maintenance Doc (OptiPlex)

## 1) What is running where

### Grafana (Docker)
- Runs as a Docker container on the OptiPlex server (**192.168.12.221**)
- Exposes port: **3000**
- Accessible:
  - LAN: `http://192.168.12.221:3000`
  - Tunnel: `https://grafana.joseai.dev`

### LMI DB (SQLite)
- Real DB used by the LMI service:
  - `/home/jose/lmi-service/data/app.db`

Tables used by dashboards:
- `snapshot_daily_current` → daily “as_of_date_local” snapshots (JSON in `payload_json`)
- `snapshots` → period snapshots (WEEK/MONTH/QUARTER/YEAR) (JSON in `payload_json`)

---

## 2) Where the Grafana provisioning files live (server)

All provisioned dashboard + datasource files live here:

```bash
/home/jose/grafana_lmi/grafana_lmi/
```

### Dashboards (JSON)
```bash
/home/jose/grafana_lmi/grafana_lmi/dashboards/
```

Examples:
- `lmi-overview.json`
- `lmi-income.json`
- `lmi-holdings.json`
- `lmi-risk.json`
- `lmi-attribution.json`
- `lmi-dividend-calendar.json`
- `lmi-diff-*.json`
- `lmi-latest-periods.json`

### Datasource provisioning
```bash
/home/jose/grafana_lmi/grafana_lmi/provisioning/datasources/sqlite.yaml
```

This defines:
- datasource name + uid: `lmi_sqlite`
- sqlite file path mount (the DB path Grafana reads)

---

## 3) Method used to update dashboards (correct workflow)

Grafana dashboards are **provisioned** (loaded from JSON files).  
That means the correct way to update is:

### Step A — edit the JSON file on the server
Example:
```bash
nano /home/jose/grafana_lmi/grafana_lmi/dashboards/lmi-overview.json
```

### Step B — restart Grafana container to reload provisioning
```bash
docker restart grafana
```

### Step C — refresh browser
Open Grafana and confirm the dashboard changed.

**Important:**
- If you edit dashboards inside the Grafana UI, those changes can get overwritten by provisioning depending on your setup.
- The source of truth is the JSON files in `/home/jose/grafana_lmi/...`

---

## 4) How to safely “upgrade” dashboards

### Recommended method
1) Make a backup copy before editing:
```bash
cp /home/jose/grafana_lmi/grafana_lmi/dashboards/lmi-risk.json \
   /home/jose/grafana_lmi/grafana_lmi/dashboards/lmi-risk.json.bak
```

2) Edit the file
3) Restart Grafana container:
```bash
docker restart grafana
```

---

## 5) Copy provisioning files to your Mac (backup/edit)

From your Mac:

### Copy everything
```bash
scp -r jose@192.168.12.221:/home/jose/grafana_lmi ~/backups/
```

### Copy only dashboards + provisioning
```bash
mkdir -p ~/backups/grafana_lmi
scp -r jose@192.168.12.221:/home/jose/grafana_lmi/grafana_lmi/dashboards ~/backups/grafana_lmi/
scp -r jose@192.168.12.221:/home/jose/grafana_lmi/grafana_lmi/provisioning ~/backups/grafana_lmi/
```

### Push changes back to server
(Example: updated dashboards folder)
```bash
scp -r ~/backups/grafana_lmi/dashboards \
  jose@192.168.12.221:/home/jose/grafana_lmi/grafana_lmi/
```

Then restart Grafana:
```bash
docker restart grafana
```

---

## 6) How the Surface dashboard appliance works

Surface (Ubuntu) runs Chromium kiosk pointed at:

- Playlist cycle:
  - `https://grafana.joseai.dev/playlists/play/afai0fb1kulfkc?kiosk=true&autofitpanels=true`

It boots into a local page first:

- Local kiosk page:
  - `http://127.0.0.1:8765/index.html`

That local page provides:
- Switchboard link
- Start Cycle link
- Auto-start cycle after 60 seconds

HOME escape:
- A small always-on-top HOME button kills Chromium
- `grafana-kiosk.service` restarts Chromium back into the kiosk start page

Night mode:
- cron dims brightness to `0` at 8pm
- restores brightness to max at 8am

---

## 7) Quick “health check” commands

On OptiPlex:

### Grafana container running?
```bash
docker ps | grep grafana
```

### LMI service running?
```bash
ps aux | grep lmi-service | grep uvicorn
```

### LMI DB has snapshots?
```bash
sqlite3 /home/jose/lmi-service/data/app.db \
"SELECT COUNT(*) FROM snapshot_daily_current;"
```
