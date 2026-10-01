# What in an enquiry predicts a booking

Research for the planned-hospitality **Industry profile** (issue #4): what in a **Lead** makes a won **Outcome**
more or less likely, how big each effect is, and which effects are not additive. Written from outside sources
only, with no knowledge of how Emva's model works.

Confidence labels follow decision 0007 and the [README](README.md): **sourced**, **estimated** (working shown),
**guessed** (no usable source, flagged). Where a source says "conversion" it means a won Outcome; this file uses
"booking rate" or "won" for it, as `CONTEXT.md` asks.

## Summary

- **Hard evidence is thin.** One peer-reviewed study models which quote requests become bookings
  (Runggaldier et al. 2023, one Italian 4-star hotel, 57,054 requests, 8.62% booked). Everything safari- or
  MICE-specific is operator reports, platform help pages, trade press or vendor marketing. Almost every
  planted-effect *size* below is therefore **guessed** or **estimated**. Only the *direction* and *form* of
  most effects have a source.
- **The strongest predictors in the one study are timing, source and origin**: days before arrival (importance
  0.31), country (0.20), source of business (0.12) and stay length (0.12). Booking rates by source ran from 1%
  to 91%.
- **Practitioners agree on these things**:
  - a budget below the product's floor almost never books (a threshold, not a slope);
  - peak-season safaris need 9–18 months' notice, so a short lead time works in green season and fails in peak
    (lead time × season);
  - referrals and repeat clients book far more often than paid or social leads;
  - fast responses matter.
- **Response speed is the best-documented effect, but it is advertiser behaviour, not lead quality.** The
  famous numbers (21× for 5 vs 30 minutes; 7× for under 1 hour vs later) measure *contact* and
  *qualification*, not won bookings. The MIT study says outright that it "did not address close ratios". The
  Telfer study found a non-monotone optimum at 10–60 minutes. In this repository that belongs to the
  **Lead simulator**'s handling, with an interaction on lead quality, not to the lead.
- **A trap is well supported**: in the one study, country and enquiry language are among the strongest
  predictors (English speakers 21% booked vs German 7%). Those are near-proxies for protected traits. The
  proposal plants a country-of-residence group that shifts **Intent signals** (budget, lead time) but has
  **no** effect once they are known. A model that leans on it is wrong.
- **Proposed**: 12 planted effects. Eight are not additive (thresholds, interactions, inverted-U shapes, a
  change over time, and a signal that only means something when a form field is optional).

## Evidence

### Base rates (context for the effect sizes)

| what | rate | confidence | source |
|---|---|---|---|
| Hotel quote requests (RFQ) that booked, Italian 4-star, 2014–2019 | 8.62% (4,919 of 57,054) | sourced (peer-reviewed) | [Runggaldier et al. 2023, doi:10.20867/thm.29.1.3](https://hrcak.srce.hr/296681) |
| Safari marketplace quote requests that book | about 1 in 5–6 (17–20%); about 20% of requesters never reply | sourced, via search snippet (page behind a bot check, not read in full) | [SafariBookings help: Quote Requests](https://help.safaribookings.com/hc/en-150/sections/16984839720349-Quote-Requests) |
| Tailor-made *proposals* (not enquiries) that book, Tourwriter platform | 42.4% benchmark; 58% at one DMC | sourced, **vendor marketing** | [Tourwriter: Bonheur Voyages](https://www.tourwriter.com/?p=22612), [Tourwriter: Tailormade 42%](https://www.tourwriter.com/?p=20942) |
| Tour-operator quotes that book, worked example | 30% (75 of 250) | **illustrative example, not data** | [Tourwriter: conversion rate and cost of sale](https://www.tourwriter.com/?p=2959) |
| Hotel group RFP leads: share of hotels booking ≤10% of inbound RFPs | 61% of about 200 webcast respondents | sourced, **vendor poll**, via search snippet | [Knowland Buzz vol. 3](https://www.knowland.com/wp-content/uploads/2019/08/knowland-buzz-vol-3.pdf) |
| Couples' venue enquiries before booking | enquire with 5 venues on average, visit 4 | sourced (survey of about 12,000 couples) | [The Knot / WeddingPro venue report](https://pros.weddingpro.com/report/the-knot-real-weddings-venue-report/) |

The stage at which a rate is measured matters: an enquiry, a quote request, a proposal and an RFP are different
**Stages**. Base rates belong in `cycle-and-deal-size.md`. They appear here only to keep the multipliers below
plausible.

### 1. Budget against package price

- Luxury advisers quote a floor of about **US$800–1,000 per person per day** for a luxury safari, and politely
  drop clients whose budget is "drastically different" unless they "seem willing to come up". This is
  practitioner advice, via search snippets; the article returned 403
  ([Travel Market Report, Ask-an-Advisor](https://travelmarketreport.com/retail-strategies/articles/ask-an-advisor-balance-between-my-conscious-clients-and-maximizing-my-income)).
- "Won't talk about budget / unrealistic budget" is the first of six tire-kicker signs in
  [Travel Market Report, 6 Signs a New Client Might Be a Tire Kicker](https://travelmarketreport.com/articles/6-Signs-a-New-Client-Might-Be-a-Tire-Kicker).
  This is anecdote from three agency owners, via snippet.
- Go2Africa: average safari budget per person sharing was about **$6,500 (2023), $7,500 (2024) and $8,625
  (2025)**. "Medium-high" budget enquiries rose from 36% to 59% in one year
  ([State of Safari 2025, PDF](https://www.go2africa.com/wp-content/uploads/2026/03/State-of-Safari-2025.pdf)).
  This is operator data, but it says nothing on which budgets book.
- **Form**: practitioners describe a *threshold* relative to the product's tier, not a slope. Nothing found on
  whether budgets far *above* the floor book more often. **Guessed**: no extra lift (saturation).

### 2. Dates, lead time and season

- **Lead time to travel** (days before arrival) is the single most important feature in Runggaldier et al.
  (importance 0.312). Booked requests were made on average about 8 days *closer* to arrival (49.3 vs 57.8
  days). This is a hotel, not a safari, and the paper reports means, not shape.
- Operator guidance on how far ahead to book ([Rhino Africa](https://blog.rhinoafrica.com/2023/07/27/how-far-in-advance-should-i-book-my-african-safari)):

  | where and when | book ahead |
  |---|---|
  | most safaris | 9–12 months |
  | Botswana | 12–18 months |
  | Kenya and Tanzania Migration (June–October) | at least a year |
  | Kenya outside the Migration | 6–10 months |
  | Rwanda | at least 4 months |
  | South Africa peak (Dec–Jan) | under 9 months is "extremely challenging" for availability |

  Yellow Zebra says 12–18 months for the Migration peak
  ([Yellow Zebra](https://yellowzebrasafaris.com/great-migration/)). These are operator content (also marketing),
  but consistent across sources.
- The booking window moves over time. Go2Africa reported booking lead time going from about **6 weeks (2022)
  to 19 weeks (2024)**
  ([Tourism Update, 6 March 2025](https://www.tourismupdate.com/article/bigger-budgets-longer-lead-times-go2africa-reveals-safari-insights)),
  and "booking windows have extended" again in 2025 (State of Safari 2025).
- Enquiries by travel month (State of Safari 2025): shoulder months (Apr, May, Sep, Oct) were **38%** of
  enquiries and Jun–Aug **34%**. Enquiries *arrive* mostly in January, while searches peak in July–August
  ([State of Safari 2024](https://www.go2africa.com/african-travel-blog/state-of-safari-2024), via snippet).
- **Form**: for safari, lead time and season interact. A short lead time is fine in green season, fails for
  peak because camps are full, and a very long or open horizon looks like a "dreamer". That makes it
  non-monotone (inverted U), with the peak's position depending on season. The interaction is **estimated**
  from the operator guidance. The sizes are **guessed**.
- **Specific dates vs "sometime next year"**: no quantified source found. The tire-kicker and qualification
  advice treats vague timing as a warning sign (anecdote). **Guessed.**

### 3. Lead source, repeat clients and referrals

- Source of business is the third most important feature in Runggaldier et al. Booking rates ranged from
  **1% in one category to 91% in another** (categories anonymised). Leads with unknown origin booked at **1%**.
  Sourced, but the categories cannot be mapped onto web, referral, agent and so on.
- Unsourced vendor ranges: referrals 25–40%, past customers 20–35%, organic 15–25%, paid search 10–18%, OTAs
  8–15%, social 5–12%
  ([Rework, travel lead generation](https://resources.rework.com/libraries/travel-tour-growth/travel-lead-generation-overview)).
  The page cites no data. **Vendor content, treat as guessed.**
- "Probability of selling to an existing customer 60–70%, to a new prospect 5–20%" is widely attributed to
  *Marketing Metrics* ([example citation](https://www.bullhorn.com/blog/selling-to-existing-customers/)). The
  original study could not be traced. **Unverified, treat as guessed.**
- Go2Africa: **25%** of 2025 enquiries came from travellers who had been to Africa before and 75% from
  first-timers (State of Safari 2025). Returning to *Africa* is not returning to *the operator*.
- Audley Travel describes agent-originated bookings as converting "really strong", with no figure
  ([Aspire, Audley targets agents](https://aspiretravelclub.co.uk/news/audley-travel-targets-increase-in-bookings-through-agents)).
  Anecdote.

### 4. Response speed (advertiser behaviour)

- **HBR 2011**: an audit of 2,241 US firms, plus 1.25 million leads at 42 firms. Firms that attempted contact
  within an hour were **7×** as likely to *qualify* the lead as firms an hour later, and **60×** as likely as
  firms waiting 24 hours or more ([Oldroyd, McElheran & Elkington, HBR](https://hbr.org/2011/03/the-short-life-of-online-sales-leads);
  figures via secondary summaries because the article is paywalled). These are firm-level comparisons, so firm
  quality is confounded with speed.
- **MIT / InsideSales 2007**: 6 companies, more than 15,000 leads, more than 100,000 dials. Calling within
  5 minutes rather than 30 gave **100×** the odds of contact and **21×** the odds of qualifying. The odds of
  qualifying fell more than 6× within the first hour. Wednesday and Thursday were best, and 8–9am and 4–5pm
  qualified 109–164% better than the worst slot. The study states it **"did not address close ratios"**
  ([study PDF](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf)).
  Vendor-run, not peer-reviewed.
- **Telfer (University of Ottawa) / VanillaSoft, preliminary**: 4 million web leads across 550 companies. The
  best response time was **10–60 minutes**, and win outcomes were **3×** more likely there than within the
  first 10 minutes or after an hour. Day and time of day had "relatively small impact". It took about 6 calls on
  average to win ([VanillaSoft](https://vanillasoft.com/resources/lead-conversion-study-telfer)).
  Vendor-co-authored, preliminary, not peer-reviewed. It is the only source with a *non-monotone* speed effect.
- Travel-specific: SafariBookings recommends replying within 4 hours (help page, via snippet). Tourwriter
  claims "quicker wins over cheapest price" and "80% of sales are made after 8 or more follow-ups" (vendor
  marketing, no source given). Tripleseat: 77% of consumers rate venue responsiveness highly important, from
  a survey of stated preference
  ([Tripleseat](https://tripleseat.com/blog/venue-responsiveness-reigns-supreme-why-lightning-fast-communication-is-your-venues-secret-weapon/)).
- **Why speed should interact with lead quality** (estimated): an enquirer who has really decided shops several
  suppliers at once (couples enquire with 5 venues; SafariBookings requests go to several operators), so the
  first credible reply wins. A low-intent enquirer is not going to book with anyone, so speed cannot rescue
  them. No source measures this interaction directly. **Guessed size.**
- For this repository: whether and when the advertiser attempts contact is the advertiser's behaviour
  (`CONTEXT.md`, **Contact attempt**). The effect belongs in the **Lead simulator**'s handling model, recorded in
  the **Hidden truth**. A **Neglected lead**'s Outcome must stay unfinished, never planted as a lost lead.

### 5. Message length and specificity

- No travel source quantifies message length. One vendor analysis of 100,000 SMS threads found length "barely
  matters" between 50 and 500 characters, but it measured replies, not bookings, and was not about enquiries
  ([Closeable](https://blog.closeable.co/we-analyzed-100-000-texts-with-customers-heres-what-converts/)).
  Vendor content.
- Go2Africa: **82%** of 2025 enquirers arrived with a destination already chosen, up from 65% in 2022. It
  attributes this partly to LLM-assisted research (State of Safari 2025). Specificity is therefore rising over
  time, so a fixed "specific = good" cut-off would drift.
- **Form** (guessed): an inverted U. A one-line enquiry ("price for safari?") does worst. A specific enquiry
  (dates, parks, camps, occasion) does best. An extremely long, wish-list enquiry (many countries, no budget,
  open dates) falls back somewhat. That is the "dreamer" the task names; practitioners describe the type,
  but no number was found.

### 6. Party size and trip type

- Runggaldier et al.: booked requests had "slightly lower" average numbers of adults and children and stays
  **about 0.8 nights shorter** (5.0 vs 5.8). Sourced, but for a hotel.
- Go2Africa 2025 enquiry mix: couples **46%**, families **28%**, solo **16%**, friends **10%** (State of Safari
  2025). No booking rates by type.
- Honeymoons: demand is reported as growing (African Travel Inc. +20% in romantic-safari requests,
  [TravelPulse](https://www.travelpulse.com/news/tour-operators/african-travel-inc-launches-romantic-safaris-series)),
  but no source gives honeymoon booking rates. **Guessed**: a fixed wedding date makes timing concrete, which
  is plausibly the mechanism.
- MICE / corporate: no source found for booking rates by group size. Group size sets the **Deal value**
  (`cycle-and-deal-size.md`) more than the chance of winning. **Guessed.**

### 7. Corporate and MICE: decision-maker and broadcast RFPs

- 61% of hotels in a Knowland webcast poll booked 10% or less of inbound RFPs. Knowland's advice is to get
  "ahead of the RFP" (vendor poll, about 200 respondents, via snippet;
  [Knowland Buzz vol. 3](https://www.knowland.com/wp-content/uploads/2019/08/knowland-buzz-vol-3.pdf)).
- Cvent's free tier lets a planner send one RFP to up to 10 venues, and unlimited on Pro
  ([Cvent Supplier Network pricing](https://www.cvent.com/en/supplier-venue/cvent-supplier-network/pricing)).
  Broadcast RFPs are therefore structurally competitive. No source gives an average number of venues per RFP.
- Doug Kennedy (hotel sales trainer) urges hotels to measure booking rate by lead source, because platforms
  (Cvent, The Knot, CVBs) flood them with leads, but he gives no figures
  ([Hotel Online, 18 July 2022](https://www.hotel-online.com/news/hotel-sales-teams-need-to-measure-conversion-of-inbound-leads-by-source)).
- Incentive Research Foundation (IRF): "leadership approval" is the largest decision factor, and lead times
  were shortening in 2023 ([Prevue, IRF 2023 Trends](https://www.prevuemeetings.com/meeting-planner-resources/incentive-travel-merchandise/incentive-travel-2023-increased-demand-and-increased-challenges/)).
  This supports *decision-maker vs researcher* as a real distinction, but gives no size.
- B2B buying committees involve 4.6–6.0 decision-maker titles per deal (survey;
  [Belkins](https://belkins.io/blog/b2b-buying-committee-study)). Vendor content.

### 8. Time of submission, destination, price changes

- **Time of submission**: the MIT study's day and time effects are about *calling*, not about submission
  (handling). Telfer found a small effect. No source shows that a lead submitted at 2am is a worse lead.
  **Not proposed as a lead effect.**
- **Destination**: South Africa, Kenya and Tanzania make up 64% of enquiries. Go2Africa notes "gorilla trekking
  bookings are rising despite softer enquiry signals" (State of Safari 2025): enquiry share is not booking
  rate. Permit-limited products such as gorilla permits plausibly behave like peak season (capacity). **Guessed.**
- **Price change over time**: the Maasai Mara non-resident fee rose to **US$200** in high season (July–December)
  from July 2024, with $100 in green season. Press reported travellers topping up existing packages and agents
  worried about switching to the Serengeti
  ([Nation](https://nation.africa/kenya/news/peak-tourism-rising-costs-operators-protest-raft-of-new-levies-as-state-targets-sh1trn-in-earnings-5518432),
  [The Star](https://www.the-star.co.ke/news/realtime/2024-03-19-is-kenya-losing-safari-allure-to-tanzania)).
  Against that, an operator told Tourism Update the fees had not "materially impacted enquiries" at its camps
  ([Tourism Update](https://www.tourismupdate.com/article/operators-weigh-in-on-kenyas-increased-park-fees)).
  The evidence is mixed. A plausible reading (**guessed**): the price rise hurts budget-tight leads and barely
  touches luxury ones. That is a time-dated change that interacts with budget.

### 9. Prohibited inputs and the proxy trap

- Runggaldier et al. found country code (importance 0.20) and enquiry language very predictive:
  - English speakers booked at **21%**, German at 7% and Italian at 9%;
  - Germany and Italy booked at 18%, Croatia at 30%.

  Country of residence, nationality and language are near-proxies for ethnicity and national origin. Whether
  country of residence is a **Prohibited input** must be decided in the profile; see the open questions. The
  paper does not ask *why* origin predicts. The obvious candidates are budget, distance and lead time, which
  are **Intent signals**.
- Go2Africa also reports spend by booking country (State of Safari 2025), so origin and budget correlate in
  safari too.
- Signals that correlate with age, such as honeymoon, family with young children, or "retirement trip", are
  trip type or occasion. Those are **Intent signals** and allowed under decision 0008 even though they
  correlate with age. Names, titles (Mr/Mrs/Dr), dates of birth and passport nationality are not.
- **The trap, supported by this evidence**: plant a country-of-residence group (and the enquiry language that
  goes with it) that shifts the *distribution* of stated budget and lead time, but has **zero** effect on the
  Outcome once budget, lead time and season are known. In the raw data the group looks very predictive, as in
  Runggaldier et al.; conditionally it is noise. A model that uses it, directly or through a near-proxy such as
  phone country code, email domain country or a name, fails the proxy check and the fairness report. It also
  generalises worse when the group mix shifts. Go2Africa reports the source-market mix changing year on year.

## Proposed planted effects

Sizes are multipliers on the odds of a won Outcome relative to a stated reference, unless the table says
otherwise. They are given as low–middle–high, the three ends the generator must run at. "Visible when" says
whether a lead carries the signal at submission (**Submit score**) or only once a **Stage** or CRM update
reveals it.

| # | effect | form | size low – middle – high | visible when | confidence | source |
|---|---|---|---|---|---|---|
| 1 | **Budget floor.** Stated budget per person per night below the floor of the tier the lead asked for (e.g. luxury about $800–1,000 pppn) | **threshold**, tier-dependent | below 50% of floor: OR 0.03 – 0.10 – 0.25 vs at or above floor. 50–100% of floor: OR 0.30 – 0.50 – 0.80. Above floor: 1 (no extra lift above 1.5× floor) | Submit | floor **estimated** (practitioner, search snippet only); multipliers **guessed** | §1; TMR Ask-an-Advisor (not read in full: 403 on 2026-10-01); TMR tire-kicker |
| 2 | **No budget stated.** Budget field empty or "flexible" | additive (but read with #1: missing is not "below floor") | OR 0.50 – 0.70 – 0.90 vs a stated budget at or above floor | Submit | **guessed** (direction: anecdote) | §1; TMR tire-kicker |
| 3 | **Lead time × season.** Months from enquiry to travel, by travel season (peak = Jul–Oct East Africa, Botswana and peak SA Dec–Jan; shoulder; green) | **interaction + inverted U** | Peak with under 4 months' lead: OR 0.20 – 0.40 – 0.70 (availability). Green or shoulder with under 4 months: OR 0.8 – 1.0 – 1.2. Any season with over 18 months or "next year sometime": OR 0.40 – 0.60 – 0.85. Best band: peak 6–14 months, green 1–8 months | Submit (dates on form) | shape **estimated** from operator lead-time guidance; sizes **guessed** | §2; Rhino Africa; Yellow Zebra; Runggaldier (closer = better on average) |
| 4 | **Date specificity.** Exact dates > month > season/year > none | ordered, additive | none vs exact: OR 0.35 – 0.55 – 0.80; month vs exact: OR 0.75 – 0.90 – 1.0 | Submit | **guessed** | §2 (qualitative only) |
| 5 | **Lead source.** Referral / repeat / agent vs organic vs paid search vs paid social | additive on log-odds | referral vs paid search: OR 1.5 – 2.5 – 4.0; paid social vs paid search: OR 0.4 – 0.6 – 0.9; organic vs paid search: OR 1.0 – 1.4 – 2.0 | Submit if captured (UTM or "how did you hear"); often missing or messy | **estimated** (ratios from vendor ranges: referral 25–40% vs paid 10–18% gives 1.4–4.0×; vendor ranges unsourced, so effectively guessed); spread **sourced** (Runggaldier 1–91%) | §3; Rework; Runggaldier |
| 6 | **Repeat client of this advertiser** | additive, *and* weakens #1 (repeat clients' budget statements are trusted) | OR 2.0 – 3.5 – 6.0 | Submit only if the form asks; otherwise at Engaged (CRM match) | **guessed** (60–70% vs 5–20% claim untraced) | §3; Marketing Metrics (unverified) |
| 7 | **Response speed × lead quality** (handling, not lead). Time to first **Contact attempt** | **interaction**, non-monotone near zero | High-quality leads (top third of hidden quality): first attempt within 1h vs over 24h, OR 1.5 – 2.5 – 4.0. Low-quality leads: OR 1.0 – 1.1 – 1.3. Optional dip: under 10 min no better than 10–60 min | Stage (Contact attempted); lives in the Lead simulator | direction **sourced** (HBR and MIT on contact or qualify, not won; Telfer on win outcomes, 3× at 10–60 min, the source of the dip); shrinkage to won and the interaction **guessed** | §4; HBR; MIT; Telfer |
| 8 | **Message length and specificity** (words; named parks, camps or occasion) | **inverted U** | under 15 words vs 40–200 specific words: OR 0.40 – 0.60 – 0.85. Over 400 words with no budget and over 3 countries ("dreamer") vs 40–200: OR 0.55 – 0.75 – 0.95 | Submit (text; a Judgment may read it) | **guessed** | §5 (qualitative only) |
| 9 | **Party size × trip type** | **interaction** | Leisure over 6 travellers vs 2: OR 0.50 – 0.70 – 0.90. Family with children vs couple: OR 0.85 – 1.0 – 1.15. MICE: no effect on the chance of winning (size goes to Deal value) | Submit | direction **sourced** (hotel: booked parties slightly smaller); sizes **guessed** | §6; Runggaldier |
| 10 | **Phone number given, only when optional** | **context-dependent**: signal exists only where the form makes phone optional; where required, no signal | phone given vs not: OR 1.2 – 1.5 – 2.0 (optional field); 1.0 (required field) | Submit | **guessed** (form-tradeoff case studies show the selection mechanism, not its size) | [Vital Design case study](https://vitaldesign.com/phone-number-form-field-case-study/), [Disruptive Advertising](https://disruptiveadvertising.com/landing-pages/optional-form-fields) |
| 11 | **MICE: broadcast RFP vs direct, and decision-maker vs researcher** | **interaction**: decision-maker lifts direct enquiries more than broadcast RFPs | broadcast platform RFP, overall win rate 4% – 8% – 15%; direct enquiry 15% – 25% – 40%; decision-maker (title or "approved budget") on a direct enquiry OR 1.5 – 2.0 – 3.0, on a broadcast RFP OR 1.0 – 1.3 – 1.6 | Submit (source, title, wording); role often confirmed only at Qualified | broadcast rate **estimated** (61% of hotels ≤10%; Cvent caps of 10+ venues per RFP imply a base of 1-in-N); others **guessed** | §7; Knowland; Cvent |
| 12 | **Dated price rise × budget** (e.g. a park fee or rate rise on a set simulated date) | **changes over time, interaction** | after the date, leads within 1.0–1.3× of the floor: OR 0.55 – 0.75 – 0.90; leads over 1.5× floor: OR 0.95 – 1.0 – 1.0; the floor itself moves up by the rise | Submit (but the model must notice the break) | event **sourced** (Mara fee to $200 from July 2024); effect **guessed**, evidence mixed | §8; Nation (amount and seasons, no date); [Governors' Camp](https://governorscamp.com/travel-planning/important-changes-to-masai-mara-park-fees/) (date); Tourism Update |
| T | **Proxy trap: country-of-residence group** | **confounded, zero conditional effect** | Group A vs B: budget distribution median 1.3 – 1.6 – 2.0× higher, lead time 1.2 – 1.5 – 2.0× longer; **direct effect on Outcome = 0** at every end | Submit (country field, phone prefix, language) | that origin looks predictive: **sourced** (Runggaldier: importance 0.20, 7–30% booking rates by group); mechanism **guessed** | §9; Runggaldier; Go2Africa spend by country |

Not additive: #1 (threshold), #3 (interaction + inverted U), #7 (interaction), #8 (inverted U), #9
(interaction), #10 (context-dependent), #11 (interaction), #12 (time-varying interaction), and T (confounded).
#2, #4 and #5 are additive. #6 is additive with a modifier on #1.

Not proposed: time of submission as lead quality (no evidence; see §8) and destination popularity on its own
(enquiry share ≠ booking rate; capacity is covered by #3).

## Open questions

1. **Is country of residence a Prohibited input for planned hospitality?** It is not in `CONTEXT.md`'s list
   (age, gender, ethnicity, religion, disability, precise postcode, name-based inference). It is a near-proxy
   for national origin and ethnicity, but it also sets flight cost and time zone, which matter commercially.
   The trap (T) works either way, but the profile's Prohibited-input list needs a ruling. The same goes for
   enquiry language and phone country code.
2. **Response speed (#7)**: confirm that it lives only in the Lead simulator's handling and the Hidden truth,
   and is never a property of the lead in the generated export. Should the under-10-minute dip (Telfer) be
   planted at all, given one preliminary vendor source?
3. **Which form fields does the profile assume?** #5, #6 and #10 depend on whether the enquiry form asks for
   source, repeat status and an optional phone (`enquiry-forms.md`).
4. **Ranges for the budget floor by tier** (#1) should come from the deal-size research (`cycle-and-deal-size.md`)
   so the two files agree. Only the luxury floor (about $800–1,000 pppn) has a source here.
5. **No source measured any interaction directly.** Every interaction's *size* is guessed. If the trust gate is
   to be passed "at every end", the low ends here are deliberately weak (near 1) so a model is not tested only
   on loud effects.
6. **MICE is the weakest area.** No source found for corporate-incentive booking rates by decision-maker, lead
   time or group size. Consider asking a DMC or incentive house for anonymised rates.
7. **Runggaldier et al. full text** could not be read (the PDF is behind a bot check). The numbers above come
   from the journal's abstract page. The non-monotone shape of lead time in that data is unknown.
