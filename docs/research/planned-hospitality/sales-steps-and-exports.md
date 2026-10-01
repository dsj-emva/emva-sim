# Sales steps and export shape: planned hospitality

Research for the planned-hospitality **Industry profile** (issue #4). Topic: which sales systems tailor-made
safari operators and MICE (corporate trips, incentives, events) sellers use, what they call their **CRM stages**,
where those sit on the **Canonical ladder**, and exactly what a CSV export from the most plausible system looks
like. Researched 2026-10-01. Confidence tags follow decision 0007 (see [README](README.md)).

Words follow `emva-app/CONTEXT.md`. Where a vendor's own word clashes with it (HubSpot calls the person record a
"contact" and its pipeline steps "stages"; Safari Portal and Tripleseat say "status"), the vendor's word is kept
only inside quotes or column names, because that is what the export contains.

## Summary

- **No single system dominates.** Safari specialists split between travel-specific itinerary/operations tools
  (Safari Portal, SafariOffice, Wetu, Tourplan, Tourwriter, Kaptio) and a general CRM (HubSpot most visible, then
  Zoho, Salesforce, Pipedrive). The itinerary tools are strong on proposals but thin on sales history; the general
  CRM is where an enquiry's **Stages** are recorded with dates.
- **Chosen export: HubSpot deals (+ contacts, + calls) CSV.** HubSpot is the CRM most often visible on safari
  operator websites in a scan of 41 sites (4 to 7 of 41, a lower bound), and it is documented in enough detail to
  reproduce its export exactly. Second option: Pipedrive deals list export ("Deal - Stage" style headers).
- **Travel stage names cluster around**: New Enquiry, Planning / Working On, Itinerary / Quote Sent (Open),
  Provisional / Pre-Booked / Option / Tentative, Booked / Confirmed / Definite (deposit paid), Travelling,
  Completed, Archived / Not Booked / Lost.
- **Main mapping ambiguity:** whether "confirmed but no deposit yet" is **Won**. Two vendors (SafariOffice,
  Tripleseat) treat deposit as the booking point and the pre-deposit hold as not yet counting; recommend Won =
  deposit paid, and the hold as a **Milestone** inside Proposal.
- **Stage history in HubSpot is patchy by design**: "Date entered/exited [stage]" columns need a Professional or
  Enterprise subscription and are off by default for new pipelines; otherwise history exists only as a
  per-property history export capped at 20 revisions per deal property.
- **Skipping and moving backwards are allowed by default** in HubSpot; preventing them needs opt-in pipeline rules
  (Professional+), which admins, workflows and API can bypass. Moving a deal to closed sets Close Date to *today*,
  so late updates move the recorded close date. No primary source gives rates for skipping, backward moves or late
  updates; those numbers below are guessed.

## Findings

### 1. Which sales systems these businesses use

Travel-specific systems (what they are, from their own sites):

| system | what it is | CRM / stage evidence | source |
|---|---|---|---|
| Safari Portal | itinerary builder + operations for DMCs, advisors, tour operators; "CRM: Contact Management & Custom Forms" | Files Dashboard tabs: Leads, Planning, Confirmed, Traveling, Completed, Archived; custom stages within tabs; CSV "Export Data" of Files; no native CRM integration (Zapier, Google Sheets, beta API) | [home](https://www.safariportal.app/), [tabs](https://help.safariportal.app/en/articles/6056-what-are-the-different-tabs-on-the-files-dashboard), [custom stages](https://help.safariportal.app/en/articles/11055-what-are-custom-files-dashboard-stages), [export](https://help.safariportal.app/en/articles/19247-what-can-i-do-with-the-data-from-my-files), [integrations](https://help.safariportal.app/en/articles/20136-what-integrations-are-currently-supported-by) |
| SafariOffice (SafariBookings) | request inbox + quoting for safari operators listing on SafariBookings | statuses New, Working-On, Open, Pre-Booked, Booked, Not Booked, Archived | [request inbox](https://help.safarioffice.com/en/articles/23-2-your-request-inbox) |
| Tourplan | back-office for tour operators and DMCs | "450 tour operators and DMCs in 75 countries" (vendor claim) | [tourplan.com](https://www.tourplan.com) |
| Kaptio | travel booking layer "built to sit naturally on top of Salesforce" | stages live in Salesforce Opportunities | [kaptio.com](https://www.kaptio.com) |
| Wetu | itinerary content platform; integrates with Tourplan | no CRM pipeline found | [Wetu-Tourplan](https://wetu.helpscoutdocs.com/article/490-integrate-your-tourplan-with-wetu) |
| TripCreator | travel CRM + itinerary | stages shown: New Enquiry, Quote Sent, Follow-up, Option | [sales CRM](https://tripcreator.com/features/sales-crm) |
| Tripleseat (events/MICE venues) | event sales for venues | event statuses Prospect, Tentative, Definite, Closed, Lost (+ optional Waitlist); leads before events | [event statuses](https://support.tripleseat.com/hc/en-us/articles/1500008796602) (status text from search-engine extract of Tripleseat's "What does each event status mean?"; page itself blocked by a bot check, so the article URL is unconfirmed) |
| Tourwriter, Travelify, TravelJoy, Tern, Lemax, Cvent | itinerary / agency / event tools | stage names **not verified** (sites are JavaScript-rendered or help pages not found) | — |

General CRMs:

- **HubSpot**: tour/safari customers named by HubSpot itself: African Bush Camps (landing pages,
  [designers.hubspot.com](https://designers.hubspot.com/inspire/entry/african-bush-camps-hubspot-landing-page-template-development)),
  My Costa Rica tour operator ([HubSpot customer story](https://blog.hubspot.com/customers/bid/191283/travel-experts-find-adventure-and-success-with-hubspot-customer-story)),
  TrekkSoft ([case study](https://www.hubspot.com/case-studies/trekksoft)).
- **Zoho CRM** publishes travel-industry pipeline templates (Inquiry received, Quote sent, Booking confirmed,
  Payment received, Booking canceled ...) ([Zoho tutorial](https://prezohoweb.zoho.com/crm/tutorials/multiple-sales-pipeline/travel-industry.html)).
- **Salesforce**: used underneath Kaptio; large operators. **Pipedrive**: generic; no safari-specific evidence found.

**Website scan (estimated, lower bound).** I fetched the homepages of 50 safari / Africa tailor-made operator and
lodge-group sites on 2026-10-01 and searched the HTML for CRM tracking or form scripts. 41 returned a usable page.
HubSpot markers: 7 of 41 (17%), of which 4 carry a HubSpot portal script or analytics (steppestravel.com,
timbuktutravel.com, artofsafari.travel, africanbushcamps.com) and 3 only a weaker marker (africa-adventure.com
chat id, go2africa.com, thesafaricollection.com). Zoho: 1 (thesafaricollection.com, 10 matches). ActiveCampaign 1,
Wetu embed 1, Mailchimp 4, Salesforce/Pardot 0 clear. Google Tag Manager was present on at least 30 of the 41,
and tags loaded through it are invisible to this scan, so true shares are higher. No system was visible on most
sites; many operators likely run on an itinerary tool plus email. Working: 4/41 = 10% (strong) to 7/41 = 17% (any
marker), widened upward to 40% for GTM-hidden use (guessed upper end).

### 2. Stage names and ladder mapping

Recorded vendor stage names (primary sources above):

- **HubSpot default deal pipeline** ("Sales Pipeline"): Appointment scheduled (20%), Qualified to buy (40%),
  Presentation scheduled (60%), Decision maker bought-in (80%), Contract sent (90%), Closed won (100%, Won), Closed
  lost (0%, Lost) ([pipelines](https://knowledge.hubspot.com/object-settings/set-up-and-customize-pipelines)).
  A safari operator would replace these with its own; every deal pipeline needs one Won and one Lost stage (same
  source). HubSpot's default **Lead** object pipeline: New, Attempting, Connected, Qualified, Disqualified (same
  source; Professional+ to manage). Default contact **Lead Status** options: New, Open, In Progress, Open Deal,
  Unqualified, Attempted to Contact, Connected, Bad Timing
  ([lifecycle stages](https://knowledge.hubspot.com/records/use-lifecycle-stages)).
- **Safari Portal** tabs: Leads, Planning, Confirmed (itinerary + guest count chosen), Traveling and Completed
  (automatic from travel dates), Archived ("budget constraints, lost contact, or client cancellation"); suggested
  custom stages "Deposit Invoice Sent", "Payment Received", "Waiting on Client".
- **SafariOffice**: New → Working-On (quote created, automatic) → Open (quote sent, automatic) → Pre-Booked
  (client confirmed, no deposit; "doesn't affect KPI metrics") → Booked (deposit received; exact value and start
  date entered) → running / completed tours; Not Booked (with reason); Archived.
- **Tripleseat**: Prospect (no documents shared) → Tentative (proposal/contract shared, calendar hold) → Definite
  (contract signed and deposit paid; counts towards sales goals) → Closed (event happened); Lost.
- **Zoho travel templates** and **TripCreator** as listed in section 1.

Mapping table (the **Mapping** a person would confirm; this is what the generator should plant):

| CRM stage (as systems name it) | seen in | Canonical ladder | Milestone? | notes |
|---|---|---|---|---|
| New Enquiry / New / Leads / Inquiry received / Prospect lead | TripCreator, SafariOffice, Safari Portal, Zoho, Tripleseat | Submitted | no | created by the enquiry form |
| Attempted to Contact / Attempting (Lead Status or Lead object) | HubSpot | Contact attempted | no | rarely a deal stage; usually a contact property or only visible as logged calls/emails |
| Connected / Discovery call / In discussion | HubSpot Lead Status; operator-defined | Engaged | no | often missing; inferred from a connected call or a reply |
| Qualified / Planning / Working-On / Prospect event | Safari Portal, SafariOffice, Tripleseat, HubSpot Lead object | Qualified | "Brief confirmed", "Call booked" can be Milestones | Working-On is automatic when a quote is started: means "work begun", not a judged qualification |
| Itinerary Sent / Quote Sent / Open / Proposal | SafariOffice, TripCreator, Zoho | Proposal | "Itinerary sent" is the Proposal entry point | revisions loop back into the same stage |
| Itinerary revised / Follow-up / Waiting on Client | TripCreator, Safari Portal | Proposal | yes ("revision sent") | can look like a backward move if modelled as a separate earlier stage |
| Provisional / Option / Pre-Booked / Tentative / Held | TripCreator, SafariOffice, Tripleseat | Proposal | yes ("held" / "verbal yes"), deepest Proposal milestone | **ambiguous**: client said yes, no money |
| Deposit Paid / Booked / Confirmed / Definite / Closed won | SafariOffice, Safari Portal, Tripleseat, HubSpot | Won | — | recommend Won = deposit received (SafariOffice and Tripleseat both treat it so) |
| Balance paid / Travelling / Traveled / Completed / Closed (event) | Safari Portal, SafariOffice, Tripleseat | after Won (not on ladder) | — | outcome already Won; the generator may emit them as post-Won CRM stages |
| Lost / Closed lost / Not Booked / Archived / Turned Down / Booking canceled | all | Lost | — | Archived mixes lost and "never qualified"; see open questions |

Ambiguities to plant in the generator: (a) Won at confirmation vs at deposit (Safari Portal "Confirmed" requires
only itinerary + guests, no deposit); (b) "Archived" used for both poor leads and handled-badly leads; (c) a Won
booking later cancelled (Zoho has "Booking canceled" after "Booking approved"); (d) automatic stages
(SafariOffice Working-On/Open, Safari Portal Traveling/Completed) carry system timestamps, while manual stages
carry the salesperson's lag.

### 3. The chosen export: HubSpot

Why HubSpot: most visible general CRM among safari operator websites (section 1); HubSpot names travel/safari
customers; it is the only candidate whose export, property labels and stage history are fully documented in a
public help centre; and an itinerary tool (Safari Portal, Wetu) does not export dated stage history. Confidence in
"most plausible": estimated, moderate. An advertiser on Safari Portal alone would hand over a Files CSV whose
columns are **not documented** (see open questions).

**How a HubSpot export is made** ([export records](https://knowledge.hubspot.com/import-and-export/export-records)):
from a view (list or board) of Deals, Contacts or Calls; CSV, XLSX or XLS; by default only the view's columns, in
the view's order; "All properties" puts columns in alphabetical order with Record ID first; associations go at the
end; up to 1,000 associated record IDs per association column by default; column headers can be translated (values
are not); CSV above 2 MB is zipped; above 1,000,000 rows it is split. Calls, notes, meetings and emails are
**not** in a deal export: calls can be exported as their own object (CRM > Calls); notes/emails need individual
record exports, reports or the API (same source).

**File conventions** (from a HubSpot-authored export file,
[hubspotdev/crm-customization-dev-bootcamp](https://github.com/hubspotdev/crm-customization-dev-bootcamp/blob/main/data/3.crm-bootcamp-vehicles.csv);
estimated to hold for deals):

- every field double-quoted, including numbers and empty cells (`""`);
- header = the property's **label**, not its internal name;
- datetime values `YYYY-MM-DD HH:MM` (minutes, no seconds, no zone), e.g. `"2023-11-15 20:09"`; the zone is the
  account's time zone for datetime properties (community report, not primary:
  [HubSpot community](https://community.hubspot.com/t5/Dashboards-Reporting/Exporting-Timestamp/m-p/721966));
- numbers as decimals, e.g. `"117.0"`; booleans `"Yes"`/`"No"`;
- user/owner properties exported as the user's **name** (e.g. `"Carter McKay"` under "Created by user ID");
- association columns in pairs: `Associated Contact` (names) and `Associated Contact IDs`;
- file name pattern `hubspot-crm-exports-<view-name>-YYYY-MM-DD.csv` (seen in many public repos, e.g.
  [search](https://github.com/search?q=hubspot-crm-exports&type=code); estimated);
- multi-value (multiple checkbox) values separated by `;` with no spaces (import rule,
  [multiple checkbox](https://knowledge.hubspot.com/import-and-export/add-or-replace-multiple-checkbox-property-values));
  multi-value association ID cells assumed `;` too (third-party parser,
  [pipecheck](https://github.com/joshua-gitmaxxing/pipecheck/blob/main/backend/app/parser.py); estimated).

Column labels below come from HubSpot's definitions
([default deal properties](https://knowledge.hubspot.com/properties/hubspots-default-deal-properties),
[default contact properties](https://knowledge.hubspot.com/properties/hubspots-default-contact-properties),
[activity properties](https://knowledge.hubspot.com/properties/hubspots-default-activity-properties)), with exact
label casing taken from a public dump of HubSpot's properties API output
([Deal_property.json](https://github.com/ShaktiPalmspire/Test-migratio/blob/main/migratio-ui-Shakti/src/context/Deal_property.json),
[Contact_pproperty.json](https://github.com/ShaktiPalmspire/Test-migratio/blob/main/migratio-ui-Shakti/src/context/Contact_pproperty.json)).
The knowledge base writes labels in sentence case ("Deal name"); the API dump, and so the export header, uses
"Deal Name". Casing is estimated from the dump, not from a real deals export file.

#### Deals export (view export of a custom "Safari Enquiries" pipeline)

| column | meaning | format | source |
|---|---|---|---|
| Record ID | deal's unique id; first column | integer as string, e.g. `"10676775052"` | deal props KB; bootcamp file |
| Deal Name | name given by the user; often "Surname – Tanzania Jun" style (guessed) | free text | deal props KB |
| Pipeline | pipeline name | label, e.g. `"Safari Enquiries"` | deal props KB |
| Deal Stage | current CRM stage label | label of a stage of that pipeline | deal props KB |
| Amount | deal value in the deal's currency | decimal | deal props KB (Deal revenue) |
| Currency | deal currency; only exists if multiple currencies are set up (Starter+) | ISO code, e.g. `USD` | deal props KB |
| Amount in company currency | amount converted at the account's rate; frozen once closed | decimal | deal props KB |
| Close Date | expected or actual close; auto-set to end of month at creation if blank, auto-set to *today* on moving to closed won/lost | datetime | deal props KB |
| Create Date | deal creation; editable by users | datetime | deal props KB |
| Deal owner | assigned user | user name | deal props KB |
| Deal Type | New Business / Existing Business by default | label | deal props KB |
| Deal Description | free text | text | deal props KB |
| Closed Lost Reason | why lost; **free text (textarea) by default**, can be made a dropdown | text | deal props KB; API dump type `textarea` |
| Closed Won Reason | why won | text | deal props KB |
| Last Activity Date | latest past note, call, email, meeting, message or completed task; can be backdated by logging an activity "yesterday" | datetime | deal props KB |
| Last Contacted | last call, chat, one-to-one email, meeting or message | datetime | deal props KB |
| Number of Sales Activities | count of calls, chats, meetings, notes, emails, tasks, messages | integer | deal props KB |
| Number of times contacted | count of calls, chats, emails, meetings, messages (no tasks/notes) | integer | deal props KB |
| Next Activity Date | next scheduled activity | datetime | deal props KB |
| Deal probability | from stage's win probability; stops auto-updating once edited by hand | 0 to 1 decimal (estimated) | deal props KB |
| Original Traffic Source | from the associated contact | enum label, e.g. Paid Search, Paid Social | deal props KB |
| Original Traffic Source Drill-Down 1 / 2 | more detail | text | deal props KB |
| Record source | how the deal was created (e.g. Import, Forms, CRM UI) | label | deal props KB |
| Last Modified Date | any property change, including hidden internal ones | datetime | deal props KB |
| Date entered current stage | when the deal entered its current stage | datetime | stage calculated props KB |
| Date entered "<Stage> (<Pipeline>)" | one column per stage, e.g. `Date entered "Itinerary Sent (Safari Enquiries)"` | datetime, blank if never entered | stage calc props KB; label format from API dump |
| Date exited "<Stage> (<Pipeline>)" | one per stage | datetime | same |
| Latest time in "<Stage> (<Pipeline>)" | time since last entry, filled only after leaving | number; unit **unverified** (milliseconds likely) | same |
| Cumulative time in "<Stage> (<Pipeline>)" | total time over re-entries | number; unit unverified | same |
| custom deal properties, e.g. "Travel month", "Number of travellers", "Budget per person", "Destinations" | copied from the enquiry form by workflow (operator-defined) | label as the operator named it; multi-select joined with `;` | guessed (names), multi-checkbox KB (delimiter) |
| Associated Contact | names of associated contacts | text, multiple joined (delimiter estimated `;`) | export records KB; bootcamp file |
| Associated Contact IDs | Record IDs of associated contacts | ids joined with `;` (estimated) | same |

Stage-calculated columns exist only on Professional/Enterprise ("A Professional or Enterprise subscription is
required to use stage calculated properties", deal props KB), and "stage calculated properties are turned off for
new pipelines and pipeline stages" by default
([stage calculated properties](https://knowledge.hubspot.com/properties/stage-calculated-properties)). When on,
their values are "populated retroactively based on existing data" and keep updating if a deal is closed then
reopened. Re-entering a stage overwrites "Date entered" (only "Cumulative time" keeps the sum), so an export shows
only the latest entry per stage (estimated from the definitions).

**Stage history otherwise**: the property history export (Settings > Properties > Deal Stage > Export property
history) gives the current and historical values with when they changed, newest first left to right, optionally
with the source (user, workflow, import); deals keep at most **20 revisions** per property, contacts 45; times in
UTC ([export property history](https://knowledge.hubspot.com/properties/export-property-history)). Exact column
headers of that file are **not documented**.

#### Contacts export

| column | meaning | format | source |
|---|---|---|---|
| Record ID | contact id | integer string | contact props KB; API dump |
| First Name / Last Name | — | text | same |
| Email | primary email | text | same |
| Phone Number | formatted by HubSpot from country code | text | same |
| Country/Region | country of residence | text | same |
| Lifecycle Stage | Subscriber ... Lead, Marketing Qualified Lead, Sales Qualified Lead, Opportunity, Customer ... | label | lifecycle KB |
| Lead Status | New, Open, In Progress, Open Deal, Unqualified, Attempted to Contact, Connected, Bad Timing | label | lifecycle KB; API dump |
| Contact owner | user | name | contact props KB |
| Create Date | contact creation | datetime | same |
| Message | the form's free-text message field | text | same |
| Recent Conversion / Recent Conversion Date | last form, as "Page title: Form name" | text / datetime | same |
| First Conversion | first form submitted | text | same |
| Number of Form Submissions | count | integer | same |
| Original Traffic Source / Original Traffic Source Drill-Down 1 | first known source | label / text | same |
| Google ad click id | GCLID | text | same; label from API dump |
| Facebook click id | fbclid-derived | text | same |
| Last Activity Date / Last Contacted / Number of times contacted | as for deals | datetime / integer | same |
| Number of Associated Deals | count | integer | API dump |
| Associated Deal / Associated Deal IDs | associations | names / ids | export records KB |

Form fields: each enquiry-form question is a contact property; custom ones appear as columns under the label
the operator chose (guessed names), multi-select joined with `;`.

#### Calls export (contact attempts)

Columns from activity properties: Activity date, Call title, Call notes, Call outcome, Call status, Call duration
(milliseconds), Call direction (estimated label), plus Associated Contact / Deal columns. Default **Call outcome**
labels: Busy, Connected, Left live message, Left voicemail, No answer, Wrong number; up to 30 custom outcomes
([activity properties](https://knowledge.hubspot.com/properties/hubspots-default-activity-properties),
[calls API](https://developers.hubspot.com/docs/api-reference/crm-calls-v3/guide),
[custom outcomes](https://knowledge.hubspot.com/calling/create-custom-call-outcomes)). Mapping: any logged call or
outbound email → **Contact attempt**; outcome Connected (or a reply) → Engaged. Notes body is "Note body"; logged
emails are not exportable from the UI (export records KB), so **Sales notes** usually reach Emva as call notes or
a separate notes report.

### 3b. Second option: Pipedrive

Pipedrive exports deals from a filtered list view (columns chosen from deal, person and organisation fields) or
from Settings, as CSV or XLSX; activities, notes and files export separately
([exporting data](https://support.pipedrive.com/en/article/exporting-data-from-pipedrive)). Lost reasons are
free-form or an admin-defined list ([lost reasons](https://support.pipedrive.com/en/article/lost-reasons)). Header
style "<Object> - <Field>", seen in code parsing real exports (third-party, estimated):
`Deal - ID`, `Deal - Title`, `Deal - Value`, `Deal - Currency of Value`, `Deal - Pipeline`, `Deal - Stage`,
`Deal - Status` (Open/Won/Lost), `Deal - Owner`, `Deal - Contact person`, `Deal - Organization`,
`Deal - Deal created`, `Deal - Update time`, `Deal - Expected close date`, `Deal - Won time`, `Deal - Lost time`,
`Deal - Lost reason`, `Deal - Last activity date`, `Deal - Next activity date`, `Deal - Probability`
([pipedrive-filter.py](https://github.com/Premium-Lithium/vercel-website/blob/main/.github/workflows/scripts/pipedrive-filter/pipedrive-filter.py),
[build-projects-import-mapped.js](https://github.com/Mihaylov-Ivan/hydr-sales-leads-tracker/blob/main/templates/projects/build-projects-import-mapped.js)). Key difference from HubSpot: won/lost is a
separate **Status** with its own timestamps, not a stage. Per-stage entry dates in the export: **not verified**.

### 4. How stage changes are recorded in practice

- **Skipping is allowed by default.** HubSpot's "Restrict [records] from skipping stages" and "Restrict
  [records] from moving backwards" are opt-in pipeline rules (Professional/Enterprise); even when on, moving
  straight to Closed/Closed Lost may skip, Super Admins and users with property-settings permission bypass them,
  and workflows and API bypass them ([pipeline rules](https://knowledge.hubspot.com/object-settings/set-up-pipeline-rules)).
- **Backward moves and reopening** happen and are expected by the product: stage-calculated properties track
  re-entry ("Cumulative time in") and records "closed then reopened"
  ([stage calculated properties](https://knowledge.hubspot.com/properties/stage-calculated-properties)).
- **Bulk updates**: HubSpot supports bulk editing of stage, which pipeline rules disable when on (pipeline rules
  KB). A bulk update stamps every record with the same time.
- **Late updates distort dates**: Close Date is set to *today* when a deal is moved into closed won/lost (deal
  props KB), so a rep who records a deposit two weeks late records a close two weeks late; Create Date can be
  edited by hand; activities can be logged with a past date.
- **Manual vs automatic**: Safari Portal and HubSpot stages move manually; SafariOffice moves New → Working-On →
  Open automatically; Safari Portal moves Confirmed → Traveling → Completed by travel date (sources in section 2).
- **Frequency**: practitioner and vendor blogs (not primary) say reps update stages rarely and late, e.g. stages
  "got updated only when managers asked" about weekly
  ([cotera](https://cotera.co/articles/how-to-automate-crm-data-entry.md)) and reps rarely move stalled deals
  backwards ([revenue.io](https://www.revenue.io/blog/bad-crm-data-is-costing-you-more-than-bad-reps)). No
  measured rates found.

## Numbers for the profile

| quantity | low | high | confidence | source |
|---|---|---|---|---|
| Share of safari operators whose general CRM is HubSpot | 10% | 40% | estimated (low: 4/41 sites with a HubSpot portal script; high widened for GTM-hidden tags, guessed) | website scan, section 1 |
| Share of safari operators using an itinerary tool as their only sales system | 30% | 70% | guessed | no source; most scanned sites showed no CRM |
| Deal property revisions kept in HubSpot property history | 20 | 20 | sourced | [export property history](https://knowledge.hubspot.com/properties/export-property-history) |
| Contact property revisions kept | 45 | 45 | sourced | same |
| Share of HubSpot exports that have "Date entered" columns (Pro+ and turned on) | 20% | 60% | guessed | tier rule sourced (deal props KB); share unknown |
| CRM stages in an operator's custom pipeline, including Won and Lost | 6 | 10 | estimated (vendor lists in section 2 have 5 to 8 steps plus Lost) | Safari Portal, SafariOffice, Tripleseat, Zoho |
| Won deals with at least one intermediate stage skipped in the record | 10% | 40% | guessed | none; skipping allowed by default (pipeline rules KB) |
| Deals with at least one backward stage move | 2% | 10% | guessed | none; re-entry supported (stage calc KB) |
| Lag between a stage event and its CRM update (manual stages), days | 0 | 14 | guessed | weekly-update anecdote (cotera, not primary) |
| Share of stage changes made by bulk edit | 0% | 15% | guessed | none |
| Share of lost deals with a Closed Lost Reason filled | 30% | 80% | guessed | free-text field, not required by default (API dump) |
| Days between "Pre-Booked/Provisional" and deposit | — | — | not researched here | see cycle-and-deal-size.md |
| Export datetime precision | minute | minute | sourced (HubSpot-authored file) | [bootcamp CSV](https://github.com/hubspotdev/crm-customization-dev-bootcamp/blob/main/data/3.crm-bootcamp-vehicles.csv) |

## Open questions

1. Safari Portal's Files CSV columns are undocumented; an advertiser who uses only Safari Portal would send a
   different file. Getting a real (anonymised) Safari Portal export would settle it.
2. Is Won "deposit paid" (recommended) or "confirmed"? Needs a decision when the profile is written; the
   generator could plant both conventions across advertisers.
3. A Won booking later cancelled: does the profile model it, and as what **Outcome**?
4. HubSpot "Latest/Cumulative time in" unit (milliseconds assumed) and the exact header row of the property
   history export are unverified.
5. Exact header casing of a real HubSpot *deals* CSV is inferred from the properties API labels and one
   HubSpot-authored custom-object export, not seen directly.
6. MICE: Cvent and Tripleseat lead (pre-event) statuses beyond "Not Converted / Converted / Turned Down" were not
   verified; corporate-incentive DMCs may use the same HubSpot/Salesforce setup as safari operators.
7. Is "Archived" (lost contact, budget, cancelled) one **Loss reason** bucket or several? Belongs with
   notes-and-loss-reasons.md.
