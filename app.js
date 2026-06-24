// Default Data Structure matching 'Requirement gathering.md'
const DEFAULT_MODULES = [
    {
        id: "product-design-bom",
        title: "Bills of Materials (BOM) and variant handling",
        description: "Configure parts, revision controls, multi-level Bills of Materials (BOM), and design lifecycles.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>`,
        items: [
            {
                id: "multi-level-bom",
                name: "Multi-level BOM",
                guidance: "Focus: Managing nested component relationships, parent-child hierarchies, and assembly roll-ups.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "variant-option-handling",
                name: "Variant/Option handling",
                guidance: "Focus: Defining product features, variables, configuration combinations, and rules.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "master-specifications",
                name: "Master product specifications",
                guidance: "Focus: Core technical attributes, tolerances, unit of measure definitions, and base configurations.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "revision-control",
                name: "Revision control",
                guidance: "Focus: Tracking revisions, history logs, approval workflow logs, and release numbers.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "design-lifecycle",
                name: "Design lifecycle management",
                guidance: "Focus: CAD integration, design release gates, obsolete/superseded parts, and maturity levels.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "npi-new",
                name: "New product introduction (NPI)",
                guidance: "Focus: Engineering change orders (ECO), pre-production verification, and transition-to-production checksheets.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "estimating-quotations",
        title: "Estimating & Quotations",
        description: "Handle margins, complex multi-line quoting, pricing agreements, and prospective pipelines.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 7.5L12 10.5M12 10.5L15 7.5M12 10.5V16.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`,
        items: [
            {
                id: "crm",
                name: "Customer Relationship Mgmt (CRM)",
                guidance: "Focus: Interaction tracking, prospect accounts, marketing pipelines, and contact directory.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "quote-mgmt",
                name: "Quote Mgmt with quote validity and price agreement",
                guidance: "Focus: Setting quote expiry, customer-specific pricing agreements, discount boundaries, and conversions.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "moq",
                name: "Minimum order Quantity",
                guidance: "Focus: Defining MOQ thresholds per product, customer group rules, and MOQ enforcement checks.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "discount-mgmt",
                name: "Discount % management",
                guidance: "Focus: Setting maximum discount limits, approval workflows for high discounts, and customer-specific discount tiers.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "sales-pipeline",
                name: "Sales Process, Pipeline Mgmt",
                guidance: "Focus: Pipeline stages, opportunity win/loss rates, quote revision logs, and forecasting metrics.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "variant-configurator",
                name: "Variant Configurator with BOM integration and compatibility rules",
                guidance: "Focus: Rules-based compatibility checking, dynamic pricing based on choices, and automatic BOM generation.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "ecommerce",
                name: "Web-shop & E-Commerce Integration",
                guidance: "Focus: API links to B2B/B2C storefronts, customer portal pricing lookups, and order imports.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "sales-order-processing",
        title: "Sales Order Processing",
        description: "Automate sales confirmations, compliance, e-commerce imports, and order release criteria.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" /></svg>`,
        items: [
            {
                id: "export-regs",
                name: "Export Regs Compliance",
                guidance: "Focus: Tariffs/HS commodity codes, customs declarations, and shipping incoterms check sheets.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "delivery-optimisation",
                name: "Delivery Vehicle Optimisation",
                guidance: "Focus: Grouping orders by geographic route and load parameters to optimize vehicle utility.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "outlook-integration",
                name: "Outlook Integration",
                guidance: "Focus: Parsing POs directly from email, sending automated order acknowledgements, and archiving correspondence.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "production-planning-scheduling",
        title: "Production Planning & Scheduling",
        description: "Balance supply and demand, run MRP calculations, and allocate factory resources capacity.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5m-9-6h.008v.008H12v-.008zM12 15h.008v.008H12V15zm0 2.25h.008v.008H12v-.008zM9.75 15h.008v.008H9.75V15zm0 2.25h.008v.008H9.75v-.008zM7.5 15h.008v.008H7.5V15zm0 2.25h.008v.008H7.5v-.008zm6.75-4.5h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V15zm0 2.25h.008v.008h-.008v-.008zm2.25-4.5h.008v.008H16.5v-.008zm0 2.25h.008v.008H16.5V15z" /></svg>`,
        items: [
            {
                id: "demand-forecasting",
                name: "Demand Forecasting",
                guidance: "Focus: Reviewing sales pipelines, historical patterns, and raw marketing inputs to create forecasting estimates.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "mrp",
                name: "Material Requirement Planning",
                guidance: "Focus: Automated net-requirement calculations, lead-time offsets, replenishment suggestions, and safety stock flags.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "gantt-kanban-calendar",
                name: "Gantt view / Calendar view / Kanban view",
                guidance: "Focus: Visual scheduling boards, interactive drag-drop timelines, calendar syncing, and status cards.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "forward-scheduling",
                name: "Forward scheduling",
                guidance: "Focus: Scheduling operations sequentially from the earliest start date to calculate delivery dates.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "backward-scheduling",
                name: "Backward scheduling",
                guidance: "Focus: Planning backwards from customer due-dates to calculate the latest release release-gate timing.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "capacity-planning",
                name: "Capacity planning",
                guidance: "Focus: Modeling machine and crew availability limits, identifying bottlenecks, and planning buffer capacity.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "aps",
                name: "Advanced Planning & Factory Scheduling (APS)",
                guidance: "Focus: Finite/infinite planner, tool/mold conflicts, setup optimization, and visual Gantt boards.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "purchasing-stock-control",
        title: "Purchasing & Stock Control",
        description: "Procure raw items, track stock movements, audit inventory, and rate supplier performances.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m8.25 3v6.75m0 0l-3-3m3 3l3-3M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" /></svg>`,
        items: [
            {
                id: "supplier-assessment-scm",
                name: "Supplier Assessment & Mgmt (SCM)",
                guidance: "Focus: Supplier performance scorecards, defect rates, target lead times, and approved lists.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "critical-stock-alerts",
                name: "Critical Stock Alerts",
                guidance: "Focus: System triggers for items dropping below safety margins, and expedited purchase procedures.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "eprocurement",
                name: "E-Procurement Portal Integration",
                guidance: "Focus: B2B portal interfaces, automated punch-out, and direct PO electronic data interchanges (EDI).",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "po-revision",
                name: "Purchase order revision",
                guidance: "Focus: Tracking revisions, supplier change acknowledgements, and delivery date shifts.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "purchase-price-agreement",
                name: "Purchase price agreement",
                guidance: "Focus: Bulk volume discount rules, contract pricing, and index-linked price lists.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "vmi",
                name: "Vendor Managed Inventory (VMI)",
                guidance: "Focus: Supplier-owned stock levels, consignment warehousing, and auto-billing configurations.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "purchase-price-variance",
                name: "Purchase price variance",
                guidance: "Focus: Auditing gap margins between target cost standard and actual vendor invoicing prices.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "production-management",
        title: "Production Management",
        description: "Release work orders, log shop floor feedback, run CAD/PDM interfaces, and assign step-by-step tasks.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12a7.5 7.5 0 0015 0m-15 0a7.5 7.5 0 1115 0m-15 0H3m16.5 0H21m-1.5 0H12m-8.457 3.077l1.41-.513m14.095-5.13l1.41-.513M5.106 17.785l1.15-.827m11.379-8.16l1.15-.827M8.14 21.27l.707-1.03m7.65-11.12l.707-1.03M12 3v1.5m0 15V21m-3.077-8.457l-.513-1.41m5.13 14.095l-.513-1.41M17.785 5.106l-.827 1.15m-8.16 11.379l-.827 1.15m-3.03-8.62l-1.03-.707m11.12 7.65l-1.03-.707" /></svg>`,
        items: [
            {
                id: "sfdc-new",
                name: "Shop Floor Data Collection",
                guidance: "Focus: Production Feedback, Shop Floor Terminal (Touch Screen, Barcode Scanner).",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "work-order-creation",
                name: "Work order creation",
                guidance: "Focus: Automatic conversion of planned orders, routing verification, and resource assignment.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "wip-tracking",
                name: "Work in progress tracking",
                guidance: "Focus: Batch identification, material usage logging, operations timing, and staging locations.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "work-instructions",
                name: "Work Instructions",
                guidance: "Focus: Visual operating procedures, tool specs, quality checks, and technician sign-offs.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "qms",
        title: "Quality Management System (QMS)",
        description: "Enforce standard quality checkpoints, capture deviations, audit material origins, and coordinate corrective actions.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0110 21a3.746 3.746 0 01-3.068-.593 3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0114 3c1.251 0 2.396.618 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" /></svg>`,
        items: [
            {
                id: "qc-plan",
                name: "Quality control plan",
                guidance: "Focus: Quality checkpoint definitions, sample rates, target thresholds, and logging conformance.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "deviation-capa",
                name: "Deviation mgmt, CAPA",
                guidance: "Focus: CAPA logs, root-cause investigations, NCR forms, and corrective tracking.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "inspection-plan",
                name: "Inspection plan",
                guidance: "Focus: Detailed step-by-step inspections for incoming parts and manufacturing checkpoints.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "root-cause-analysis",
                name: "Root cause analysis",
                guidance: "Focus: Fault trees, 5-Why templates, Ishikawa fishbones, and prevention planning.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "approval-workflow",
                name: "Approval workflow",
                guidance: "Focus: Sign-off boundaries, electronic signatures, and approval hierarchies.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "pick-pack-despatch",
        title: "Pick, Pack & Despatch",
        description: "Manage pick lists, track carton packs, print label requirements, and manage fleet configurations.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124l-.047-.75m-14.773-2.625h14.773M2.25 12.75V4.875A1.125 1.125 0 013.375 3.75h9.81c.318 0 .624.146.82.4l3.06 3.89c.18.23.28.514.28.808v.538m0-2.25H12a1.125 1.125 0 01-1.125-1.125V3.75m-9 10.5h16.5V18a1.5 1.5 0 01-1.5 1.5h-13.5A1.5 1.5 0 012.25 18v-3.75z" /></svg>`,
        items: [
            {
                id: "export-doc-mgmt",
                name: "Export Document Mgmt",
                guidance: "Focus: Automated packing lists, commercial invoices, and country-of-origin documentation.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "route-planning",
                name: "Vehicle Route Planning",
                guidance: "Focus: Dispatch sorting, drop sequencing, vehicle dimensions boundaries, and carrier dispatch.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "fleet-mgmt",
                name: "Delivery Fleet Management",
                guidance: "Focus: Tracking in-house trucks, driver qualifications, safety checks, and third-party logistics (3PL) links.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "route-optimisation",
                name: "Delivery Route Optimisation",
                guidance: "Focus: Algorithmic mapping based on traffic patterns, fuel conservation, and drop-off windows.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "warehouse-heatmap",
                name: "Warehouse heat map",
                guidance: "Focus: Visual pick-frequency mapping to improve warehouse staging layout and reduce picking times.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "field-service",
        title: "Field Service mgmt",
        description: "Track installations, manage maintenance, repair, and overhaul (MRO) tasks, and coordinate engineering timesheets.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.67 2.67 0 1113.5 17.25l-5.83-5.83m.084-2.113l-5.83-5.83A2.67 2.67 0 115.67 1.83l5.83 5.83m0 0L17.25 1.83A2.67 2.67 0 1121 5.67l-5.83 5.83m0 0L21 17.25a2.67 2.67 0 11-3.75 3.75l-5.83-5.83" /></svg>`,
        items: [
            {
                id: "field-service-engineer",
                name: "Field Service Engineer",
                guidance: "Focus: Dispatch queues, engineer location links, tools configuration, and availability schedules.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "job-card-mgmt",
                name: "Job card creation and mgmt",
                guidance: "Focus: Writing technical repair details, safety check logs, and parts consumption on-site.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "installation-commissioning",
                name: "Installation & Commissioning",
                guidance: "Focus: Customer sign-offs, site preparation checks, equipment startups, and calibration records.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "mobile-access",
                name: "Mobile access",
                guidance: "Focus: Responsive design or app interface for engineers to input field data without desks.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "service-contract-mgmt",
                name: "Service contract mgmt",
                guidance: "Focus: Tracking warranties, SLA terms, annual service intervals, and renewals.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "hr",
        title: "HR",
        description: "Administer staffing directories, log skills matrices, track certifications, and record working shifts.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a.75.75 0 000-1.5.75.75 0 000 1.5zM12 18.72a.75.75 0 000-1.5.75.75 0 000 1.5zM6 18.72a.75.75 0 000-1.5.75.75 0 000 1.5zM12 12.75a3 3 0 100-6 3 3 0 000 6zM2.25 12a9.75 9.75 0 0119.5 0c0 .35-.018.692-.053 1.03a9.75 9.75 0 11-19.394 0c-.035-.338-.053-.68-.053-1.03z" /></svg>`,
        items: [
            {
                id: "timesheets-new",
                name: "Timesheets",
                guidance: "Focus: Recording direct/indirect hours, overtime calculation, project codes, and line manager approvals.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "skills-matrix-organogram",
                name: "Skill matrix/organogram",
                guidance: "Focus: Certifications mapping, shift schedules, department hierarchy, and skills search.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "training-mgmt",
                name: "training mgmt",
                guidance: "Focus: Safety courses, training schedules, course histories, and renewals reminders.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "expense-tracking",
                name: "expense tracking",
                guidance: "Focus: Travel expenses logging, receipt uploads, mileage limits, and project invoicing linkages.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "integrations",
        title: "Integrations",
        description: "Connect your system with external platforms, CRM tools, email applications, shipping, and payment systems.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" /></svg>`,
        items: [
            {
                id: "api-documentation",
                name: "API Documentation",
                guidance: "Focus: Developer REST API endpoints, webhooks, authentication standards, and data payloads.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "integrations-outlook",
                name: "Outlook Integration",
                guidance: "Focus: Syncing emails, calendar meetings, task tracking, and automated contact lookups.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "crm-systems",
                name: "CRM system - Salesforce, HubSpot, Zoho etc",
                guidance: "Focus: Account synchronization, lead routing, pipeline progression sync, and custom field maps.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "finance-systems",
                name: "Finance Systems eg. Sage, Xero, Quickbooks, etc",
                guidance: "Focus: Ledger exports, tax settings alignment, invoicing flows, bank feeds, and reconciliation.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "ecommerce-platforms",
                name: "E-commerce platforms eg. Shopify, Magento, WooCommerce",
                guidance: "Focus: Inventory syncing, order imports, tracking numbers update, and pricing alignments.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "shipping-carriers",
                name: "Shipping carriers eg. DHL, FedEx, UPS",
                guidance: "Focus: Real-time freight calculations, label generation, pickup booking, and tracking links.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "payment-gateways",
                name: "Payment gateways eg. Stripe, PayPal",
                guidance: "Focus: Direct checkout integrations, refund flows, transaction fee accounting, and payouts reconciliation.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    },
    {
        id: "dashboards",
        title: "Dashboards",
        description: "Establish overview metrics, stock analytics, sales insights, production logs, and financial KPIs.",
        icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" /></svg>`,
        items: [
            {
                id: "overview-dashboard",
                name: "Overview Dashboard",
                guidance: "Focus: High-level KPI summaries, cross-department analytics, task queues, and performance metrics.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "stock-dashboard",
                name: "Stock Dashboard",
                guidance: "Focus: Warehouse stock value, turnover ratios, out-of-stock items, safety-stock alerts, and expiration dates.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "sales-dashboard",
                name: "Sales Dashboard",
                guidance: "Focus: Monthly recurring revenue, win-rates, salesperson conversion performance, and average deal sizes.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "production-dashboard",
                name: "Production Dashboard",
                guidance: "Focus: Work order progression stats, machinery utilization rate, labor efficiencies, and scrap metrics.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            },
            {
                id: "financial-dashboard",
                name: "Financial Dashboard",
                guidance: "Focus: Gross margins, purchase price variance metrics, cost of goods sold (COGS), and cash flows.",
                scope: "pending",
                priority: "med",
                criticality: "normal",
                notes: ""
            }
        ]
    }
];

// App State Manager
class ReqGatherApp {
    constructor() {
        this.modules = [];
        this.activeModuleId = null;
        
        // Dom Elements
        this.cardsGrid = document.getElementById('cards-grid');
        this.drawer = document.getElementById('drawer');
        this.drawerOverlay = document.getElementById('drawer-overlay');
        this.btnCloseDrawer = document.getElementById('btn-close-drawer');
        this.drawerTitle = document.getElementById('drawer-title');
        this.drawerSubtitle = document.getElementById('drawer-subtitle');
        this.drawerIcon = document.getElementById('drawer-module-icon');
        this.focusList = document.getElementById('focus-list');
        this.toast = document.getElementById('toast');
        
        // Custom Focus Area input elements
        this.inputNewFocusName = document.getElementById('input-new-focus-name');
        this.btnAddCustomFocus = document.getElementById('btn-add-custom-focus');
        
        // Modal
        this.exportModal = document.getElementById('export-modal');
        this.btnExportMd = document.getElementById('btn-export-md');
        this.btnExportCsv = document.getElementById('btn-export-csv');
        this.btnCloseExportModal = document.getElementById('btn-close-export-modal');
        this.exportPreviewContent = document.getElementById('export-preview-content');
        this.btnCopyPreview = document.getElementById('btn-copy-preview');
        this.btnDownloadPreview = document.getElementById('btn-download-preview');

        // Add Custom Module Modal elements
        this.addModuleModal = document.getElementById('add-module-modal');
        this.inputModuleTitle = document.getElementById('input-module-title');
        this.inputModuleDesc = document.getElementById('input-module-desc');
        this.btnConfirmAddModule = document.getElementById('btn-confirm-add-module');
        this.btnCancelAddModule = document.getElementById('btn-cancel-add-module');
        this.btnCloseAddModuleModal = document.getElementById('btn-close-add-module-modal');
        
        // JSON backup/restore
        this.btnExportJson = document.getElementById('btn-export-json');
        this.btnImportJson = document.getElementById('btn-import-json');
        this.importFileInput = document.getElementById('import-file-input');
        
        // Reset
        this.btnReset = document.getElementById('btn-reset-data');

        // Suppressed Items elements
        this.suppressedSection = document.getElementById('suppressed-items-section');
        this.suppressedHeader = document.getElementById('suppressed-items-header');
        this.btnToggleSuppressed = document.getElementById('btn-toggle-suppressed');
        this.suppressedListEl = document.getElementById('suppressed-list');
        this.suppressedCountEl = document.getElementById('suppressed-count');
        this.isSuppressedExpanded = false;

        this.init();
    }

    init() {
        this.loadData();
        this.renderCards();
        this.updateOverallProgress();
        this.setupEventListeners();
    }

    // Load from local storage or set defaults
    loadData() {
        const savedData = localStorage.getItem('mrp_requirements_data');
        if (savedData) {
            try {
                this.modules = JSON.parse(savedData);
            } catch (e) {
                console.error("Failed to parse saved data. Reverting to default.", e);
                this.modules = JSON.parse(JSON.stringify(DEFAULT_MODULES));
            }
        } else {
            this.modules = JSON.parse(JSON.stringify(DEFAULT_MODULES));
        }

        // Ensure all items (including from legacy localstorage or defaults) have criticality & suppressed defined
        this.modules.forEach(mod => {
            mod.items.forEach(item => {
                if (!item.criticality) {
                    item.criticality = "normal";
                }
                if (item.suppressed === undefined) {
                    item.suppressed = false;
                }
            });
        });
    }

    // Save to local storage
    saveData() {
        localStorage.setItem('mrp_requirements_data', JSON.stringify(this.modules));
        this.updateOverallProgress();
        this.renderCards();
    }

    // Show save toast
    showToast(message = "Changes saved!") {
        this.toast.textContent = message;
        this.toast.classList.add('show');
        setTimeout(() => {
            this.toast.classList.remove('show');
        }, 2000);
    }

    // Calculate progress indicators
    updateOverallProgress() {
        let totalItems = 0;
        let scopedItems = 0;

        this.modules.forEach(mod => {
            mod.items.forEach(item => {
                if (item.suppressed) return; // Skip suppressed items
                totalItems++;
                if (item.scope !== "pending") {
                    scopedItems++;
                }
            });
        });

        const percentage = totalItems > 0 ? Math.round((scopedItems / totalItems) * 100) : 0;
        
        // Update DOM
        document.getElementById('overall-percentage').textContent = `${percentage}%`;
        document.getElementById('overall-progress-bar').style.width = `${percentage}%`;
        document.getElementById('completed-stats').textContent = `${scopedItems} of ${totalItems} items scoped`;
    }

    // Render main cards
    renderCards() {
        this.cardsGrid.innerHTML = '';
        
        this.modules.forEach(mod => {
            const card = document.createElement('div');
            card.className = 'mrp-card';
            card.dataset.id = mod.id;
            
            // Calculate progress for card
            const activeItems = mod.items.filter(item => !item.suppressed);
            const total = activeItems.length;
            const scoped = activeItems.filter(item => item.scope !== "pending").length;
            const progressPercent = total > 0 ? Math.round((scoped / total) * 100) : 0;

            card.innerHTML = `
                <div class="card-top">
                    <div class="card-icon-wrapper">
                        ${mod.icon}
                    </div>
                    <h3>${mod.title}</h3>
                    <p class="card-desc">${mod.description}</p>
                </div>
                <div class="card-bottom">
                    <div class="card-progress-bar" title="${progressPercent}% Complete">
                        <div class="card-progress-fill" style="width: ${progressPercent}%;"></div>
                    </div>
                    <span class="card-badge">${scoped}/${total} scoped</span>
                </div>
            `;
            
            card.addEventListener('click', () => this.openDrawer(mod.id));
            this.cardsGrid.appendChild(card);
        });

        // Append the special "+" card for adding custom modules
        const addCard = document.createElement('div');
        addCard.className = 'mrp-card add-card-trigger';
        addCard.innerHTML = `
            <div class="card-add-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width: 24px; height: 24px;">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
            </div>
            <h3>Add Custom Module</h3>
            <p class="card-desc">Create a new business module card to gather customized requirements.</p>
        `;
        addCard.addEventListener('click', () => this.openAddModuleModal());
        this.cardsGrid.appendChild(addCard);
    }

    // Slide in drawer and load focus areas with morphing animation
    openDrawer(moduleId) {
        this.activeModuleId = moduleId;
        const mod = this.modules.find(m => m.id === moduleId);
        if (!mod) return;

        this.drawerTitle.textContent = mod.title;
        this.drawerSubtitle.textContent = `Gathering requirements for: ${mod.title}`;
        this.drawerIcon.innerHTML = mod.icon;

        // Remove existing delete module button if any
        const existingDeleteBtn = this.drawer.querySelector('.btn-delete-module');
        if (existingDeleteBtn) {
            existingDeleteBtn.remove();
        }

        // If it's a custom module, insert a delete button in the header
        if (moduleId.startsWith('module-custom-')) {
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn-delete-module';
            deleteBtn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 14px; height: 14px;">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Module
            `;
            deleteBtn.addEventListener('click', () => this.deleteCustomModule(moduleId));
            
            // Insert it before the close button
            const closeBtn = document.getElementById('btn-close-drawer');
            closeBtn.parentNode.insertBefore(deleteBtn, closeBtn);
        }

        this.renderDrawerFocusItems();
        this.updateDrawerSummaryStats();

        // Get clicked card element
        const cardEl = document.querySelector(`.mrp-card[data-id="${moduleId}"]`);
        if (cardEl) {
            const rect = cardEl.getBoundingClientRect();
            
            // Set initial style matching clicked card (rotated in 3D space)
            this.drawer.style.transition = 'none';
            this.drawer.style.top = rect.top + 'px';
            this.drawer.style.left = rect.left + 'px';
            this.drawer.style.width = rect.width + 'px';
            this.drawer.style.height = rect.height + 'px';
            this.drawer.style.borderRadius = '16px';
            this.drawer.style.transform = 'perspective(1500px) rotateY(-180deg) rotateZ(12deg) scale(0.9)';
            
            // Force reflow
            this.drawer.offsetHeight;
            
            // Set final expanded style with transition (flips and straightens, centered)
            this.drawer.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.1), visibility 0s linear 0s';
            if (window.innerWidth <= 600) {
                this.drawer.style.top = '0';
                this.drawer.style.left = '0';
                this.drawer.style.width = '100vw';
                this.drawer.style.height = '100vh';
                this.drawer.style.borderRadius = '0';
            } else {
                this.drawer.style.top = '5vh';
                this.drawer.style.left = '10vw';
                this.drawer.style.width = '80vw';
                this.drawer.style.height = '90vh';
                this.drawer.style.borderRadius = '24px';
            }
            this.drawer.style.transform = 'perspective(1500px) rotateY(0deg) rotateZ(0deg) scale(1)';
        }

        this.drawer.classList.add('open');
        this.drawerOverlay.classList.add('open');
    }

    closeDrawer() {
        if (!this.activeModuleId) return;

        const cardEl = document.querySelector(`.mrp-card[data-id="${this.activeModuleId}"]`);
        if (cardEl) {
            const rect = cardEl.getBoundingClientRect();
            
            // Transition back to card boundary, twisting in reverse
            this.drawer.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.1), visibility 0s linear 0.8s';
            this.drawer.style.top = rect.top + 'px';
            this.drawer.style.left = rect.left + 'px';
            this.drawer.style.width = rect.width + 'px';
            this.drawer.style.height = rect.height + 'px';
            this.drawer.style.borderRadius = '16px';
            this.drawer.style.transform = 'perspective(1500px) rotateY(180deg) rotateZ(-12deg) scale(0.9)';
        }

        this.drawer.classList.remove('open');
        this.drawerOverlay.classList.remove('open');
        
        this.activeModuleId = null;

        // Clean up inline styles after transition finishes
        setTimeout(() => {
            if (this.activeModuleId === null) {
                this.drawer.style.transition = '';
                this.drawer.style.top = '';
                this.drawer.style.left = '';
                this.drawer.style.width = '';
                this.drawer.style.height = '';
                this.drawer.style.borderRadius = '';
                this.drawer.style.transform = '';
            }
        }, 800);
    }

    updateDrawerSummaryStats() {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const activeItems = mod.items.filter(item => !item.suppressed);
        const inScope = activeItems.filter(i => i.scope === 'in').length;
        const niceHave = activeItems.filter(i => i.scope === 'nice').length;
        const outScope = activeItems.filter(i => i.scope === 'out').length;
        const pending = activeItems.filter(i => i.scope === 'pending').length;

        document.getElementById('mod-in-scope').textContent = inScope;
        document.getElementById('mod-nice-have').textContent = niceHave;
        document.getElementById('mod-out-scope').textContent = outScope;
        document.getElementById('mod-pending').textContent = pending;
    }

    renderDrawerFocusItems() {
        this.focusList.innerHTML = '';
        this.suppressedListEl.innerHTML = '';
        
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const activeItems = mod.items.filter(item => !item.suppressed);
        const suppressedItems = mod.items.filter(item => item.suppressed);

        // Update suppressed section visibility and count
        if (suppressedItems.length > 0) {
            this.suppressedSection.style.display = 'block';
            this.suppressedCountEl.textContent = suppressedItems.length;
        } else {
            this.suppressedSection.style.display = 'none';
        }

        if (activeItems.length === 0) {
            this.focusList.innerHTML = '<p class="text-secondary" style="font-size: 0.9rem; text-align: center; padding: 2rem;">No items yet. Add custom focus items below.</p>';
        } else {
            activeItems.forEach(item => {
                const card = document.createElement('div');
                card.className = 'focus-item-card';
                card.dataset.itemId = item.id;

                const isCustom = item.id.startsWith('custom-');

                card.innerHTML = `
                    <div class="focus-item-top">
                        <div class="focus-item-info">
                            <h4>${item.name}</h4>
                            ${isCustom ? '<p class="sub-detail">Custom Focus Area</p>' : ''}
                        </div>
                        <div class="focus-item-actions">
                            ${isCustom ? `
                                <button class="btn-delete-custom" title="Delete custom focus item" data-item-id="${item.id}">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            ` : ''}
                            <button class="btn-suppress-item" title="Suppress requirement" data-item-id="${item.id}">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="focus-controls">
                        <div class="control-group">
                            <label>Scope Status</label>
                            <div class="scope-selectors" data-item-id="${item.id}">
                                <button class="scope-pill ${item.scope === 'in' ? 'active' : ''}" data-scope="in">In Scope</button>
                                <button class="scope-pill ${item.scope === 'nice' ? 'active' : ''}" data-scope="nice">Nice-to-Have</button>
                                <button class="scope-pill ${item.scope === 'out' ? 'active' : ''}" data-scope="out">Out of Scope</button>
                            </div>
                        </div>
                        <div class="control-group">
                            <label>Priority</label>
                            <select class="priority-select" data-item-id="${item.id}" data-val="${item.priority}">
                                <option value="high" ${item.priority === 'high' ? 'selected' : ''}>High</option>
                                <option value="med" ${item.priority === 'med' ? 'selected' : ''}>Medium</option>
                                <option value="low" ${item.priority === 'low' ? 'selected' : ''}>Low</option>
                            </select>
                        </div>
                        <div class="control-group">
                            <label>Criticality</label>
                            <select class="criticality-select" data-item-id="${item.id}" data-val="${item.criticality || 'normal'}">
                                <option value="super" ${(item.criticality || 'normal') === 'super' ? 'selected' : ''}>Super Critical</option>
                                <option value="critical" ${(item.criticality || 'normal') === 'critical' ? 'selected' : ''}>Critical</option>
                                <option value="normal" ${(item.criticality || 'normal') === 'normal' ? 'selected' : ''}>Normal</option>
                            </select>
                        </div>
                    </div>
                    ${item.guidance ? `
                    <div class="guidance-box">
                        <div class="guidance-title">Guidance Prompt</div>
                        <div class="guidance-text">${item.guidance}</div>
                    </div>` : ''}
                    <div class="notes-wrapper">
                        <label>Specific Requirements & Notes</label>
                        <textarea class="notes-textarea" data-item-id="${item.id}" placeholder="Write notes, volume estimations, existing vendor details or specific requirements here...">${item.notes || ''}</textarea>
                    </div>
                `;

                // Bind selectors events
                const pills = card.querySelectorAll('.scope-pill');
                pills.forEach(pill => {
                    pill.addEventListener('click', (e) => {
                        const scope = e.target.dataset.scope;
                        this.updateItemScope(item.id, scope, pills);
                    });
                });

                // Bind priority change
                const select = card.querySelector('.priority-select');
                select.addEventListener('change', (e) => {
                    const priority = e.target.value;
                    this.updateItemPriority(item.id, priority, select);
                });

                // Bind criticality change
                const critSelect = card.querySelector('.criticality-select');
                critSelect.addEventListener('change', (e) => {
                    const criticality = e.target.value;
                    this.updateItemCriticality(item.id, criticality, critSelect);
                });

                // Bind notes textarea input with simple autosave / blur event
                const textarea = card.querySelector('.notes-textarea');
                textarea.addEventListener('blur', (e) => {
                    this.updateItemNotes(item.id, e.target.value);
                });
                textarea.addEventListener('input', (e) => {
                    // Autosave helper to avoid losing content if closed
                    this.updateItemNotesSilent(item.id, e.target.value);
                });

                // Bind custom delete buttons
                if (isCustom) {
                    const btnDel = card.querySelector('.btn-delete-custom');
                    btnDel.addEventListener('click', () => {
                        this.deleteCustomFocus(item.id);
                    });
                }

                // Bind suppress button
                card.querySelector('.btn-suppress-item').addEventListener('click', () => {
                    this.suppressItem(item.id);
                });

                this.focusList.appendChild(card);
            });
        }

        // Render suppressed items
        suppressedItems.forEach(item => {
            const row = document.createElement('div');
            row.className = 'suppressed-item-row';
            row.dataset.itemId = item.id;

            const isCustom = item.id.startsWith('custom-');

            row.innerHTML = `
                <div class="suppressed-item-info">
                    <h5>${item.name}</h5>
                </div>
                <div class="suppressed-item-actions">
                    <button class="btn-restore-item" data-item-id="${item.id}">Restore</button>
                    ${isCustom ? `
                        <button class="btn-delete-suppressed" title="Delete custom focus item" data-item-id="${item.id}">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    ` : ''}
                </div>
            `;

            // Bind restore
            row.querySelector('.btn-restore-item').addEventListener('click', () => {
                this.restoreItem(item.id);
            });

            // Bind delete if custom
            if (isCustom) {
                row.querySelector('.btn-delete-suppressed').addEventListener('click', () => {
                    this.deleteCustomFocus(item.id);
                });
            }

            this.suppressedListEl.appendChild(row);
        });
    }

    suppressItem(itemId) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        item.suppressed = true;
        this.saveData();
        this.renderDrawerFocusItems();
        this.updateDrawerSummaryStats();
        this.showToast(`Suppressed "${item.name}"`);
    }

    restoreItem(itemId) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        item.suppressed = false;
        this.saveData();
        this.renderDrawerFocusItems();
        this.updateDrawerSummaryStats();
        this.showToast(`Restored "${item.name}"`);
    }

    toggleSuppressedList() {
        this.isSuppressedExpanded = !this.isSuppressedExpanded;
        if (this.isSuppressedExpanded) {
            this.suppressedListEl.style.display = 'flex';
            this.btnToggleSuppressed.classList.add('expanded');
            this.btnToggleSuppressed.querySelector('.toggle-text').textContent = 'Hide';
        } else {
            this.suppressedListEl.style.display = 'none';
            this.btnToggleSuppressed.classList.remove('expanded');
            this.btnToggleSuppressed.querySelector('.toggle-text').textContent = 'Show';
        }
    }

    updateItemScope(itemId, scopeVal, pills) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        // Toggle logic: click active scope pill again resets it to pending
        if (item.scope === scopeVal) {
            item.scope = "pending";
        } else {
            item.scope = scopeVal;
        }

        // Update pills styling
        pills.forEach(p => {
            p.classList.remove('active');
            if (p.dataset.scope === item.scope) {
                p.classList.add('active');
            }
        });

        this.saveData();
        this.updateDrawerSummaryStats();
        this.showToast(`Scope updated for ${item.name}!`);
    }

    updateItemPriority(itemId, priorityVal, selectEl) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        item.priority = priorityVal;
        selectEl.dataset.val = priorityVal;
        this.saveData();
        this.showToast(`Priority updated for ${item.name}!`);
    }

    updateItemCriticality(itemId, criticalityVal, selectEl) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        item.criticality = criticalityVal;
        selectEl.dataset.val = criticalityVal;
        this.saveData();
        this.showToast(`Criticality updated for ${item.name}!`);
    }

    updateItemNotes(itemId, notesText) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        item.notes = notesText;
        this.saveData();
        this.showToast("Notes saved.");
    }

    updateItemNotesSilent(itemId, notesText) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const item = mod.items.find(i => i.id === itemId);
        if (!item) return;

        item.notes = notesText;
        // Save silently without toast
        localStorage.setItem('mrp_requirements_data', JSON.stringify(this.modules));
    }

    addCustomFocus() {
        const nameText = this.inputNewFocusName.value.trim();
        if (!nameText) return;

        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const newItem = {
            id: `custom-${Date.now()}`,
            name: nameText,
            guidance: "Custom focus item added by user.",
            scope: "pending",
            priority: "med",
            criticality: "normal",
            notes: ""
        };

        mod.items.push(newItem);
        this.inputNewFocusName.value = '';
        this.saveData();
        this.renderDrawerFocusItems();
        this.updateDrawerSummaryStats();
        this.showToast(`Custom item "${nameText}" added!`);
    }

    deleteCustomFocus(itemId) {
        const mod = this.modules.find(m => m.id === this.activeModuleId);
        if (!mod) return;

        const itemIndex = mod.items.findIndex(i => i.id === itemId);
        if (itemIndex === -1) return;

        const itemName = mod.items[itemIndex].name;
        if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
            mod.items.splice(itemIndex, 1);
            this.saveData();
            this.renderDrawerFocusItems();
            this.updateDrawerSummaryStats();
            this.showToast(`Deleted "${itemName}"`);
        }
    }

    // Export Markdown Report Generation
    generateMarkdown() {
        let md = `# MRP Requirement Gathering Report\n`;
        md += `Generated on: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}\n\n`;
        
        let overallTotal = 0;
        let overallScoped = 0;
        this.modules.forEach(m => {
            m.items.forEach(i => {
                if (i.suppressed) return; // Skip suppressed items
                overallTotal++;
                if (i.scope !== 'pending') overallScoped++;
            });
        });
        const pct = overallTotal > 0 ? Math.round((overallScoped / overallTotal) * 100) : 0;
        md += `## Progress Summary: **${pct}% Complete** (${overallScoped} of ${overallTotal} items scoped)\n\n`;
        
        md += `| Module | Total Items | Scoped Items | Completion | \n`;
        md += `| :--- | :---: | :---: | :---: | \n`;
        this.modules.forEach(mod => {
            const activeItems = mod.items.filter(item => !item.suppressed);
            const tot = activeItems.length;
            const scp = activeItems.filter(i => i.scope !== 'pending').length;
            const p = tot > 0 ? Math.round((scp / tot) * 100) : 0;
            md += `| ${mod.title} | ${tot} | ${scp} | ${p}% |\n`;
        });
        md += `\n---\n\n`;

        this.modules.forEach(mod => {
            md += `## ${mod.title}\n`;
            md += `*${mod.description}*\n\n`;

            const activeItems = mod.items.filter(item => !item.suppressed);
            const inScopeList = activeItems.filter(i => i.scope === 'in');
            const niceHaveList = activeItems.filter(i => i.scope === 'nice');
            const outScopeList = activeItems.filter(i => i.scope === 'out');
            const pendingList = activeItems.filter(i => i.scope === 'pending');

            if (inScopeList.length > 0) {
                md += `### In Scope\n\n`;
                inScopeList.forEach(item => {
                    md += `#### ${item.name} (Priority: ${item.priority.toUpperCase()}, Criticality: ${(item.criticality || 'normal').toUpperCase()})\n`;
                    if (item.notes.trim()) {
                        md += `**Notes:**\n${item.notes.trim()}\n\n`;
                    } else {
                        md += `*No notes provided.*\n\n`;
                    }
                });
            }

            if (niceHaveList.length > 0) {
                md += `### Nice-to-Have\n\n`;
                niceHaveList.forEach(item => {
                    md += `#### ${item.name} (Priority: ${item.priority.toUpperCase()}, Criticality: ${(item.criticality || 'normal').toUpperCase()})\n`;
                    if (item.notes.trim()) {
                        md += `**Notes:**\n${item.notes.trim()}\n\n`;
                    } else {
                        md += `*No notes provided.*\n\n`;
                    }
                });
            }

            if (outScopeList.length > 0) {
                md += `### Out of Scope\n\n`;
                outScopeList.forEach(item => {
                    md += `#### ${item.name} (Priority: ${item.priority.toUpperCase()}, Criticality: ${(item.criticality || 'normal').toUpperCase()})\n`;
                    if (item.notes.trim()) {
                        md += `**Notes:**\n${item.notes.trim()}\n\n`;
                    } else {
                        md += `*No notes provided.*\n\n`;
                    }
                });
            }

            if (pendingList.length > 0) {
                md += `### Unassigned / Pending Items\n`;
                pendingList.forEach(item => {
                    md += `- **${item.name}**\n`;
                });
                md += `\n`;
            }
            
            md += `\n---\n\n`;
        });

        return md;
    }

    openExportModal() {
        const mdContent = this.generateMarkdown();
        this.exportPreviewContent.value = mdContent;
        this.exportModal.classList.add('open');
    }

    closeExportModal() {
        this.exportModal.classList.remove('open');
    }

    copyExportToClipboard() {
        this.exportPreviewContent.select();
        navigator.clipboard.writeText(this.exportPreviewContent.value)
            .then(() => {
                this.showToast("Copied to clipboard!");
            })
            .catch(err => {
                console.error("Failed to copy", err);
                alert("Failed to copy. Please copy the text manually from the screen.");
            });
    }

    downloadExportMarkdown() {
        const mdText = this.exportPreviewContent.value;
        const blob = new Blob([mdText], { type: 'text/markdown;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "MRP_Requirement_Gathering_Report.md");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        this.showToast("Markdown downloaded!");
    }

    exportCsv() {
        const headers = ["Module", "Item ID", "Item Name", "Scope Status", "Priority", "Criticality", "Notes"];
        const rows = [];
        
        this.modules.forEach(mod => {
            mod.items.forEach(item => {
                if (item.suppressed) return; // Skip suppressed items
                const scopeLabels = { 
                    'in': 'In Scope', 
                    'nice': 'Nice-to-Have', 
                    'out': 'Out of Scope', 
                    'pending': 'Unassigned' 
                };
                const scopeStr = scopeLabels[item.scope] || item.scope;
                
                rows.push([
                    mod.title,
                    item.id,
                    item.name,
                    scopeStr,
                    item.priority.toUpperCase(),
                    (item.criticality || 'normal').toUpperCase(),
                    item.notes || ""
                ]);
            });
        });

        const escapeCsvCell = (cell) => {
            if (cell === null || cell === undefined) return "";
            let str = String(cell);
            str = str.replace(/"/g, '""');
            if (str.includes(",") || str.includes('"') || str.includes("\n") || str.includes("\r")) {
                str = `"${str}"`;
            }
            return str;
        };

        const csvContent = [
            headers.map(escapeCsvCell).join(","),
            ...rows.map(row => row.map(escapeCsvCell).join(","))
        ].join("\r\n");

        const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "MRP_Requirements_Export.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        this.showToast("CSV downloaded (Excel ready)!");
    }

    // JSON export
    exportJsonConfig() {
        const jsonString = JSON.stringify(this.modules, null, 4);
        const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "ReqGather_Backup_Config.json");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        this.showToast("JSON Config downloaded!");
    }

    // JSON Import
    triggerJsonImport() {
        this.importFileInput.click();
    }

    handleJsonImport(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const importedData = JSON.parse(e.target.result);
                // Basic check to see if structure is valid (contains array with id, title, items)
                if (Array.isArray(importedData) && importedData.length > 0 && importedData[0].items) {
                    // Ensure all imported items have criticality & suppressed defined
                    importedData.forEach(mod => {
                        mod.items.forEach(item => {
                            if (!item.criticality) {
                                item.criticality = "normal";
                            }
                            if (item.suppressed === undefined) {
                                item.suppressed = false;
                            }
                        });
                    });
                    this.modules = importedData;
                    this.saveData();
                    this.renderCards();
                    if (this.activeModuleId) {
                        this.openDrawer(this.activeModuleId);
                    }
                    this.showToast("Configuration imported successfully!");
                } else {
                    alert("Invalid JSON format. Please upload a valid ReqGather backup config file.");
                }
            } catch (err) {
                console.error("Error reading JSON file", err);
                alert("Error parsing file. Please check that it is a valid JSON file.");
            }
        };
        reader.readAsText(file);
    }

    // Reset all data
    resetAllData() {
        if (confirm("Are you sure you want to reset ALL data? This will clear all notes, scopes, priorities, and custom items, and restore default templates. This action cannot be undone.")) {
            localStorage.removeItem('mrp_requirements_data');
            this.modules = JSON.parse(JSON.stringify(DEFAULT_MODULES));
            this.saveData();
            this.renderCards();
            if (this.activeModuleId) {
                this.closeDrawer();
            }
            this.showToast("All data has been reset.");
        }
    }

    // Custom Module Modal methods
    openAddModuleModal() {
        this.inputModuleTitle.value = '';
        this.inputModuleDesc.value = '';
        this.addModuleModal.classList.add('open');
        setTimeout(() => this.inputModuleTitle.focus(), 100);
    }

    closeAddModuleModal() {
        this.addModuleModal.classList.remove('open');
    }

    createCustomModule() {
        const titleText = this.inputModuleTitle.value.trim();
        const descText = this.inputModuleDesc.value.trim();
        if (!titleText) {
            alert("Please enter a module title.");
            return;
        }

        const newModule = {
            id: `module-custom-${Date.now()}`,
            title: titleText,
            description: descText || "Custom business module configuration.",
            icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>`,
            items: []
        };

        this.modules.push(newModule);
        this.saveData();
        this.closeAddModuleModal();
        this.showToast(`Module "${titleText}" created successfully!`);
    }

    deleteCustomModule(moduleId) {
        const mod = this.modules.find(m => m.id === moduleId);
        if (!mod) return;

        if (confirm(`Are you sure you want to delete the module "${mod.title}" and all its requirements? This action cannot be undone.`)) {
            const index = this.modules.findIndex(m => m.id === moduleId);
            if (index !== -1) {
                this.modules.splice(index, 1);
                this.saveData();
                this.closeDrawer();
                this.showToast(`Deleted module "${mod.title}"`);
            }
        }
    }

    // Setup Event Listeners
    setupEventListeners() {
        // Close drawer buttons
        this.btnCloseDrawer.addEventListener('click', () => this.closeDrawer());
        this.drawerOverlay.addEventListener('click', () => this.closeDrawer());
        
        // Escape key to close drawer/modals
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDrawer();
                this.closeExportModal();
                this.closeAddModuleModal();
            }
        });

        // Add custom focus area
        this.btnAddCustomFocus.addEventListener('click', () => this.addCustomFocus());
        this.inputNewFocusName.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.addCustomFocus();
            }
        });

        // Export Modal controls
        this.btnExportMd.addEventListener('click', () => this.openExportModal());
        this.btnExportCsv.addEventListener('click', () => this.exportCsv());
        this.btnCloseExportModal.addEventListener('click', () => this.closeExportModal());
        this.btnCopyPreview.addEventListener('click', () => this.copyExportToClipboard());
        this.btnDownloadPreview.addEventListener('click', () => this.downloadExportMarkdown());

        // JSON config controls
        this.btnExportJson.addEventListener('click', () => this.exportJsonConfig());
        this.btnImportJson.addEventListener('click', () => this.triggerJsonImport());
        this.importFileInput.addEventListener('change', (e) => this.handleJsonImport(e));

        // Reset
        this.btnReset.addEventListener('click', () => this.resetAllData());

        // Toggle suppressed items list
        this.suppressedHeader.addEventListener('click', () => this.toggleSuppressedList());

        // Add Custom Module Modal controls
        this.btnCancelAddModule.addEventListener('click', () => this.closeAddModuleModal());
        this.btnCloseAddModuleModal.addEventListener('click', () => this.closeAddModuleModal());
        this.btnConfirmAddModule.addEventListener('click', () => this.createCustomModule());
        this.inputModuleTitle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.createCustomModule();
            }
        });
    }
}

// Initialise App on DOM Content Loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ReqGatherApp();
});
