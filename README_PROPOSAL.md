# 🏭 Kotyol — Manufacturing ERP & Direct POS Printing Engine

> **Industrial-grade Manufacturing Enterprise Resource Planning (ERP), Bill of Materials (BOM) calculation engine, dual-currency ledger, and direct thermal POS receipt printing platform designed for heating boiler factories and assembly plants.**

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15%2B-red.svg)](https://www.django-rest-framework.org/)
[![POS](https://img.shields.io/badge/POS-Thermal%20Receipt%20Engine-orange.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Service--Layer%20DDD-purple.svg)]()

---

## 📋 Overview

**Kotyol ERP** is a full-featured industrial operations platform architected for boiler manufacturing, assembly lines, and heavy equipment producers. It bridges the critical divide between factory floor production, warehouse raw material consumption, distributor sales pipelines, and direct point-of-sale thermal receipt generation.

Comprising **148+ Python modules** and over **8,600 lines of clean, decoupled code**, the system enforces strict traceability from raw metal intake to finished product warranty and post-sale service tickets.

---

## 🛑 Business Problem

Manufacturing factories often struggle with:
1. **Material Leakage**: Discrepancies between theoretical recipe consumption and actual warehouse inventory.
2. **Delivery Penalties**: Lack of automated discounts and contract guarantees for delayed custom boiler builds.
3. **Fragmented Hardware**: Disconnected accounting software unable to trigger physical thermal receipt printers at point-of-sale desks.
4. **Post-Sale Blindspots**: Missing audit trails linking customer warranty claims back to specific production batches and assigned factory technicians.

Kotyol solves all four challenges through an integrated, service-oriented architecture.

---

## 🌟 Key Modules & Features

### 1. ⚙️ Manufacturing & Assembly Tracking
- **Production Batches**: Track batch lifecycles (`PLANNED` -> `IN_PROGRESS` -> `QUALITY_CHECK` -> `COMPLETED`).
- **Operation Stages**: Modular assembly steps (Cutting, Welding, Pressure Testing, Insulation, Painting, Packaging).
- **Assigned Technicians**: Log employee labor hours and piece-rate wage calculations per production stage.

### 2. 📑 Bill of Materials (BOM) & Recipe Engine
- **Hierarchical Recipes**: Link finished boilers to raw materials (sheet steel, burner valves, heat exchangers, fasteners).
- **Auto-Deduction**: Automatically deducts exact bill-of-materials raw components from warehouse stock upon batch completion.
- **Defect Recording**: Track scrap rates, rejected parts, and defect reasons during quality inspection.

### 3. 📦 Warehouse & Inventory Ledger
- **Multi-Location Inventory**: Separate tracking for Raw Materials, Semi-Finished Components, and Ready Products.
- **Purchasing & Supplier POs**: Purchase orders, supplier category categorization, unit costs, and receiving docks.
- **Stock Movement Log**: Immutable audit ledger recording every receipt, write-off, transfer, and sales deduction.

### 4. 💼 Sales, Orders & Automated Late Discounts
- **Lead & Deal Tracking**: Commercial inquiries, quotations, contractor agreements, and deposit records.
- **SLA & Auto-Discount Engine**: Automatically applies contractually mandated penalty discounts if custom manufacturing deadlines exceed the promised delivery date.
- **Dual-Currency Support**: Handles foreign currency raw material costs and local currency retail sales.

### 5. 🧾 Direct POS & Thermal Receipt Printing
- **Hardware Integration**: Built-in Direct Thermal Print engine generating ESC/POS-compatible receipt structures and official invoice summaries.
- **Zero-Setup Receipt API**: Provides normalized JSON receipt schemas (`/api/sales/<id>/receipt/`) ready for ESC/POS network, USB, or Bluetooth printers.
- **Invoice Formatting**: Clean, printable trade bills with QR-code ready payloads, VAT breakdowns, itemized specs, and warranty disclaimers.

### 6. 🛠️ Service Tickets & Warranty Management
- **After-Sales Support**: Log boiler maintenance requests, field technician visits, and replacement part costs.
- **Quality Feedback Loop**: Correlates service tickets back to original assembly batches to identify recurring component failures.

---

## 🏛️ Architecture & Clean Design

The project employs a robust **Service Layer Pattern**, separating HTTP serialization, business logic, and database persistence:

```
kotyol/
├── apps/
│   ├── products/       # Boilers, Technical specifications, Recipes (BOM)
│   ├── production/     # Production batches, Operations, Stage assignments, Quality inspection
│   ├── warehouse/      # Inventory ledger, Stock movements, Reorder limits (WarehouseService)
│   ├── purchasing/     # Suppliers, Purchase orders, Inbound shipments (PurchasingService)
│   ├── sales/          # Orders, Leads, Receipt generator, SLA discounts (SalesService)
│   ├── master_data/    # Defect reasons, Production stages, Service tickets, Currency
│   ├── finance/        # Cash transactions, Invoices, Dual-currency conversions
│   ├── dashboard/      # Executive KPIs, Production bottleneck reports, Sales analytics
│   └── audit/          # Immutable system activity log & user actions
├── core/               # Safe-delete models, Custom JWT authentication, RBAC permissions
└── config/             # Django settings, WSGI, URLs
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, Django 5.x, Django REST Framework
- **Architecture**: Service Layer, Separation of Concerns, Domain-Driven Design
- **Database**: PostgreSQL (Production) / SQLite (Development) with Alembic migration compatibility
- **Hardware Interop**: ESC/POS thermal receipt formatting, raw print stream generation
- **Security**: Granular RBAC Permissions Matrix, JWT Authentication, Custom Exception Handler

---

## 🚀 Installation & Local Development

### 1. Clone and Setup
```bash
git clone https://github.com/umidjonminecrafter-spec/kotyol.git
cd kotyol

# Virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Initialize Database
```bash
python manage.py migrate
python manage.py runserver
```

---

## ⚙️ Environment Variables (`.env.example`)

```ini
SECRET_KEY=your-secure-random-key-here
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 💼 Real-World Commercial Use Cases

1. **Heating Boiler & Radiator Manufacturers**: Complete production-to-retail lifecycle tracking.
2. **Metal Fabrication & Assembly Workshops**: BOM recipes, technician piece-rates, and inventory write-offs.
3. **Equipment Wholesalers with Retail Showrooms**: Warehouse supply chain combined with desk thermal receipt printing.
