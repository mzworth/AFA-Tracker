# BUILDPLAN — HRH AFA Billing Tracker

## What This App Does

A **single-file, client-side web app** for Emergency Medicine physicians at HRH (Halton Region Hospital) working under Ontario's Alternative Funding Arrangement (AFA). It tracks shift data, calculates OHIP billings, computes AFA earnings, and exports analytics — all without a backend server.

---

## File Structure

```
AFA Software/
├── HRH_AFA_V1.html    # The entire application — HTML, CSS, JS in one file
├── OHIPMASTER.001     # Official OHIP fee schedule (fixed-width ASCII, ~7,300 lines)
└── BUILDPLAN.md       # This file
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| UI Framework | Tailwind CSS (CDN) |
| JavaScript | Vanilla ES6+ (no frameworks) |
| Storage | IndexedDB (browser-native, persistent) |
| Fonts | Google Fonts — Inter |
| External Dependencies | None (fully offline-capable after initial load) |

---

## Database Schema (IndexedDB)

**Database Name:** `ohipCalculatorDB` (version 2)

### Object Store: `feeScheduleStore`
```json
{
  "id": "ohipSchedule",
  "data": {
    "schedule": {
      "<CODE>": { "description": "", "amount": 0.00, "anaeUnits": 0 }
    },
    "anaeUnitsData": {
      "<CODE>": 0
    }
  }
}
```

### Object Store: `shiftsStore`
```json
{
  "id": "2025-06-15",
  "shiftType": "Shift 1 - Casino - 04:00",
  "isStatHoliday": false,
  "basePay": 1200.00,
  "onCallHours": { "day": 0, "evening": 0, "night": 0, "weekend": 0 },
  "patients": [
    {
      "timePeriod": "day",
      "age80plus": false,
      "isWSIB": false,
      "isSelfPay": false,
      "isIFH": false,
      "isTrauma": false,
      "codes": [
        { "code": "A008", "units": 1, "isReferred": false }
      ]
    }
  ]
}
```

---

## App Architecture

### 8 Tabs (UI Sections)

1. **Shift Data Entry** — Select/create a shift date, enter patient billing codes
2. **Billing Summary** — OHIP billing totals broken down by patient type
3. **Shift AFA Earnings** — Detailed earnings calculation for the selected shift
4. **Analytics** — Monthly/yearly dashboard aggregating all stored shifts
5. **OHIP Schedule** — Searchable table of all 7,000+ OHIP fee codes
6. **AFA Rates** — Reference table for base pay and per-patient stipends
7. **Backup & Restore** — Export/import all data as JSON, CSV
8. **Instructions** — Built-in user guide

---

## Key Business Logic

### Billing Calculation (3-Pass Algorithm)
1. **Pass 1:** Calculate base OHIP value for all non-premium codes using fee schedule
2. **Pass 2:** Calculate positional premiums (E412 = 20%, E413 = 40%) applied to the immediately preceding code's value
3. **Pass 3:** Apply 75% reduction to any referred procedure codes and their attached premiums

After passes: Apply **Trauma multiplier (1.5×)** if flagged, then apply **10% Relativity Increase** globally.

### Shadow Billing (AFA Clawback)
- OHIP patients: 38% of billings returned to AFA pool (regular days), 63% on statutory holidays
- WSIB patients: 100% of billings retained
- IFH patients: 100% of billings retained
- Self-Pay patients: 38% of billings retained

### Per-Patient Stipends
| Time Period | Stipend |
|---|---|
| Day | $32.18 |
| Evening | $38.30 |
| Night | $59.54 |
| Weekend | $51.49 |
| Age 80+ bonus | +$15.00 |
| WSIB bonus | +$85.00 |

### Base Pay Rate Tables (hard-coded)
Two rate tables exist:
- **June 2025 Rates** — 19 shift types (weekday/Friday/weekend variants)
- **Sept 2025 Rates** — 20 shift types, effective **Dec 1, 2025**

### On-Call Hourly Rates
| Period | Rate |
|---|---|
| Day (08:00–17:00) | $60/hr |
| Evening (17:00–00:00) | $72/hr |
| Night (00:00–08:00) | $105/hr |
| Weekend | $90/hr |

### Anaesthesia/Sedation Calculator
- Base units: 6
- Time units: 1 per 15-minute block
- Modifiers: patient age, ASA status, position, BMI >40
- Time premium: Evening/Weekend +50%, Night +75%
- Unit fee: $15.49 × 1.10 (relativity) = $17.04/unit

### Special Billing Code Premiums (hard-coded)
| Code | Type | Value |
|---|---|---|
| E412 / E412A | Positional Premium | 20% of preceding code |
| E413 / E413A | Positional Premium | 40% of preceding code |
| E409C | OT Evening | $15.80 flat |
| E410C | OT Night | $21.05 flat |
| E411C | OT Sat/Sun/Holiday | $31.55 flat |
| E420 | Trauma Premium | included in 1.5× multiplier |
| J149 | Ultrasound Guidance | $36.85 flat |

---

## OHIPMASTER.001 File Format (Fixed-Width ASCII)

Lines are CRLF-terminated. Key field positions:
- **0–4:** Billing code + suffix character
- **12–19:** Termination date (YYYYMMDD); active codes have `99991231`
- **20–30:** Provider fee (in 10,000ths of a dollar, i.e., divide by 10,000)
- **31–33:** Anaesthesia base units
- **42–52:** Specialist fee (in 10,000ths of a dollar)

Only codes where termination date = `99991231` are loaded as active.

---

## Data Flow

```
User selects shift date
    → Load from IndexedDB (or create new)
    → User enters patient billing codes (autocomplete from fee schedule)
    → On save: Run 3-pass billing calculation
    → Store shift object in IndexedDB

Analytics tab
    → Load all shifts from IndexedDB
    → Aggregate by month/year
    → Render summary cards and tables
```

---

## Key Constants (as of last update)

```javascript
ANAESTHESIA_UNIT_FEE = 15.49
RELATIVITY_PREMIUM = 1.10       // 10% increase applied globally
OHIP_SHADOW_PCT = 0.38          // Regular days
OHIP_STAT_SHADOW_PCT = 0.63     // Statutory holidays
AGE_80_BONUS = 15.00
WSIB_FORM_FEE = 85.00
```

---

## Export Formats

| Format | Contents |
|---|---|
| JSON (full backup) | All shifts, all patient data |
| JSON (single shift) | One shift's complete data |
| CSV (shift earnings) | Earnings summary for one shift |
| CSV (analytics) | Monthly or yearly aggregate report |

---

## Known Architecture Decisions

- **Single HTML file** — intentional for portability (easy to share, no install required)
- **No backend** — all data lives in browser IndexedDB; no network requests after initial CDN load
- **No build step** — edit the HTML directly; no webpack/npm/node required
- **Hard-coded rates** — AFA rate tables are embedded in JS; must be manually updated when rates change
- **OHIPMASTER.001 loaded once** — fee schedule is parsed and stored in IndexedDB on first use; can be refreshed via Settings

---

## Future Development Notes

- Rate tables should be externalized to a config JSON when rates change frequently
- Consider a simple Node/Express backend + SQLite if multi-user or multi-device sync is needed
- The 3-pass billing algorithm is in the `calculatePatientBilling()` function
- Shift rate lookup is in `getShiftBasePay()` / the rate tables near the top of the JS section
- All IndexedDB operations are wrapped in promise-based helpers (`getShift`, `saveShift`, `getAllShifts`, etc.)
