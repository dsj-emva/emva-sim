# Sales notes and loss reasons (planned hospitality)

Research for the planned-hospitality **Industry profile** (issue #4): how a sales team writes **Sales notes**
about a **Lead**, which **Loss reasons** it records, and how often either is present. Covers tailor-made
safari operators and travel designers, and corporate trips, incentives and events (MICE).

Confidence follows decision 0007: **sourced** (a cited source states it), **estimated** (worked out from cited
sources, working shown), **guessed** (no usable source; reasoned judgement, flagged). Forum and vendor-blog
material is flagged as such.

## Summary

- No public source gives the share of leads with notes, note lengths, or the share of each loss reason for
  this industry. Those numbers below are **guessed** and should get the widest ranges in the profile.
- The one usable industry number: SafariBookings (a safari marketplace) says its operators win about one
  booking per five to six requests, and one or two of the four to five that do not book never answer an
  email. That puts "no reply" at roughly 20–50% of lost leads (estimated).
- Shorthand is well documented: generic travel terms (pax, FIT, BB/HB/FB, AI, PPPN, DMC, MICE), safari rate
  terms (pps/pn, FI, game package, single supplement), event terms (RFP, BEO, F&B, DDR, room block,
  attrition) and generic call shorthand (NA, LM, CB, f/u).
- Loss-reason lists are configured by each business, not fixed by the vendor. HubSpot and Pipedrive default to
  free text; Tripleseat and Amadeus Delphi leave the list to the admin; Event Temple suggests a categorised
  list, with "Unidentified" and "No reason provided" among the options. So exports will mix picklist values,
  free text and blanks.
- Recorded loss reasons are unreliable: a hospitality consultancy (HVS) says "other" is often the largest
  value and "lost to competitor" gets misused, and a win/loss vendor (Clozd) says reps are wrong about why
  they lose about 60% of the time. "Price" is said to be the easy default. The generator should record a
  loss reason that often differs from the **Hidden truth**.
- "Could not reach them" is ambiguous by design: a lead who gave a dead number (the lead was poor) and a
  lead the team called once, two days late (the handling was poor) get the same **Loss reason**. Only the
  **Sales notes** and the attempt history tell them apart. That is the main place where meaning, not
  keywords, carries the signal.

## Findings

### 1. What notes record

The enquiry form already gives the team the facts the first notes confirm or correct. Expert Africa's form
asks for the number and ages of travellers, room sharing, country, fixed or flexible dates, whether flights
are booked, budget per person and free-text comments
([Expert Africa enquiry](https://www.expertafrica.com/enquiry)). Discovery-call guides for travel advisers
list the same things: how many are travelling, ages, when, how flexible, where, and travel class as a budget
clue ([Travelweek, power of the discovery call](https://www.travelweek.ca/blog/sphere-homebased/the-power-of-the-discovery-call/);
[open exam-prep study guide, consultative selling](https://open-exam-prep.com/study-guides/tap/sales-ethics-communication/consultative-selling),
the second is training material, not primary).

So notes after first contact typically record (synthesis of the above; the list itself is **estimated**):

- whether the lead was reached (NA, LM, VM, email sent, replied);
- party: pax, adults/children and ages, honeymoon, family, group size (MICE: delegates, room block);
- dates and flexibility; month and year; nights;
- budget: per person or total, whether it covers flights; whether the budget is realistic for what was asked;
- style: camps vs lodges, private vehicle, fly-in vs road, luxury level, rate basis (FI, FB);
- flights: booked already, need quoting, using points;
- who decides: spoke to partner, needs to check with wife/husband, PA booking for the boss, procurement /
  committee for corporate, client of a client for agencies;
- competition: "also talking to X", "has 3 quotes", "found it cheaper on lodge website";
- next action and date: f/u Tue, send itinerary v2, hold space at camp, deposit invoice sent;
- MICE extras: RFP received, site visit, BEO, F&B minimum, DDR, contract out, attrition clause.

### 2. How notes are written

Generic CRM shorthand for call outcomes (NA, LM, CB, WCB, f/u, appt) is common practice across sales teams
([GoldMine success, "Make your LM more effective"](https://goldminesuccess.com/?p=227); [IRC Sales Solutions
glossary, call notes](https://ircsalessolutions.com/glossary/C/call-notes/); vendor blogs). Travel jargon
adds its own (abbreviations table below). Nothing found measures length or typo rates in travel CRMs.

Patterns to plant (**guessed**, from how such notes are generally written; no source measures them):

- Mostly short, telegraphic fragments with no subject: "LM. Will try thurs."
- A few long notes after the main discovery call (a paragraph that summarises the trip and the people).
- Logged emails: either pasted email text (long, polite, full sentences) or a one-line summary ("sent
  itin v2 + costing").
- Inconsistent casing and spelling; lodge and park names misspelt (Serengetti, Okavanga, Ngorongoro
  variants); currency written several ways ($12k, USD12,000, 12K pp).
- Tone differs by lead quality more than by keywords. Promising: specific, next step dated, rep writes
  about the client as a person ("lovely couple, 10th anniv"). Hopeless: short, repetitive, attempts
  counted ("3rd LM", "no reply x2"), hedged ("says still keen but..."), irony or exasperation
  ("wants Mombasa beach + Mara + gorillas for $3k total for 4, lol").
- Same words, opposite meaning: "budget fine" (client said so) vs "budget 'fine'" (rep doubts it);
  "will discuss with husband" is neutral early and a stalling signal after two itinerary versions.
- Negation and sarcasm defeat keyword matching: "not price sensitive at all", "price not an issue (apparently)".

### 3. Loss-reason lists businesses use

- **Event Temple** (hotel and venue sales and catering) suggests grouped lost reasons: competitive (another
  venue in or outside the market, competitor brand, better package elsewhere), pricing (room rates, catering
  prices, budget limits, rate not met), client communication (no customer response at lead stage or contract
  stage, delayed decision), property-specific (space, rooms, physical attributes), timing and availability
  (dates not available, blackout dates), client cancellations (cancelled, on hold, restructuring), and other
  (unidentified, no reason provided). They are examples, not system defaults
  ([Event Temple support](https://support.eventtemple.com/en/articles/12824397-how-to-add-lost-reasons)).
  **Sourced.**
- **Tripleseat** (event sales for venues and restaurants): lost reasons are a customisable dropdown; setting
  an event to Lost asks for a reason plus free-text details, which feed lost-event reports
  ([Tripleseat dropdowns](https://support.tripleseat.com/hc/en-us/articles/16342612340887-Dropdowns);
  [Tripleseat customisable fields](https://support.tripleseat.com/hc/en-us/articles/115004844114)). **Sourced.**
- **Amadeus Delphi** (hotel group sales): statuses Lost, Cancelled, Turned Down; each has a lost reason the
  property's admin defines ([Amadeus group lost business report](https://help.amadeus-hospitality.com/sales-and-event-management/advanced/content/group-lost-business-report.html)).
  **Sourced.** Hotels split turnaways into *denials* (the property said no: sold out, room type unavailable)
  and *regrets* (the guest said no: price, location, facilities)
  ([setupmyhotel SOP](https://setupmyhotel.com/hotel-sop-standard-operating-procedures/sales-and-marketing-sop/sop-sales-and-marketing-lost-business-or-turnaways/),
  a hotel SOP site, not a vendor).
- **HVS** (hospitality consultancy) lists nine reasons group business is lost: capacity, services, price,
  destination appeal, transport access, security, climate, responsiveness, date conflicts
  ([HVS via Hospitality Net](https://www.hospitalitynet.org/opinion/4037801.html)). **Sourced.**
- **HubSpot**: closed-lost reason is a free-text deal property by default; agencies advise turning it into a
  dropdown such as bad timing, bad fit, cost, competitor
  ([Weidert, HubSpot how-to](https://weidert.com/blog/hubspot-deals-properties); agency blog).
- **Pipedrive**: lost reasons are free-form by default; an admin can enable predefined reasons and still
  allow free text ([Pipedrive knowledge base](https://support.pipedrive.com/en/article/how-can-i-enable-predefined-lost-reasons)).
  **Sourced.**
- Safari-specific tools (Safari Portal, SafariOffice, Wetu, Tourwriter): no public documentation of a
  lost-reason list was found ([Safari Portal CRM page](https://www.safariportal.app/travel-crm-contact-management-custom-forms);
  [SafariOffice](https://www.safarioffice.com/?p=1961)). Open question.

### 4. How common each reason is

- **No reply.** SafariBookings tells its operators they average one booking per five to six requests, and that
  one or two of the four to five non-bookings never reply to an email
  ([SafariBookings help, quote request legitimacy](https://help.safaribookings.com/hc/en-150/articles/30458407229597-Ensuring-the-Legitimacy-of-Quote-Requests);
  page returned 403 to direct fetch, content read via search-engine extract, so treat as sourced but
  unverified). **Estimated** share of lost leads with no reply: 1 of 5 = 20% to 2 of 4 = 50%. Marketplace
  leads are likely weaker than a tour operator's own website leads, so the low end may suit an operator's
  own site.
- The same SafariBookings help pages recommend a first follow-up three working days after the quote, and a
  second two working days later ([SafariBookings, converting more requests](https://help.safaribookings.com/hc/en-150/articles/19487006345117),
  same access caveat), which sets the expected attempt pattern before a lead is closed as no reply.
- **Booked elsewhere after a quote.** UK agents report clients taking a quoted itinerary and booking it
  elsewhere, sometimes for slightly less; no rate is given
  ([Aspire Travel Club](https://www.aspiretravelclub.co.uk/news/agency-calls-for-honesty-from-clients-following-rise-in-customers-booking-independently),
  trade press, anecdote).
- **Price.** Trade surveys of UK agents put price rises as the top issue they face in some months
  ([TTG](https://www.ttgmedia.com/news/price-hikes-slowing-conversions-despite-renewed-lates-demand-36212)),
  but that is an issue ranking, not a share of lost leads. Revenue.io (vendor) argues price is the most
  selected close reason and the least accurate one
  ([Revenue.io](https://www.revenue.io/blog/what-your-lost-deal-recordings-tell-you-that-crm-close-reasons-dont)).
- **Events.** A venue-software vendor says event teams lose 20–30% of enquiries to slow replies or missed
  channels ([Tripleseat blog](https://tripleseat.com/blog/3-automated-ways-tripleseat-can-help-your-venue-grow-leads/),
  vendor marketing, no method given).
- No source gives the share of price, postponed, competitor, dates, destination fears or fake leads. All
  those shares below are **guessed**.

### 5. Missing and wrong loss reasons

- HVS: in hotel lost-business databases a single catch-all such as "other" often covers most events, "lost to
  competitor" is used where it does not apply, the winning competitor is rarely named, and planners give
  convenient excuses ([HVS via Hospitality Net](https://www.hospitalitynet.org/opinion/4037801.html)).
  **Sourced (qualitative).**
- Clozd (win/loss vendor) states reps are wrong about why they win and lose about 60% of the time, without
  citing a study ([Clozd blog](https://www.clozd.com/blog/win-loss-analysis-5-common-mistakes)). Vendor claim;
  treat as **guessed**-quality.
- Because HubSpot and Pipedrive default to free text and the hospitality tools let each admin build the list,
  the same reason appears in several spellings within one export, plus blanks.

### 6. How often notes exist

No source measures note coverage in travel CRMs. Sales-tool vendors claim reps log only part of their
activity (for example, that manual logging captures under 28% of emails and meetings,
[Avoma](https://www.avoma.com/blog/salesforce-activity-capture); that 79% of opportunity data never reaches the
CRM, attributed to Salesso, [SyncGTM](https://syncgtm.com/blog/why-sales-reps-dont-log-emails-crm)). These are
vendor marketing with no method, so they only support "notes are incomplete", not a number. A hotel-call study
claims 92% of luxury hotel calls capture no guest data
([Hospitality Net](https://www.hospitalitynet.org/news/4134252/92-of-luxury-hotel-calls-capture-no-guest-data-luxury-marketing-is-structurally-incomplete-your-largest-corporate-account-may-be-your-worst-investment),
reservation calls, not planned trips; not used).

Reasoning for the guesses below: a tailor-made safari or event needs an itinerary or proposal, so any lead
that reaches **Engaged** almost always has some written record (logged emails at least); leads that only had
**Contact attempts** often have none, or only "LM"; **Neglected leads** have none by definition.

## Abbreviations

| term | meaning | where used | source |
|---|---|---|---|
| pax | passengers / travellers (any age) | all travel | [AltexSoft glossary](https://www.altexsoft.com/glossary/travel-industry-terms/); [PTN Travel](https://ptntravel.com/the-top-30-travel-industry-abbreviations-you-need-to-know-as-you-start-your-travel-business/) |
| FIT | free (or fully) independent traveller: tailor-made, not a group tour | tour operators | [Gifted Travel Network](https://www.giftedtravelnetwork.com/blog/how-to-speak-travel-advisor-the-most-common-industry-terrms); AltexSoft |
| BB / HB / FB | bed and breakfast / half board / full board | lodges, hotels | AltexSoft |
| AI | all-inclusive | resorts, beach extensions | PTN Travel; AltexSoft |
| FB (safari) | lodge full board, often with house drinks and laundry | safari lodges | [Elewana rates](https://elewanacollection.com/sand-river-masai-mara/rates-and-seasons) |
| GP | game package: full board plus shared game drives, walks, sundowners, airstrip transfers | safari lodges | Elewana rates |
| FI | fully inclusive: meals, drinks, game drives | safari lodges | [Sabi Sabi rates](https://www.sabisabi.com/rates) |
| pps/pn, PPPN, pp | per person sharing per night; per person per night; per person | safari rates, quotes | Sabi Sabi rates; AltexSoft |
| SS / single supp | single supplement (40–50% at some lodges) | safari rates | Sabi Sabi rates |
| DBL / TWN / SGL | double / twin / single room | all | AltexSoft |
| DMC | destination management company (ground handler) | operators, MICE | Gifted Travel Network; AltexSoft |
| FAM | familiarisation trip | agents | Gifted Travel Network |
| NR | non-refundable | quotes | PTN Travel |
| MICE | meetings, incentives, conferences/conventions, events/exhibitions | corporate | AltexSoft; [Marriott Bonvoy Events](https://marriottbonvoyevents.com/news-and-highlights/article/780/what-does-beo-stand-for-and-other-meeting-planning-terms) |
| RFP | request for proposal | MICE | [Skift Meetings](https://meetings.skift.com/2026/05/11/25-of-the-most-common-event-planning-terms/); Marriott Bonvoy Events |
| BEO | banquet event order | MICE, venues | Marriott Bonvoy Events |
| F&B | food and beverage | MICE, venues | Skift Meetings |
| DDR | day delegate rate | MICE (UK/EU) | Skift Meetings |
| room block / attrition | rooms held for a group / share of the block not used | MICE | Skift Meetings |
| NA, LM, CB, WCB, f/u, appt | no answer, left message, call back, will call back, follow-up, appointment | generic sales | [GoldMine success](https://goldminesuccess.com/?p=227); generic usage |
| VM, LVM, DM | voicemail, left voicemail, decision-maker | generic sales | generic usage, **no source found** |
| HM, anniv, bday | honeymoon, anniversary, birthday | leisure travel | generic usage, **no source found** |
| itin, v2, costing, dep, bal | itinerary, version 2, priced quote, deposit, balance due | tour operators | generic usage, **no source found** |
| Mara, Seren, Ngoro, Kruger, Okav, Vic Falls | park and area short names | safari | generic usage, **no source found** |

## Illustrative notes

Written for this file, **illustrative only**, not copied from any source. Each tagged with what the Hidden
truth behind it would be. Several are deliberately ambiguous on keywords.

Promising (leisure safari):

1. "Spoke w/ Sarah 25 min. 2 pax, 10th anniv, Sept 2027 fixed (his 50th). Want Mara migration + 3n beach.
   Budget ~12-15k pp excl flights, fine w/ that. Flights on points, already holding BA. Send itin by Fri."
2. "Call w/ both of them this time. Husband had read up on Ruaha vs Selous, asked good qs re private
   vehicle. Happy to go FI. Wants deposit invoice once camp confirms."
3. "Itin v3 sent. Only change asked: swap night 2 to Sand River. Said 'this is the one'. Holding space till 14th."
4. "Repeat client (Botswana 2023). 6 pax multigen, kids 9 & 12. Wants same guide if poss. No budget given
   but last trip was $68k."
5. "PA for Mr K called. Exec + wife + 2 kids, Xmas. 'Best available, cost no object' - check Singita
   Grumeti avail asap, decision by Monday."

Hopeless or never a real buyer:

6. "3rd LM. Email bounced. Number on form is 1234567890."
7. "Wants Kenya + Tanzania + gorillas + Zanzibar, 14n, 4 pax, total budget $6k incl flights. Explained
   pricing. Said will 'have a think'."
8. "Student doing research project on safari pricing, not travelling. Closed."
9. "Asked for a quote for 'whenever is cheapest'. No dates, no destination, wouldn't give a budget. Has
   'loads of quotes already'."
10. "Spoke briefly, she said she only filled the form to see a sample itinerary. Maybe in a few yrs."

Could not reach them (handling vs lead):

11. "NA x1. Will try next week." (dated 6 days after the enquiry; handling poor)
12. "Called same day, NA, LM. Emailed. Called day 3, NA. Emailed day 5 w/ sample itin. No reply." (handling
    fine; lead went quiet)
13. "no reply x2" (nothing else; cannot tell)

Price and timing (real buyer, lost on offer or calendar):

14. "Loved the itin but Mombasa lodge too pricey. Found the same camp cheaper direct. Matched what we could,
    she's going direct."
15. "Mum's surgery moved - pushing to 2028. Genuinely keen, asked us to keep the itin. Set reminder Jan."
16. "Camp full for their dates (Aug). Offered alternatives, didn't like any. Lost to dates."
17. "Went with [competitor], said our proposal was nicer but they had a friend who'd used them."

Ambiguous on keywords, clear on meaning:

18. "Budget fine." vs "Budget 'fine' - asked for 5* for price of 3*." (same words, opposite truth)
19. "Says price isn't an issue. Third time she's asked for a cheaper version."
20. "Will discuss with husband." (early: neutral) / "Still discussing w/ husband. v4 sent. LM." (late: stall)
21. "worried abt safety in Kenya after news. reassured. she seemed ok?"

Corporate trips and events:

22. "RFP rec'd via agency for incentive, 40 pax, Cape Town + Sabi Sand, Mar. 4 suppliers bidding. Client
    decision by procurement 15th. DDR not relevant. Need costing by Wed."
23. "Site visit done w/ event mgr. Loved the boma for gala dinner. F&B min ok. Contract out, legal reviewing."
24. "Event cancelled - company restructuring, whole offsite on hold. Not our fault."
25. "Co. wants 120 delegates, 3n, $900 pp all in incl intl flights. Told them not possible. They're 'checking
    other options'."

## Loss reasons

Mapping to CONTEXT terms: **never a real buyer** (the lead was poor), **could not reach them** (may be the
handling, may be the lead; the notes decide), **price**, **timing**. "Chose a competitor" and "availability"
do not fit the four CONTEXT examples cleanly; mapped below as the nearest and flagged in open questions.

All shares are of lost leads that have a reason, unless stated. Shares do not need to sum to 100 at any
end; the profile should normalise.

| reason (as CRMs word it) | meaning in CONTEXT terms | share low–high | confidence | source |
|---|---|---|---|---|
| No response / no reply / unable to reach | could not reach them | 20–50% | estimated (SafariBookings: 1–2 of 4–5 non-bookings never reply; 1/5 to 2/4) | [SafariBookings](https://help.safaribookings.com/hc/en-150/articles/30458407229597-Ensuring-the-Legitimacy-of-Quote-Requests) |
| Price / too expensive / budget too low | price (if budget was realistic for the trip asked) or never a real buyer (if budget could never buy it) | 15–35% | guessed | list values: [Event Temple](https://support.eventtemple.com/en/articles/12824397-how-to-add-lost-reasons), [HVS](https://www.hospitalitynet.org/opinion/4037801.html); share: none |
| Chose a competitor / booked with another operator | price (lost on the offer; the lead was real) | 10–25% | guessed | Event Temple; [Aspire Travel Club](https://www.aspiretravelclub.co.uk/news/agency-calls-for-honesty-from-clients-following-rise-in-customers-booking-independently) |
| Booked direct with lodge / DIY / OTA | price (lead real, went round the operator) | 2–10% | guessed | Aspire Travel Club (anecdote) |
| Postponed / not this year / travel plans changed | timing | 10–25% | guessed | Event Temple ("project on hold", "delayed decision") |
| Dates not available / camp full / venue unavailable | timing (the advertiser's denial, not the lead's) | safari 3–10%, events 5–20% | guessed | Event Temple; [setupmyhotel](https://setupmyhotel.com/hotel-sop-standard-operating-procedures/sales-and-marketing-sop/sop-sales-and-marketing-lost-business-or-turnaways/) (denials) |
| Just browsing / research only / not serious / fake or spam | never a real buyer | 5–20% | guessed | SafariBookings legitimacy page (fake requests exist); no share |
| Destination concerns (safety, health, malaria, visa) | timing-like; usually a real buyer who backed out | 1–5% | guessed | [HVS](https://www.hospitalitynet.org/opinion/4037801.html) (security, climate as group reasons) |
| Cancelled / company on hold / restructuring (corporate) | timing | MICE 5–15%, leisure ~0% | guessed | Event Temple |
| Space or product unsuitable (capacity, rooms, wrong style of trip) | never a real buyer for this advertiser (poor fit), not poor in general | 2–10% | guessed | Event Temple; HVS (capacity) |
| Other / unidentified | unknown | 5–30% | guessed (HVS says "other" is often the majority in hotel lost-business databases, so the high end could be higher for events) | [HVS](https://www.hospitalitynet.org/opinion/4037801.html); Event Temple |

## Numbers for the profile

| number | low–high | confidence | working / source |
|---|---|---|---|
| Lost leads with no reply as share of all lost leads | 20–50% | estimated | SafariBookings: 4–5 of 5–6 requests do not book, 1–2 of those never reply; 1/5 = 20%, 2/4 = 50% |
| Lost leads with blank loss reason | 15–50% | guessed | HubSpot and Pipedrive default to free text (blank allowed); Event Temple lists "no reason provided" as an option |
| Lost leads with reason "other" / unidentified (of those with a reason) | 5–30% | guessed | HVS: often the largest value in hotel databases |
| Recorded loss reason differs from the Hidden truth | 20–60% | guessed | Clozd vendor claim (~60% wrong, unsourced); HVS on misuse of "lost to competitor"; Revenue.io on "price" as default |
| Most common wrong reason when wrong | price, then no response | guessed | Revenue.io, HVS |
| Loss reasons written as free text rather than picklist | 20–100% of advertisers' exports | guessed | HubSpot, Pipedrive defaults; hospitality tools admin-defined |
| Leads with at least one note, among leads with a Contact attempt | 50–90% | guessed | proposal work forces written records; attempts-only leads often have none |
| Leads with at least one note, among Neglected leads | 0–5% | guessed | none by definition; a few systems add an auto-note on intake |
| Leads with at least one note, among leads reaching Engaged or later | 85–100% | guessed | itinerary and quote work is logged as emails |
| Notes per lead (leads with any note): lost early | 1–3 | guessed | |
| Notes per lead: reached Proposal | 3–12 | guessed | itinerary versions, follow-ups |
| Note length, short notes (most notes) | 2–25 words | guessed | call-outcome shorthand |
| Note length, discovery-call notes | 40–200 words | guessed | |
| Logged emails pasted in full | 10–40% of notes, 80–400 words | guessed | |
| Notes containing at least one abbreviation | 30–70% | guessed | |
| Notes with a typo or misspelt place name | 5–20% | guessed | |
| Follow-up attempts before closing as no reply | 2–4 over 1–3 weeks | estimated | SafariBookings advises follow-ups at +3 and +5 working days after the quote |

All counts and shares come from synthetic data and must be labelled "on simulated data" once generated.

## Open questions

1. CONTEXT's **Loss reason** examples are price, timing, never a real buyer, could not reach them. Where do
   "chose a competitor", "booked direct" and "dates not available" (the advertiser's own denial) sit? Mapped
   here as price, price and timing respectively; needs a decision.
2. "Budget too low" is price when the budget was realistic and "never a real buyer" when it could never buy
   the trip asked for. Should the generator plant that split in the Hidden truth, with the recorded reason
   always saying "price"?
3. Should **Sales notes** on a **Neglected lead** ever exist (an intake auto-note such as "web enquiry
   received")? If so they must not count as a Contact attempt.
4. No safari-specific CRM documents a lost-reason list. A real advertiser's export, or a call with a safari
   operator, would replace most of the guessed shares above.
5. The SafariBookings pages returned 403 to direct fetch; their content was read through a search-engine
   extract. Someone should open them in a browser to confirm the wording.
6. Should notes be written in more than English (operators in South Africa, Kenya, Germany, the Netherlands
   often write in their own language)? Not researched here.
