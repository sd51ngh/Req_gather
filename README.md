# MRP & ERP Requirement Gathering Assistant (Team & Workshop Edition)

A collaborative, real-time web application for conducting manufacturing ERP, MRP, and MES requirement gathering workshops. Built with a zero-dependency Python standard-library backend (`server.py` + SQLite WAL persistence + Server-Sent Events) and two live views:

- **Staff Workspace (`/` or `/staff`)**: Authenticated team workspace where multiple consultants/engineers can scope modules, set priorities and criticality, push timestamped notes simultaneously without overwriting each other, switch between client companies, and export reports (Markdown, JSON, Excel CSV).
- **Client Workshop Screen (`/client`)**: Sanitised, projector-friendly live overview that shows the active company name, overall progress, and module/topic check-offs—while keeping the **active topic card automatically pinned and expanded at the top of the screen** and never exposing internal notes, guidance prompts, or priorities.

---

## Quick Start

```bash
# Start the server on http://localhost:8000
python server.py

# Add a team member or administrator from the CLI
python server.py adduser alice
python server.py adduser bob --admin

# Reset a user's password
python server.py passwd alice
```

---

## Built-in Manufacturing Industry Presets

Staff can create and switch between multiple client companies from the **Companies & Presets** menu in the sidebar or top header. Each new company can be initialised with one of the following industry presets (defined in `backend/presets.py`):

1. **Metal Fabrication & Precision Engineering (`metal_fabrication`)** — 15 modules covering multi-level & variant BOMs, estimating/quoting, job routing, APS, shop floor data collection (SFDC), QMS/CAPA, pick/pack/despatch, field service/MRO, customer ticketing portal, HR skills matrix, integrations, dashboards, and finance.
2. **Injection Moulding & Plastics (`injection_moulding`)** — 12 modules covering multi-cavity & family moulds, shot counters & tool maintenance, runner/regrind % & masterbatch dosing, press clamp tonnage & colour sequence scheduling, Euromap/OPC-UA cycle monitoring, resin drying & silo control, SPC/PPAP/ISIR, and tooling amortisation.
3. **Food Processing & Beverage (`food_beverage`)** — 11 modules covering multi-stage recipes, cooking yield/evaporation, 14-allergen matrices, nutritional/QUID calculation, strict FEFO & retailer minimum remaining shelf-life (MLOR), catch-weight inventory & billing, allergen/CIP washdown scheduling, dispensary scale interlocks, digital HACCP, BRCGS 4-hour recall traceability, and supermarket EDI.
4. **Pharmaceutical & Life Sciences (`pharma_lifesciences`)** — 11 modules covering Master Batch Records (MBR/DMR), API potency/assay compensation, 21 CFR Part 11 / EU GMP Annex 11 Electronic Batch Records (eBR/eDHR) with review-by-exception, weigh & dispense booths, GMP quarantine/retest statuses, LIMS/CoA/OOS/stability, QP certification, serialisation (FMD/DSCSA) & UDI, cleanroom logbooks, and GAMP 5 CSV.
5. **Chemical, Coatings & Process Manufacturing (`chemical_process`)** — 11 modules covering weight/volume/% formulas with SG/VOC/solids roll-up, co-products & solvent recovery, GHS/CLP drum labelling, SDS & UK/EU REACH tonnage tracking, reactor/tank farm scheduling, metered vessel charging, multi-container pack-out (IBC, drum, pail), hazmat segregation, ADR Dangerous Goods Notes (DGN), and ATEX compliance.
6. **Electronics, PCB & High-Tech Assembly (`electronics_assembly`)** — 7 modules covering CAD/EDA BOM import with reference designators, Approved Manufacturer Lists (AML/AVL), distributor API quoting, unique reel IDs & JEDEC MSL floor-life tracking, SMT feeder grouping, panel-to-board serial genealogy, AOI/X-ray/ICT test capture, IPC-A-610/RoHS/REACH, and RMA repair.
7. **Automotive, Aerospace & Complex Discrete (`automotive_aerospace`)** — 7 modules covering serial/tail/VIN BOM effectivity, As-Designed vs As-Built digital thread, ITAR/export control, AS9102 FAIR & PPAP, OEM EDI (DELFOR/DELJIT) & Kanban, digital route cards with smart torque wrench & NADCAP operator certification interlocks, and aftermarket MRO.
8. **Blank Custom Workspace (`blank`)** — Empty workspace to build custom modules and focus items from scratch.

---

## Changelog

> **Maintenance Rule:** Always update this Changelog section whenever any changes are made to the codebase.

### v2.1.0 — 2026-11-02
- **Client Screen — Active Card Always Pinned at Top (`web/client.js`, `web/client.css`, `web/client.html`)**:
  - Updated the `/client` screen so the currently active module card (spotlighted by staff, opened in the staff drawer, most recently updated, or clicked on the client screen) is automatically placed at **index 0 at the very top of the topic grid** and expanded full-width in a multi-column layout.
  - Inside the active card, the spotlighted requirement item is also sorted to the top of the item list and highlighted so viewers never have to scroll down to see bottom cards or items.
  - Added the active company name and industry preset badge to the client screen header and hero section.
- **Multi-Company Management (`backend/store.py`, `server.py`, `web/staff.html`, `web/staff.js`, `web/staff.css`)**:
  - Added `companies` table and automatic non-destructive SQLite schema migration (`modules.company_id`, `companies.last_active_module_id`) so existing databases upgrade seamlessly.
  - Added staff API endpoints (`GET /api/companies`, `POST /api/companies`, `PUT /api/companies/active`, `PATCH /api/companies/<id>`, `DELETE /api/companies/<id>`) allowing any signed-in staff member to create, switch, rename, and delete companies.
  - Added quick company switcher in the sidebar, active company button in the top header, and a full **Companies & Industry Presets** modal (`#companies-modal`).
  - Automatically spotlights a module on the client screen when a staff member opens its drawer (`openDrawer`), and prefixes exported Markdown/CSV/JSON filenames with the active company's slug.
- **Manufacturing Industry Presets (`backend/presets.py`)**:
  - Preserved the existing 15-module configuration as the **Metal Fabrication & Precision Engineering** preset.
  - Created 6 new sector-specific presets (**Injection Moulding & Plastics**, **Food Processing & Beverage**, **Pharmaceutical & Life Sciences**, **Chemical, Coatings & Process Manufacturing**, **Electronics, PCB & High-Tech Assembly**, **Automotive, Aerospace & Complex Discrete**) plus a **Blank Custom Workspace** option.
- **Changelog & Documentation (`README.md`)**:
  - Created `README.md` with project documentation and a persistent Changelog section to be updated on every change.

### v2.0.0 — 2026-11-01
- **Collaborative Python Backend & Dual-Screen Architecture (`server.py`, `backend/`, `web/`)**:
  - Added threaded Python HTTP server (`server.py`) with SQLite WAL persistence (`backend/store.py`), PBKDF2-SHA256 authentication & rate limiting (`backend/auth.py`), and Server-Sent Events pub/sub hub (`backend/events.py`).
  - Built real-time collaborative Staff Workspace (`web/staff.html`, `web/staff.js`, `web/staff.css`) with append-only multi-author notes, live presence avatars, and client screen controls.
  - Built sanitised public Client Screen (`web/client.html`, `web/client.js`, `web/client.css`) with strict allow-list data isolation.

### v1.0.0 — Initial Single-Page Edition
- Initial client-side MRP & ERP Requirement Gathering Assistant (`index.html`, `app.js`, `style.css`, `ReqGather_Backup_Config.json`, `cheatsheet.md`) with dark/light theme, font scaling, and Markdown/CSV/JSON exports.

