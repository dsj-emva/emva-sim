# Sales-cycle length, deal sizes and stage rates (Planned hospitality)

Research for the planned-hospitality **Industry profile** (issue #4). Three segments, kept apart throughout:

- **(a) Tailor-made safari (leisure)**: Africa tour operators and travel designers selling to UK, US and EU travellers.
- **(b) Corporate incentive trips**: reward trips for qualifying staff, sold by incentive houses and destination
  management companies (DMCs).
- **(c) Corporate events**: meetings, conferences and offsites sold by agencies, DMCs and venues.

Confidence follows decision 0007 (see [README](README.md)): **sourced**, **estimated** (working shown) or
**guessed** (no usable source). Researched 2026-10-01 with web search only; several primary reports (Travel Weekly,
Phocuswright, the full Incentive Travel Index, SafariBookings' help centre) are paywalled or blocked. Where a figure
came only from a search-result snippet of a page that could not be opened, it says so.

"Booking rate" below means the share of **Leads** whose **Outcome** is won. Sources call this "conversion"; this
file uses that word only when quoting them.

## Summary

- **Good primary sources are scarce for stage rates.** The only operator-wide figure for safari leads is
  SafariBookings' "about 6 quote requests per confirmed booking" (≈17%), and those leads come from a marketplace
  where travellers ask several operators at once. All other stage-rate figures are vendor marketing or targets, so
  the ranges have to be wide.
- **(a) Safari**: the cycle from first website visit to deposit is short and getting longer: 14.9 days (2024)
  and 22.4 days (2025) at Safari.com, with 2.2 and then 3.8 interactions, counting only bookings made within 90 days.
  Travel is about 6 months after booking (Rhino Africa: 186–190 days). Spend is about $8,600 per person sharing
  (Go2Africa 2025). Typical trips are 7–10 days. Parties are mostly couples (46%) and families (28%). Lodge rates
  run from about $200 to $5,000+ per person per night.
- **(b) Incentives**: about $5,100 per person on average (Incentive Travel Index 2025; North America $6,000, Europe
  $3,200) over 2–4 nights. Most programmes have fewer than 200 attendees. Booking lead time is 6–18 months.
- **(c) Events**: about $169 per attendee per day (CWT/GBTA forecast for 2025). RFPs are spread evenly across sizes
  from fewer than 25 to more than 200 attendees. Planners source 4–6 months ahead. In multi-bid RFP channels the
  share of RFPs won is very low (hotels win 3–7%).
- **Deal value is right-skewed in every segment.** A lognormal fits the evidence for (a), with σ of about 0.7–1.0
  (estimated). Corporate deal values span two orders of magnitude because group size varies so much.
- **Not found**: lead volume per month for a mid-size operator, and itinerary revisions per won deal. Both are
  guessed or estimated from guessed inputs.

## 1. Sales-cycle length

### (a) Tailor-made safari

**Enquiry to deposit (the Won stage).**

- Safari.com analysed "several thousand" confirmed bookings (Jan 2024–Jun 2025). From first website visit to
  deposit payment, counting only bookings made within 90 days, it found **14.9 days with 2.2 interactions
  (Apr/May 2024)** and **22.4 days with 3.8 interactions (Apr/May 2025)**. The report calls this "decision drag".
  Source: [Safari.com Safari Travel Report 2025](https://www.safari.com/blog/safari-travel-pulse-2025). **Sourced**,
  with two caveats. The clock starts at the first website visit, not at the enquiry, so the time from enquiry is
  probably a few days shorter. The 90-day cut also leaves out the long tail.
- Other operators also report slower decisions. African Bush Camps sees travellers "taking longer to commit" and
  more shopping around, including "multiple agents making enquiries for what appears to be the same underlying
  client" ([Tourism Update](https://www.tourismupdate.com/article/safari-interest-strong-but-bookings-harder-won)).
- Vendor content (no source cited) puts luxury ($8k+) quote-to-booking at "18–30% over 30–60 days" and says to
  track luxury bookings over 90 days
  ([Rework, vendor marketing](https://resources.rework.com/libraries/travel-tour-growth/booking-conversion-metrics)).
- An affiliate publisher says planning takes "4–12 weeks from first research to confirmed booking", with quotes
  compared in weeks 5–8 ([African Safari Mag, affiliate; earns referral fees](https://www.africansafarimag.com/plan-african-safari/safari-booking-explained)).
- Most operators place a provisional hold before the deposit. Go2Africa holds for about 2 weeks, then takes a 30%
  deposit on the land package and 100% of flights; the balance is due 60 days before travel
  ([Go2Africa booking process](https://www.go2africa.com/african-travel-blog/how-it-works-our-booking-process)).
  The affiliate guide puts typical deposits at 25–50%, with the balance due 60–90 days out. A provisional hold is a
  natural **Milestone** inside Proposal.

**Estimate for the profile.** Days from Submitted to Won, among won leads:

- Median: 14–35 days, middle 21 (**estimated**). Safari.com's 15–22 days from first visit is truncated at 90 days.
  Allowing for the cut and for the extra days a visit takes to become an enquiry roughly offset, the median sits
  near 3 weeks. The 30–60 day vendor window is an upper anchor.
- Long tail: p90 of 60–180 days (**guessed**). Travellers who enquire 12–18 months before a peak season trip can
  hold off for months.
- Shape: right-skewed. A lognormal of days with median 21 and σ around 0.8–1.0 puts p90 at about 60–75 days
  (**estimated**). Use σ near 1.2 at the high end.
- Lost leads: most go quiet rather than refuse outright, so a Lost date mostly reflects how the advertiser cleans
  its sales system. That belongs to the neglect-and-mess topic.

**Booking lead time (deposit to travel).**

- Rhino Africa's average lead time on high-end safari bookings is **186–190 days**
  ([Tourism Update](https://www.tourismupdate.com/article/safari-interest-strong-but-bookings-harder-won)).
  **Sourced**.
- Operators' recommended booking windows: 9–12 months in general. Botswana: 12–18 months. Kenya or Tanzania for the
  migration: at least a year. Rwanda: at least 4 months
  ([Rhino Africa blog](https://blog.rhinoafrica.com/2026/07/23/how-far-in-advance-should-i-book-my-african-safari/)).
  These are advice, not measured behaviour, and they run longer than the measured average.
- Travel Weekly's advisor survey (cited in a search snippet; the page returned 403): the most common booking window
  is "between six months and one year before departure", cited by 38% of advisors (all trip types).
- Shorter windows are rising: UK luxury agents report tailor-made trips booked for departures "in just a few
  months", and some late January business departing in 2–4 weeks
  ([Aspire, Jan 2026](https://www.aspiretravelclub.co.uk/insight/peaks-unpacked-why-the-traditional-peak-selling-season-is-shifting-in-the-luxury-sector)).
- **Profile**: median 4–9 months, middle 6. Range 1–18 months, right-skewed with a bump at 12+ months for peak
  season and Botswana trips. **Estimated** from the above.

**Seasonality of enquiries (by month).**

- UK luxury agents: Designer Travel "takes 22% of its entire business for the year during January". At Carrier,
  "a third of its annual revenue" arrives in Q1
  ([Aspire](https://www.aspiretravelclub.co.uk/insight/peaks-unpacked-why-the-traditional-peak-selling-season-is-shifting-in-the-luxury-sector)).
  This covers all luxury travel, not safari only.
- For high-end safari, Rhino Africa's peak booking period is January–March, with January "brilliant" for
  conversion ([Tourism Update](https://www.tourismupdate.com/article/safari-interest-strong-but-bookings-harder-won)).
- Go2Africa (mostly US, Australian and UK enquirers): the lowest enquiry months are November and December. In 2025
  enquiries fell most noticeably in January and July
  ([Go2Africa State of Safari 2025](https://www.go2africa.com/african-travel-blog/state-of-safari-2025)).
  US-led demand may peak less in January than UK-led demand.
- **Profile**: monthly enquiry weight relative to the average month:
  - January: 1.3–2.0, middle 1.6 (**estimated**: 22% of a year in January is 2.6× an average month for Designer
    Travel, but that counts bookings, not enquiries, and is UK-only).
  - February–March: 1.1–1.3.
  - November–December: 0.6–0.8.
  - Rest of the year: about 0.9–1.0.

  The spread should be flatter for US-led advertisers (**guessed**).

**Seasonality of travel.**

- Travel months of Go2Africa's 2025 enquiries: shoulder months (April, May, September, October) **38%**, high season
  (June–August) **34%** ([Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025)). That
  leaves about 28% for November–March (**estimated**: 100 − 38 − 34).
- Safari.com: even its quietest months (November, February) reach 70% of peak occupancy
  ([Safari.com](https://www.safari.com/blog/safari-travel-pulse-2025)).
- Rates follow season. For example, Mombo charges $3,285 per person per night in November–mid-December and
  $5,040 in June–October 2026; the page (read 2026-10-01) lists no January–May rate
  ([Safari.com Mombo](https://www.safari.com/lodges/mombo-camp)). Season changes Deal value as
  well as when trips happen.

### (b) Corporate incentive trips

- **Lead time (booking to travel)**:
  - DMC GO (a DMC, vendor content): most programmes are booked 6–12 months ahead and up to 18 months for luxury or
    peak season. Small groups of 10–20 need 4–6 months; groups of 50+ need 8–12 months
    ([DMC GO](https://dmc-go.com/blog/how-far-in-advance-should-you-book-an-incentive-travel-program/)).
  - Another planner says 12–18 months for groups of 20+, 18 months for 75+ rooms a night and 24 months for 150+
    rooms (search snippet,
    [Travel Squad](https://travelsquadvacations.com/journal/incentive-travel-planning-guide)).
  - **Profile**: median 6–12 months, middle 9; range 3–24 months. **Estimated**.
- **Enquiry to contract**: no source found. Incentive buyers usually send an RFP, shortlist suppliers, and may run a
  site inspection before contracting. **Guessed**: median 4–12 weeks, middle 6; tail to 6 months.
- **Seasonality**: no source found. **Guessed**: enquiries follow the corporate budget cycle, peaking in Q4 and Q1
  as the next year's programmes are planned. Travel avoids July–August and December. Use a flat profile at the low
  end.

### (c) Corporate events

- **Lead time**:
  - Cvent data for India in H1 2024 gives an average booking window of 118 days for new planners (search snippet;
    [Cvent/HSMAI deck](https://asia.hsmai.org/wp-content/uploads/sites/12/2024/07/presentation_presley-barretto.pdf)
    not read in full).
  - A Northstar survey of APAC planners (March 2025), shown in a Cvent deck: 77% "are sourcing between 4 and 6
    months" ahead ([Cvent at HSMAI Singapore 2025](https://asia.hsmai.org/wp-content/uploads/sites/12/2025/05/hsmai-commercial-conf-mice-cvent.pdf)).
  - **Profile**: median 2–6 months, middle 4; range 3 weeks to 18 months (large conferences). **Estimated** from
    APAC data; no UK, US or EU figure found.
- **Enquiry to contract**: Cvent says 80% of planners expect a reply to an RFP within four days
  ([Cvent press release](https://cvent.com/en/press-release/cvent-group-sourcing-volume-sets-new-record-2024)).
  Time to decide: no source found. **Guessed**: median 2–6 weeks, middle 3.
- **Seasonality**: no source found. **Guessed**: event enquiries dip in late July–August and late December.

## 2. Deal size

### (a) Tailor-made safari

**Price per person per night: published rates, 2026, USD per person sharing unless stated.**

| tier | property (operator) | rate | source |
|---|---|---|---|
| ultra-luxury | Mombo (Wilderness), Botswana | $3,285 (Nov–mid-Dec 2026) to $5,040 (Jun–Oct, festive). All-inclusive including drinks and activities | [Safari.com](https://www.safari.com/lodges/mombo-camp) |
| ultra-luxury | Singita Lebombo, Kruger | ZAR 51,660–60,470 per adult. About $2,800–3,500 at R17–19/$ (exchange rate assumed, not checked) | [Safari.com](https://www.safari.com/singita-lebombo) |
| ultra-luxury | Singita Serengeti House (exclusive-use villa, up to 8 guests) | 2026: $3,075 (Nov–mid-Dec) to $4,300 (May–Sep); 2027: $3,285 to $4,600 | [Safari.com](https://www.safari.com/singita-serengeti-house) |
| ultra-luxury | Singita Kwitonda, Rwanda; Singita Pamushana, Zimbabwe | $2,720–3,630; $2,380–3,130 (search snippet of Singita rate sheets) | [Singita library](https://library.singita.com/download/public/assets/17454796030125.pdf) |
| ultra-luxury | &Beyond Ngorongoro Crater Lodge | from $2,470. Closed Jan–Aug 2026 for refurbishment (search snippet) | [African Mecca rate page](https://www.africanmeccasafaris.com/travel-guide/tanzania/accommodation/ngorongoro/crater-rim/ngorongoro-crater-lodge/room-rates) |
| mid-market | Serengeti Kati Kati Camp, Tanzania | $196–237 full board. Excludes park fees (Serengeti about $83 a day) and vehicle and guide | [search snippet, safari.co.za](https://www.safari.co.za/pricing_Tanzania_Safari_Lodges-travel/serengeti-kati-kati-camp.html); park fee from [Atlasperk](https://atlasperk.com/intelligence/types/safari-tours/) |

Whole-trip pricing from tailor-made operators (land package including internal flights and transfers; excluding
international flights):

- Yellow Zebra Safaris, 6 nights per person
  ([Yellow Zebra](https://yellowzebrasafaris.com/us/your-first-safari/how-much-does-a-safari-cost/)):
  - Value: $5k–6k+ ("authentic tented camps or 4-star lodges").
  - Classic: $7k–8k+ (most popular).
  - Luxury: $13k+.
  - High season can reach $16k+ in Botswana.
- Yellow Zebra UK guide prices (GBP): 8 nights in Botswana from £4,983 (low season) to £8,726 (high season); 10 nights
  in Zambia from £13,751 to £16,658 (search snippet).
- Safari.com's packages run from about $1,000 per person per day ("value-oriented luxury") to $2,500+ per day
  ([Safari.com](https://www.safari.com/ngorongoro-crater-lodge)).

**Tiers for the profile.** All-in land price per person per night, **estimated** from the tables above. Yellow
Zebra's prices are divided by 6 nights. Lodge rack rates plus about 10–25% for flights, transfers and fees.

| tier | low | middle | high |
|---|---|---|---|
| mid-market | $300 | $550 | $900 |
| luxury | $900 | $1,300 | $2,000 |
| ultra-luxury | $2,000 | $3,000 | $5,000+ |

**Nights.**

- Go2Africa's 2025 enquiries: 10 days was most popular (35%), 7 days 22% (down from 26%). Trips shorter than 7 days
  showed the largest increase, and trips of 2+ weeks also grew
  ([Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025)).
- Safari.com's average trip length on confirmed bookings: 5.6 days (2024), 6.1 (2025), 7.3 (2026)
  ([Safari.com](https://www.safari.com/blog/safari-travel-pulse-2025)).
- **Profile**: 5–10 nights, middle 7. Spread from 3 nights (a safari add-on) to 21 nights. **Estimated**.

**Party size.**

- Go2Africa's 2025 enquiries: couples 46%, families 28%, solo 16% (up from 13%), friends 10%
  ([Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025)). **Sourced** for the mix.
- **Estimated** mean party size: 0.46×2 + 0.28×4 + 0.16×1 + 0.10×4 = **2.6**. This assumes a family is 4 and a
  friends group is 4, both **guessed** at 3–6. Range 2.3–3.0.
- **Profile**: party size is 1 (16%), 2 (46%), or 3–8 (38%). Large multigenerational and exclusive-villa groups go
  up to about 12 (**guessed** tail).

**Total trip value (Deal value).**

- Go2Africa's average spend per person sharing: **$6,500 (2023), $7,500 (2024), $8,625 (2025)**. "Medium-high"
  budgets were 59% of 2025 enquiries, up from 36%
  ([Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025)). **Sourced** (enquiry budgets,
  not booked values).
- **Estimated** mean Deal value per booking: $8,625 × 2.6 ≈ **$22,400**. Range $15k–30k: per-person spend of
  $7k–10k times a party of 2.3–3.0, less child discounts of about 50% at many lodges (Singita Serengeti House:
  children 2–16 typically 50%).
- Shape: a lognormal fits. Rates rise multiplicatively with tier and season, and value is party × nights × rate,
  a product of independent-ish factors, which gives a lognormal sum of logs. **Estimated** spread: 5th–95th
  percentile of about $5k (couple, mid-market, 5 nights) to $100k (ultra-luxury family, 10 nights).
  ln(100/5)/(2×1.645) ≈ **σ 0.9**; use 0.7–1.1. Then median = mean / exp(σ²/2) ≈ $22.4k / 1.5 ≈ **$15k** (range
  $10k–20k).
- Tail anchor: press coverage of a "$94K" quote for a 13-day honeymoon
  ([BoardingArea headline](https://boardingarea.com/?p=260595), not read in full).
- **Currency**: USD dominates. East African and Botswana camps quote USD; South African lodges quote ZAR, as Singita
  Lebombo does; UK operators quote GBP to clients, as Yellow Zebra does. **Profile**: Deal value in the operator's
  selling currency: GBP for UK, USD for US, EUR for EU advertisers.

### (b) Corporate incentive trips

- **Per person**:
  - Incentive Travel Index 2025 (IRF/SITE/Oxford Economics, 2,700 respondents): average **$5,100** (+4% year on
    year). North America **$6,000**, Europe **$3,200** (down 20%)
    ([MPI summary](https://www.mpi.org/blog/article/what-the-incentive-travel-index-2025-tells-us-about-the-future-of-incentive-travel);
    [Skift Meetings](https://meetings.skift.com/2026/06/26/the-key-incentive-industry-statistics-that-matter/)).
  - Prevue survey (382 planners): **$6,177** per person in 2023
    ([Prevue Incentive Trends 2024](https://www.prevuemeetings.com/wp-content/uploads/2024/01/Incentive-Trends-WP-2024.pdf)).
- **Nights**: Prevue reports that the most popular trip is 5 days / 4 nights (22%), then 3 days / 2 nights (21%);
  only 12% run 7+ days (same source). **Profile**: 2–5 nights, middle 4. **Sourced**.
- **Group size**:
  - Prevue: 58% of respondents average under 200 attendees; 15% plan programmes of 500+.
  - An incentive agency says groups are "typically 40+ people for agency engagement"
    ([Brightspot, vendor](https://brightspotincentivesevents.com/incentive-travel/average-cost-incentive-travel-program/)).
  - DMC GO cites small groups of 10–20.
  - **Profile** for an Africa or safari incentive seller: 10–150, middle 40. **Estimated**: safari camps are small,
    with "only a handful of suites" each
    ([Rhino Africa](https://blog.rhinoafrica.com/2026/07/23/how-far-in-advance-should-i-book-my-african-safari/)),
    so large groups split across camps or go to bigger lodges.
- **Per person for an Africa or safari incentive**: $5,000–12,000, middle $7,000. **Estimated**: above the
  $5,100–6,177 average because of long-haul air and lodge rates of $900+ per person per night, against 4-night
  programmes.
- **Total Deal value**: low 10 × $5,000 = $50k; middle 40 × $7,000 = **$280k**; high 150 × $8,000 = $1.2M.
  **Estimated**. Lognormal-ish with a wide σ (about 1.0–1.3), driven mainly by group size.
- **Currency**: USD for US buyers. GBP or EUR for UK and EU buyers (Europe's per-person spend is about half North
  America's).

### (c) Corporate events

- **Cost per attendee per day**: **$169** forecast for 2025, up from $155 in 2023
  ([CWT/GBTA forecast via Skift Meetings](https://meetings.skift.com/2024/09/26/rising-event-costs-to-challenge-2025-budgets/)).
  Amex GBT's 2026 forecast expects costs per attendee to rise further. Its measure excludes air ("total meeting
  budget divided by total planned attendees excluding air costs"; Amex GBT Meetings & Events Forecast 2026,
  [PDF copy](https://irp.cdn-website.com/f6c3a4cd/files/uploaded/ME-Forecast-2026.pdf)).
- **Group size** (Cvent Supplier Network RFPs, Singapore, Jan–Apr 2025): 0–25 attendees 23.6%, 26–50 20.6%, 51–100
  20.2%, 101–200 14.5%, 201+ 21.1%. The 24% of RFPs for 201+ attendees carried 81% of RFP value
  ([Cvent at HSMAI](https://asia.hsmai.org/wp-content/uploads/sites/12/2025/05/hsmai-commercial-conf-mice-cvent.pdf)).
  Median about 50–60 attendees (**estimated** from the cumulative shares: 44% are ≤50).
- **RFP value** (same deck): average RFP value $39k for Singapore-based planners and $255k for US-based planners
  sending RFPs to Singapore. These are hotel and venue values only.
- **Profile**: Deal value per event:
  - Low: 20 attendees × 1 day × $250 = $5k.
  - Middle: 60 × 2 × $400 ≈ $50k.
  - High: 300 × 3 × $600 ≈ $540k.

  **Estimated**. The per-day figures are above $169 because an agency or DMC sale bundles rooms, food and drink,
  and production; the $169 average includes small internal meetings. Strongly right-skewed (the Cvent value
  concentration above): lognormal σ about 1.2–1.5.

## 3. Stage rates

Canonical ladder: Submitted → Contact attempted → Engaged → Qualified → Proposal → Won (Lost can follow any stage).

### Evidence

| figure | what it measures | type | source |
|---|---|---|---|
| ~6 quote requests per confirmed booking ("RPB"); "one booking out of every five to six requests" | marketplace lead → Won, safari (≈17%) | platform statement (search snippet; page behind Cloudflare, not read) | [SafariBookings onboarding summary](https://help.safaribookings.com/hc/en-150/articles/20583096001949) |
| Rhino Africa tracks "E2B (Enquiry to Booking ratio)" as a consultant KPI | confirms the metric exists; no value | job ad | [Rhino Africa careers](https://careers.rhinoafrica.com/senior-travel-consultant-108224) |
| 42% proposal-to-booking | Proposal → Won, Spain DMC selling through travel agents | vendor case study | [Tourwriter](https://www.tourwriter.com/tailormade/) |
| 30% (75 sales / 250 quotes) | Proposal → Won | illustrative example, not a benchmark | [Tourwriter](https://www.tourwriter.com/know-conversion-rate-cost-sale/) |
| inquiry-to-quote 75–85%; quote-to-booking 20–40% (top 45–55%); luxury 18–30%; corporate/group 15–25% | Qualified → Proposal; Proposal → Won | vendor marketing, no source cited | [Rework](https://resources.rework.com/libraries/travel-tour-growth/booking-conversion-metrics) |
| 14% inquiry-to-booking for luxury "considered excellent" | Submitted → Won | vendor example (search snippet) | [Rework sales team guide](https://resources.rework.com/libraries/travel-tour-growth/travel-sales-team-performance) |
| aim for 50% lead-to-proposal and 50% proposal close, so 25% lead-to-booking | targets | host-agency advice | [WorldVia](https://worldviatravelnetwork.com/blog/top-20-metrics-travel-advisors-should-monitor) |
| hotels have "a 3–7% chance" of winning a planner's programme; about 45% of RFPs answered | venue RFP → Won, events | vendor analysis (Groups360) | [Hospitality Net](https://www.hospitalitynet.org/news/4118318.html) |
| some DMCs said "75% or more of their proposals never resulted in a contract" (ADMEI survey) | Proposal → Won ≤25%, incentives and events | search snippet; not found in the text of the IRF DMC study PDF | [IRF DMC study (2015)](https://theirf.org/wp-content/uploads/2016/02/dmcstudy-full.pdf) |
| "80% of sales are made after 8 or more follow-ups" | follow-up effort | generic sales claim, vendor | [Tourwriter](https://www.tourwriter.com/know-conversion-rate-cost-sale/) |
| website visitor → enquiry 2–3% | before Submitted; not a stage | vendor | [Tars](https://hellotars.com/ai-agents/safari-booking-ai-agent-wildlife-tours) |

### (a) Tailor-made safari: stage rates

These rates are **estimated** and partly **guessed**. Each column is a consistent set: multiplying the column
gives the overall booking rate. The column ends are not each stage's own worst or best case; combining every
stage's own low would give an implausible ~4%.

| Transition | low | middle | high | basis |
|---|---|---|---|---|
| Submitted → Contact attempted | 0.88 | 0.95 | 0.98 | guessed; operators promise contact within 24h (Go2Africa) or 15 min (Safari.com). Neglect is covered in neglect-and-mess.md |
| Contact attempted → Engaged (lead replied) | 0.55 | 0.70 | 0.80 | guessed; travellers ask several operators (SafariBookings, African Bush Camps) |
| Engaged → Qualified | 0.65 | 0.75 | 0.85 | guessed; 82% of Go2Africa's 2025 enquirers were "decided" on destination (up from 68%) |
| Qualified → Proposal (itinerary sent) | 0.80 | 0.85 | 0.90 | vendor 75–85%, WorldVia target 50% (lead → proposal) |
| Proposal → Won (deposit paid) | 0.25 | 0.33 | 0.45 | vendor 18–30% luxury; examples 30% and 42% |
| **Submitted → Won (product)** | **0.063** | **0.14** | **0.27** | SafariBookings ≈17% sits inside; 14% vendor example; 25% target |

- Lead source matters. Marketplace leads (SafariBookings) are shared with several operators. Paid-ad leads are
  probably weaker than direct referrals; Rhino Africa reports 60–65% repeat and referral business
  ([Tourism Update](https://www.tourismupdate.com/article/safari-interest-strong-but-bookings-harder-won)).
  **Guessed**: the profile's low end is the paid-ad case Emva will see.
- **Itinerary revisions per won deal**: Safari.com counted 2.2 interactions before deposit in 2024 and 3.8 in 2025.
  "Interaction" is not defined, but it bounds revisions from above. **Profile**: proposal versions per won deal 1–4,
  middle 2; lost leads with a proposal 1–2. **Estimated/guessed**. Proposal versions are a candidate Milestone
  ("revised itinerary sent") inside Proposal.

### (b) Corporate incentive trips: stage rates

- Proposal → Won: 0.15–0.35, middle 0.22. **Estimated** from the ADMEI claim (≤25% for many DMCs) and the vendor's
  15–25% for corporate and group. The upper end allows for direct inbound enquiries that are not multi-bid RFPs.
- Submitted → Won: 0.04–0.20, middle 0.10. **Guessed**, using the same stage pattern as (a) with lower Engaged and
  Proposal → Won. Many corporate enquiries are RFPs sent to several suppliers, or early budget-checking.
- Proposal versions per won deal: 2–6, middle 3 (**guessed**; site inspections and programme redesigns are common).

### (c) Corporate events: stage rates

- Multi-bid RFP channels: Submitted → Won 0.03–0.07 (Groups360's hotel figures). **Sourced**, but from vendor
  analysis and for venues.
- Direct inbound enquiries to an agency or DMC: Submitted → Won 0.08–0.25, middle 0.15. **Guessed**; the vendor's
  corporate 15–25% is quote-to-booking.
- Profile: 0.04 low, 0.12 middle, 0.25 high. **Guessed**. Leads from ads are direct inbound, but planners often send
  the same brief to several suppliers.
- Proposal versions per won deal: 1–4, middle 2 (**guessed**).

## 4. Lead volume per month (mid-size operator)

No source states this; operators keep it private. **Estimated**, with guessed inputs:

- (a) Safari: a mid-size tailor-made operator with $10–30M a year in land sales (**guessed** size band) makes
  $10M–30M / $22k ≈ 450–1,350 bookings a year. At a 14% booking rate that is about 3,200–9,600 Leads a year, or
  **270–800 a month** (middle about 500). A small specialist (1–5 consultants) sees 30–150 a month (**guessed**).
  The profile range is **100–1,000**, middle 400. Peaks in January follow the seasonality weights above.
- (b) Incentives: an Africa DMC or incentive house: **5–60 enquiries a month**, middle 20 (**guessed**). At about
  10% won and $280k each, that is roughly $6–7M a year at the middle.
- (c) Events: **10–150 enquiries a month**, middle 40 (**guessed**).

## Numbers for the profile

Money is per booking (Deal value) unless stated. Days count calendar days on the Simulated clock.

| quantity | segment | low | middle | high | confidence | source |
|---|---|---|---|---|---|---|
| days Submitted → Won (median of won leads) | safari | 14 | 21 | 35 | estimated | [Safari.com report](https://www.safari.com/blog/safari-travel-pulse-2025); [Rework](https://resources.rework.com/libraries/travel-tour-growth/booking-conversion-metrics) |
| days Submitted → Won, lognormal σ | safari | 0.8 | 1.0 | 1.2 | estimated | as above (p90 ≈ 60–180 days) |
| interactions before deposit | safari | 2 | 3 | 4 | sourced (2.2 → 3.8) | [Safari.com report](https://www.safari.com/blog/safari-travel-pulse-2025) |
| booking lead time, deposit → travel (median, months) | safari | 4 | 6 | 9 | sourced (186–190 days) / estimated range | [Tourism Update](https://www.tourismupdate.com/article/safari-interest-strong-but-bookings-harder-won); [Rhino Africa](https://blog.rhinoafrica.com/2026/07/23/how-far-in-advance-should-i-book-my-african-safari/) |
| January enquiry weight (× average month) | safari | 1.3 | 1.6 | 2.0 | estimated | [Aspire](https://www.aspiretravelclub.co.uk/insight/peaks-unpacked-why-the-traditional-peak-selling-season-is-shifting-in-the-luxury-sector); [Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025) |
| Nov–Dec enquiry weight | safari | 0.6 | 0.7 | 0.8 | estimated | [Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025) |
| share of trips travelling Jun–Aug / Apr-May-Sep-Oct / Nov–Mar | safari | — | 34% / 38% / 28% | — | sourced / estimated (remainder) | [Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025) |
| price per person per night, mid-market | safari | $300 | $550 | $900 | estimated | [Yellow Zebra](https://yellowzebrasafaris.com/us/your-first-safari/how-much-does-a-safari-cost/); Kati Kati rate |
| price per person per night, luxury | safari | $900 | $1,300 | $2,000 | estimated | Yellow Zebra; [Safari.com](https://www.safari.com/ngorongoro-crater-lodge) |
| price per person per night, ultra-luxury | safari | $2,000 | $3,000 | $5,000 | sourced (middle and high: rack rates $3,075–5,040 on the cited pages) / estimated (low: below both cited lodges; snippet rates for Kwitonda and Pamushana from $2,380) | [Mombo](https://www.safari.com/lodges/mombo-camp); [Singita](https://www.safari.com/singita-serengeti-house) |
| peak / low season rate ratio | safari | 1.3 | 1.4 | 1.55 | sourced middle (Mombo 5,040/3,285 = 1.53; Singita Serengeti 4,300/3,075 = 1.40 in 2026 and 4,600/3,285 = 1.40 in 2027) / estimated ends. Corrected 2026-10-01: the earlier 1.75 used Mombo rates ($2,889, $5,043) not on the page, and 1.5 divided a 2027 peak by a 2026 low | as above |
| nights | safari | 5 | 7 | 10 | estimated (spread 3–21) | [Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025); [Safari.com report](https://www.safari.com/blog/safari-travel-pulse-2025) |
| party mix solo / couple / family / friends | safari | — | 16 / 46 / 28 / 10 % | — | sourced | [Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025) |
| mean party size | safari | 2.3 | 2.6 | 3.0 | estimated | Go2Africa mix × guessed family and friends size |
| spend per person sharing | safari | $7,000 | $8,625 | $10,000 | sourced (middle) / estimated (ends) | [Go2Africa](https://www.go2africa.com/african-travel-blog/state-of-safari-2025) |
| median Deal value | safari | $10,000 | $15,000 | $20,000 | estimated | mean ≈ $22k, σ ≈ 0.9 |
| Deal value lognormal σ | safari | 0.7 | 0.9 | 1.1 | estimated | 5th–95th pct ≈ $5k–100k |
| Submitted → Won | safari | 6% | 14% | 27% | estimated | [SafariBookings](https://help.safaribookings.com/hc/en-150/articles/20583096001949) ≈17%; vendor figures |
| Contact attempted / Engaged / Qualified / Proposal / Won (Transition rates) | safari | .88 / .55 / .65 / .80 / .25 | .95 / .70 / .75 / .85 / .33 | .98 / .80 / .85 / .90 / .45 | guessed / estimated | see section 3 |
| proposal versions per won deal | safari | 1 | 2 | 4 | estimated / guessed | Safari.com interactions |
| Leads per month | safari | 100 | 400 | 1,000 | estimated (guessed inputs) | section 4 |
| booking lead time (months) | incentive | 3 | 9 | 18 | estimated | [DMC GO](https://dmc-go.com/blog/how-far-in-advance-should-you-book-an-incentive-travel-program/) |
| days Submitted → Won (median) | incentive | 28 | 42 | 90 | guessed | — |
| per person | incentive | $5,000 | $7,000 | $12,000 | estimated (avg $5,100–6,177) | [MPI/ITI 2025](https://www.mpi.org/blog/article/what-the-incentive-travel-index-2025-tells-us-about-the-future-of-incentive-travel); [Prevue](https://www.prevuemeetings.com/wp-content/uploads/2024/01/Incentive-Trends-WP-2024.pdf) |
| nights | incentive | 2 | 4 | 5 | sourced | [Prevue](https://www.prevuemeetings.com/wp-content/uploads/2024/01/Incentive-Trends-WP-2024.pdf) |
| group size | incentive | 10 | 40 | 150 | estimated | Prevue; [Brightspot](https://brightspotincentivesevents.com/incentive-travel/average-cost-incentive-travel-program/); DMC GO |
| Deal value | incentive | $50k | $280k | $1.2M | estimated | product of the rows above |
| Submitted → Won | incentive | 4% | 10% | 20% | guessed | ADMEI claim; Rework |
| Proposal → Won | incentive | 15% | 22% | 35% | estimated | [IRF DMC study](https://theirf.org/wp-content/uploads/2016/02/dmcstudy-full.pdf) (snippet); [Rework](https://resources.rework.com/libraries/travel-tour-growth/booking-conversion-metrics) |
| proposal versions per won deal | incentive | 2 | 3 | 6 | guessed | — |
| Leads per month | incentive | 5 | 20 | 60 | guessed | — |
| booking lead time (months) | events | 1 | 4 | 9 | estimated (APAC data) | [Cvent/HSMAI 2025](https://asia.hsmai.org/wp-content/uploads/sites/12/2025/05/hsmai-commercial-conf-mice-cvent.pdf) |
| days Submitted → Won (median) | events | 14 | 21 | 42 | guessed | [Cvent](https://cvent.com/en/press-release/cvent-group-sourcing-volume-sets-new-record-2024) (4-day reply expectation only) |
| cost per attendee per day | events | $169 | $400 | $600 | sourced (low) / estimated | [Skift/CWT-GBTA](https://meetings.skift.com/2024/09/26/rising-event-costs-to-challenge-2025-budgets/) |
| attendees (median) | events | 25 | 55 | 200 | sourced distribution / estimated | [Cvent/HSMAI 2025](https://asia.hsmai.org/wp-content/uploads/sites/12/2025/05/hsmai-commercial-conf-mice-cvent.pdf) |
| event days | events | 1 | 2 | 3 | guessed | — |
| Deal value | events | $5k | $50k | $540k | estimated | product of the rows above; Cvent RFP value $39k–255k |
| Deal value lognormal σ | events / incentive | 1.0 | 1.3 | 1.5 | estimated | Cvent: 24% of RFPs hold 81% of value |
| Submitted → Won | events | 4% | 12% | 25% | guessed (multi-bid floor 3–7% sourced) | [Hospitality Net/Groups360](https://www.hospitalitynet.org/news/4118318.html) |
| proposal versions per won deal | events | 1 | 2 | 4 | guessed | — |
| Leads per month | events | 10 | 40 | 150 | guessed | — |
| deposit at Won | safari | 25% | 30% | 50% | sourced | [Go2Africa](https://www.go2africa.com/african-travel-blog/how-it-works-our-booking-process); [African Safari Mag](https://www.africansafarimag.com/plan-african-safari/safari-booking-explained) |

## Open questions

1. **Is "Won" the deposit or the final balance?** The deposit (25–50%) is paid weeks after the enquiry; the balance
   comes 60–90 days before travel. Cancellations between the two are not researched here. Should the profile model
   a Won lead that later cancels? This belongs to sales-steps-and-exports.md.
2. **Where does the Deal value come from?** The quoted value may change across proposal versions, often rising as
   camps are upgraded. Which version does a sales-system export record as the deal amount? This changes how Stage
   scores see deal size.
3. **Paid-ad leads versus marketplace and referral leads.** No source separates booking rates by lead source for
   safari. The profile's low end assumes paid-ad leads are the weakest; this needs checking against a real
   advertiser export when one exists.
4. **Corporate segments have almost no stage-rate evidence.** The ADMEI "75%+ of proposals never contract" claim
   came from a search snippet and could not be found in the IRF DMC study text. Should corporate incentives and
   events stay in the first profile, or be added as a second profile once the safari one is validated?
5. **Lead volume** is entirely estimated from a guessed operator size. A real advertiser's monthly volume should
   replace it as soon as one is known.
6. **Exchange rates** were assumed (ZAR 17–19 per USD) and not checked. Deal values are in USD here; the generator
   needs a currency rule per advertiser (GBP, USD or EUR).
7. **Paywalled sources not read**: the full Incentive Travel Index 2025 (group sizes, lead times by region), the
   Travel Weekly / Phocuswright advisor surveys (booking windows), Virtuoso's luxury reports, and the SafariBookings
   help centre (behind a Cloudflare check; not bypassed). Any of these could narrow the ranges.
