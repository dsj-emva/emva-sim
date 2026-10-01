# Planned hospitality: the enquiry form and how enquiries are written

Research for the planned-hospitality **Industry profile** (issue #4). Confidence follows decision 0007:
**sourced** (a cited source states it), **estimated** (worked out from cited sources, working shown),
**guessed** (no usable source, reasoned, flagged). Forms were read on 2026-10-01 by loading each live page and
listing its fields. Nothing was submitted.

## Summary

- We read 12 leisure enquiry forms: 11 safari or tailor-made operators and 1 small independent travel designer.
  Abercrombie & Kent's US contact page has no form, only a phone number, so it is not counted. We also read 3
  corporate/MICE forms (a DMC network's request for proposal, an event agency's needs survey, a Zanzibar DMC's
  contact form), plus vendor guidance from Cvent, Safari Portal, SafariOffice and SafariBookings.
- Every form asks for name, email and a free-text message. Nearly every one asks for destination (11/12) and
  timing (11/12). Most ask for a budget per person (10/12), usually as bands or a slider, and that budget usually
  excludes international flights.
- The forms that require a budget all offer a way out: an "Undecided" or "Not sure" option, or the slider's
  bottom end. So a filled budget field doesn't mean the lead stated a budget. The generator needs a
  separate "stated a real value" rate.
- Many forms let the lead dodge the question: "Not sure yet", "Open to ideas", "Any month", "Any year". The
  generator should emit these literal values, not blanks.
- Real exports carry some mess:
  - Audley writes the radio-button choice into the record as text with asterisks.
  - Euromic's year dropdown still stops at 2026.
  - &Beyond passes referrer, visit counts, UTM tags and `gclid` into the enquiry.
  - SafariBookings confirms that leads sometimes leave the message blank.
- How enquiry text is written (length, tone, vague vs specific) has **no primary statistical source**. Those
  numbers are guessed, held in by form limits (Scott Dunn caps the message at 1,000 characters) and by the
  prompts the forms show.
- No source gives the share of enquiries that state a budget, dates or group size. Every such share below is
  **guessed** and depends on the form's design. The profile should model that dependence rather than use one
  number.
- Prohibited inputs for this industry:
  - Title (Mr/Mrs/Miss/Lord/Dame…) and first name: gender and name-based inference.
  - Travellers' ages, including children's ages and age bands.
  - The occasions "Retirement" and "Graduation": age proxies.
  - Dietary requirements: religion.
  - Mobility, medical or accessibility needs, and "how physical" an activity may be: disability or age.
  - Nationality or passport: ethnicity.
  - Street address and ZIP/postcode: precise postcode.

  Country of residence, honeymoon and party type are hard cases, listed under open questions.

## 1. Fields on real enquiry forms

### Forms read

| id | form | kind | URL |
|---|---|---|---|
| EA | Expert Africa | UK safari specialist | https://www.expertafrica.com/enquiry |
| G2A | Go2Africa | SA-based safari seller, US-facing | https://www.go2africa.com/enquire-now |
| RA | Rhino Africa | SA-based safari seller | https://www.rhinoafrica.com/en/contact-us |
| ST | Steppes Travel | UK tailor-made, luxury | https://www.steppestravel.com/contact/ |
| AU | Audley Travel | UK tailor-made, mid-to-upper market | https://www.audleytravel.com/contact-us |
| SD | Scott Dunn | UK luxury tailor-made | https://www.scottdunn.com/plan-your-trip |
| AB | &Beyond | luxury lodge owner and operator | https://enquire.andbeyond.com/plan-trip |
| CL | Cazenove+Loyd | UK luxury tailor-made | https://www.cazloyd.com/enquire |
| NS | Natural Selection | safari camp group | https://naturalselection.travel/contact/ |
| PO | Porini | Kenya camp operator | https://www.porini.com/?p=24 |
| SB | Safari Nuggets via SafariBookings | marketplace quote request (mid-market Tanzania) | https://www.safaribookings.com/enquiry/form/p5678 |
| NB | Noboru Travel | independent travel designer (Tally form) | https://tally.so/r/dWlg2V |
| EU | Euromic | DMC network, request for proposal (MICE) | https://www.euromic.com/request-a-proposal/ |
| BC | Bespoke Connects | event agency needs survey (Jotform) | https://form.jotform.com/243266282566160 |
| ZT | ZanTours MICE | Zanzibar/Tanzania DMC | https://zantours.com/?p=252 |

Not counted: Abercrombie & Kent's US contact page (https://www.abercrombiekent.com/contact) shows only a phone
number. Its `/enquire` URL redirects to the home page.

Two of the forms are multi-step wizards (G2A, RA). For RA, the step questions were read from the page's
embedded configuration because the wizard did not advance without input. Whether RA's later steps are required
is not known.

### Leisure fields (12 forms)

"Present" counts the forms out of 12 that ask for the field in its own control (not only through the message
placeholder). "Required" counts the forms where the field is marked required, where that could be seen.

| field (typical label) | type, typical options | present | required | forms and notes |
|---|---|---|---|---|
| Email | free text (email) | 12/12 | 12/12 | all |
| Name ("First name", "Last name"; sometimes "Full name") | free text | 12/12 | 12/12 | SB and NB use one field; SafariOffice splits a full name automatically [SO] |
| Message ("Tell us more", "Your travel preferences", "Anything else…") | free text | 12/12 | 6–8/12 | required: EA, ST, AU, AB, NS, SB, NB; optional: SD (capped at 1,000 characters), CL, PO; G2A's status not seen |
| Destination ("Where would you like to go?") | dropdown or multi-select of countries or regions; often includes "Not sure yet", "I don't know where yet", "Open to ideas", "General enquiry" | 11/12 | 8–11/12 | not NS. An explicit "not sure" option appears in EA, G2A, RA, AU, SD, CL (6 of 11) |
| Timing ("When would you like to travel?") | many shapes: free text (EA, ST, PO); exact date range (AB, G2A option); year and month dropdowns with "Any year"/"Any month" (SD, CL, G2A); relative buckets "Within 3 months / 3-6 months / Over 6 months" (AU); date plus "flexible" checkbox (SB) | 11/12 | 7–9/12 | not NS. EA also asks "Are they fixed or flexible?" |
| Phone | free text (tel), sometimes with a country-code selector | 11/12 | 5–6/11 | required: ST, AU, SD, CL, SB; optional: EA (mobile, home and work), AB, PO, NB; not NS |
| Budget per person | bands (G2A: $4,000–7,000 / $7,000–10,000 / $10,000+ / Not sure; SD: £2,000–5,000 / £5,000–10,000 / Over £10,000 pp; CL: Undecided / £5,000–10,000 / £10,000–20,000 / More than £20,000 pp); slider (RA, ST, AB); free number with currency (EA, PO); accommodation tier with a per-day price (SB); per-night bands plus a total (NB) | 10/12 | 3–5/12 | not AU, NS. Required: ST, SD, CL; G2A's wizard step cannot be skipped. Usually stated to exclude international flights (RA, PO) |
| Number of travellers | number steppers (adults, children, sometimes teens and infants), or one number | 8/12 | 3–6/8 | EA (free text), RA, ST (required), SD (adults/teens/children), AB (required), PO, SB (required), NB (required). AU asks for it only in the message placeholder |
| Ages of travellers or children | free text, a dropdown per child (0–17), or counts by age band | 7/12 | 2–4/7 | exact ages: EA (asks the ages of *all* travellers), RA, SB, NB. Age bands only: PO (>16, 13–15, 2–12, ≤1), SD (adults/teens/children), AB (adults/children) |
| Party type ("Who are you travelling with?") | dropdown: solo / partner or couple / family / friends / group | 3/12 | 2–3/3 | G2A, AB, PO |
| Trip length | dropdown buckets: "Less than one week… 2 weeks +" (G2A); "1-3 days… 4 weeks" (PO); 1–15+ days (SB); RA asks how long | 4/12 | 3–4/4 | plus AB and G2A when an exact date range is given; ST and AU in the message placeholder |
| Interests or trip type | dropdown or multi-select (AB: Active, Adventurous, Birding, Cultural, Foodie, Private Travel, Responsible Travel, Slow Travel, Wellness, Wildlife; PO: Safari / Beach / Safari & Beach; NB: Adventure, Beach, City, Wellness, Safari, Not sure); free text (EA) | 4–5/12 | 2–3 | EA, AB, PO, NB, RA (asks what you want to experience); ST asks group tour vs bespoke |
| Accommodation level or rooms | dropdown (SB: camping / budget / mid-range / luxury); free text (EA: rooms separate or sharing); lodge picker (AB) | 3/12 | 1 | SB, EA, AB; NB's per-night budget plays the same role |
| Special occasion | dropdown (AB: Anniversary, Birthday, Engagement, Graduation, Honeymoon, Retirement, Wedding) | 1/12 | 0 | AB only. The AB message placeholder and the SD comment prompt also invite occasions and must-dos |
| Flights already booked? | yes/no or free text | 2/12 | 0–1 | EA, G2A |
| Repeat or referred client | radio (RA: travelled with us before? referred by a past client?; ST: Yes / enquired before / first enquiry) | 2/12 | 1–2 | RA, ST |
| How did you hear about us? | dropdown of 8–12 options (search, referral, previous travel, magazine, social, advert, event, AI chat recommendation [ST]) | 4–5/12 | 2 | CL (required), NB (required), NS, ST (plus "What has prompted you to contact us today?"), RA (referral only) |
| Country of residence | dropdown | 5/12 | 5/5 | EA, AB, PO, SB, ST (as "Where would you like to depart from?"). SD gets it from the required phone country code |
| Title (salutation) | dropdown (Mr, Mrs, Ms, Miss, Dr, Prof, Sir, Lord, Lady, Dame…; ST adds Mx, Countess, Duke…) | 3/12 | 2/3 | EA (required), AU (required), ST; SafariOffice's default form always requires one [SO] |
| Preferred contact method or time | checkboxes (SD: Email / Phone call / Text, plus best time to call); dropdown (CL: best time to call; NB: email / call / WhatsApp); "online meeting" or "video call" checkbox (ST, AU) | 4–5/12 | 1 | SD, CL, NB, ST, AU |
| Newsletter or marketing opt-in | checkbox | 6–7/12 | 0–1 | EA, G2A, ST, AU (opt-out wording), CL (yes/no required), PO, NS (permission to share) |
| Postal address | street, city, region, ZIP, country | 1/12 | 0 | ST only (optional) |
| Traveller vs travel trade | radio | 1/12 | 1 | AB ("Curious Traveller" / "Member of the Travel Trade") |
| Hidden attribution | hidden fields or URL parameters | seen in 1–2/12 | n/a | AB's "Plan my trip" link carries referrer, landing page, page views, visits, first visit, `utm_*` and `gclid`. AU attaches saved "favourites" |

Typical budget ranges on the forms (per person, excluding international flights):

- Rhino Africa's slider runs 4,000–40,000 in steps of 1,000 for its foreign currencies, and R80,000–800,000 for
  rand. This is read from the page's embedded configuration; which foreign currencies use that range was not
  confirmed.
- Steppes' slider runs £1,500 to £20,000+.
- Go2Africa's lowest band starts at $4,000.
- Scott Dunn's lowest band starts at £2,000.
- Cazenove+Loyd's lowest band starts at £5,000.
- &Beyond's USD slider starts at $1,000.

SafariBookings tiers for a mid-market Tanzania operator are priced per person per day.

Messages the forms show the lead (these shape what people write):

- Go2Africa: "The more you can tell us, the faster we can send you an itinerary".
- Steppes asks who is travelling, how long, and the key elements wanted.
- Audley suggests number of travellers, duration, dates and level of accommodation.
- &Beyond asks about special occasions, interests, and must-dos or don'ts.
- Scott Dunn asks about hotels or tours already seen, set dates, room needs, or whether the lead is unsure where
  to start.
- SafariBookings asks for at least a couple of sentences.

### Corporate and MICE fields (3 forms plus vendor guidance)

| field | type, options | where |
|---|---|---|
| Company name | free text, required | EU, BC |
| Contact's role or title; whether they decide; main point of contact | free text; yes/no radios | BC (all required); EU (title optional) |
| Programme or event type | dropdown. EU: Incentive, Meeting, Event, Congress, Conference, Exhibition, Product Launch, Press Trip, Special Interest group, Tour Group, Shore Excursion. BC: Meeting, Conference, Gala, Incentive Trip, Business Retreat, Sourcing, Consulting, Facilitation, Other | EU, BC |
| Number of delegates | free text, required | EU ("Expected Number of Delegates") |
| Dates | arrival and departure dates, or month and year dropdowns. EU's year list runs 2023–2026, so stale options are real | EU |
| Destination | up to 3 ranked dropdowns (EU, all required); free text (BC) | EU, BC |
| Budget | "Budget per participant", free text, optional (EU); "Budget information", free text, optional (BC) | EU, BC |
| Accommodation | hotel category, counts of singles/doubles/twins/suites, special requests | EU |
| Meeting space | plenary yes/no and size, set-up style (Cinema, Boardroom, U shape, Classroom, Banquet…), number of breakout rooms | EU |
| Extras | AV, photography, food and drink, welcome reception, gala dinner, dinners off site, spouse programme, transfers, gifts, team building ("please note how physical") | EU |
| Brief upload, website, time zone | file, text | EU |
| Recurring or annual programme | free text | BC |
| Free text | "Event vision & support needs" (required), audience description, venue preferences | BC |
| Minimal form | email, message and consent only | ZT |

Cvent's guidance on writing an RFP adds:

- the event's history (past attendance, room nights)
- whether dates are flexible
- the guest-room rate range
- the food and drink budget
- the decision date and site-inspection timeline
- the reason for the RFP
- the chance of future business
- **attendee demographics including age and gender**, which are Prohibited inputs if they reach Emva

Source: https://www.cvent.com/en/blog/events/event-planning-basics-writing-perfect-rfp

### What sales systems keep beyond the form

Safari Portal, a safari-agency CRM, keeps these on each contact: passport details, nationality, dietary
requirements, emergency contacts, loyalty numbers, activity level, seat preferences, and birthdays and
anniversaries. Its forms create leads straight from the website, Typeform or Meta Lead Ads.

Sources: https://www.safariportal.app/travel-crm-contact-management-custom-forms and
https://atta.travel/resource/safari-portal-launches-custom-forms-to-streamline-travel-operations.html

These fields appear after the first contact, but they can end up in an export. See section 4.

## 2. How enquiry free text is written

**All guessed, held in by the form evidence above.** No source we found samples or measures real enquiry text.

- **Length.**
  - Most messages are short: guessed median 25–80 words. Range: 0 words (blank) up to about 300–400 words,
    rarely more.
  - A cap like Scott Dunn's 1,000 characters is about 150–200 words. Estimated: 1,000 ÷ 5–6.5 characters per
    word including spaces.
  - Blank messages happen: SafariBookings lists "the client leaves the quote request blank" among cases an
    operator may *not* decline (https://help.safaribookings.com/hc/en-150/articles/18236530430749). The rate is
    not given.
  - Where the message is optional and the form already collects structured fields, guessed 10–35% of messages
    are blank or a token ("please call me", "see above").
- **Where the facts go.** Forms with many structured fields (SD, RA, G2A) get shorter messages. Forms where the
  message is the main field (AU, ST, NS, EA's first step) get the dates, party and budget written into the text.
  So the generator should move facts between structured fields and text depending on the form's shape, and
  sometimes state them in both, inconsistently. That inconsistency is guessed but follows from the redundancy.
- **Tone.** Friendly and first-person; often opens with the occasion or with experience ("first safari", "we've
  been to Kenya before"). Leads write in the language of the site, often in imperfect English for non-UK/US
  residents. Corporate enquiries are terser and written in the third person about the client ("our client
  requires…"), especially when the agency is the enquirer.
- **What it contains**, in rough order of frequency (guessed):
  1. who is travelling, often with relationships and ages ("my wife and I, kids 9 and 12")
  2. when, often only as a month or season
  3. what they want to see: the Migration, gorillas, the Big Five, "not too many other vehicles"
  4. where, by country, park or a named lodge
  5. style or comfort: "luxury but not over the top", tented camp, a private vehicle
  6. the occasion: honeymoon, a big birthday, an anniversary
  7. a budget, often hedged ("around $10k each", "flexible for the right trip")
  8. limits: dietary needs, mobility, fear of small planes, malaria worries
  9. a question: "is September a good time?", "can we combine with Zanzibar?"
  10. a contact preference: "please email, I'm in Texas"
- **The range from vague to specific** (guessed shares of messages, mainly as a setting for the generator):
  - **Vague, about 20–40%:** a region and a rough year, nothing else ("thinking of Africa next year").
  - **Partly specific, about 35–55%:** country or season, party, one or two must-dos.
  - **Very specific, about 15–30%:** exact dates, named lodges or a named itinerary, nights per camp, a budget,
    flights already booked.
  - The specific end clusters among repeat or referred clients and people who have researched for a long time.
- **Corporate.**
  - Specific on dates, delegate numbers and programme type; vague on budget.
  - Often points to an attached brief (EU allows uploads).
  - May come from an agency rather than the end client.
  - The ZT-style minimal form gives one paragraph carrying everything.

## 3. Share of enquiries that state key facts

**No source states any of these shares.** The ranges are guessed, except where the form forces a value. The
profile should make each rate depend on the form shape: a required structured field, an optional structured
field, or free text only. The "present on forms" counts from section 1 set how often each shape occurs.

| quantity | required structured field | optional field or free text only | confidence |
|---|---|---|---|
| states a destination (not "not sure / open to ideas") | 70–95% | 60–90% | guessed |
| states any travel timing (at least year or season) | 90–100% (may be "Any month/year") | 65–90% | guessed |
| states exact dates (day-level) | 20–45% | 10–30% | guessed |
| states group size (a number) | 95–100% | 55–85% | guessed |
| includes children | 15–35% of leisure enquiries | same | guessed |
| states a real budget (not "Not sure / Undecided", not the slider's default) | 55–85% | 15–40% | guessed |
| states trip length or nights | 85–100% | 40–75% | guessed |
| mentions a special occasion (honeymoon, anniversary, birthday…) | n/a (optional dropdown on 1/12 forms) | 10–25% | guessed |
| mentions dietary, medical or mobility needs at enquiry | n/a | 2–10% | guessed |
| corporate: states delegate numbers | 95–100% (EU required) | 70–95% | guessed |
| corporate: states a budget | n/a (optional on EU and BC) | 20–50% | guessed |

Reasons behind the guesses:

- Requiring a field with an escape option still leaves real non-answers.
- An optional budget is the field leads skip most, because travel advice tells them a rough range is enough.
  An example from a safari magazine's booking guide: https://www.africansafarimag.com/plan-african-safari/safari-booking-explained
- Stating exact dates is rare because safari leads usually plan many months ahead. Audley's own buckets begin
  at "Within 3 months".

## 4. Prohibited inputs and Intent signals

Decision 0008 prohibits protected traits (age, gender, ethnicity, religion, disability) and near-proxies (precise
postcode, name-based inference). Intent signals are always allowed, even where they correlate with a trait.

For context: UK law lists 9 protected characteristics, adding gender reassignment, marriage and civil
partnership, pregnancy and maternity, and sexual orientation (https://www.gov.uk/discrimination-your-rights). But
for goods and services, the Equality Act's Part 3 does not cover marriage and civil partnership, or age for
under-18s (s.28, https://www.legislation.gov.uk/ukpga/2010/15/section/28).

### Prohibited inputs (the formatter should refuse them)

| input | where it appears | trait |
|---|---|---|
| Title / salutation (Mr, Mrs, Miss, Ms, Mx, Lord, Lady, Dame, Sir, Countess…) | EA, AU, ST; SafariOffice default | gender (and marital status through Mrs/Miss) |
| First name, last name | all forms | name-based inference (gender, ethnicity) |
| Travellers' ages, including the lead's own (EA asks the ages of all travellers) | EA, RA, SB, NB; message text | age |
| Children's ages and age-band counts (PO, SD, AB) | as above | age (they show the parents' life stage). See open question 1 |
| Occasion "Retirement", "Graduation"; "60th birthday" and similar in text | AB dropdown; message text | age |
| Dietary requirements (halal, kosher, "no pork") | message text; CRM contact profile (Safari Portal) | religion |
| Mobility, medical, accessibility needs; "how physical" in team building | message text; EU form | disability (and age) |
| Pregnancy ("I'll be 6 months pregnant") | message text | pregnancy (UK-protected; not on Emva's list, see open questions) |
| Same-sex partner mentioned ("my husband and I" from a man) | message text | sexual orientation (UK-protected; not on Emva's list) |
| Nationality, passport details | CRM contact profile (Safari Portal), later in exports | ethnicity / national origin |
| Street address, ZIP/postcode | ST address block; CRM | precise postcode |
| Attendee demographics (age, gender) | corporate RFPs, as Cvent recommends | age, gender |

Free text needs the same treatment. If **Sales notes** or the enquiry message are read by a language model,
ages, names, religion, health, pregnancy and orientation must be removed or ignored before they become features.
The synthetic text should plant these on purpose so the proxy check can be tested.

### Intent signals (allowed)

Purchase details:

- budget per person and its band
- nights or trip length
- number of travellers and rooms
- destination and how specific it is
- a named lodge or itinerary
- accommodation tier
- timing and how far ahead
- fixed vs flexible dates
- flights already booked

Relationship and channel:

- repeat client, referred by a past client, enquired before
- how they heard about us, and attribution (UTM, `gclid`, landing page, visit count)
- preferred contact method, and a request for a video call or online meeting
- trade vs consumer

The message itself:

- its length and how specific it is
- the trip interests

Corporate:

- programme type
- delegate numbers
- budget per participant
- hotel category and meeting-space needs
- whether the contact is the decision-maker
- a brief attached
- a recurring programme

### Hard cases (see open questions)

- **Country of residence and phone country code.** These are coarse, not "precise postcode". They link to deal
  size through the market: SafariBookings says North American and Western European travellers usually spend
  more per booking (https://help.safaribookings.com/hc/en-150/articles/19487006345117). But they partly stand in
  for nationality and ethnicity.
- **Honeymoon, wedding, engagement, anniversary.** These describe the trip (Intent signal). They also reveal
  marital status, which UK law does not protect for services, and lean towards an age group.
- **Party type (solo, couple, family, friends).** This sizes the deal, so it is an Intent signal, but it leans
  towards age and marital status.
- **Email domain.** Corporate vs personal is an Intent signal for MICE. For leisure, old webmail domains may
  lean towards age (guessed).

## Numbers for the profile

| quantity | low | high | confidence | source |
|---|---|---|---|---|
| leisure forms asking email, name, message | 100% | 100% | sourced | 12/12 forms in section 1 |
| leisure forms asking destination | 85% | 95% | estimated | 11/12 = 92% |
| leisure forms asking timing | 85% | 95% | estimated | 11/12 = 92% |
| leisure forms asking budget per person | 75% | 90% | estimated | 10/12 = 83% |
| leisure forms requiring budget | 25% | 45% | estimated | 3–5/12 (ST, SD, CL; G2A wizard) |
| leisure forms asking number of travellers (own field) | 60% | 75% | estimated | 8/12 = 67% |
| leisure forms asking ages (exact or band) | 50% | 65% | estimated | 7/12 = 58% |
| leisure forms asking phone | 85% | 95% | estimated | 11/12 = 92%; required in 5–6 |
| leisure forms asking title | 20% | 30% | estimated | 3/12 = 25% |
| leisure forms asking country of residence | 40% | 50% | estimated | 5/12 = 42% (+SD via phone code) |
| leisure forms offering a "not sure" destination option | 50% | 60% | estimated | 6/11 = 55% |
| leisure forms asking how heard | 33% | 42% | estimated | 4–5/12 |
| leisure forms with a newsletter opt-in | 50% | 60% | estimated | 6–7/12 |
| budget band lower edge, luxury UK operators (pp, excl. flights) | £1,500 | £5,000 | sourced | ST slider £1,500; SD £2,000; CL £5,000 |
| budget band top band start (pp) | $10,000 / £10,000 | £20,000 | sourced | G2A $10k+; SD >£10k; CL >£20k; ST £20k+ |
| budget slider range, foreign currencies (pp) | 4,000 | 40,000 | estimated | RA page configuration (min/max/step 1,000), currency mapping not confirmed |
| message length, median (words) | 25 | 80 | guessed | none |
| message length, max typical (words) | 300 | 400 | guessed | SD cap 1,000 chars ≈ 150–200 words (estimated) |
| messages blank or token, optional-message forms | 10% | 35% | guessed | blank requests happen (SafariBookings, sourced); rate unknown |
| messages vague / partly specific / very specific | 20–40 / 35–55 / 15–30% | | guessed | none |
| states real budget, required-band form | 55% | 85% | guessed | none |
| states real budget, optional or text-only | 15% | 40% | guessed | none |
| states exact dates | 10% | 45% | guessed | none (lower for text-only forms) |
| states group size, text-only form | 55% | 85% | guessed | none |
| enquiries including children | 15% | 35% | guessed | none |
| mentions a special occasion | 10% | 25% | guessed | none |
| mentions dietary/medical/mobility at enquiry | 2% | 10% | guessed | none |
| corporate: states delegate numbers | 70% | 100% | guessed | EU makes it required |
| corporate: states a budget | 20% | 50% | guessed | optional on EU, BC |

## Open questions

1. **Children's ages vs deal size.** Child rates often depend on age (RA counts anyone aged 12 or over as an
   adult). If the ages are prohibited, the **Submit score**'s size can use counts of paying adults and children
   only. Should the formatter allow "children counted as adults by the operator's own rule" as a sizing input
   while still refusing the ages? This needs the user's ruling.
2. **Country of residence.** It is not on 0008's near-proxy list, and it predicts **Deal value** through the
   market. Is it allowed and covered by the proxy check, or prohibited? The same question applies to phone
   country code.
3. **Marital status, pregnancy, sexual orientation, gender reassignment.** These are UK-protected but not on
   Emva's trait list (age, gender, ethnicity, religion, disability). Should the profile treat honeymoon and
   wedding as Intent signals, and plant pregnancy and orientation mentions as prohibited anyway?
4. **No measured shares.** No source found for any share of enquiries stating budget, dates, party or occasion,
   or for message length. ATTA, ASTA, Virtuoso and SATSA material we could reach did not cover enquiry
   contents. An advertiser's own export (the third rung of the **Evidence ladder**) is the only real source;
   until then these ranges stay guessed and wide.
5. **Unread forms.** Abercrombie & Kent's US site is phone-led. Wilderness's form is a multi-step wizard that we
   could not read past the first step. Larger operators may route more leads by phone than by form, which
   changes how much structured data a **Lead** carries. Phone leads are not covered here.
6. **Multi-step wizards.** In G2A and RA, a lead who drops out part-way may still be captured as a partial
   **Lead** by some sales systems. We could not confirm this. If it happens, it is a source of near-empty Leads.
7. **Corporate sample is thin.** We read 3 forms plus Cvent guidance. Venue and hotel group-sales RFP forms
   (e.g. lodge conference desks) were not read.

## Vendor and other sources referred to above

- [SO] SafariOffice general request form: https://help.safarioffice.com/en/articles/64-how-to-add-safarioffice-general-request-form-to-your-website
- SafariBookings, when a quote request can be declined: https://help.safaribookings.com/hc/en-150/articles/18236530430749
- SafariBookings, converting requests to bookings: https://help.safaribookings.com/hc/en-150/articles/19487006345117
- Safari Portal contact fields: https://www.safariportal.app/travel-crm-contact-management-custom-forms
- Cvent, writing an RFP: https://www.cvent.com/en/blog/events/event-planning-basics-writing-perfect-rfp
- GOV.UK protected characteristics: https://www.gov.uk/discrimination-your-rights
- Equality Act 2010 s.28: https://www.legislation.gov.uk/ukpga/2010/15/section/28
