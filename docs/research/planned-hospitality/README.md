# Planned hospitality: research notes

Research behind the planned-hospitality **Industry profile** (issue #4). One file per topic, each written by a
helper agent with `/research`, then checked before the profile used it.

Every number is a range with a confidence, following decision 0007:

- **sourced**: a cited source states it (or states numbers it follows from directly).
- **estimated**: worked out from cited sources that do not state it, with the working shown.
- **guessed**: no usable source; a reasoned judgement, flagged as such.

| file | topic |
|---|---|
| [enquiry-forms.md](enquiry-forms.md) | enquiry form fields, how enquiries are written, prohibited inputs |
| [sales-steps-and-exports.md](sales-steps-and-exports.md) | sales steps as the sales system names them, export column layout |
| [cycle-and-deal-size.md](cycle-and-deal-size.md) | sales-cycle length, deal sizes, stage rates |
| [neglect-and-mess.md](neglect-and-mess.md) | neglect rates, contact attempts, data mess rates |
| [notes-and-loss-reasons.md](notes-and-loss-reasons.md) | how sales notes are written, loss reasons |
| [what-predicts-a-booking.md](what-predicts-a-booking.md) | what in an enquiry predicts a booking, including effects that are not additive |

## Check of sourced numbers (2026-10-01)

Every row marked sourced (in full or in part) in a "Numbers for the profile" or "Proposed planted effects" table
was checked against its cited source. Totals: 20 confirmed, 3 corrected, 2 downgraded.

| file | quantity | outcome | note |
|---|---|---|---|
| cycle-and-deal-size.md | interactions before deposit (safari) | confirmed | Safari.com: 2.2 (2024) and 3.8 (2025) interactions; 14.9 and 22.4 days to deposit |
| cycle-and-deal-size.md | booking lead time, deposit → travel (safari) | confirmed | Tourism Update: Rhino Africa average 186–190 days |
| cycle-and-deal-size.md | share of trips travelling by season (safari) | confirmed | Go2Africa: 38% shoulder, 34% Jun–Aug; these are enquiries by intended travel month, not trips taken |
| cycle-and-deal-size.md | price per person per night, ultra-luxury (safari) | corrected | cited pages show $3,075–5,040; the $2,000 low end is not on them, so it is now estimated |
| cycle-and-deal-size.md | peak / low season rate ratio (safari) | corrected | Mombo page shows $3,285 and $5,040 (no $2,889 or $5,043; no Jan–May rate); Singita Serengeti 1.40 within each year. Range 1.3 / 1.5 / 1.75 changed to 1.3 / 1.4 / 1.55 |
| cycle-and-deal-size.md | party mix solo / couple / family / friends (safari) | confirmed | Go2Africa: 16 / 46 / 28 / 10 % of enquiries |
| cycle-and-deal-size.md | spend per person sharing (safari) | confirmed | Go2Africa: $8,625 in 2025; it is the budget stated in enquiries, not booked spend |
| cycle-and-deal-size.md | nights (incentive) | confirmed | Prevue PDF: 4 nights most popular (22%), then 2 nights (21%); 12% run 7+ days |
| cycle-and-deal-size.md | cost per attendee per day (events) | confirmed | Skift: CWT/GBTA forecast $169 for 2025, $155 in 2023 |
| cycle-and-deal-size.md | attendees (events) | confirmed | Cvent deck p. 10: 23.6 / 20.6 / 20.2 / 14.5 / 21.1 % (Singapore, Jan–Apr 2025). The same deck (p. 16) says planners take 61 days on average to award an RFP sent to Singapore, well above the guessed 14 / 21 / 42 days Submitted → Won for events (not changed) |
| cycle-and-deal-size.md | Submitted → Won, multi-bid floor (events) | confirmed | Hospitality Net: hotels have a 3–7% chance of winning; about 45% of RFPs answered, 55 of 100 ignored |
| cycle-and-deal-size.md | deposit at Won (safari) | confirmed | Go2Africa 30% of land package; African Safari Mag 25% common, 30–50% at some operators, 50% for permit-heavy trips |
| enquiry-forms.md | leisure forms asking email, name, message | confirmed | re-read 8 of 12 forms (EA, ST, SD, CL, NS, PO, NB, SB); AU returned 403; G2A, RA and AB render by script and could not be re-read |
| enquiry-forms.md | budget band lower edge, luxury UK operators | confirmed | ST slider from £1,500; SD from £2,000; CL from £5,000 |
| enquiry-forms.md | budget band top band start | confirmed | SD over £10,000; CL more than £20,000; ST £20,000+; G2A $10,000+ not re-read (script-rendered) |
| neglect-and-mess.md | share of attempted leads who never reply | downgraded | SafariBookings help centre returned 403 behind a Cloudflare check; figure came only from a search snippet |
| sales-steps-and-exports.md | deal property revisions kept | confirmed | HubSpot KB: company, deal, ticket and custom object properties up to 20 revisions |
| sales-steps-and-exports.md | contact property revisions kept | confirmed | HubSpot KB: contact properties up to 45 revisions |
| sales-steps-and-exports.md | export datetime precision | confirmed | bootcamp CSV has `YYYY-MM-DD HH:MM` values (custom-object file, not deals); link added to the citation |
| what-predicts-a-booking.md | 1. budget floor (luxury about $800–1,000) | downgraded | Travel Market Report returned 403; floor came only from a search snippet |
| what-predicts-a-booking.md | 5. lead source spread | confirmed | Runggaldier et al.: booking rates by source from 1% to 91% |
| what-predicts-a-booking.md | 7. response speed direction | corrected | MIT study confirmed on contact and qualify ("did not address close ratios"); Telfer/VanillaSoft measures win outcomes (3× at 10–60 min), so the row no longer says all three stop at qualify. HBR is paywalled and not read |
| what-predicts-a-booking.md | 9. party size direction | confirmed | Runggaldier et al.: booked requests slightly fewer adults and children, stays 5.04 vs 5.78 days |
| what-predicts-a-booking.md | 12. Mara fee rise | confirmed | Nation states $200 high season (Jul–Dec) and $100 green season but no date; Governors' Camp states $200 from 1 July 2024, citation added |
| what-predicts-a-booking.md | T. country-of-residence proxy | confirmed | Runggaldier et al.: country code importance 0.202; booking rates 7–21% by language, 18–30% by country |
