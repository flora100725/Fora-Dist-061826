M-ARCH-0616 TFDA Compliance Hub (v2.5.0) — Technical Specification Addendum
Title: “WOW AI Expansion Pack” (3 Additional Advanced AI Modules)
Baseline: v2.4.0-Agentic-Harmonics (all existing modules and behaviors preserved)
Target Platform: Full-Stack Node.js (Express v4 + Vite v6 + React 19)
Security Standard: TUDID / TFDA Medical Device Logistics Compliance Shield
Scope of this Addendum: Add three new “wow” AI features while keeping every original feature (GIS, ledgers, anomalies, War Room, Neural Chat, rules fallback, Gemini integration patterns, etc.).
Non-goal: Provide implementation code. This document specifies architecture, UX, data contracts, safeguards, and operational requirements.

1. Design Intent & “WOW” Principle
The platform already excels at identifying anomalies (duplicate serials, timeline inversions, expired permits), simulating multi-agent debate (War Room), and providing a grounded regulatory chat assistant. The next leap is to deliver regulator-grade evidentiary strength and field-operational readiness—meaning:

Evidence is provable and replayable (audit-grade traceability, reproducible AI outcomes, chain-of-custody).
Counterfeit/grey-market signals are detectable beyond structured tables (documents, labels, packaging, scanned PDFs, shipment photos).
Recall actions become executable playbooks (not just analysis—task lists, stakeholder communications, scenario simulation, and measurable closure).
This addendum introduces three new advanced AI modules:

6.4 Evidence Graph & Explainability Ledger (EGEL)
6.5 Counterfeit & Grey-Market Forensics Studio (CGFS)
6.6 Recall Orchestrator & Playbook Generator (ROPG)
Each module is designed to integrate with the existing data models and anomaly system, and to operate under the same “API key optional + fallback rules engine” philosophy.

2. Compatibility Requirements (Hard Constraints)
2.1 Preserve All Existing Features
The following must remain unchanged in capability (UI refinements allowed, but no regressions):

Leaflet GIS with hub markers, status pulse animations, and facility overlays
Distribution & Purchase ledgers, serial normalization, anomaly highlighting, and resolve workflow
Compliance score degradation and recovery logic
War Room multi-agent debate mode and JSON schema output behavior
Neural Chat grounded context injection from current dataset slices
Server lazy initialization and rules-engine fallback if no AI key
Single-port server runtime and SPA routing behavior
2.2 Data & Audit Integrity
New features must not modify original records silently. Any transformation must be:

Versioned
Attributed (actor: user vs system vs AI)
Reversible (restore prior version)
Exportable for inspection (regulatory audit readiness)
3. New Shared Foundations (Cross-Cutting Enhancements)
The three new AI modules require shared platform-level capabilities. These are not “separate features”; they are enabling infrastructure.

3.1 Unified Artifact Repository (UAR)
A logical repository for non-tabular evidence and generated outputs:

Ingested artifacts: PDFs, scanned invoices, shipping labels, photos of packaging, email text, regulatory documents
Derived artifacts: OCR output, extracted tables, normalized UDI/serial fields, AI summaries, risk memos, recall playbooks
Storage model:

In container-only deployments, artifacts are ephemeral and must be explicitly exported by the user.
In production deployments, artifacts should be stored in a persistent object store (vendor-neutral in spec; implementation may use a managed blob storage).
Artifact metadata (minimum fields):

Artifact ID, original filename, MIME type, file size, checksum (SHA-256), upload actor, upload timestamp
Linkage pointers: related DistributionItem IDs, PurchaseItem IDs, Anomaly IDs, Station IDs
Processing status: pending OCR, OCR completed, extraction completed, AI-reviewed, human-approved
Access classification: internal, restricted, confidential-medical
3.2 AI Event Trace (AIET)
A standardized trace log for any AI-assisted operation, to support reproducibility and investigations:

Model name, provider, request timestamp, response timestamp, latency
Prompt template ID + prompt variables hash (not raw sensitive content by default)
Input artifact checksums referenced
Output checksum and structured summary of outputs (e.g., “found 2 UDI mismatches”)
Safety flags and policy gating decisions (e.g., “PHI detected → redaction applied”)
Human actions taken after AI output (accept/edit/reject)
This trace is displayed in a dedicated “AI Trace” panel and exportable as an audit package.

3.3 Redaction & Sensitive Data Policy Layer
Because evidence documents may contain personal data or sensitive facility references:

Detect and optionally redact: patient identifiers, physician names, contact phone numbers, email addresses
Provide “Regulatory Mode” toggles:
“Strict redaction” (default for external sharing)
“Internal review” (more permissive, still logged)
Redaction actions must themselves be logged in AIET as a transformation event.

4. Feature 6.4 — Evidence Graph & Explainability Ledger (EGEL)
4.1 Overview
EGEL transforms scattered anomalies, shipments, receipts, stations, permits, and evidence files into a navigable evidence graph. It answers:

“Why is this flagged?”
“What evidence supports this?”
“What changed, when, and who approved it?”
This module upgrades the platform from analytics to audit-proof compliance reasoning.

4.2 User Experience (UX)
A new workspace tab: Evidence Graph with three synchronized panes:

Graph Canvas (center): Nodes and edges representing entities and relationships
Evidence Timeline (right): Chronological event ledger including uploads, OCR events, AI analyses, human approvals, anomaly resolution
Inspector (left): Selected node details, linked artifacts, derived fields, and “generate memo” actions
Key interactions:

Click an anomaly → highlight all contributing records (distribution row, purchase row, permit record, station) and attached artifacts
“Explain this anomaly” button → generates a structured, citation-style explanation referencing node IDs and artifact excerpts
“Compare two nodes” → e.g., compare the same serial number across two hospitals, showing normalized vs raw serial, date stamps, and evidence sources
4.3 Graph Data Model (Conceptual)
Node types (minimum):

Device instance node (serial-centered)
Transaction nodes (shipment, receipt)
Organization nodes (reporter, supplier, hospital)
Permit/license nodes
Station/location nodes (GIS hubs)
Artifact nodes (PDF/photo/email)
AI output nodes (OCR result, extraction table, risk memo)
Human action nodes (approval, override, resolution)
Edge types (minimum):

“mentions serial”, “references permit”, “uploaded as evidence for”, “derived from”, “supplied by”, “received by”, “conflicts with”
“supports anomaly” vs “disputes anomaly” (critical for human-in-loop appeals)
4.4 AI Capabilities
EGEL uses LLM assistance to:

Auto-link evidence excerpts to graph nodes (“this invoice line refers to serial RNJ146480G”)
Generate “explainability memos” in structured Markdown:
Summary
Observations
Evidence list (artifact ID, excerpt hash, timestamp)
Risk rating rationale
Recommended regulator actions
Detect contradictory evidence (e.g., two documents claiming mutually exclusive delivery dates)
4.5 Controls, Safeguards, and Quality
Every auto-link is created with a confidence score and defaults to “unverified” until a reviewer confirms.
Confidence thresholds are configurable per organization role:
Auditor role can lower threshold for investigation
Public export role requires high confidence or explicit human confirmation
Explanations must include citations to internal IDs; avoid “because the AI says so.”
4.6 Outputs
Exportable “Evidence Pack” bundle:
Graph snapshot (JSON)
Timeline log (CSV/JSON)
Selected artifacts (optional)
AIET trace excerpt
Generated memos (Markdown/PDF-ready)
5. Feature 6.5 — Counterfeit & Grey-Market Forensics Studio (CGFS)
5.1 Overview
CGFS extends anomaly detection beyond structured ledgers into real-world evidence such as scanned invoices, shipping labels, packaging photos, and certificates. Its goal is to expose grey-market patterns like:

Repackaging / label tampering
UDI/serial mismatches between label and paperwork
Duplicate serial reuse with altered suffixes
Suspicious distributor identity patterns and document template reuse
5.2 UX: The Forensics Studio
A new tab: Forensics Studio with a guided workflow:

Ingest evidence
Upload: PDF, image (JPG/PNG), text files
Optional: drag-and-drop batch upload with auto-tagging
Extract
OCR (for scans)
Table extraction (invoice line items)
Barcode/UDI string detection (from photos or embedded PDF text)
Validate
Compare extracted serial/UDI/permit fields to ledger entries
Detect formatting tricks (hidden characters, homoglyphs, inserted slashes)
Investigate
“Suspicion signals” dashboard
Visual diff on label text (what differs from known-good templates)
Attach results
Link findings to anomalies and graph nodes (integrates with EGEL)
5.3 Detection Signals (No single-point AI verdict)
CGFS produces an interpretable “Forensics Signal Panel” with independent signals, each with confidence and supporting excerpt:

UDI structure plausibility: check digit rules or known formatting expectations (spec-defined rules; vendor-specific rules can be configured)
Serial normalization collision: extracted serials normalize into an already-known serial
Permit mismatch: permit on invoice differs from permit in shipment declaration for same serial
Document template reuse fingerprint: detect repeated layout/text patterns across “different” suppliers (grey-market clue)
Label tamper heuristics: inconsistent font spacing, misaligned baselines, suspicious edge halos (image-based heuristic scoring; always advisory)
Timeline corroboration failure: document date conflicts with declared shipment/receipt windows
5.4 Data Products
CGFS yields standardized outputs:

Extracted fields table (serial, UDI, permit, dates, org names, line-item quantities)
Evidence excerpts: coordinate-based (page, bounding box) for PDFs/images
Suspicion scorecard:
Overall risk band: Low / Medium / High / Critical
Signal-level breakdown and citations
5.5 Human-in-the-Loop Requirements
The studio must support reviewer actions:
Confirm extracted field
Correct extracted field
Mark as “unreliable scan”
Escalate to “Enforcement Review” queue
Any escalation generates an EGEL node and an AIET trace entry.
5.6 Safety & Compliance Boundaries
The module must avoid making definitive medical safety claims (e.g., “device is unsafe”) solely from packaging. It may recommend “quarantine and physical inspection” with documented reasons.
If patient/clinical data appears in uploaded artifacts, redaction policy triggers before any AI summarization.
6. Feature 6.6 — Recall Orchestrator & Playbook Generator (ROPG)
6.1 Overview
ROPG turns detection into action. It creates scenario-based recall simulations and produces a regulator-ready playbook: tasks, communications, timelines, accountability, and measurable closure criteria.

This feature is designed for rapid response when anomalies indicate possible counterfeit injection, expired permits, or serial multiplexing across hospitals.

6.2 UX: Recall Console
A new tab: Recall Console with four stages:

Define scope
Select triggering anomalies (e.g., duplicate serial + expired permit cluster)
Choose scope rules:
Serial-only
Permit-based expansion (all devices under permit X within date window)
Batch/lot expansion (if batch numbers exist)
Station radius expansion (GIS-based proximity)
Simulate impact
Affected institutions list
Estimated devices impacted (with uncertainty intervals if data incomplete)
Logistics impact (stock rebalancing needs)
Generate playbook
Action plan phases:
Containment (freeze shipments, quarantine stock)
Verification (inventory checks, physical inspections)
Communication (notices to suppliers/hospitals)
Remediation (replacement allocation plans)
Closure (evidence pack + compliance scoring restoration criteria)
Execute & track
Checklist tasks with owners and deadlines
Status updates and audit log entries
Exportable regulator package
6.3 AI Responsibilities (Structured, Not Freeform)
ROPG uses AI to propose:

Scope recommendations with rationale and explicit assumptions
Draft communications in Traditional Chinese suitable for:
Hospitals (inventory quarantine instructions)
Distributors (document request and legal basis)
Internal TFDA/regulatory coordination memos
Risk prioritization:
Criticality scoring combining anomaly severity, evidence strength, and distribution breadth
“What to request next” evidence checklist:
Certificates, shipment manifests, cold-chain logs, warehouse release logs
6.4 Simulation Model (Deterministic + AI Advisory)
To ensure reproducibility:

The impact calculation (counts, lists, date windows) must be deterministic and based on explicit rule sets.
AI provides advisory narrative and optional alternative scenarios, but cannot silently change scope logic.
Simulations must support:

Baseline scenario (strictly confirmed data)
Expanded scenario (includes high-confidence inferred links from EGEL/CGFS)
Worst-case scenario (assumes maximum plausible spread within configured bounds)
6.5 Outputs
Recall Playbook (Markdown) with:
Executive summary
Triggering events and evidence citations
Scope definition rules
Affected entity table
Action timeline and owners
Communications appendix
Closure criteria and post-mortem template
GIS overlay export: impacted stations/hospitals with severity coloring
Evidence Pack integration: links to EGEL exports and CGFS scorecards
7. Integration With Existing Modules
7.1 With GIS View
New overlays:
“Evidence density” heat layer (count of linked artifacts/anomalies per station)
“Recall scope” polygon/radius overlay from ROPG scenarios
Clicking a station now includes:
Top linked anomalies
Evidence pack shortcuts
Recall participation status
7.2 With Reports View (Ledger)
New per-row affordances:
“Attach evidence” (links to CGFS artifact ingestion)
“View evidence graph” deep-link
“Add to recall scope” (ROPG)
New computed columns (optional toggles):
Evidence strength (none / weak / moderate / strong)
Forensics suspicion band (from CGFS)
7.3 With War Room Simulation
War Room gains optional “Evidence-aware debate mode”:

Agents can reference evidence IDs and confidence scores
Consensus output includes a “next evidence request” list if uncertainty remains
7.4 With Neural Chat
Chat can answer:

“Show me all evidence supporting anomaly X”
“Draft a notice letter using these attached documents”
“Summarize recall playbook for Hospital C00306”
Chat must not reveal sensitive artifact contents unless user has access and redaction policy permits.

8. Backend & API Requirements (No Code, Behavior Only)
8.1 New API Capability Categories
Artifact ingestion and retrieval (upload, list, metadata, checksum validation)
OCR/extraction job orchestration (async job states)
Evidence graph operations (build, link suggestions, export)
Recall simulation and playbook generation (deterministic simulation + AI narrative)
AI trace logging endpoints (append-only semantics)
8.2 Job Model (Asynchronous Processing)
OCR and extraction should run as background jobs with:

Job ID, status (queued/running/succeeded/failed), progress percent, timestamps
Partial results streaming to UI is optional but recommended for “wow” responsiveness
If the deployment environment cannot support background workers, the system must still function via:

Foreground processing with clear UI progress indicators
Timeouts and chunked processing constraints
8.3 Model Provider Policy
The platform already uses Gemini; this addendum remains provider-neutral but requires:

A provider abstraction to call available models for:
OCR post-processing summarization
Evidence linking suggestions
Playbook drafting
Fallback mode:
If AI unavailable, allow manual evidence linking, manual playbook templates, and deterministic recall impact calculation.
9. Security, Governance, and Auditability
9.1 Role-Based Access (Recommended)
Introduce roles (even if initially local-only):

Viewer: read-only
Auditor: resolve anomalies, link evidence, export packs
Enforcement: create recall playbooks, generate notices, mark escalations
Admin: configure policies, thresholds, retention rules
9.2 Chain-of-Custody Guarantees
Every artifact must have a checksum; any modification creates a new artifact version.
Evidence exports include checksums and timestamps.
9.3 Prompt & Output Retention
Because regulatory audits may require reproducibility:

Store prompt template IDs and variable hashes by default
Store full prompts only under explicit “retain full prompts” policy (sensitive)
Store AI outputs with checksums and version tags
10. Performance & Scalability Targets
Evidence graph should handle:
Thousands of nodes and edges without freezing the UI (use incremental rendering and clustering)
OCR/extraction:
Must provide progress and not block critical UI usage
Recall simulation:
Deterministic calculations must complete within interactive tolerances for typical dataset sizes; AI drafting runs asynchronously with clear status
11. Acceptance Criteria (Definition of Done)
EGEL: User can select an anomaly and see a graph of linked shipments/receipts/permits/artifacts, generate an explanation memo with citations, and export an evidence pack.
CGFS: User can upload a PDF/image, extract serial/UDI/permit/date fields, see suspicion signals, correct extraction results, and attach outputs to an anomaly.
ROPG: User can select anomalies, define scope rules, run a deterministic impact simulation, generate a playbook, and track execution tasks with audit logs.
No regressions: All v2.4.0 features remain functional with identical outputs under the same inputs (except UI additions).
Fallback: Without any AI key, the system still supports manual workflows and deterministic calculations, and clearly indicates “AI unavailable” states.
12. 20 Comprehensive Follow-up Questions (Engineering & Regulatory Review)
Evidence retention policy: What is the mandatory retention period for artifacts, AI traces, and exports under TFDA-related audit practices, and how should retention differ between “investigation” vs “closed” cases?
Chain-of-custody enforcement: Do we require digital signatures (in addition to checksums) for evidence packs to be admissible in administrative or legal proceedings?
Graph scale strategy: What maximum graph size (nodes/edges) should EGEL support before switching to clustering, pagination, or server-side graph queries?
Confidence governance: What confidence thresholds and reviewer rules should govern auto-link suggestions from OCR/LLM, and do thresholds vary by anomaly severity?
Redaction policy: Which specific fields must be redacted by default (names, phone numbers, addresses, patient IDs), and what is the approval workflow to view unredacted content?
PHI/PII detection quality: Should the system use deterministic regex rules, ML-based detectors, or hybrid approaches for PII/PHI detection in Chinese/English documents?
OCR vendor choice: Will OCR be handled via an external API, an on-prem/local library, or a hybrid—given deployment constraints and confidentiality requirements?
Image forensics limits: What level of “tamper detection” is acceptable as an advisory heuristic without over-claiming, and how should uncertainty be presented to auditors?
UDI validation rules: Do we have authoritative UDI/DI formatting rules per manufacturer/model, and how will these rule sets be updated and versioned?
Document template fingerprinting: What are acceptable methods to detect template reuse (layout hashing, text similarity, visual embeddings), and what false-positive rate is tolerable?
Recall scope rules: Which recall expansion rules are permitted operationally (serial-only vs permit-based vs batch-based vs geofence-based), and who is authorized to apply each?
Deterministic simulation spec: What exact deterministic algorithms should compute “affected devices,” especially when batch numbers are missing or serials appear with suffix noise?
Task accountability: Should Recall Console tasks integrate with external ticketing (e.g., Jira/ServiceNow) or remain internal-only, and how do we sync status bidirectionally?
Notice letter compliance: What official templates, legal citations, and required fields must appear in generated TFDA notices, and who must approve before sending?
Export format standards: Should evidence packs be exportable as a single archive, a PDF dossier, or both—and what metadata must be embedded for audit acceptance?
Access control architecture: Will role-based access be enforced purely in-app, via an identity provider (SSO), or via a regulator-managed account system, and what is the minimum viable secure setup?
Audit log immutability: Do we need append-only, tamper-evident logs (e.g., hash-chained entries) for human actions and AI events, and what are the performance costs?
Provider abstraction: Which model providers are approved for regulatory workloads, and how do we validate output consistency across providers for the same prompt templates?
Fallback correctness: What is the required behavioral equivalence between AI-enabled and AI-disabled modes for core compliance outcomes, and how will we test it?
Validation & testing plan: What is the target test matrix (unit/integration/e2e) for EGEL/CGFS/ROPG, including golden datasets for known anomalies, counterfeit scenarios, and recall drills?
