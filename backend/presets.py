"""Industry presets for the Requirement Gathering Assistant.

Each preset provides a curated list of modules and focus items tailored to a
specific manufacturing sector, while sharing the same data structure as
``ReqGather_Backup_Config.json``.
"""
import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SEED_FILE = os.path.join(ROOT, "ReqGather_Backup_Config.json")

# Reusable clean SVG icons (Heroicons outline style, all safe under _SAFE_SVG_TAGS)
ICONS = {
    "bom": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>',
    "quote": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 7.5L12 10.5M12 10.5L15 7.5M12 10.5V16.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
    "sales": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" /></svg>',
    "planning": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5m-9-6h.008v.008H12v-.008zM12 15h.008v.008H12V15zm0 2.25h.008v.008H12v-.008zM9.75 15h.008v.008H9.75V15zm0 2.25h.008v.008H9.75v-.008zM7.5 15h.008v.008H7.5V15zm0 2.25h.008v.008H7.5v-.008zm6.75-4.5h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V15zm0 2.25h.008v.008h-.008v-.008zm2.25-4.5h.008v.008H16.5v-.008zm0 2.25h.008v.008H16.5V15z" /></svg>',
    "stock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" /></svg>',
    "production": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12a7.5 7.5 0 0015 0m-15 0a7.5 7.5 0 1115 0m-15 0H3m16.5 0H21m-1.5 0H12m-8.457 3.077l1.41-.513m14.095-5.13l1.41-.513M5.106 17.785l1.15-.827m11.379-8.16l1.15-.827M8.14 21.27l.707-1.03m7.65-11.12l.707-1.03M12 3v1.5m0 15V21m-3.077-8.457l-.513-1.41m5.13 14.095l-.513-1.41M17.785 5.106l-.827 1.15m-8.16 11.379l-.827 1.15m-3.03-8.62l-1.03-.707m11.12 7.65l-1.03-.707" /></svg>',
    "qms": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0110 21a3.746 3.746 0 01-3.068-.593 3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0114 3c1.251 0 2.396.618 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" /></svg>',
    "despatch": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124l-.047-.75m-14.773-2.625h14.773M2.25 12.75V4.875A1.125 1.125 0 013.375 3.75h9.81c.318 0 .624.146.82.4l3.06 3.89c.18.23.28.514.28.808v.538m0-2.25H12a1.125 1.125 0 01-1.125-1.125V3.75m-9 10.5h16.5V18a1.5 1.5 0 01-1.5 1.5h-13.5A1.5 1.5 0 012.25 18v-3.75z" /></svg>',
    "tools": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.67 2.67 0 1113.5 17.25l-5.83-5.83m.084-2.113l-5.83-5.83A2.67 2.67 0 115.67 1.83l5.83 5.83m0 0L17.25 1.83A2.67 2.67 0 1121 5.67l-5.83 5.83m0 0L21 17.25a2.67 2.67 0 11-3.75 3.75l-5.83-5.83" /></svg>',
    "portal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 6v.75m0 3v.75m0 3v.75m0 3V18m-9-12h12c1.38 0 2.5 1.12 2.5 2.5v7c0 1.38-1.12 2.5-2.5 2.5h-12A2.5 2.5 0 015 15.5v-7A2.5 2.5 0 017.5 6z" /></svg>',
    "hr": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a.75.75 0 000-1.5.75.75 0 000 1.5zM12 18.72a.75.75 0 000-1.5.75.75 0 000 1.5zM6 18.72a.75.75 0 000-1.5.75.75 0 000 1.5zM12 12.75a3 3 0 100-6 3 3 0 000 6zM2.25 12a9.75 9.75 0 0119.5 0c0 .35-.018.692-.053 1.03a9.75 9.75 0 11-19.394 0c-.035-.338-.053-.68-.053-1.03z" /></svg>',
    "integrations": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" /></svg>',
    "dashboards": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>',
    "questions": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" /></svg>',
    "finance": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.83-1.106-2.171 0-3.007.562-.439 1.278-.659 2.003-.659.725 0 1.45.22 2.003.659.271.203.48.455.626.732M12 2a10 10 0 110 20 10 10 0 010-20z" /></svg>',
    "lab": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" /></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>',
    "chip": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z" /></svg>',
}


def _mod(mid, title, desc, icon_key, items):
    return {
        "id": mid,
        "title": title,
        "description": desc,
        "icon": ICONS.get(icon_key, ICONS["bom"]),
        "items": [
            {
                "id": iid,
                "name": name,
                "guidance": guidance,
                "scope": "pending",
                "priority": "phase2",
                "criticality": "normal",
                "notes": [],
            }
            for iid, name, guidance in items
        ],
    }


def _load_metal_fabrication(seed_path=None):
    path = seed_path or DEFAULT_SEED_FILE
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8-sig") as fh:
                return json.load(fh)
        except Exception:
            pass
    return []


# ---------------------------------------------------------------------------
# 2. Injection Moulding & Plastics Manufacturing
# ---------------------------------------------------------------------------
INJECTION_MOULDING_MODULES = [
    _mod(
        "tooling-mould-cavity",
        "Tooling, Moulds & Cavity Management",
        "Manage multi-cavity moulds, family tools, shot counters, preventive tool maintenance, and runner/regrind calculations.",
        "tools",
        [
            ("multi-cavity-bom", "Multi-Cavity & Family Mould BOMs",
             "Focus: Handling tools with 1, 2, 4, 16+ cavities, family moulds producing multiple different part numbers per shot, and blocked-off cavities when one cavity is damaged."),
            ("shot-counter-tool-life", "Tool Life & Shot Counter Tracking",
             "Focus: Automatically counting press cycles/shots against each mould tool and triggering alerts when preventive maintenance or refurbishment is due (e.g. every 50,000 shots)."),
            ("regrind-runner-calc", "Sprue, Runner & Regrind % Calculation",
             "Focus: Calculating shot weight = part weight + runner weight, tracking granulated regrind, and enforcing maximum allowed regrind percentage (e.g. 85% virgin / 15% regrind)."),
            ("masterbatch-dosing", "Masterbatch, Colourant & Additive Dosing",
             "Focus: Defining let-down ratios (e.g. 2% colour masterbatch, UV stabiliser, flame retardant) and linking them to gravimetric or volumetric dosing units."),
            ("insert-overmoulding", "Insert Moulding & Overmoulding Sub-Assemblies",
             "Focus: Managing brass/metal threaded inserts or substrate parts that are loaded into the press during the moulding cycle."),
            ("customer-owned-tooling", "Customer-Owned Tooling Register & Location",
             "Focus: Tracking which customer owns each mould tool, tool storage rack location, insurance value, and customer sign-off before tool modifications."),
        ],
    ),
    _mod(
        "press-planning-scheduling",
        "Press Planning, Tonnage & Sequencing (APS)",
        "Schedule injection moulding presses by clamp tonnage, shot size, colour sequence, and tool availability.",
        "planning",
        [
            ("press-tonnage-matching", "Press Clamp Tonnage & Tie-Bar Compatibility",
             "Focus: Restricting which presses a mould can run on based on clamp tonnage (e.g. 50T to 1200T), platen/tie-bar spacing, screw size, and robot interface."),
            ("colour-sequence-optimisation", "Colour & Material Sequence Optimisation",
             "Focus: Grouping jobs from natural/light to dark colours and compatible polymers (PP, ABS, PA66, PC) to minimise barrel purging time and resin waste."),
            ("smed-tool-changeover", "Tool Changeover (SMED) & Setter Scheduling",
             "Focus: Scheduling finite setter/technician availability so two presses aren't scheduled for a 3-hour mould change at the same time."),
            ("lights-out-shift-planning", "24/7 & Lights-Out Unmanned Shift Planning",
             "Focus: Planning automated cell runs overnight or on weekends vs jobs requiring dedicated manual de-gating or packing operators."),
            ("mrp-resin-packaging", "MRP for Resin, Masterbatch, Inserts & Cartons",
             "Focus: Calculating exact kg of polymer, masterbatch, and gaylord/carton packaging needed across the 4–12 week production schedule."),
            ("trial-sample-scheduling", "NPI Tool Trials (T0, T1, T2) Scheduling",
             "Focus: Slotting engineering mould trials and sampling runs into the press schedule without disrupting volume production."),
        ],
    ),
    _mod(
        "mes-press-monitoring",
        "Shop Floor Execution (MES) & Press Monitoring",
        "Capture live cycle times, shot counts, downtime reasons, cavitation changes, and scrap on the press.",
        "production",
        [
            ("real-time-cycle-monitoring", "Real-Time Cycle Time & Shot Count Capture",
             "Focus: Connecting presses (via dry contacts, OPC-UA, or Euromap 63/77) to compare actual cycle time (e.g. 24.5s) against quoted standard cycle time (22.0s)."),
            ("scrap-defect-codes", "Moulding Scrap & Defect Reason Logging",
             "Focus: Operator touchscreens to log start-up purge scrap and part defects (short shots, flash, sink marks, weld lines, splay, burn marks, warpage)."),
            ("active-cavity-override", "Live Active-Cavity Adjustment on Shop Floor",
             "Focus: Updating the job's active cavities (e.g. 7 of 8 cavities running) so completion time and part count per shot recalculate automatically."),
            ("resin-backflushing", "Automated Resin, Regrind & Masterbatch Backflushing",
             "Focus: Automatically deducting polymer and colourant from line-side dryers/gaylords as good and scrap shots are recorded."),
            ("digital-set-sheets", "Digital Mould Setup Sheets & Process Parameters",
             "Focus: Displaying approved barrel temperatures, injection pressures, cooling times, and robot programs at the press terminal."),
            ("box-ticket-labelling", "Automated Box/Pallet Barcode Label Printing",
             "Focus: Printing a barcode label automatically every N shots when a carton or stillage reaches its standard pack quantity."),
        ],
    ),
    _mod(
        "polymer-warehouse-inventory",
        "Polymer, Silo & Warehouse Management",
        "Track bulk silos, octabins/gaylords, resin drying times, regrind batches, and finished moulded stock.",
        "stock",
        [
            ("silo-octabin-tracking", "Bulk Silo, Octabin & 25kg Bag Inventory",
             "Focus: Managing bulk resin deliveries into silos alongside octabins/gaylords and partial bags returned from the shop floor."),
            ("resin-drying-control", "Hygroscopic Resin Drying Time & Moisture Tracking",
             "Focus: Ensuring materials like Nylon (PA), PC, PBT, and PET are dried for the required hours and dew point before moulding begins."),
            ("regrind-batch-traceability", "Regrind Generation & Lot Traceability",
             "Focus: Labelling granulated runners/sprues by polymer grade, colour, and source batch so regrind isn't cross-contaminated."),
            ("fifo-lot-control", "Polymer Lot/Batch FIFO & Location Control",
             "Focus: Scanning resin lot numbers at the press hopper or central material feed manifold for full forward/backward traceability."),
            ("returnable-packaging", "Returnable Stillages, Tote Bins & Layer Pads",
             "Focus: Tracking customer-owned collapsible boxes, KLT totes, and pallet collars shipped to and returned from customers."),
        ],
    ),
    _mod(
        "plastics-qms-spc",
        "Quality Management (QMS), SPC & PPAP",
        "Manage First-Off/Last-Off checks, in-process patrol inspections, SPC part weight/dimension charting, and PPAP/ISIR.",
        "qms",
        [
            ("first-last-off-inspection", "First-Off, Patrol & Last-Off Press Approval",
             "Focus: Hard-gating production until QA or the setter approves the First-Off sample after a tool change or restart, and retaining the Last-Off shot for tool health review."),
            ("spc-weight-dimensions", "Statistical Process Control (SPC) & Part Weight Checks",
             "Focus: Recording hourly cavity-by-cavity part weights and critical CTQ dimensions with live Cp/Cpk control charts."),
            ("ppap-isir-management", "PPAP / ISIR & Control Plan Documentation",
             "Focus: Managing Production Part Approval Process (PPAP) packages, dimensional layouts, material certs, and PFMEAs."),
            ("incoming-resin-coa", "Incoming Resin Certificate of Analysis (CoA) & MFI",
             "Focus: Verifying supplier CoA and Melt Flow Index (MFI) / density test results before releasing polymer batches to stock."),
            ("quarantine-capa-8d", "Quarantine, Concession & 8D CAPA Workflows",
             "Focus: Blocking suspect pallets by time-window (e.g. shots moulded between 02:00 and 04:00) and generating customer 8D root-cause reports."),
        ],
    ),
    _mod(
        "estimating-quoting-plastics",
        "Estimating, Quoting & Tooling Amortisation",
        "Calculate part cost from shot weight, cycle time, cavitation, and press rate, plus tooling quotes.",
        "quote",
        [
            ("cycle-weight-calculator", "Part Cost Calculator (Weight, Cycle Time & Cavities)",
             "Focus: Quoting part unit cost from resin price/kg, part + runner weight, regrind credit, cycle time (s), cavitation, press hourly rate, and packing labour."),
            ("tooling-project-quoting", "Mould Tooling Quoting & Milestone Billing",
             "Focus: Quoting new mould tools with staged payment milestones (e.g. 40% on order, 40% on T1 sample, 20% on PPAP sign-off)."),
            ("tooling-amortisation", "Tooling Cost Amortisation over Piece Price",
             "Focus: Spreading tooling cost over the first X,000 moulded parts and automatically dropping the piece price once amortised."),
            ("resin-index-adjustments", "Polymer Price Index Escalation / De-escalation",
             "Focus: Adjusting customer part prices quarterly when raw polymer prices move beyond an agreed band."),
            ("moq-volume-breaks", "MOQ, Setup Recovery & Tiered Volume Breaks",
             "Focus: Quoting price breaks for 1,000 vs 10,000 vs 100,000 parts to cover tool setup and barrel purge costs."),
        ],
    ),
    _mod(
        "sales-edi-calloffs",
        "Sales Orders, Blanket Call-Offs & EDI",
        "Process scheduled customer call-offs, EDI forecasts, blanket orders, and despatch schedules.",
        "sales",
        [
            ("blanket-orders-calloffs", "Blanket Sales Orders & Scheduled Call-Offs",
             "Focus: Managing annual blanket agreements with weekly/monthly delivery schedules and firm vs forecast horizons."),
            ("edi-automotive-retail", "Customer EDI Integration (DELFOR, DELJIT, ASN)",
             "Focus: Importing customer schedules electronically and sending Advance Shipping Notices (ASN) on despatch."),
            ("min-stock-buffer-agreements", "Consignment & Buffer Stock Agreements",
             "Focus: Holding agreed safety stock of moulded parts for rapid call-off while tracking customer liability."),
        ],
    ),
    _mod(
        "subcontract-purchasing",
        "Purchasing, Toolmakers & Secondary Operations",
        "Procure polymers, inserts, packaging, and subcontracted toolmaking, chrome plating, or ultrasonic welding.",
        "despatch",
        [
            ("subcontract-toolmaking", "Subcontract Toolmaker & Mould Repair Tracking",
             "Focus: Sending mould tools out for modification, laser texturing, hot-runner repair, or polishing and tracking return dates."),
            ("secondary-ops-post-moulding", "Post-Moulding Assembly, Printing & Ultrasonic Welding",
             "Focus: Routing moulded parts through pad printing, laser marking, ultrasonic welding, heat staking, or kitting."),
            ("supplier-otd-scorecards", "Polymer & Insert Supplier Scorecards",
             "Focus: Rating resin distributors and metal insert suppliers on delivery reliability, price variance, and CoA compliance."),
        ],
    ),
    _mod(
        "dashboards-oee-energy",
        "OEE, Scrap & Energy Dashboards",
        "Monitor live press OEE, cavitation efficiency, scrap rate, and kWh per kg energy consumption.",
        "dashboards",
        [
            ("press-oee-dashboard", "Live Press OEE (Availability, Performance, Quality)",
             "Focus: Shop-floor TV and management dashboards showing running presses, slow-cycling machines, and idle tools."),
            ("energy-kwh-monitoring", "Energy Consumption (kWh per kg Moulded)",
             "Focus: Tracking machine power draw and chiller/dryer energy costs per job and per tonne of polymer processed."),
            ("tool-downtime-pareto", "Tool Breakdown & Changeover Duration Analytics",
             "Focus: Identifying which mould tools cause the most unplanned press stops or overrun setup times."),
        ],
    ),
    _mod(
        "finance-costing",
        "Finance, Machine-Hour Costing & Accounting",
        "Track actual vs standard cycle/material variances, tooling WIP, and integrate with accounting packages.",
        "finance",
        [
            ("machine-hour-variance", "Actual vs Standard Cycle Time & Material Variance",
             "Focus: Highlighting margin erosion when a job runs at a 30s cycle instead of 24s or uses 100% virgin resin instead of regrind."),
            ("accounting-integration", "Accounting & Finance Integration (Sage, Xero, SAP, etc.)",
             "Focus: Syncing sales invoices, purchase invoices, inventory valuation, and WIP journals with your finance system."),
            ("multi-currency-pricing", "Multi-Currency Tooling & Resin Purchasing",
             "Focus: Handling USD/EUR/GBP purchases for overseas toolmakers and international polymer shipments."),
        ],
    ),
    _mod(
        "hr-skills-shifts",
        "HR, Setter Skills Matrix & Shift Rotas",
        "Manage 3-shift continental rotas, setter/technician qualifications, and operator training.",
        "hr",
        [
            ("setter-skills-matrix", "Mould Setter, Process Tech & Operator Skills Matrix",
             "Focus: Tracking who is certified for overhead crane tool changes, robotics programming, scientific moulding, and forklift operation."),
            ("shift-rota-attendance", "Continental / 3-Shift Rota & Time Attendance",
             "Focus: Clocking operators in and out across 8-hour or 12-hour shifts and allocating labour across multiple presses per operator."),
        ],
    ),
    _mod(
        "sizing-integrations-plastics",
        "Operational Volumes, Press Connectivity & Sizing",
        "Capture press count, PLC/Euromap interfaces, terminal count, and user licensing requirements.",
        "questions",
        [
            ("press-fleet-count", "Number of Injection Moulding Presses & Tonnage Range",
             "Focus: Recording total number of presses, control brands (Arburg, Engel, KraussMaffei, Haitian, Sumitomo, Fanuc), and connectivity options."),
            ("shop-floor-kiosks", "Number of Shop Floor Terminals & Barcode Scanners",
             "Focus: Counting ruggedised press-side tablets/PCs, label printers, and warehouse handheld scanners required."),
            ("user-licenses-sizing", "Total Concurrent / Named User Licenses Required",
             "Focus: Sizing office, QA, warehouse, and setter user accounts."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# 3. Food Processing & Beverage Manufacturing
# ---------------------------------------------------------------------------
FOOD_BEVERAGE_MODULES = [
    _mod(
        "recipe-allergen-npd",
        "Recipe, Formulation & Allergen Management",
        "Manage multi-stage recipes, batch scaling, cooking/evaporation yields, allergens, and nutritional labelling.",
        "lab",
        [
            ("multi-stage-recipes", "Multi-Stage Recipes (Pre-Mix, Base, Sauce, Filling, Pack)",
             "Focus: Structuring recipes from raw ingredients through intermediate bulk mixes to multiple finished pack sizes (retail, foodservice, multipack)."),
            ("yield-evaporation-loss", "Cooking/Baking Yield, Moisture Loss & Overrun Modelling",
             "Focus: Accounting for weight loss during cooking/baking/cooling or volume overrun in whipping/carbonation."),
            ("allergen-matrix-control", "14 Major Allergens Tracking & Cross-Contamination Flags",
             "Focus: Automatically rolling up allergens (gluten, milk, nuts, soya, egg, sulphites, etc.) from ingredients to finished product labels and factory warnings."),
            ("nutritional-label-calc", "Nutritional Calculation & Ingredient Declaration (QUID)",
             "Focus: Calculating per-100g / per-serving kcal, fat, saturates, sugar, protein, salt, and Quantitative Ingredient Declarations (QUID)."),
            ("npd-kitchen-to-factory", "NPD Stage-Gate (Kitchen Trial → Line Trial → Launch)",
             "Focus: Managing New Product Development briefs, costing kitchen samples, customer tasting sign-off, and artwork approval."),
        ],
    ),
    _mod(
        "fefo-shelf-life-coldchain",
        "Shelf-Life, FEFO & Cold-Chain Warehouse Management",
        "Enforce strict First-Expired-First-Out picking, retailer minimum life rules, chill/freeze zones, and catch-weight.",
        "stock",
        [
            ("strict-fefo-picking", "Strict FEFO (First Expired, First Out) & Use-By Enforcement",
             "Focus: Directing warehouse pickers to the oldest valid batch and blocking expired or short-dated ingredients at the scanner."),
            ("retailer-min-life-rules", "Customer Minimum Remaining Shelf-Life (MLOR) Rules",
             "Focus: Ensuring each supermarket/customer only receives stock with at least their required remaining shelf-life (e.g. 75% life or minimum 14 days on delivery)."),
            ("temperature-zone-storage", "Frozen, Chilled & Ambient Storage Zone Segregation",
             "Focus: Tracking stock across blast freezers, chill stores (+1 to +4°C), ambient racks, and allergen-segregated racking."),
            ("catch-weight-inventory", "Catch-Weight & Variable-Weight Inventory (Cases + kg)",
             "Focus: Tracking meat, cheese, fish, or produce in dual units of measure—both case/unit count and exact actual weight in kg."),
            ("defrost-tempering-control", "Ingredient Defrost / Tempering Time Window Control",
             "Focus: Enforcing minimum tempering time (e.g. 24h chill defrost) AND maximum post-defrost shelf life before an ingredient must be used."),
            ("gs1-128-pallet-labels", "GS1-128 / SSCC Barcode & Pallet Labelling",
             "Focus: Printing compliant GS1-128 pallet labels with GTIN, Best Before / Use By date, batch code, net weight, and SSCC."),
        ],
    ),
    _mod(
        "food-planning-allergen-seq",
        "Production Planning, Line Scheduling & CIP Washdowns",
        "Sequence production lines to minimise allergen changeovers, schedule CIP washdowns, and meet daily retailer orders.",
        "planning",
        [
            ("allergen-aware-scheduling", "Allergen-Aware Line Sequencing (Free-From First, Allergens Last)",
             "Focus: Scheduling gluten-free / vegan / non-allergen runs at the start of the day and scheduling nut/dairy/allergen runs right before a full deep clean."),
            ("cip-washdown-scheduling", "Clean-in-Place (CIP) & Hygiene Changeover Windows",
             "Focus: Automatically inserting 30-min rinse vs 4-hour full allergen strip-down wash times into the line schedule."),
            ("short-shelf-life-mps", "Daily Make-to-Order & Short Shelf-Life Fresh Planning",
             "Focus: Fast morning planning when supermarket EDI orders drop at 06:00 for same-day production and evening despatch."),
            ("vessel-kettle-capacity", "Kettle, Mixer, Oven, Filler & Bottling Line Capacity",
             "Focus: Balancing batch vessel sizes (e.g. 1,000L cooking kettles) with continuous packaging/bottling line speeds."),
            ("seasonal-promotional-forecast", "Seasonal, Weather & Retailer Promotion Forecasting",
             "Focus: Uplifting ingredient and packaging MRP for summer BBQ / Christmas peaks and supermarket BOGOF/feature promotions."),
        ],
    ),
    _mod(
        "food-shop-floor-execution",
        "Dispensary Weighing, Batch Cooking & Packaging Line MES",
        "Control recipe dispensary scales, log cooking/chilling CCPs, and integrate checkweighers, metal detectors, and date coders.",
        "production",
        [
            ("dispensary-scale-integration", "Pre-Weigh Dispensary & Scale Tolerance Interlocks",
             "Focus: Connecting bench and floor scales so operators must scan the right ingredient batch and weigh within ±1% tolerance before printing a bag label."),
            ("cooking-cooling-ccp-logs", "Batch Cooking, Pasteurisation & Blast-Chilling Time/Temp Logs",
             "Focus: Recording core probe temperatures (e.g. ≥75°C for 2 mins) and rapid chill times down to <4°C for every batch."),
            ("high-care-low-risk-handover", "Low-Risk to High-Care / High-Risk Zone WIP Handover",
             "Focus: Tracking cooked/pasteurised batches across physical barrier ovens/kettles into high-care assembly and packing rooms."),
            ("date-coder-printer-control", "Automated Date Coder & Label Verification (Prevent Date Errors)",
             "Focus: Pushing the exact Use-By / Best-Before date and artwork code from the work order directly to line printers and vision scanners to prevent supermarket recalls."),
            ("checkweigher-giveaway", "Checkweigher, Average Weight (e-mark) & Giveaway Tracking",
             "Focus: Monitoring T1/T2 weight compliance and minimising overfill giveaway on filling and bagging lines."),
        ],
    ),
    _mod(
        "haccp-brcgs-traceability",
        "Food Safety, HACCP & BRCGS / SALSA Compliance",
        "Digitise paperless HACCP checks, metal detector challenges, positive batch release, and 4-hour recall traceability.",
        "shield",
        [
            ("digital-haccp-ccp", "Paperless HACCP & Critical Control Point (CCP) Prompting",
             "Focus: Prompting line QA every 30–60 minutes on washdown tablets to complete metal detector/X-ray test-piece checks, seal integrity, and gas-flush O2/CO2 checks."),
            ("four-hour-mass-balance-trace", "One-Click Forward/Backward Traceability & Mass Balance",
             "Focus: Generating a full BRCGS audit recall & mass-balance report (raw material batch → WIP → finished goods → customer deliveries) in under 5 minutes."),
            ("micro-organoleptic-release", "Microbiological Lab Testing, Taste Panel & Positive Release",
             "Focus: Holding finished goods in quarantine until external micro lab results (Listeria, Salmonella, TVC) and organoleptic taste checks pass."),
            ("foreign-body-complaints", "Customer Complaint, Foreign Body & CAPA Management",
             "Focus: Logging retailer/consumer complaints, linking to production batch/line/shift records, and tracking corrective actions."),
            ("environmental-swabbing", "Hygiene Swabbing (ATP / Listeria) & Allergen Validation",
             "Focus: Recording pre-start hygiene swab results before releasing a line for production after cleaning."),
        ],
    ),
    _mod(
        "agri-procurement-supplier",
        "Ingredient Procurement & Supplier Assurance (VACCP/TACCP)",
        "Manage approved suppliers, BRCGS/Red Tractor/Organic certificates, CoA on receipt, and forward commodity contracts.",
        "bom",
        [
            ("supplier-cert-expiry", "Supplier Certification Tracking (BRCGS, Red Tractor, Organic, Halal, Kosher)",
             "Focus: Blocking POs or goods receipts if a supplier's food safety certificate or organic/halal accreditation has expired."),
            ("goods-in-temp-coa", "Inbound Vehicle Temperature, Hygiene & CoA Inspection",
             "Focus: Recording delivery lorry temperature, pest/damage checks, and Certificate of Analysis on a tablet at the loading bay."),
            ("commodity-contract-drawdown", "Forward Commodity Contracts & Call-Off Drawdowns",
             "Focus: Contracting 500 tonnes of flour, sugar, oil, or milk solids at a fixed price and calling off weekly tanker/pallet loads."),
        ],
    ),
    _mod(
        "retailer-sales-edi-pricing",
        "Sales, Supermarket EDI, Catch-Weight Billing & Promotions",
        "Handle supermarket EDI orders, catch-weight invoicing, promotional rebates, and foodservice/wholesale telesales.",
        "sales",
        [
            ("supermarket-edi-orders", "Retailer & Foodservice EDI (Orders, ASN, Self-Billing Invoices)",
             "Focus: Automating daily EDI order imports, DESADV/ASN pallet notifications, and invoice matching with major retailers and wholesalers."),
            ("catch-weight-invoicing", "Catch-Weight Invoicing (Order in Cases, Bill by Actual kg)",
             "Focus: Pricing and invoicing customers by the exact scanned net weight of variable-weight products picked."),
            ("promotional-rebates-retros", "Promotional Pricing, Retro Rebates & Overrider Accruals",
             "Focus: Managing temporary promotional discounts, retrospective rebates, and customer net-margin profitability."),
            ("standing-orders-van-sales", "Standing Daily Orders, Van Sales & B2B Trade Portal",
             "Focus: Managing recurring Monday–Saturday standing orders for bakeries/dairies/foodservice and online trade ordering."),
        ],
    ),
    _mod(
        "chill-despatch-fleet",
        "Chilled Despatch, Pod Signing & Returnable Crates",
        "Manage multi-temperature loading bays, route planning, electronic Proof of Delivery (ePOD), and crate/keg tracking.",
        "despatch",
        [
            ("pre-load-chill-checks", "Pre-Load Vehicle Temperature & Seal Number Logging",
             "Focus: Verifying fridge trailer set-point temperature and hygiene before scanning SSCC pallets onto the vehicle."),
            ("returnable-crates-dolavs", "Returnable Bread Trays, Dolavs, Kegs & CHEP Pallet Ledger",
             "Focus: Tracking returnable containers and pallets out with customers and at wash depots."),
            ("multi-drop-epod", "Multi-Drop Route Planning & Driver ePOD App",
             "Focus: Optimising refrigerated van routes and capturing customer signatures, temperature on arrival, and short/damaged returns."),
        ],
    ),
    _mod(
        "food-finance-yield-costing",
        "Finance, Batch Yield Costing & Margin Analytics",
        "Track ingredient price variance, batch yield losses, giveaway cost, labour efficiency, and accounting sync.",
        "finance",
        [
            ("batch-yield-variance", "Recipe Yield, Waste & Overfill Giveaway Costing",
             "Focus: Comparing theoretical recipe output against actual packed cases to pinpoint kitchen waste, trim loss, and line giveaway."),
            ("sku-customer-margin", "True SKU & Customer Net Margin (After Rebates & Distribution)",
             "Focus: Seeing net profit per SKU and per retailer after ingredient moves, packaging, direct labour, and promotional rebates."),
            ("finance-erp-sync", "Finance & General Ledger Integration",
             "Focus: Automating AP/AR, 3-way PO matching, and daily stock/WIP journals."),
        ],
    ),
    _mod(
        "food-hr-hygiene",
        "HR, Food Hygiene Certifications & Shift Attendance",
        "Track Level 2/3 Food Safety & Allergen training, occupational health, and factory shift clocking.",
        "hr",
        [
            ("food-hygiene-training", "Food Safety, Allergen & HACCP Training Matrix",
             "Focus: Tracking staff and agency worker inductions, Level 2/3 Food Hygiene certificates, and medical return-to-work questionnaires."),
            ("agency-shift-clocking", "Biometric / Badge Shift Clocking & Agency Labour Tracking",
             "Focus: Tracking permanent and temporary agency hours by production line to measure labour cost per case/kg."),
        ],
    ),
    _mod(
        "food-dashboards-sizing",
        "Factory Dashboards, IP69K Terminals & System Sizing",
        "Monitor line OEE, short-dated stock risks, washdown terminal hardware, and scale/printer integrations.",
        "dashboards",
        [
            ("short-dated-stock-alerts", "Expiry Risk, Slow-Moving & Short-Dated Stock Dashboard",
             "Focus: Highlighting raw materials or finished goods approaching minimum shelf-life so sales or production can act before write-off."),
            ("ip69k-washdown-terminals", "Washdown Shop Floor Terminals, Scales & Line Integrations",
             "Focus: Counting stainless-steel IP69K touchscreens, industrial checkweighers/scales, label printers, and user licenses needed."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# 4. Pharmaceutical, Biotech & Medical Devices
# ---------------------------------------------------------------------------
PHARMA_LIFESCIENCES_MODULES = [
    _mod(
        "mbr-dmr-specifications",
        "Master Batch Records (MBR / DMR) & Change Control",
        "Manage GxP version-controlled Master Batch Records, potency-adjusted BOMs, and formal change control.",
        "bom",
        [
            ("controlled-mbr-versioning", "Master Batch Record (MBR) / Device Master Record (DMR) Versioning",
             "Focus: Enforcing QA-approved effective dates, dual electronic signatures, and superseding obsolete versions automatically."),
            ("potency-assay-compensation", "Active Ingredient Potency & Assay Compensation Calculation",
             "Focus: Automatically adjusting the required quantity of Active Pharmaceutical Ingredient (API) and excipient filler (e.g. lactose) based on the specific lot's assay/moisture certificate."),
            ("gxp-change-control", "Formal Engineering / GMP Change Control Workflow",
             "Focus: Impact assessment across regulatory filings, validation, stability, and SOPs before any specification or BOM change goes live."),
            ("clinical-to-commercial", "Clinical Trial (IMP) to Commercial Scale-Up BOMs",
             "Focus: Managing blinded/placebo clinical supplies alongside commercial pack configurations by country/market authorisation."),
        ],
    ),
    _mod(
        "ebr-edhr-part11",
        "Electronic Batch Records (eBR / eDHR) & 21 CFR Part 11",
        "Execute paperless batch records with hard-gated steps, dual sign-offs, audit trails, and review-by-exception.",
        "production",
        [
            ("part11-annex11-compliance", "21 CFR Part 11 & EU GMP Annex 11 Electronic Signatures",
             "Focus: Enforcing unique user credentials, signature meaning (Performed By / Verified By / QA Approved By), and immutable timestamped audit trails with reason-for-change."),
            ("hard-gated-step-execution", "Hard-Gated Step-by-Step Work Instructions & Interlocks",
             "Focus: Preventing operators from advancing to the next manufacturing step if an in-process parameter is out of specification or a second verifier hasn't signed."),
            ("line-clearance-verification", "Digital Line Clearance & Room Readiness Checklists",
             "Focus: Recording removal of previous batch materials/labels and QA sign-off before a new batch or packaging run can start."),
            ("review-by-exception", "QA Review-by-Exception (RBE) Batch Release Dashboard",
             "Focus: Highlighting only batch steps with deviations, overrides, or out-of-limit parameters so QA/QP can review and release batches in hours instead of weeks."),
            ("yield-reconciliation-limits", "In-Process Yield & Printed Label Reconciliation Gates",
             "Focus: Enforcing strict reconciliation of printed cartons/leaflets/labels (e.g. 99.5%–100.0% accountability) to prevent mix-ups."),
        ],
    ),
    _mod(
        "weigh-dispense-material-status",
        "Weigh & Dispense, Quarantine & Material Status Control",
        "Control dispensing booths, balance integration, quarantine/sampling/release statuses, and controlled substances.",
        "lab",
        [
            ("dispensing-booth-balances", "Guided Weigh & Dispense with Analytical Balance Integration",
             "Focus: Verifying clean booth status, balance daily calibration check, barcode lot scan, tare/net weight capture directly from the scale, and container sub-lot labelling."),
            ("gmp-material-statuses", "Strict GMP Material Statuses (Quarantine, Sampled, Released, Rejected, Blocked)",
             "Focus: Preventing any material in Quarantine, Rejected, or past its Retest/Expiry Date from being allocated or dispensed."),
            ("retest-date-management", "Retest Date vs Expiry Date & Re-Assay Workflows",
             "Focus: Automatically moving materials approaching their Retest Date back into Quarantine until QC re-tests and extends the release date."),
            ("controlled-substances-vault", "Controlled Drugs / Narcotics Vault & Witnessed Balance Ledger",
             "Focus: Maintaining gram-by-gram Home Office / DEA register balances with mandatory two-person witness signatures."),
        ],
    ),
    _mod(
        "lims-qc-stability-qp",
        "QC Laboratory (LIMS), CoA, Stability & QP Certification",
        "Manage sampling plans, analytical testing, OOS/OOT investigations, stability chambers, and QP batch certification.",
        "qms",
        [
            ("sampling-plans-retain", "Statistical Sampling Plans (AQL / √n+1) & Retain Samples",
             "Focus: Generating sample container labels on goods receipt, tracking reference/retain samples, and deducting sample quantities from inventory."),
            ("analytical-testing-coa", "QC Test Specifications & Automated Certificate of Analysis (CoA)",
             "Focus: Recording HPLC, dissolution, sterility, endotoxin, and assay results against compendial (USP/Ph.Eur/BP) specs and generating the batch CoA."),
            ("oos-oot-investigations", "Out-of-Specification (OOS) & Out-of-Trend (OOT) Lab Workflows",
             "Focus: Structured Phase I (lab error) and Phase II (manufacturing root cause) investigation workflows before any re-testing is permitted."),
            ("stability-study-management", "ICH Stability Study Protocols, Chamber Pull Schedules & Trending",
             "Focus: Scheduling 3, 6, 9, 12, 24, 36-month stability pulls across 25°C/60%RH and 40°C/75%RH chambers."),
            ("qp-batch-register", "Qualified Person (QP) Certification & Batch Release Register",
             "Focus: Maintaining the statutory QP certification register with linked MBR, CoA, deviation closure, and TSE/BSE declarations."),
        ],
    ),
    _mod(
        "capa-deviations-serialisation",
        "Deviations, CAPA, ISO 13485 & Serialisation / UDI",
        "Coordinate minor/major/critical deviations, CAPA effectiveness, UDI device labelling, and FMD/DSCSA serialisation.",
        "shield",
        [
            ("deviation-capa-workflow", "Deviation Classification (Minor/Major/Critical) & CAPA Tracking",
             "Focus: Linking shop-floor deviations directly to the affected batch, assigning root-cause investigation (5-Why/Fishbone), and verifying CAPA effectiveness."),
            ("serialisation-aggregation", "Pack Serialisation & Aggregation (EU FMD / US DSCSA)",
             "Focus: Generating/commissioning 2D DataMatrix serial numbers, tamper-evident seal checks, and parent-child case/pallet aggregation."),
            ("udi-medical-device", "Medical Device UDI (Unique Device Identification) & ISO 13485",
             "Focus: Managing UDI-DI / UDI-PI barcodes, EUDAMED/FDA GUDID attributes, and post-market surveillance / complaint vigilance."),
        ],
    ),
    _mod(
        "cleanroom-equipment-logbooks",
        "Cleanroom, Equipment Logbooks & Calibration Interlocks",
        "Enforce equipment cleaning status, IQ/OQ/PQ qualification, calibration expiry locks, and environmental monitoring.",
        "tools",
        [
            ("equipment-cleaning-status", "Digital Equipment Logbooks & Cleaning Hold Times",
             "Focus: Tracking equipment status (Clean, Dirty, In-Use, Out-of-Service) and enforcing Dirty Hold Time and Clean Hold Time expiry limits."),
            ("calibration-interlocks", "Calibration & Qualification (IQ/OQ/PQ) Hard Interlocks",
             "Focus: Blocking an operator from using a balance, autoclave, tablet press, or gauge in an eBR if its calibration or PM is overdue."),
            ("environmental-monitoring", "Cleanroom Grade A/B/C/D Environmental Excursion Logging",
             "Focus: Logging viable/non-viable particle counts, pressure differentials, and temperature/humidity excursions linked to active batches in that room."),
        ],
    ),
    _mod(
        "pharma-planning-campaigns",
        "Campaign Planning, Suite Scheduling & Cold-Chain MRP",
        "Schedule dispensing, compounding, filling/tableting, and packaging suites while respecting cleaning validation rules.",
        "planning",
        [
            ("campaign-scheduling", "Campaign Production Scheduling to Minimise Cleaning Overheads",
             "Focus: Grouping back-to-back batches of the same product/strength into a validated campaign before a full changeover clean."),
            ("suite-resource-allocation", "Cleanroom Suite, Isolator & Lyophiliser Finite Scheduling",
             "Focus: Scheduling constrained cleanroom suites, isolators, freeze-dryers, and blister/vial packaging lines."),
            ("mrp-leadtime-qc-buffer", "MRP with Mandatory QC Testing & Quarantine Lead-Time Buffers",
             "Focus: Factoring 14-day sterility testing or 10-day incoming QC quarantine lead times into material availability dates."),
        ],
    ),
    _mod(
        "pharma-vendor-cdmo",
        "Vendor Qualification, QTAs & Subcontract / CDMO Management",
        "Enforce Approved Vendor Lists, Quality Technical Agreements, and external contract manufacturing/sterilisation.",
        "stock",
        [
            ("avl-qta-enforcement", "Approved Vendor List (AVL) & Quality Technical Agreement (QTA) Gates",
             "Focus: Restricting PO creation for APIs, excipients, and primary packaging to audited, QA-approved manufacturers and suppliers."),
            ("cdmo-external-sterilisation", "Subcontract CDMO, Gamma/EtO Sterilisation & External Lab Tracking",
             "Focus: Tracking batches sent out for contract irradiation/sterilisation, micronisation, or specialist analytical testing."),
        ],
    ),
    _mod(
        "gdp-coldchain-distribution",
        "Good Distribution Practice (GDP), Cold-Chain & Recalls",
        "Verify customer wholesale dealer licences, track temperature data loggers in transit, and execute rapid recalls.",
        "despatch",
        [
            ("gdp-customer-authorisation", "GDP Customer License Verification (WDA / Pharmacy / Hospital)",
             "Focus: Blocking despatch of prescription/controlled medicines unless the customer's Wholesale Distribution Authorisation (WDA) or licence is valid."),
            ("cold-chain-transit-loggers", "Cold-Chain Shipment Validation & TempTale Logger Sign-Off",
             "Focus: Recording insulated shipper qualification, temperature logger serial numbers, and excursion evaluation upon delivery."),
            ("batch-recall-matrix", "Instant Batch Genealogy & Regulatory Recall Notification",
             "Focus: Tracing every vial, blister pack, or device serial/lot number to every hospital, distributor, and clinical site."),
        ],
    ),
    _mod(
        "pharma-hr-sop-training",
        "GMP Training Matrix, SOP Read & Understand Interlocks",
        "Verify operator SOP training before batch execution and manage GxP role qualifications.",
        "hr",
        [
            ("sop-training-interlock", "Hard-Gated Operator SOP Training Check in eBR",
             "Focus: Verifying in real time that the operator signing a batch step has completed training on the current effective version of the governing SOP."),
            ("aseptic-gowning-qualification", "Aseptic Gowning, Visual Inspection & Analyst Qualification Expiry",
             "Focus: Tracking periodic re-qualification dates for cleanroom operators, visual inspectors, and QC analysts."),
        ],
    ),
    _mod(
        "pharma-finance-validation",
        "Finance, R&D Project Costing & CSV / GAMP 5 Validation",
        "Manage batch costing, R&D/clinical project tracking, and Computer System Validation (CSV) requirements.",
        "finance",
        [
            ("batch-qc-scrap-costing", "Full Batch Costing (API, Excipients, QC Testing & Yield Loss)",
             "Focus: Capturing true cost per batch including destructive QC sample costs, cleanroom hours, and rejected batch write-offs."),
            ("csv-gamp5-validation", "Computer System Validation (CSV / GAMP 5) & Data Integrity (ALCOA+)",
             "Focus: Defining User Requirements Specification (URS), IQ/OQ/PQ validation documentation, backup/restore, and role-based access controls."),
            ("pharma-sizing-integrations", "Cleanroom Terminals, Balances, LIMS & ERP Integrations",
             "Focus: Sizing cleanroom-grade terminals, barcode scanners, balance interfaces, and concurrent user licenses."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# 5. Chemical, Coatings, Adhesives & Process Manufacturing
# ---------------------------------------------------------------------------
CHEMICAL_PROCESS_MODULES = [
    _mod(
        "formula-management-rd",
        "Formula Management, Physical Properties & Lab R&D",
        "Manage weight/volume/% formulas, specific gravity, VOC/solids calculations, co-products, and lab-to-plant scaling.",
        "lab",
        [
            ("pct-weight-volume-formulas", "Percentage (%), Weight (kg) & Volume (Litre) Formula Management",
             "Focus: Designing formulas by weight % or volume % with automatic conversion between kg and litres using each component's Specific Gravity (SG / density)."),
            ("physical-properties-calc", "Automated Solids %, VOC, Density, pH & Viscosity Roll-Up",
             "Focus: Calculating theoretical VOC (g/L), non-volatile solids %, flash point category, and raw material cost per kg/litre as the chemist adjusts the formula."),
            ("co-products-by-products", "Intermediates, Co-Products, By-Products & Wash-Solvent Recycle",
             "Focus: Handling reactions that produce multiple outputs and recovering wash-water/solvent heels into the next compatible batch."),
            ("potency-concentration-adj", "Active Concentration / Acid-Base Titration Adjustment",
             "Focus: Adjusting batch additions when raw material strength varies (e.g. 32% vs 36% HCl or moisture content in powders)."),
        ],
    ),
    _mod(
        "sds-ghs-reach-compliance",
        "Safety Data Sheets (SDS), GHS/CLP & REACH Compliance",
        "Automate hazard classification, GHS label printing, SDS distribution, and regulatory substance volume tracking.",
        "shield",
        [
            ("ghs-clp-label-printing", "GHS / CLP Hazard Pictograms, H/P Statements & Drum Labels",
             "Focus: Printing compliant BS 5609 chemical drum/IBC/pail labels with hazard diamonds, signal words, Precautionary/Hazard statements, and UFI codes."),
            ("sds-version-dispatch", "Safety Data Sheet (SDS) Version Control & Auto-Send to Customers",
             "Focus: Automatically emailing the latest language-specific SDS to a customer on their first order of a chemical product or whenever the SDS is revised."),
            ("reach-tonnage-tracking", "UK REACH / EU REACH Substance Tonnage & SVHC Tracking",
             "Focus: Aggregating annual imported/manufactured tonnage of each CAS/EC chemical substance across all raw materials and blends."),
            ("adr-iata-imdg-dg", "Dangerous Goods Classification (UN Number, Packing Group, ADR/IMDG/IATA)",
             "Focus: Storing UN numbers, Proper Shipping Names, tunnel codes, and marine pollutant flags on every product."),
        ],
    ),
    _mod(
        "reactor-tank-scheduling",
        "Reactor, Mixer & Bulk Tank Farm Scheduling",
        "Schedule batch vessels, high-shear mixers, mills, and filling lines with compatibility and washout rules.",
        "planning",
        [
            ("vessel-mixer-scaling", "Vessel Min/Max Fill Capacity & Batch Splitting",
             "Focus: Scaling customer demand into optimal vessel batch sizes (e.g. 500L, 2,500L, 10,000L mixers) without exceeding min agitator level or max headroom."),
            ("chemical-compatibility-seq", "Vessel Sequencing & Campaigning (Light-to-Dark / Solvent-to-Water)",
             "Focus: Sequencing batches on shared mixers and filling lines to prevent cross-contamination (e.g. silicone-free rules, biocide rules, tinting progression) and minimise solvent washouts."),
            ("bulk-to-multipack-mrp", "Bulk Intermediate to Multi-Pack Size Planning (IBC, Drum, Pail, Bottle)",
             "Focus: Planning one 5,000L bulk batch to be filled simultaneously into two 1,000L IBCs, ten 200L drums, and forty 25L pails."),
            ("tank-farm-ullage-planning", "Bulk Raw Material & Finished Tank Farm Ullage / Headspace Planning",
             "Focus: Checking available tank farm capacity before scheduling a 25-tonne road tanker delivery or bulk production run."),
        ],
    ),
    _mod(
        "batch-ticket-plant-execution",
        "Batch Ticket Execution, Metered Charging & Pack-Out",
        "Execute digital batch sheets with phased additions, mixing/heating timers, in-process tint/pH adjustments, and multi-pack filling.",
        "production",
        [
            ("phased-batch-instructions", "Phased Batch Tickets (Charge, Heat, React, Cool, Adjust, Filter, Fill)",
             "Focus: Guiding operators through sequenced chemical additions, agitation speeds, exothermic temperature limits, and safety PPE prompts."),
            ("flowmeter-loadcell-charging", "Bulk Tanker / Silo Flowmeter & Vessel Load-Cell Integration",
             "Focus: Recording bulk liquid/powder additions pumped directly from storage tanks alongside manual bag tips and drum pre-weighs."),
            ("in-process-qc-adjustments", "In-Process Lab Adjustment Loops (Viscosity, pH, Colour Tint)",
             "Focus: Recording lab corrective additions (e.g. 'Add 12kg water and 1.5kg pigment paste, mix 15 mins, re-sample') directly on the batch record."),
            ("multi-container-packout", "Multi-Container Pack-Out, Tare/Net Weighing & Heel Accounting",
             "Focus: Recording actual filled counts of IBCs, drums, jerrycans, and tins from a bulk batch and accounting for vessel heel/filtration loss."),
        ],
    ),
    _mod(
        "hazmat-warehouse-containers",
        "Hazmat Warehouse Segregation, Tank Farm & Returnable IBCs",
        "Enforce incompatible chemical storage rules, bund capacity limits, lot control, and returnable IBC/drum tracking.",
        "stock",
        [
            ("hazmat-storage-segregation", "Incompatible Chemical Storage Segregation (Flammables, Oxidisers, Acids, Alkalis)",
             "Focus: Preventing warehouse put-away of incompatible hazard classes in the same zone or exceeding COMAH / fire-zone tonnage limits."),
            ("returnable-ibc-drum-ledger", "Returnable Stainless/Plastic IBCs & Drum Deposit Tracking",
             "Focus: Tracking serialized IBCs and returnable containers at customer sites, cleaning status, and UN pressure-test expiry dates."),
            ("lot-shelf-life-agitation", "Lot Traceability, Shelf-Life & Periodic Re-Agitation Alerts",
             "Focus: Flagging settling dispersions/coatings that require periodic drum rolling or re-testing before despatch."),
        ],
    ),
    _mod(
        "chemical-qc-retain",
        "Quality Control (QC), Customer CoA & Retain Samples",
        "Test batch physical/chemical properties, match customer-specific spec ranges, and manage retain sample libraries.",
        "qms",
        [
            ("chemical-qc-testing", "Batch QC Testing (Viscosity, SG, pH, Solids %, Flash Point, Colour ΔE)",
             "Focus: Logging lab test results per batch and blocking filling/despatch until QC grants pass status."),
            ("customer-specific-coa", "Customer-Specific Spec Matching & Automated CoA Generation",
             "Focus: Checking if a batch meets Customer A's tighter viscosity/purity window and auto-generating a branded Certificate of Analysis on shipment."),
            ("retain-sample-library", "Batch Retain Sample Storage & Hazmat Disposal Alerts",
             "Focus: Indexing physical retain sample bottles by rack/shelf and alerting the lab when retention periods expire for safe disposal."),
            ("off-spec-rework-blending", "Off-Spec Quarantine & Controlled Rework Blending",
             "Focus: Calculating how much of an off-spec or slow-moving batch can be blended into a new batch while staying within specification."),
        ],
    ),
    _mod(
        "chemical-sales-toll-adr",
        "Sales, Pack-Size Pricing, Toll Manufacturing & ADR Despatch",
        "Handle bulk vs packed pricing, customer toll/contract blending, and Dangerous Goods Notes (DGN) on shipment.",
        "despatch",
        [
            ("pack-size-density-pricing", "Price Lists per kg / Litre / Container across Bulk, IBC, Drum & Pail",
             "Focus: Managing price differentials for the same formula sold in bulk road tankers vs IBCs, 200L drums, and small packs."),
            ("toll-contract-blending", "Toll & Contract Manufacturing (Customer-Supplied Raw Materials & Formulas)",
             "Focus: Segregating customer-owned raw materials/packaging and charging a processing/filling fee per kg or per batch."),
            ("adr-dgn-tremcard", "ADR Dangerous Goods Note (DGN), Load Points & IMDG Paperwork",
             "Focus: Calculating ADR 1.1.3.6 vehicle points, checking mixed-load prohibitions, and printing Dangerous Goods Notes and Tremcards."),
        ],
    ),
    _mod(
        "atex-maintenance-ehs",
        "Plant Maintenance, ATEX Inspections & Work Permits (CMMS)",
        "Manage Ex/ATEX equipment inspections, pressure vessel statutory checks, and safe work permits.",
        "tools",
        [
            ("atex-vessel-inspections", "ATEX / Ex Equipment, Pressure Vessel & Bund Statutory Inspections",
             "Focus: Scheduling mandatory inspections for flameproof motors, earthing straps, relief valves, and tank bunds."),
            ("permit-to-work", "Digital Permit-to-Work (Hot Work, Confined Space, Line Breaking, LOTO)",
             "Focus: Issuing and signing off safety permits before maintenance begins on reactors or solvent lines."),
        ],
    ),
    _mod(
        "chemical-finance-env",
        "Finance, Formula Re-Costing & Environmental Levies",
        "Roll up formula costs from live raw material prices, track Plastic Packaging Tax / waste levies, and sync accounting.",
        "finance",
        [
            ("formula-recosting-margins", "Live Formula Cost Roll-Up & Raw Material Replacement Cost Quotes",
             "Focus: Instantly seeing how a 10% feedstock or solvent price increase impacts every intermediate and finished product's margin."),
            ("packaging-environmental-tax", "UK Plastic Packaging Tax (PPT) & Hazardous Waste Cost Tracking",
             "Focus: Tracking recycled plastic content (<30% vs ≥30%) on jerrycans/IBCs/drums and allocating effluent/waste disposal costs."),
        ],
    ),
    _mod(
        "chemical-hr-coshh",
        "HR, COSHH, ADR Driver & Operator Certifications",
        "Track COSHH training, health surveillance, ADR licences, and shift rotas.",
        "hr",
        [
            ("coshh-adr-training", "COSHH, Spill Response, Forklift & ADR Driver Certification Matrix",
             "Focus: Tracking employee safety certifications, occupational health checks, and PPE issuance."),
        ],
    ),
    _mod(
        "chemical-sizing-atex",
        "Operational Volumes, Intrinsically Safe (ATEX) Terminals & Sizing",
        "Capture Zone 1/2 ATEX terminal requirements, weighbridge/PLC connections, and user licensing.",
        "questions",
        [
            ("atex-zone-terminals", "ATEX Zone 1 / Zone 2 Intrinsically Safe Tablets, Scales & Scanners",
             "Focus: Counting Ex-rated shop-floor terminals, drum label printers, weighbridge interfaces, and total user licenses."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# 6. Electronics, PCB & High-Tech Assembly (EMS / OEM)
# ---------------------------------------------------------------------------
ELECTRONICS_ASSEMBLY_MODULES = [
    _mod(
        "ebom-mbom-aml",
        "Engineering BOM, CAD Import & Approved Manufacturer List (AML)",
        "Import EDA/CAD BOMs, manage reference designators, Approved Manufacturer Lists (AML/AVL), alternates, and ECOs.",
        "chip",
        [
            ("cad-eda-bom-import", "Altium / Cadence / KiCad BOM Import & Reference Designator Mapping",
             "Focus: Importing engineering BOMs with PCB reference designators (R1, R2, C14, U3), DNP (Do Not Populate) variants, and centroid data."),
            ("aml-avl-alternates", "Approved Manufacturer List (AML) & Alternate / Substitute MPNs",
             "Focus: Linking one internal part number to multiple approved Manufacturer Part Numbers (MPNs) and footprint-compatible alternates."),
            ("eco-revision-effectivity", "Engineering Change Orders (ECO), Gerber/Firmware Revision Control",
             "Focus: Controlling PCB bare-board rev, BOM rev, pick-and-place program rev, and firmware version together with full disposition of existing WIP/stock."),
        ],
    ),
    _mod(
        "component-sourcing-msl-reels",
        "Component Sourcing, Distributor APIs, MSL & Reel Control",
        "Connect to component distributors, track Moisture Sensitivity Levels (MSL), and manage unique reel IDs.",
        "stock",
        [
            ("distributor-api-quoting", "Electronic Component Distributor Integration (DigiKey, Mouser, Farnell, Arrow)",
             "Focus: Pulling live distributor stock, price breaks, lead times, and lifecycle status (Active, NRND, EOL/Obsolete) across hundreds of BOM lines."),
            ("unique-reel-id-tracking", "Unique Component Reel / Tray Barcode ID & Splice Tracking",
             "Focus: Assigning a unique UID barcode to every incoming tape reel, cut-tape, or IC tray and tracking exact remaining component count."),
            ("msl-floor-life-baking", "JEDEC Moisture Sensitivity Level (MSL 2–6) Floor-Life & Bake Timer",
             "Focus: Automatically starting the countdown timer when a dry-bagged IC reel is opened and blocking SMT placement if floor-life expires before re-baking."),
            ("customer-free-issue-stock", "Customer-Consigned / Free-Issue Material (FIM) Segregation",
             "Focus: Managing customer-supplied reels and kits for EMS subcontract builds separately from house-owned inventory."),
        ],
    ),
    _mod(
        "smt-boxbuild-scheduling",
        "SMT Line, Through-Hole & Box-Build Scheduling",
        "Schedule SMT placement lines, feeder setups, wave/selective soldering, conformal coating, and final box-build.",
        "planning",
        [
            ("clear-to-build-shortages", "Clear-to-Build (CTB) Shortage Matrix & Kit Readiness",
             "Focus: Visualising across all open work orders which jobs have 100% of components on hand vs which are waiting on 1 or 2 golden-screw shortages."),
            ("smt-feeder-family-grouping", "SMT Feeder Setup Grouping & Stencil / Solder Paste Scheduling",
             "Focus: Grouping PCB assemblies that share common SMT feeder bank setups to slash changeover times."),
            ("prototype-npi-fasttrack", "Fast-Turn NPI / Prototype Cell vs Volume Line Scheduling",
             "Focus: Balancing 24-hour quick-turn engineering prototypes alongside scheduled production batches."),
        ],
    ),
    _mod(
        "pcb-mes-serial-traceability",
        "Shop Floor MES, PCB Serialisation & Test Log Integration",
        "Track individual PCB serial numbers, reel-to-board genealogy, AOI/X-ray/ICT test results, and rework loops.",
        "production",
        [
            ("panel-to-board-serialisation", "Multi-Board Panel Array to Individual PCB Serial Number Tracking",
             "Focus: Laser-marking or barcoding multi-up PCB panels and automatically splitting genealogy to individual board serial numbers at depanelisation."),
            ("reel-to-serial-genealogy", "Component Reel UID & Solder Paste Lot to PCB Serial Traceability",
             "Focus: Knowing exactly which manufacturer lot/reel of microcontroller U1 or capacitor C5 was placed onto every serialized board."),
            ("aoi-xray-ict-test-logs", "Automated Optical Inspection (AOI), X-Ray, ICT & Functional Test Capture",
             "Focus: Ingesting pass/fail logs and parametric test data from AOI, Flying Probe, ICT, and LabVIEW/Python functional test rigs."),
            ("bonepile-rework-routing", "Diagnostic Troubleshooting, Bonepile & Rework Loop Routing",
             "Focus: Routing failed boards to a debug technician, logging the defective reference designator (e.g. 'Solder bridge on U4 pin 12'), and forcing re-test after repair."),
            ("firmware-flashing-mac", "Firmware Flashing, MAC Address Assignment & Calibration Certificates",
             "Focus: Recording the exact firmware binary hash, cryptographic keys, and MAC/IMEI addresses programmed into each unit."),
        ],
    ),
    _mod(
        "ipc-quality-rohs-rma",
        "Quality (IPC-A-610), ESD, RoHS/REACH & RMA Management",
        "Manage IPC inspection classes, ESD compliance, environmental declarations, and customer returns (RMA).",
        "qms",
        [
            ("ipc-class-inspection", "IPC-A-610 (Class 1, 2, 3) Inspection Plans & First Article (FAI)",
             "Focus: Enforcing inspection criteria and solder joint quality gates based on whether the product is consumer, industrial, or medical/aerospace Class 3."),
            ("rohs-reach-conflict-minerals", "RoHS, REACH & Conflict Minerals (CMRT) BOM Roll-Up",
             "Focus: Verifying component compliance certificates across the entire BOM and generating customer compliance declarations."),
            ("fpy-defect-pareto", "First Pass Yield (FPY) & Defect Per Million Opportunities (DPMO) Analytics",
             "Focus: Tracking FPY across SMT, wave, and final test, with Pareto charts by defect code, reference designator, and machine."),
            ("rma-warranty-repair", "Customer RMA Portal, Failure Analysis (FA) & Warranty Repair",
             "Focus: Issuing RMA numbers, inspecting returned units against their original as-built genealogy, and issuing 8D failure analysis reports."),
        ],
    ),
    _mod(
        "ems-quoting-costing",
        "Fast BOM Quoting, NRE Billing & PPV Finance",
        "Price multi-hundred-line BOMs rapidly, quote stencils/fixtures (NRE), and track Purchase Price Variance (PPV).",
        "quote",
        [
            ("bom-scrub-multi-qty-quote", "Rapid BOM Scrubbing & Multi-Quantity EMS Quoting (10 / 100 / 1,000+)",
             "Focus: Calculating component attrition/overage, reel minimum order quantities (MOQ) excess material cost, SMT placement time, and test labour."),
            ("nre-stencil-fixture-billing", "Non-Recurring Engineering (NRE), Stencil & Test Fixture Billing",
             "Focus: Quoting and invoicing one-off charges for solder stencils, wave pallets, programming jigs, and ICT fixtures."),
            ("ppv-broker-variance", "Component Purchase Price Variance (PPV) & Spot-Buy Rebilling",
             "Focus: Tracking price differences when shortage components must be bought on the spot market and rebilling approved variances to the customer."),
        ],
    ),
    _mod(
        "electronics-hr-sizing",
        "IPC/ESD Skills Matrix, Shop Floor Scanners & System Sizing",
        "Track IPC-A-610 / J-STD-001 operator certifications, ESD wrist/footwear checks, and system sizing.",
        "hr",
        [
            ("ipc-jstd-certification", "IPC-A-610, J-STD-001 & Rework Operator Certification Tracking",
             "Focus: Alerting supervisors before an operator's IPC soldering or inspection certification expires."),
            ("electronics-sizing-integrations", "2D Barcode Scanners, X-Ray Reel Counters, EDA & ERP Integrations",
             "Focus: Sizing 2D DataMatrix scanners, smart storage towers, test rig connections, and user licenses."),
        ],
    ),
]


# ---------------------------------------------------------------------------
# 7. Automotive, Aerospace & Discrete Assembly (AS9100 / IATF 16949)
# ---------------------------------------------------------------------------
AUTOMOTIVE_AEROSPACE_MODULES = [
    _mod(
        "config-mgmt-asbuilt",
        "Configuration Management, As-Designed vs As-Built & Export Control",
        "Control complex multi-level assemblies, serial/lot effectivity, engineering concessions, and ITAR/Export locks.",
        "bom",
        [
            ("serial-date-effectivity", "BOM Effectivity by Serial Number, Tail/VIN Number or Date",
             "Focus: Specifying that a design change applies from Serial #0051 onwards while units #0001–#0050 retain the prior configuration."),
            ("as-designed-vs-as-built", "As-Designed vs As-Built / As-Maintained Digital Thread",
             "Focus: Recording the exact serialized child sub-assemblies, material heat/cast numbers, and approved concessions installed into each parent unit."),
            ("itar-ear-export-control", "ITAR / EAR / UK Strategic Export Control & Drawing Access Locks",
             "Focus: Restricting access to defence/aerospace technical drawings and BOMs to cleared personnel and approved nationalities."),
        ],
    ),
    _mod(
        "apqp-ppap-fair-qms",
        "AS9100 / IATF 16949 Quality, FAIR (AS9102) & PPAP",
        "Manage APQP milestones, First Article Inspection Reports, FMEA/Control Plans, NDT, and Material Review Board (MRB).",
        "qms",
        [
            ("as9102-fair-ppap", "AS9102 First Article Inspection (FAIR Form 1, 2, 3) & PPAP Packages",
             "Focus: Generating ballooned drawing characteristic tables, CMM dimensional results, and triggering delta-FAIRs when a revision or process changes."),
            ("ncr-mrb-concession", "Non-Conformance (NCR), Material Review Board (MRB) & Customer Concession",
             "Focus: Formal disposition workflows (Use-As-Is with customer concession, Rework to instruction, Return to Vendor, Scrap with witness)."),
            ("mill-cert-en10204", "Raw Material Heat/Cast Number & EN 10204 3.1 / 3.2 Mill Cert Traceability",
             "Focus: Scanning and linking alloy heat numbers, chemical/mechanical mill certs, and DFARS specialty metal declarations from bar/plate stock to finished parts."),
        ],
    ),
    _mod(
        "sequenced-jit-aps",
        "MRP, Finite Bottleneck Scheduling & JIT / Kanban",
        "Schedule 5-axis CNCs, autoclaves, NDT, and assembly cells against OEM EDI schedules and programme milestones.",
        "planning",
        [
            ("oem-edi-schedules", "OEM EDI Schedules (DELFOR / DELJIT / 830 / 862) & Cumulative Reconciliation",
             "Focus: Importing rolling customer forecasts, comparing against previous schedules, and managing cumulative shipped quantities."),
            ("finite-bottleneck-aps", "Finite Scheduling for CNCs, Autoclaves, Heat Treat, Paint & CMM",
             "Focus: Scheduling constrained machines, fixtures, and skilled setters across multi-week routings."),
            ("lineside-kanban-two-bin", "Line-Side Kanban, Two-Bin Fastener VMI & Kit Marshalling",
             "Focus: Replenishing assembly cells via barcode Kanban cards and staging complete serialized assembly kits."),
        ],
    ),
    _mod(
        "digital-traveller-torque",
        "Digital Shop Floor Traveller, Torque Tools & Operator Interlocks",
        "Replace paper route cards with hard-gated digital travellers, smart torque wrench capture, and NADCAP skill checks.",
        "production",
        [
            ("digital-route-card-stamps", "Digital Route Card / Traveller with Electronic Inspector Stamps",
             "Focus: Enforcing operation sequence sign-off, mandatory hold points for source inspection, and digital inspector stamp verification."),
            ("smart-torque-cmm-capture", "Connected DC Torque Wrench & CMM Measurement Capture",
             "Focus: Recording actual torque/angle values per bolt and CMM inspection files directly against the unit's serial number."),
            ("operator-cert-interlock", "Hard Interlock on Operator Welding / NDT / Bonding Certification Expiry",
             "Focus: Blocking sign-off on special processes (e.g. TIG welding, composite layup, FPI/X-ray NDT, crimping) if the operator's certification has lapsed."),
            ("tool-crib-gauge-calibration", "Tool Crib, Fixture & Gauge Calibration Usage Tracking",
             "Focus: Recording exactly which calibrated micrometer, thread gauge, or assembly jig serial number was used on each work order operation."),
        ],
    ),
    _mod(
        "nadcap-subcontract-scm",
        "Purchasing, NADCAP Special Processes & Bonded Stores",
        "Manage subcontract heat treatment, plating, NDT, approved supplier flow-down, and customer-furnished material.",
        "stock",
        [
            ("nadcap-special-process-flowdown", "Subcontract Special Process Flow-Down (Heat Treat, Anodising, Passivation, NDT)",
             "Focus: Automatically flowing down required aerospace/automotive specification revisions and NADCAP accreditation checks on subcontract POs."),
            ("supplier-scar-otd", "Supplier Corrective Action Requests (SCAR), PPM & OTD Scorecards",
             "Focus: Tracking supplier parts-per-million (PPM) defect rates, on-time delivery, and mandatory 8D SCAR responses."),
        ],
    ),
    _mod(
        "aftermarket-mro-rotable",
        "Aftermarket, MRO (Maintenance, Repair & Overhaul) & Rotables",
        "Manage returned units, strip-and-survey routings, service bulletins, and warranty claims.",
        "tools",
        [
            ("mro-strip-survey-quote", "MRO Receipt, Strip & Survey Inspection, and Repair Quoting",
             "Focus: Receiving a customer asset for overhaul, logging strip-down findings, quoting required replacement parts/labour, and issuing release certificates (e.g. Form 1 / 8130-3 / Certificate of Conformity)."),
            ("service-bulletins-mod-state", "Service Bulletins, Mod-State Tracking & Field Retrofits",
             "Focus: Tracking which modification standard each fielded serial number is at and scheduling upgrades."),
        ],
    ),
    _mod(
        "programme-finance-sizing",
        "Programme Accounting, WIP Valuation, Despatch & Sizing",
        "Track programme Estimate at Completion (EAC), AIAG/Odette barcoding, and shop-floor sizing.",
        "finance",
        [
            ("programme-wbs-costing", "Programme / Contract WBS Costing, Learning Curves & Milestone Billing",
             "Focus: Tracking non-recurring engineering, tooling, and unit production costs by programme work breakdown structure."),
            ("aiag-odette-vda-despatch", "AIAG / Odette / VDA Despatch Labels, Returnable Stillages & ASN",
             "Focus: Printing customer-compliant barcoded shipping labels, CofCs, and transmitting EDI ASNs."),
            ("aero-auto-sizing", "Shop Floor Kiosks, PLM/CAD Integration & User Licensing",
             "Focus: Sizing shop-floor terminals, SolidWorks/Teamcenter/Windchill PLM links, and user licenses."),
        ],
    ),
]


PRESETS = [
    {
        "id": "metal_fabrication",
        "name": "Metal Fabrication & Precision Engineering",
        "short_name": "Metal Fab & Precision Eng",
        "badge": "Discrete / Job Shop",
        "description": "Tailored for CNC machining, sheet metal fabrication, welding, laser/plasma cutting, surface finishing, and engineering job shops (15 modules).",
        "loader": _load_metal_fabrication,
    },
    {
        "id": "injection_moulding",
        "name": "Injection Moulding & Plastics",
        "short_name": "Injection Moulding",
        "badge": "Plastics & Polymers",
        "description": "Multi-cavity & family tooling, shot counters, press tonnage scheduling, colour sequencing, regrind/masterbatch ratios, Euromap MES, and SPC/PPAP (12 modules).",
        "modules": INJECTION_MOULDING_MODULES,
    },
    {
        "id": "food_beverage",
        "name": "Food Processing & Beverage",
        "short_name": "Food & Beverage",
        "badge": "FMCG / Chilled / Ambient",
        "description": "Recipes & allergen matrices, strict FEFO & retailer minimum shelf-life, catch-weight, CIP washdowns, digital HACCP, BRCGS 4-hour traceability, and EDI (11 modules).",
        "modules": FOOD_BEVERAGE_MODULES,
    },
    {
        "id": "pharma_lifesciences",
        "name": "Pharmaceutical & Life Sciences",
        "short_name": "Pharma & MedTech",
        "badge": "GMP / 21 CFR Part 11 / ISO 13485",
        "description": "Master Batch Records (MBR), Electronic Batch Records (eBR/eDHR), potency adjustment, weigh & dispense booths, LIMS/CoA, QP certification, CAPA, and serialisation/UDI (11 modules).",
        "modules": PHARMA_LIFESCIENCES_MODULES,
    },
    {
        "id": "chemical_process",
        "name": "Chemical, Coatings & Process Manufacturing",
        "short_name": "Chemical & Process",
        "badge": "Batch / Continuous Process",
        "description": "Weight/volume/% formulas, SG/VOC/solids roll-up, GHS/CLP drum labels, SDS & REACH tracking, reactor/tank scheduling, hazmat segregation, and ADR dangerous goods (11 modules).",
        "modules": CHEMICAL_PROCESS_MODULES,
    },
    {
        "id": "electronics_assembly",
        "name": "Electronics, PCB & High-Tech Assembly",
        "short_name": "Electronics & EMS",
        "badge": "SMT / Box-Build / OEM",
        "description": "CAD/EDA BOM import, Approved Manufacturer Lists (AML), distributor API quoting, MSL floor-life & unique reel IDs, SMT/AOI/ICT serial traceability, IPC-A-610, and RMA (7 modules).",
        "modules": ELECTRONICS_ASSEMBLY_MODULES,
    },
    {
        "id": "automotive_aerospace",
        "name": "Automotive, Aerospace & Complex Discrete",
        "short_name": "Automotive & Aerospace",
        "badge": "AS9100 / IATF 16949",
        "description": "Serial effectivity, As-Designed vs As-Built genealogy, FAIR (AS9102) & PPAP, EDI JIT/Kanban, digital travellers with torque/certification interlocks, NADCAP, and MRO (7 modules).",
        "modules": AUTOMOTIVE_AEROSPACE_MODULES,
    },
    {
        "id": "blank",
        "name": "Blank Custom Workspace",
        "short_name": "Blank Workspace",
        "badge": "Custom",
        "description": "Start with an empty workspace and create your own custom modules and focus items from scratch (0 modules).",
        "modules": [],
    },
]

PRESETS_BY_ID = {p["id"]: p for p in PRESETS}


def get_preset_modules(preset_id, seed_path=None):
    """Return a fresh deep-copied list of raw module dicts for `preset_id`."""
    preset = PRESETS_BY_ID.get(preset_id) or PRESETS_BY_ID["metal_fabrication"]
    if "loader" in preset:
        raw = preset["loader"](seed_path)
    else:
        raw = copy.deepcopy(preset.get("modules") or [])
    # Ensure preset modules start clean (scope='pending', notes=[]) when used as a template
    for mod in raw:
        for it in mod.get("items") or []:
            it["scope"] = "pending"
            it["priority"] = "phase2"
            it["criticality"] = "normal"
            it["notes"] = []
    return raw


def list_presets(seed_path=None):
    """Return metadata for every available industry preset (for the UI picker)."""
    out = []
    for p in PRESETS:
        mods = p["loader"](seed_path) if "loader" in p else (p.get("modules") or [])
        item_count = sum(len(m.get("items") or []) for m in mods)
        out.append({
            "id": p["id"],
            "name": p["name"],
            "short_name": p["short_name"],
            "badge": p["badge"],
            "description": p["description"],
            "module_count": len(mods),
            "item_count": item_count,
        })
    return out

