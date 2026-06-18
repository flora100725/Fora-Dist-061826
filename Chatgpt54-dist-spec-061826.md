WOW Agentic Workspace & AI Note Keeper
Comprehensive Technical Specification
Version: v3.0.0-WOW-Orchestrator
Target Platform: Hugging Face Spaces with Streamlit
Core Assets: agents.yaml, SKILL.md, Gemini API, OpenAI API, Anthropic API, xAI API
Primary Languages: Traditional Chinese (default), English
Document Type: Product and Technical Specification
Implementation Constraint: No code in this document

1. Executive Summary
This specification defines an upgraded design for a Streamlit-based agentic AI application deployed on Hugging Face Spaces. The upgraded product must preserve all existing capabilities while introducing a more polished, highly interactive, and visually impressive “WOW” experience. The system combines three major functional pillars:

Agentic Workspace for multi-agent execution, prompt control, model selection, YAML/skill editing, and step-by-step human-in-the-loop orchestration.
WOW Visualization Layer for live execution status, interactive indicators, live logs, progress telemetry, and a real-time dashboard that makes model behavior understandable and editable.
AI Note Keeper for transforming pasted or uploaded notes into organized markdown, applying coral-colored keywords, enabling note refinement, and offering a suite of AI “Magics” including three newly added advanced features.
The application must run effectively within Hugging Face Spaces constraints, support multiple AI providers, and allow secure API key handling from either environment variables or session-based web inputs. The user experience must feel premium, modern, and flexible without sacrificing transparency, safety, editability, or interoperability with configuration files such as agents.yaml and SKILL.md.

2. Product Goals
2.1 Primary Goals
Preserve all original features.
Add a new WOW UI with light/dark modes, bilingual interface, and 10 Pantone-inspired visual styles.
Allow Jackpot style selection, where the system randomly selects one of the 10 design styles.
Make LLM execution visually impressive and operationally transparent.
Let users configure prompts, token limits, and model choices before each agent runs.
Let users manually edit agent output before handing it to the next agent.
Add a robust AI Note Keeper that supports paste, upload, edit, transform, and export workflows.
Add 3 additional WOW AI features, bringing the AI Magic suite to 9 features total.
Add an in-app Agent Configuration Studio for agents.yaml and SKILL.md.
2.2 Success Definition
A successful release is one where a user can:

Launch the app in a Hugging Face Space.
Choose theme, language, and style instantly.
Input an API key only when environment variables are absent.
Configure and run agents one by one with visible logs and editable handoffs.
Import or paste note content, convert it into structured markdown, apply keyword coloring, and use AI Magics.
Edit, standardize, validate, and download agents.yaml and SKILL.md.
Understand what happened during every LLM execution without needing developer tools.
3. Scope and Feature Preservation
The upgraded system must retain all original capabilities and add new layers rather than replacing previous flows. Existing features to preserve include:

Multi-provider AI access.
Agent execution pipeline.
Streamlit deployment compatibility.
Prompt-driven workflows.
File upload and text editing.
Export and download functions.
Agent configuration using agents.yaml.
Skill definition using SKILL.md.
New capabilities must integrate with existing workflows, not fork them into disconnected sub-apps.

4. System Architecture Overview
4.1 Platform Model
The application is a single Streamlit app operating as an orchestration shell over:

UI state and interaction logic
session-level secure settings
AI provider abstraction
file ingestion and transformation
multi-agent execution
note processing
visualization and live telemetry
4.2 Logical Architecture
The system should be organized into the following layers:

Layer	Purpose
Presentation Layer	Streamlit pages, tabs, sidebars, theme engine, bilingual text
Interaction Layer	Forms, editors, uploaders, toggles, action panels, dashboards
Orchestration Layer	Agent execution manager, prompt manager, handoff pipeline
Provider Layer	OpenAI, Gemini, Anthropic, xAI adapters with unified request/response model
Content Layer	Note parser, markdown transformer, keyword highlighter, YAML normalizer
State Layer	Session state, execution history, model settings, edit buffers
Persistence Layer	Temporary HF Space storage, downloadable exports, optional remote persistence
4.3 Runtime Constraints
Hugging Face Spaces imposes practical constraints:

Filesystem persistence may be limited or ephemeral.
Long-running tasks should provide progress and cancel affordances.
API keys should default to in-memory session handling.
Heavy operations such as large PDF parsing should degrade gracefully.
5. WOW UI and Visual Design System
5.1 Theme Modes
The UI must support:

Light mode
Dark mode
Theme switching should be global and immediate.

5.2 Language Modes
The UI must support:

Traditional Chinese as default
English
All core labels, status indicators, navigation items, system notices, and tool descriptions must be localized. User content itself should remain unmodified unless processed by AI.

5.3 Pantone-Inspired Style System
The application must include 10 named style presets, each with coordinated colors for:

primary accent
secondary accent
background
surface cards
success
warning
error
keyword highlight
chart palette
live execution glow
One accent family should reserve coral for keyword emphasis. Suggested style naming can be conceptual rather than trademark-specific, such as Coral Pulse, Ocean Slate, Moss Signal, Orchid Glass, Midnight Ember, Arctic Mint, Sandstone, Electric Plum, Solar Bloom, and Graphite Aqua.

5.4 Jackpot Style
A prominent “Jackpot” button should randomly apply one of the 10 styles. The selection should animate briefly and update the dashboard, note editor, and execution panels together, reinforcing delight without harming usability.

5.5 UX Tone
The design language should feel:

sleek
premium
responsive
slightly cinematic
information-dense but not noisy
Recommended visual motifs:

glassmorphism cards
soft neon edge glows
animated status pulses
compact metric chips
collapsible advanced controls
6. Information Architecture
The app should be organized into six main workspaces:

Home / Command Center
Agent Runner
WOW Dashboard
AI Note Keeper
Agent Config Studio
Settings & Keys
6.1 Home / Command Center
This landing area summarizes:

provider readiness
active theme/style/language
current agent sequence
latest notes
recent runs
system alerts
quick actions
6.2 Agent Runner
This is the core orchestration workspace for:

loading agent sequence
editing prompt per agent
selecting model per agent
setting max tokens per agent
executing one agent at a time
reviewing/editing output
forwarding edited output to next agent
6.3 WOW Dashboard
This area provides visual telemetry:

execution timeline
live logs
provider latency
token consumption estimate
success/failure state
agent agreement or divergence summaries
run history comparison
6.4 AI Note Keeper
This workspace handles:

paste text or markdown
upload PDF/text/markdown
transform into organized markdown
coral keyword highlighting
edit in markdown or plain text view
run AI Magics
export refined notes
6.5 Agent Config Studio
This module lets the user:

paste agents.yaml
upload agents.yaml
standardize it before import
edit and validate it
paste/upload/edit/download SKILL.md
preview markdown
compare versions
6.6 Settings & Keys
This area manages:

provider status
secure key entry if env keys are missing
model defaults
token defaults
interface preferences
language and style
optional safety toggles
7. Provider and API Key Management
7.1 Provider Support
The application must support:

OpenAI
Gemini
Anthropic
xAI
7.2 Key Visibility Rules
If a provider key is found in environment variables:

do not display the key
do not expose even masked raw contents
display only a readiness badge such as “Available from Environment”
If no environment key exists:

show a secure input field on the webpage
store it only in session memory by default
allow explicit user clearing
7.3 Provider Status States
Each provider should show one of:

Ready from Environment
Ready from Session Input
Missing
Invalid
Rate Limited
Temporarily Unavailable
7.4 Key Security Principles
Never log API keys.
Never include keys in download files.
Never echo keys into live execution logs.
Expire session-entered keys when the session ends unless the user explicitly chooses a local browser-only convenience mechanism.
8. Agent Orchestration and Execution Flow
8.1 Per-Agent Configuration
Before each agent executes, the user must be able to modify:

prompt
selected model
max tokens, defaulting to 12000
optional temperature or reasoning mode if supported
input content source
8.2 Model Options
The UI must include direct support for:

gpt-4o-mini
gpt-5-mini
gpt-5-nano
gemini-3.1-flash-lite as default
gemini-3-flash-preview
gemini-3.5-flash
gemini-3.1-pro-preview
supported Anthropic models
supported xAI models
8.3 Human-in-the-Loop Handoff
After an agent completes:

output appears in text view and markdown view
user may edit output
user may approve output as-is
edited output becomes the next agent’s input
execution provenance records whether the handoff was raw or modified
8.4 Execution Modes
Recommended modes:

Single Agent Run
Sequential Agent Run
Review-Then-Continue
Dry Run Preview using prompts/config only
8.5 Failure Handling
If a provider fails:

show structured error state
allow retry with same provider
allow switch provider/model
preserve current prompt and edited content
keep logs visible for debugging
9. WOW Visualization Layer
This is one of the most important upgrades.

9.1 Live Execution Indicator
A highly visible interactive indicator should display:

queued
preparing
sending
waiting
streaming
completed
failed
cancelled
9.2 Live Log Console
The log panel should show user-friendly events such as:

agent selected
model selected
prompt size estimate
request start
provider response progress
parse success
handoff ready
user modified output
forwarded to next agent
Two log levels are recommended:

Standard
Detailed
9.3 Interactive Dashboard Components
The WOW Dashboard should contain:

run timeline
per-agent duration bars
token estimate cards
provider/model usage breakdown
success rate trend
editable handoff count
note transformation metrics
file import validation summaries
9.4 Visual Storytelling
The dashboard should communicate not only status, but narrative:

where the workflow is
what the model is doing
what changed between steps
where the user intervened
which provider performed best
9.5 Diff and Evolution Views
For agent outputs and notes, the app should provide:

original vs edited diff
previous agent vs next agent input mapping
before vs after organization view for Note Keeper
YAML original vs standardized view
10. AI Note Keeper
10.1 Input Sources
Users must be able to:

paste plain text
paste markdown
upload PDF
upload TXT
upload Markdown files
10.2 Transformation Goal
The system transforms raw notes into:

organized markdown
clear headings
sections and bullets
extracted key points
highlighted keywords in coral color
editable structure
10.3 Editing Modes
Two synchronized editing modes are required:

Plain Text
Markdown
Users can switch between them without losing content.

10.4 Keyword Highlighting
By default, extracted keywords should appear in coral. The feature should also allow user-defined keyword colors through AI Keywords.

10.5 Export
Users should be able to download:

markdown
plain text
optionally PDF-ready formatted content in later phases
11. AI Magics: 9 Total Features
The AI Note Keeper should include six baseline AI Magics plus three new WOW AI features.

11.1 Baseline Six AI Magics
AI Structurer
Converts messy text into organized markdown with headings, subheadings, bullets, and action sections.

AI Summarizer
Produces short, medium, or detailed summaries.

AI Keywords
Extracts keywords and lets the user specify highlight colors for selected terms.

AI Rewriter
Rewrites notes by tone or intent, such as concise, academic, executive, friendly, or bilingual.

AI Action Extractor
Pulls tasks, deadlines, owners, and decision items from notes.

AI Study Cards
Generates flashcards, quick review prompts, or FAQ-style learning aids from note content.

11.2 Three New WOW AI Features
AI Contradiction Radar
Detects contradictions, unresolved ambiguities, duplicated claims, and logical mismatches across notes and agent outputs.
Output should categorize findings into:

direct contradiction
missing evidence
unclear wording
duplicate insight
likely hallucination risk
AI Insight Fusion
Merges outputs from multiple agents or multiple note versions into a single synthesized document.
It should preserve:

agreements
disagreements
unresolved issues
best combined answer
confidence labels
AI Knowledge Graph Mapper
Converts notes into an interactive entity-relationship map, showing links among concepts, tasks, people, dates, tools, and decisions.
This is a wow feature because it makes notes visually explorable rather than static.

12. Agent Config Studio for agents.yaml and SKILL.md
12.1 Core Capabilities
Users must be able to:

paste content
upload files
view content
modify content
download content
validate content before use
12.2 agents.yaml Standardization Pipeline
Before import, the system should standardize the YAML by:

stripping invalid BOM characters
normalizing line endings
converting tabs to spaces
normalizing indentation
validating encoding as UTF-8
ordering top-level keys consistently
filling missing defaults where possible
validating agent IDs and names
ensuring unique identifiers
validating model references against supported provider registry
normalizing prompt block formatting
flagging suspicious fields rather than silently deleting them
12.3 Validation Output
Validation should produce:

pass/fail result
warnings
normalization summary
schema mapping summary
preview of corrected structure
12.4 SKILL.md Editing
SKILL.md requires:

markdown editor
rendered preview
diff against previous version
optional structure linting
compatibility check against referenced agents
12.5 Safe Import Policy
No imported config should become active until the user confirms:

standardized YAML preview
validation results
target agent sequence impact
13. Data Model and State Design
Key conceptual entities include:

Entity	Description
SessionProfile	language, theme, style, provider readiness, token defaults
ProviderCredentialState	source, validity, visibility, session lifetime
AgentDefinition	name, role, prompt template, default model, constraints
AgentRunRecord	timestamps, status, provider, model, token estimate, logs
HandoffRecord	source agent, original output, edited output, approval state
NoteDocument	source type, raw content, transformed markdown, keywords, versions
AIMagicJob	feature type, parameters, result, status, provenance
ConfigAsset	file type, original content, standardized content, validation report
State should be session-scoped by default, with explicit export for persistence.

14. Non-Functional Requirements
14.1 Performance
Initial page load should remain lightweight.
Long tasks must surface progress feedback.
PDF parsing should have size thresholds and fallback notices.
Large logs should be collapsible and paginated if needed.
14.2 Reliability
Provider failure must not erase user edits.
YAML validation errors must not corrupt original content.
Note transformation should preserve a recoverable raw version.
14.3 Accessibility
Contrast must remain acceptable in all 10 styles.
Keyboard navigation should be usable in editors and controls.
Theme and language changes should not require page reload.
14.4 Security
API keys masked or hidden as required.
Sensitive content excluded from diagnostic logs where possible.
Downloaded exports must omit secrets and session metadata.
14.5 Internationalization
All system text should exist in both Traditional Chinese and English, with Traditional Chinese as the default.

15. Deployment and Operations for Hugging Face Spaces
15.1 Deployment Fit
The application should be optimized for Streamlit deployment in Hugging Face Spaces:

minimal operational complexity
no dependence on local persistent databases by default
graceful behavior under cold starts
compact asset footprint
15.2 File Handling
Uploaded files should be processed in temporary storage or memory buffers. Users should be encouraged to download final artifacts for persistence.

15.3 Observability
A lightweight admin-facing diagnostic panel is recommended for:

provider availability
queue depth
recent failures
average runtime
configuration load status
15.4 Future Expansion
The architecture should remain flexible enough to support:

authentication
shared workspaces
external vector storage
persistent project saving
collaborative editing
audit trails
16. Acceptance Criteria
The release is acceptable when:

Users can switch light/dark themes and bilingual interface.
Ten style presets and Jackpot mode work across all key pages.
API key input appears only when environment keys are absent.
Users can configure prompt, max tokens, and model before each agent execution.
Agent output is editable before passing to the next agent.
Live execution indicator, live log, and dashboard are visible and useful.
Note Keeper supports paste plus PDF/TXT/MD upload.
Notes transform into organized markdown with coral keyword highlighting.
Nine AI Magics are accessible, including the three new WOW features.
agents.yaml and SKILL.md can be pasted, uploaded, validated, edited, and downloaded.
YAML is standardized before import.
The app remains deployable on Hugging Face Spaces with Streamlit.
17. 20 Comprehensive Follow-Up Questions
Should the app support project-level persistence beyond the current session, and if yes, should that persistence be implemented via Hugging Face Datasets, an external database, or downloadable project bundles only?

For agents.yaml standardization, do you want a strict schema enforcement mode that blocks import on any warning, or a lenient mode that allows import with warnings and auto-filled defaults?

Should model selection be available globally, per agent, or both, and if both are provided, what precedence rules should apply when the agent default conflicts with the global selection?

Do you want streaming token-by-token output in the Agent Runner and Note Keeper where supported by the provider, or is chunked stage-level progress sufficient for Hugging Face Space performance constraints?

For API key handling, should user-entered keys remain only in session memory, or do you want an optional browser-local encrypted convenience cache for repeat users on the same device?

Which Anthropic and xAI models should be explicitly listed at launch, and should the UI fetch model lists dynamically or use a curated static registry for reliability?

Should the AI Note Keeper include OCR fallback for image-based PDFs, and if yes, should OCR be optional due to latency and compute cost in Streamlit on Hugging Face Spaces?

In the markdown editor, do you want a side-by-side editor/preview, a tabbed text/markdown switcher, or both depending on screen size?

For coral keyword highlighting, should the system apply highlights directly inside the markdown source, or should it preserve raw markdown and apply highlights only at the rendering layer to avoid altering user-authored text?

How should AI Contradiction Radar define contradiction severity: purely semantic mismatch, factual inconsistency, unsupported inference, or configurable categories chosen by the user?

For AI Knowledge Graph Mapper, should the graph remain a lightweight visual summary inside Streamlit, or should it support filtering, clicking nodes, exporting images, and linking nodes back to original note passages?

Should the WOW Dashboard include cost estimation per provider/model based on token usage, even if pricing tables must be maintained manually and may change over time?

How much execution history should be retained in session: only the current run, the last 10 runs, or a more extensive in-session audit trail with diff snapshots and user-edit provenance?

Should SKILL.md validation include a semantic compatibility check against the currently loaded agents, such as identifying skills referenced by no agents or agent roles with missing skill coverage?

When a user edits one agent’s output before handoff, should the system record a structured provenance note explaining what changed, or is a simple modified/unmodified indicator enough?

Would you like the app to support a template gallery for notes, prompts, agent flows, and YAML presets so users can start with curated best-practice configurations rather than blank inputs?

Should the Note Keeper’s AI Magics be allowed to operate on selected text only, full document only, or both, especially for long notes where users may want granular transformations?

Do you want a dedicated comparison mode where outputs from Gemini, OpenAI, Anthropic, and xAI can be run on the same prompt and displayed side by side for evaluation?

Should the system generate a downloadable run package containing prompts, outputs, edited handoffs, note versions, YAML config, and dashboard summaries for reproducibility and compliance review?

For the next design phase, which direction is more important: deeper visual polish and delight, stronger multi-provider reliability and observability, or heavier collaboration/persistence features for team-based workflows?
