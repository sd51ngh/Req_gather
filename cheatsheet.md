# Manufacturing ERP / MES System — Requirements Cheatsheet

---

## Functional Areas & Business Domains (Manufacturing Focus)

- Manufacturing & Production
- Supply Chain Management (SCM)
- Quality Management (QMS)
- Plant Maintenance & Asset Management (CMMS)
- Warehouse & Inventory Management
- Finance & Accounting (Manufacturing Cost)
- Human Resources & Workforce
- Health, Safety & Environment (HSE/EHSQ)
- Sales, CRM & Configure-Price-Quote (CPQ)
- Project Management (ETO / Make-to-Order)
- Compliance & Regulatory (UK / ISO)
- Reporting, Analytics & Industry 4.0

---

# Production Planning & Scheduling

- Master Production Schedule (MPS)
- Material Requirements Planning (MRP / MRP II)
- Capacity Requirements Planning (CRP)
- Rough-Cut Capacity Planning (RCCP)
- Finite / Infinite Scheduling
- Work Center & Machine Capacity Management
- Production Order Creation & Release
- Planned vs Actual Production Tracking
- Make-to-Stock (MTS) / Make-to-Order (MTO) / Engineer-to-Order (ETO) Support
- Discrete, Process & Repetitive Manufacturing Modes
- Demand Forecasting & Sales & Operations Planning (S&OP)
- What-If Scenario Planning

---

# Bill of Materials (BOM) & Product Structure

- Multi-Level BOM Management (Raw → Sub-Assembly → Finished Good)
- Engineering BOM (EBOM) vs Manufacturing BOM (MBOM) vs Sales BOM (SBOM)
- BOM Version & Revision Control
- Configurable / Variant BOM Support
- Engineering Change Orders (ECO) & Change Request Workflow
- BOM Cost Roll-Up & Where-Used Analysis
- BOM Comparison & Impact Analysis
- Integration with MRP for Automated Procurement
- Phantom / Non-Stocked BOM Items
- Co-Products & By-Products Management

---

# Shop Floor Control & Manufacturing Execution (MES)

- Work Order Management (Create, Release, Complete)
- Job Routing & Operation Sequencing
- Work-in-Progress (WIP) Tracking
- Real-Time Shop Floor Data Collection (SFDC)
- Labour Booking & Time Tracking per Operation
- Material Issue & Backflushing
- Scrap & Rework Recording
- Standard Operating Procedures (SOPs) Enforcement
- Hard-Gated Execution (Step completion validation)
- Electronic Work Instructions (EWI / Digital Job Cards)
- Operator Sign-Off & Electronic Signatures
- Overall Equipment Effectiveness (OEE) Monitoring
- Production Batch & Lot Control
- Genealogy & Full Forward/Backward Traceability
- Integration with SCADA / PLC / IoT Machines

---

# Inventory & Warehouse Management

- Real-Time Inventory Tracking (Multi-Location / Multi-Site)
- Lot / Serial / Batch Number Control
- Expiry Date & FEFO (First Expired, First Out) Management
- Raw Material, WIP & Finished Goods Inventory Segregation
- Goods Receipt & Goods Issue Processing
- Stock Transfers & Inter-Site Movements
- Cycle Counting & Physical Inventory Auditing
- Automated Reorder Points (ROP) & Safety Stock
- Barcode & RFID Scanning Support
- Warehouse Layout & Bin / Location Management
- Inbound Inspection (Quality Gate on Receipt)
- Quarantine & Blocked Stock Management
- Returns & Reverse Logistics
- Inventory Valuation (FIFO, LIFO, Weighted Average, Standard Cost)

---

# Procurement & Supplier Management

- Purchase Requisition & Purchase Order (PO) Management
- MRP-Driven Suggested Purchase Orders
- Supplier / Vendor Master Data Management
- Supplier Qualification & Approved Vendor List (AVL)
- Supplier Performance Scorecards (OTD, Quality, Lead Time)
- Request for Quotation (RFQ) & Supplier Comparison
- PO Tracking & Expediting
- Goods Receipt & 3-Way Matching (PO / GR / Invoice)
- Supplier Contracts & Blanket Orders
- Drop-Shipping & Subcontract (Toll Manufacturing) Management
- Supply Chain Risk Management
- Multi-Currency & International Purchasing

---

# Quality Management (QMS)

- Incoming Goods Inspection (IQC)
- In-Process Quality Checks (IPQC / SPC)
- Final Inspection & Outgoing Quality Control (OQC)
- Inspection Plans, Sampling Rules & AQL Levels
- Non-Conformance Reports (NCR) & Defect Logging
- Corrective & Preventive Action (CAPA) Workflow
- Customer Complaint Management (RMA / 8D Process)
- First Article Inspection (FAI)
- Statistical Process Control (SPC) & Control Charts
- Certificate of Analysis (CoA) Generation
- Document Control & Quality Records Management
- Calibration Management (Measuring Equipment Register)
- Internal & External Audit Management
- ISO 9001:2015 Compliance Support
- Risk-Based Thinking & Quality Risk Register
- Continuous Improvement (Kaizen / PDCA)


---

# Plant Maintenance & Asset Management (CMMS)

- Asset Register & Equipment Hierarchy (Site → Line → Machine → Component)
- Preventive Maintenance (PM) Plans & Scheduling
- Predictive Maintenance (PdM) via IoT Sensor Integration
- Condition-Based Monitoring (CBM)
- Work Order Management for Maintenance Tasks
- Breakdown / Corrective Maintenance Recording
- Mean Time Between Failures (MTBF) & Mean Time to Repair (MTTR)
- OEE Tracking (Availability, Performance, Quality)
- Spare Parts Inventory & MRO (Maintenance, Repair & Operations) Procurement
- Maintenance Cost Tracking per Asset
- Equipment Downtime Logging & Root Cause Analysis
- Statutory Inspection Management (LOLER, PSSR, Pressure Vessels)
- Calibration & Tooling Lifecycle Management
- Mobile Work Order Access for Maintenance Technicians

---

# Finance & Manufacturing Cost Accounting

- Standard Costing & Cost Roll-Up (Material + Labour + Overhead)
- Actual Costing & Variance Analysis (Purchase Price, Labour, Overhead Variances)
- Activity-Based Costing (ABC)
- Product Profitability Reporting
- Job / Work Order Costing
- Work-in-Progress (WIP) Valuation & Reporting
- Accounts Payable (AP) & Accounts Receivable (AR)
- General Ledger & Chart of Accounts (UK GAAP / IFRS)
- Budgeting & Forecasting
- Multi-Company / Multi-Currency / Multi-Entity Consolidation
- VAT Management (UK VAT, Making Tax Digital – MTD)
- Cash Flow Management & Payment Scheduling
- Fixed Asset Accounting & Depreciation
- Inter-Company Transactions
- Financial Statements (P&L, Balance Sheet, Cash Flow)
- Journal Entries & Reconciliations

---

# Sales, CRM & Configure-Price-Quote (CPQ)

- Customer & Contact Management
- Opportunity & Pipeline Management
- Quotation & Proposal Generation
- Configure-Price-Quote (CPQ) for Complex / Configurable Products
- Rules-Based Product Configuration & Constraint Validation
- Dynamic Pricing (Volume Discounts, Customer Tiers, Cost-Plus)
- Margin Protection & Approval Workflows
- Sales Order Entry & Acknowledgement
- Delivery Scheduling & Available-to-Promise (ATP)
- Customer Portal / Self-Service Ordering
- Forecast Integration with Production Planning
- Customer Returns & Credit Note Management
- Sales Analytics & Dashboards

---

# Supply Chain Management (SCM)

- Demand Planning & Statistical Forecasting
- S&OP (Sales & Operations Planning) Process
- Supplier Collaboration & VMI (Vendor Managed Inventory)
- Subcontract Manufacturing Management
- Import / Export Compliance (UK Trade Tariffs, HMRC)
- Landed Cost Calculation
- 3PL / 4PL Integration
- Supply Chain Risk & Disruption Alerting
- End-to-End Lot Traceability Across the Supply Chain

---

# Warehouse Management

- Inventory Management (See Inventory section above)
- Order Processing & Pick List Generation
- Inbound Receive Logistics (ASN / GRNI)
- Barcode & RFID Technology
- Outbound Logistics (Pick, Pack & Ship)
- Wave & Batch Picking
- Packing Station & Carton Management
- Despatch Notes & Proof of Delivery (POD)
- Courier / Carrier Integration (DPD, DHL, Royal Mail, UPS)
- Cross-Docking Support
- Returns Processing & Restocking
- Integration with Supply Chain & ERP

---

# Human Resources & Workforce Management

- Employee Master Data & Organisation Structure
- Attendance & Time Tracking (Clock-in / Clock-out)
- Timesheet Management (Shop Floor Labour Capture)
- Shift & Rota Planning
- Leave Management & Holiday Entitlements (UK Statutory Leave)
- Skills Matrix & Training Records
- Labour Costing & Productivity Reporting
- Payroll Integration (HMRC RTI / PAYE)
- Expense Management
- Performance Management & Appraisals

---

# Health, Safety & Environment (HSE / EHSQ)

- Risk Assessment Management (COSHH, Manual Handling, Machinery)
- Incident, Near-Miss & Accident Reporting
- RIDDOR Compliance (Reporting of Injuries, Diseases & Dangerous Occurrences Regulations 2013)
- Investigation & Root Cause Analysis
- CAPA (Corrective & Preventive Action) for Safety Incidents
- PPE Register & Issuance Tracking
- Permit to Work (PTW) Management
- Safety Observation & Tour Tracking
- Hazardous Substances Register (COSHH / UK REACH)
- Environmental Monitoring & Waste Management
- ISO 45001 (OH&S) & ISO 14001 (EMS) Alignment
- Audit & Inspection Scheduling
- Emergency Response Planning
- Safety Training Records & Competency Tracking

---

# Compliance & Regulatory (UK Manufacturing)

## Quality & Product Standards
- ISO 9001:2015 — Quality Management System
- ISO 13485:2016 — Medical Devices QMS
- IATF 16949 — Automotive Quality Management
- AS9100 — Aerospace Quality Management
- GMP (Good Manufacturing Practice) — Pharma / Food

## UK Regulatory Bodies & Frameworks
- **MHRA** — Medicines & Healthcare Products Regulatory Agency
- **UK MDR** — UK Medical Device Regulations (UKCA Marking)
- **UK REACH** — Chemical Substance Registration (HSE)
- **COSHH** — Control of Substances Hazardous to Health
- **PUWER** — Provision & Use of Work Equipment Regulations
- **LOLER** — Lifting Operations & Lifting Equipment Regulations
- **RIDDOR** — Injury & Incident Reporting to HSE
- **Making Tax Digital (MTD)** — HMRC VAT digital compliance
- **BS Standards** (British Standards Institution)

## Traceability & Documentation
- Full Forward & Backward Lot/Batch Traceability
- Certificate of Conformance (CoC) & Certificate of Analysis (CoA)
- Technical Documentation & Design History Files (DHF)
- Product Recall Management
- Audit-Ready Record Keeping

---

# Project Management (ETO / Complex Manufacturing)

- Project Workbench & Work Breakdown Structure (WBS)
- Project Scheduling (Gantt, Critical Path)
- Tasks, Milestones & Dependencies
- Resource Allocation & Capacity Planning
- Project Budgeting & Cost Management
- Actual vs Budget Variance Tracking
- Project Billing & Milestone Invoicing
- Subcontractor Management within Projects
- Document Management & Drawing Revision Control
- Project Analytics & Dashboards

---

# Reporting, Analytics & Industry 4.0

## Operational KPIs & Dashboards
- Overall Equipment Effectiveness (OEE)
- Schedule Adherence & On-Time Delivery (OTD)
- First-Pass Yield (FPY) & Scrap Rate
- Cycle Time & Throughput
- MTBF & MTTR (Maintenance)
- Cost per Unit Produced
- Inventory Turns & Days Inventory Outstanding (DIO)
- Supplier On-Time Delivery Rate
- Purchase Price Variance (PPV)

## Reporting & Analytics
- Real-Time Production Dashboards
- Financial Reporting (P&L, Costing Reports, Variance Analysis)
- Quality Performance Reports
- Supply Chain & Procurement Analytics
- Role-Based Dashboards (Shop Floor Operator, Plant Manager, CFO)
- Self-Service BI & Ad-hoc Reporting

## Industry 4.0 & Digital Manufacturing
- IoT / IIoT Sensor Integration & Machine Connectivity
- OPC UA / MQTT Industrial Protocol Support
- Digital Twin Modelling (Simulation & Optimisation)
- Predictive Analytics & AI-Driven Demand Forecasting
- Edge Computing for Shop Floor Data Processing
- Cloud & On-Premise Deployment Options
- Mobile & Tablet Interface for Shop Floor Workers
- API / Integration Layer (REST API, EDI, Webhooks)
- Cybersecurity & Role-Based Access Control (RBAC)

---

# Integration Landscape (Manufacturing Systems)

| Layer | System Type | Examples |
|---|---|---|
| Business Planning | ERP | SAP S/4HANA, Oracle ERP, Microsoft Dynamics 365, Infor LN, Epicor, Sage X3 |
| Shop Floor Execution | MES | Siemens Opcenter, Rockwell Plex, Tulip, Apriso |
| Quality Management | QMS | Ideagen Q-Pulse, MasterControl, ETQ, Intelex |
| Maintenance | CMMS | IBM Maximo, Infor EAM, UpKeep, Fiix |
| Warehouse | WMS | Manhattan, Deposco, Infor WMS |
| Sales & CRM | CRM/CPQ | Salesforce, Microsoft Dynamics CRM, PROS CPQ |
| Analytics | BI/Reporting | Power BI, Qlik, Tableau, Cognos |
| Connectivity | Integration | MuleSoft, Azure Integration Services, Dell Boomi |