# Neglect, contact attempts and data mess (planned hospitality)

Research for the planned-hospitality **Industry profile** (issue #4): how often a **Lead** is never attempted, how
fast and how often the advertiser makes a **Contact attempt**, whether a sales system records those attempts at
all, and how messy the exported data is. Confidence labels follow decision 0007 and this folder's README
(sourced, estimated, guessed).

Researched 2026-10-01 with web search and fetch. Several primary pages could not be read in full (paywall,
Cloudflare challenge, 410 Gone); where a number was seen only in a search-result snippet or a secondary page,
that is said next to it.

## Summary

- **Almost all hard evidence on neglect is general, not travel-specific**: secret-shopper audits of web forms in
  the US (Harvard Business Review 2011, InsideSales 2008/2016, Drift 2017) and US real estate (2024). They find
  that 23% to 55% of test enquiries get no response. Travel and hospitality audits exist but are older or
  measure customer-service email rather than sales enquiries; they show 25% to 70% unanswered. There is no
  published audit of safari tour operators or travel designers.
- These audits send one identical enquiry to many firms, so the variation they find is **the firm's behaviour,
  not the lead's quality**. The one audit that looked inside firms found handling "consistently inconsistent"
  within the same brokerage, and a hotel audit found "little or no difference" across hotel tiers. This supports
  modelling neglect mainly as advertiser behaviour (workload, weekends, staff). One caveat: in group/MICE
  requests (RFPs), much non-response is a deliberate decline (no availability, poor fit), which is a quality
  judgement, not neglect.
- **Speed to first contact has a long tail**: among firms that respond, roughly half respond within an hour and
  about a third take over a day; mean response times of 38 to 47 hours are reported, with medians far lower
  (39 minutes in the one study that gives a median). Hotel/venue RFP replies average about 5 days.
- **Contact attempts are few**: about 1.3 attempts per lead on average; about half of leads never get a
  second call; email dominates (87% of responses in one audit; 77% of leads never phoned in another).
- **Many sales systems do not record contact attempts**: vendor observation puts manually logged activity at
  24% to 52% of real activity; only 47% of B2B sellers say they use their CRM regularly. Travel operators often
  run leads from inboxes and spreadsheets (qualitative only). The profile should assume many exports carry no
  contact-attempt record at all, only a **CRM stage**.
- **Data mess numbers are mostly vendor marketing.** Duplicates: 10% to 30% of CRM records is the commonly
  repeated range. Bots: 18% to 30% of web traffic is invalid in lead-generation sectors, 41% to 45% in travel,
  but far less reaches a CRM after form filtering; a UK lead firewall rejects 5% to 10% of quote-form leads as
  fake data. Stage skipping, late or bulk stage updates and stale open leads have no quantitative primary
  source found; those numbers are guessed.

## Findings

### 1. Neglect: share of leads never attempted

#### General (not travel-specific) web-lead audits

| study | year | sample | method | no response | source |
|---|---|---|---|---|---|
| Oldroyd, McElheran, Elkington (Harvard Business Review) | 2011 | 2,241 US companies | test web lead | 23% never; 24% took over 24 h; 37% within 1 h; 16% in 1 to 24 h; mean 42 h among responders within 30 days | [HBR](https://hbr.org/2011/03/the-short-life-of-online-sales-leads) (paywalled; figures via [BYU record](https://scholarsarchive.byu.edu/facpub/9711) and [secondary summary](https://ainora.lt/blog/lead-response-time-statistics-every-study-2026)) |
| InsideSales.com with Incoho | 2008 | top 500 web companies | test web lead | 45% never contacted; 47% replied by email, 8% by phone | [destinationCRM](https://www.destinationcrm.com/Articles/CRM-News/CRM-Featured-Articles/Can-I-Call-You-Back-Later-48699.aspx) |
| InsideSales.com lead audit | 2016 | 4,700+ leads, many sectors | test leads | 50% never got a personalised response; mean 38 h 35 min; 28.4% of first emails automatic; 77% never phoned | [B2B Marketing](https://www.b2bmarketing.net/half-of-sales-leads-never-receive-personalised-response/) |
| Drift | 2017 | 433 B2B companies | secret shopper | 55% did not respond within 5 business days; 7% within 5 minutes | [archived Drift post](https://web.archive.org/web/20190703161359/https://www.drift.com/blog/lead-response-survey/) (not fetchable here; figures via [secondary summary](https://ainora.lt/blog/lead-response-time-statistics-every-study-2026)) |
| Mike DelPrete, US real estate | 2024 | 100+ secret shops, 25+ brokerages | web inquiry, weekday business hours | 47% no human response; over 1 in 3 no response of any kind; mean 8 h 17 min, median 39 min | [mikedp.com](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored) |
| WAV Group, US real estate | older (undated in source) | buyer inquiries via broker sites and portals | secret shopper | 48% never responded | via [Inman](https://inman.com/2024/07/30/delprete-secret-shopper-sting-reveals-agents-lose-hosts-of-leads) search snippet; not verified |

All of these are vendor-run or vendor-funded except HBR (academics, with InsideSales data). InsideSales and
Drift sell lead-response software; treat their numbers as likely to overstate neglect.

#### Travel and hospitality

| study | year | sample | what was tested | no response | source |
|---|---|---|---|---|---|
| Quality Track International (hotel sales departments) | 2007 | 3,000+ calls to 750+ North American hotels | sales enquiry by phone, message left | sales manager reachable 49.4% of the time; 51.7% of messages not returned by end of next business day; "over 25%" of enquiries unanswered; little difference across deluxe, upscale, midprice | [Hospitality Upgrade](https://www.hospitalityupgrade.com/news/blowing-the-basics-hotel-sales-managers-fail-to-respond-to-customer-inquiries-more-than-25-of-the-time) (vendor of mystery shopping) |
| Groups360 (group/MICE RFPs to hotels) | ~2020 to 2023 | not stated | planner RFPs | about 55% of RFPs "completely ignored" (45% response); planners source 10% to 20% more hotels to compensate | [Hospitality Net](https://www.hospitalitynet.org/news/4118318.html) (vendor; sample not given) |
| CM.com, UK top 25 tour operators | 2022 | 25 operators, 12 channels | customer enquiries across channels (email, forms, phone, social) | 48% of enquiries not responded to | [CM.com press release](https://www.cm.com/en-gb/press/almost-half-of-customer-enquires-to-leading-uk-travel-companies-fail-to-get-a-response/) (vendor; customer-service, not sales leads; includes social channels) |
| Eptica, travel firms (UK) | 2013 | 10 travel firms within 100 companies | routine questions by email | travel firms answered 30% of emailed questions (50% the year before); replies 19 min to 5 days | [Travolution](https://travolution.com/articles/6870/eptica-study-suggests-falling-customer-service-levels-on-email-in-travel) (vendor; customer service) |
| Kuzma, tourism agencies in 8 developing countries | 2011 | 200 agencies | email enquiry | 30% response | [Worcester repository](https://eprints.worc.ac.uk/1469) (academic conference paper; abstract only) |
| Tunisian hotels | 2003 | 260 hotels | room enquiry by email | 1 in 10 replied within a day | [Emerald abstract](https://emerald.com/insight/content/doi/10.1108/eb058405/full/html) (academic) |
| SafariBookings (safari quote marketplace) | undated | its partner operators | operator help pages | recommends replying within 4 hours; partners book about 1 in 5 to 6 requests; about 20% of travellers never reply to the operator | search-result snippet of [SafariBookings help centre](https://help.safaribookings.com/hc/en-150/categories/16984062191645-Quote-Requests-Performance); page behind a Cloudflare challenge, not read in full |

The only safari-specific figure found describes the traveller going silent (about 20%), not the operator
neglecting the lead. That is the lead's side of the first **Transition** after a **Contact attempt**, not
neglect. A claim that "60% of travel inquiries never receive a response" appears on
[rework.com](https://resources.rework.com/vi/libraries/travel-tour-growth/travel-inquiry-management) with no
source; it is not used.

Caveats for using audits as neglect rates:

- An audit counts one test enquiry per firm. A **Neglected lead** in the profile is a share of one advertiser's
  leads. The audit number is a mix of firms that neglect nearly everything and firms that neglect nearly nothing.
  A profile that varies neglect between simulated advertisers matches this better than one fixed rate.
- Advertisers who buy ads and pay for scoring are probably more attentive than the average audited firm, and a
  tailor-made safari enquiry is worth more than a typical web lead, so the planned-hospitality middle should sit
  below the general audits (estimated, see table).
- Customer-service audits (CM.com, Eptica) count questions, not sales enquiries; they are upper bounds.

#### Is neglect driven by lead quality?

Evidence that it is mostly not:

- Audits send identical enquiries to many firms, so the spread they show (from replies within 5 minutes to no
  reply) is the firm's behaviour ([HBR](https://hbr.org/2011/03/the-short-life-of-online-sales-leads),
  [Drift via summary](https://ainora.lt/blog/lead-response-time-statistics-every-study-2026)).
- DelPrete found service "consistently inconsistent" with "no rhyme or reason", including within one brokerage
  tested 2 to 3 times ([mikedp.com](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored)).
- Quality Track found little or no difference across hotel tiers ([Hospitality Upgrade](https://www.hospitalityupgrade.com/news/blowing-the-basics-hotel-sales-managers-fail-to-respond-to-customer-inquiries-more-than-25-of-the-time)).
- Availability drives it: hotel sales managers were reachable only 49.4% of the time (same source). Day of week
  and time of day change contact rates by 50% to 114% in the MIT/InsideSales data
  ([MIT study PDF](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf)), and
  enquiries left at a weekend or evening wait until the next working day (franchise example, vendor:
  [FranFunnel](https://www.franfunnel.com/blog/franchise-leads-after-hours-weekends)). Only 20% of UK tour
  operators offer 24-hour contact and 48% office hours only ([CM.com](https://www.cm.com/en-gb/press/almost-half-of-customer-enquires-to-leading-uk-travel-companies-fail-to-get-a-response/)).

Evidence that some of it is:

- Group/MICE RFPs: hotels often do not reply when they have no availability or the event does not fit
  ([Hospitality Net](https://www.hospitalitynet.org/news/4118318.html) argues hotels should reply to every RFP,
  implying many deliberately do not). For an event agency or DMC this would show up as a lead quietly dropped,
  which is a judgement on fit, not neglect.
- Teams triage by how a lead looks (a vague one-line enquiry vs a detailed one). No quantitative study of this was
  found; it is plausible and should be a planted, small effect at most (guessed).

No source was found on staff turnover, holidays or peak-season workload as causes of neglect. For safari
operators, workload plausibly peaks when travellers plan (and when the team is on trips or at trade shows);
this is guessed.

### 2. Speed to first contact attempt

- HBR 2011: of all firms, 37% within 1 h, 16% in 1 to 24 h, 24% over 24 h, 23% never. Among responders only:
  37/77 = 48% within 1 h, 16/77 = 21% in 1 to 24 h, 24/77 = 31% over 24 h (estimated from
  [HBR figures](https://scholarsarchive.byu.edu/facpub/9711)). Mean 42 h.
- InsideSales 2016: mean 38 h 35 min ([B2B Marketing](https://www.b2bmarketing.net/half-of-sales-leads-never-receive-personalised-response/)).
  InsideSales ResponseAudit: mean near 47 h over five years ([InsideSales](https://www.insidesales.com/responseaudit-research-aa-isp-2012/)).
- DelPrete 2024 (weekday business hours only): mean 8 h 17 min, median 39 min. The gap between mean and median
  shows a heavy right tail ([mikedp.com](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored)).
- MICE: Amadeus survey of 315+ hotel and venue sales leaders: mean RFP reply 4.84 days (March 2025) and 5.08
  days (March 2026); planners expect about 4 business days
  ([AltexSoft news summary](https://www.altexsoft.com/travel-industry-news/hotels-risk-group-bookings-with-slow-replies/)).
- Travel practice: SafariBookings advises replying within 4 hours (snippet, above); Responsible Travel advises
  24 h, 48 h at the latest, noting some operators target 3 h
  ([Responsible Travel](https://www.responsibletravel.com/copy/best-practice-for-converting-leads-into-bookings)).
- Speed matters for the lead's outcome, which the **Lead simulator** must keep separate from the lead's quality:
  odds of reaching a lead fall about 100 times from 5 to 30 minutes and qualifying falls 21 times
  ([MIT study PDF](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf), vendor data,
  six companies, mostly phone-led mortgage and insurance; unlikely to carry over at that size to emailed safari
  enquiries).

A log-normal delay with a median of a few hours and a long tail fits these shapes; the parameters below are
estimated.

### 3. Contact attempts before giving up

- InsideSales ResponseAudit (AA-ISP 2012): reps attempted contact 1.30 times on average; 87% of responses by
  email; about half of leads answered only by email ([InsideSales](https://www.insidesales.com/responseaudit-research-aa-isp-2012/)).
- "The average rep makes 1.2 call-back attempts" is widely attributed to MIT/InsideSales; the primary was not
  found ([search snippet](https://www.natlawreview.com/article/best-practices-responding-to-online-leads)). Not
  used beyond agreeing with 1.3.
- Velocify (vendor platform data): about 50% of leads are never called a second time; 93% of leads that convert
  are reached by the sixth call ([Velocify on SlideShare](https://www.slideshare.net/Velocify/the-ultimate-contact-strategy), via search snippet).
- InsideSales 2016: 77% of leads never got a phone call ([B2B Marketing](https://www.b2bmarketing.net/half-of-sales-leads-never-receive-personalised-response/)).
- Travel: Responsible Travel advises a follow-up system within a week ([Responsible Travel](https://www.responsibletravel.com/copy/best-practice-for-converting-leads-into-bookings)).

For planned hospitality the first **Contact attempt** is usually an emailed reply or a proposal draft, sometimes
a call; a lead who does not answer typically gets one to three follow-up emails (guessed from the above).

### 4. Do sales systems record contact attempts at all?

- Weflow (vendor, observed across "hundreds of Salesforce orgs"): where logging depends on an Outlook or Gmail
  add-in, 24% to 52% of activity reaches the CRM ([Weflow](https://www.weflow.ai/blog/half-your-salesforce-fields-are-empty)).
- Avoma (vendor): manual logging captures under 28% of emails and meetings; no method given
  ([Avoma](https://www.avoma.com/blog/salesforce-activity-capture)). Weak.
- Beagle Research Group for Oracle, 500+ US B2B sellers, 2020: 47% use their CRM regularly, 40% as intended;
  66% would rather do a chore than update it; 46% use non-standard workarounds
  ([SalesTechStar](https://salestechstar.com/sales-marketing/new-study-66-of-sellers-would-rather-clean-the-bathroom-than-update-their-crm-system/)).
- Freshworks own survey of 600 US business people, April 2024: 71% of businesses under 500 staff use a CRM
  ([Freshworks](https://freshworks.com/theworks/insights/crm-statistics)). Vendor; "use a CRM" says nothing about
  logging activities.
- Travel: vendor blogs describe operators running enquiries from spreadsheets and email threads until volume
  forces a CRM (one cites trouble at about 200 leads a month)
  ([InsideA](https://insidea.com/spotlight/blog/crm-for-tourism/when-should-a-travel-agency-move-from-excel-to-crm/),
  [Tourwriter](https://www.tourwriter.com/?p=21039)). Qualitative only; no survey of safari operators' systems was
  found.

Implication for the profile: three export shapes are realistic, in roughly guessed proportions: (a) activities
logged per lead (attempt dates and channel), (b) only a **CRM stage** such as "Contacted" or "Quote sent" with
a last-modified date, (c) a spreadsheet with free-text notes and progress columns and no dates. Decision 0002
already plans for (b) and (c): the first **Transition** stays unfinished until a later **Stage** appears.

### 5. Data mess

#### Duplicates

- "10% to 30% of CRM records are duplicates" is repeated across vendor blogs with no primary
  ([Landbase](https://www.landbase.com/blog/duplicate-record-rate-statistics),
  [Databar](https://databar.ai/blog/article/duplicate-record-management-in-crm-the-hidden-revenue-killer-and-how-to-fix-thousands-fast)).
  An "average 18%" is attributed to Dun & Bradstreet (snippet; primary not found).
- Plauti (dedupe vendor) reported over 45% of new records entering Salesforce in 2021 as duplicates, from 12
  billion records; the page now returns 410 Gone ([Plauti](https://plauti.com/blog/2021-average-rate-duplicates-crm), via search snippet).
  This counts records from integrations and imports, not inbound enquiries.
- Planned hospitality has a specific source of repeat leads: the same traveller enquires again (new dates,
  another channel, a partner submits too), and travellers are told to contact several operators (SafariBookings
  suggests three, up to five; search snippet of [SafariBookings](https://www.safaribookings.com/request-quote/p1981)).
  Contacting several operators makes duplicates across advertisers (a **Cross-advertiser history** matter), not
  within one export.

#### Spam, bot and fake submissions

- CHEQ (vendor), 2023 traffic: 17.9% of observed traffic invalid; lead-generation sectors about 29% to 32%
  (real estate about 29%) ([CHEQ report PDF](https://cheq.ai/wp-content/uploads/2024/03/State-of-Fake-Traffic-2024.pdf); figures via search snippet, PDF too large to fetch).
- Imperva Bad Bot Report: travel had 44.5% bad-bot traffic in 2023
  ([Travel Weekly](https://travelweekly.co.uk/news/air/half-of-online-travel-traffic-automated-and-44-malicious))
  and 41% in 2024 ([Imperva via Intelligent CIO](https://www.intelligentcio.com/me/2025/04/20/ai-fuels-hard-to-detect-bots-that-generate-half-of-internet-traffic-says-imperva/)).
  This is mostly fare scraping and account attacks, not enquiry forms.
- Contact State (UK lead-validation vendor, financial quote forms): 5% of leads rejected as fake data per month
  in 2022, 9.7% in January 2023; consumers give fake details to avoid sales calls
  ([Financial Reporter](https://www.financialreporter.co.uk/consumers-inputting-fake-data-into-quote-forms-for-fear-of-becoming-a-lead.html)).
- No vendor publishes the share of enquiry-form submissions that are spam after captcha. Traffic numbers are
  upper bounds; what reaches an export is much lower.

#### Invalid emails and phones

- ZeroBounce (email-verification vendor): 24.3% of addresses it checked were invalid, and its form API caught
  over 10 million typos ([ZeroBounce](https://zerobounce.net/email-list-decay)). Biased upward: lists sent for
  verification are suspect lists, and many are old.
- Contact State's 5% to 10% fake-data rate (above) includes fake phone numbers.
- Travel enquiry forms often make the phone number optional, so the phone is more often missing than invalid
  (guessed; see `enquiry-forms.md`).

#### Missing values and wrong entries

- Firmable survey of 222 B2B sales professionals: about 32% of records inaccurate, incomplete or outdated (their
  own estimate) ([PPC Land](https://ppc.land/b2b-sales-teams-estimate-32-of-their-crm-data-is-flawed-firmable-finds/)).
- "91% of CRM data is incomplete" is attributed to Salesforce in Dun & Bradstreet brochures; no primary found.
  Not used.
- Validity 2022, 1,241 CRM administrators (US, UK, Australia; travel among industries): 75% say staff fabricate
  data to tell the story they want; 44% lose over 10% of revenue to poor data
  ([Validity](https://www.validity.com/press-releases/validity-launches-2022-state-of-crm-data-health-report-finds-data-confidence-does-not-match-reality/)).
- Beagle/Oracle 2020: 85% of sellers made mistakes because of faulty CRM data; 33% called someone by the wrong
  name ([SalesTechStar](https://salestechstar.com/sales-marketing/new-study-66-of-sellers-would-rather-clean-the-bathroom-than-update-their-crm-system/)).

#### Skipped stages, late or bulk updates, stale open leads, back-dated entries

- No quantitative primary source found for stage skipping or for the delay between an event and its entry.
  Vendor writing describes updates gathered in a "scramble before each review"
  ([Attention](https://wf-origin.attention.com/blog-posts/sales-teams-hate-crm-data-entry-heres-how-to-make-it-effortless)),
  i.e. bulk updates before a weekly pipeline meeting.
- Stale pipeline: a Fullcast analysis (vendor, snippet) found 67% of enterprise software opportunities over
  $250,000 past their expected close date ([Coffee](https://www.coffee.ai/articles/sales-pipeline-mistakes-forecasting-accuracy)).
  Not travel and not small business.
- Weflow: reps log less "during high-activity deal periods" ([Weflow](https://www.weflow.ai/blog/half-your-salesforce-fields-are-empty)),
  which means mess is worst when the most is happening (peak season for an operator).

Mess the **Lead simulator** should therefore produce, with guessed rates: leads jumping from Submitted straight
to Proposal or Won; several **Stage** changes stamped with the same date (bulk); stage dates days after the
event; leads that went silent left at their last stage instead of Lost; won deals with no **Deal value**; lost
leads with no **Loss reason**.

## Numbers for the profile

"General" means the source is not travel-specific. Shares are of one advertiser's leads unless stated.

| quantity | low | middle | high | confidence | source |
|---|---|---|---|---|---|
| Share of leads that become a **Neglected lead** (never any **Contact attempt**), per advertiser | 3% | 15% | 45% | estimated: general audits give 23% to 55% ([HBR](https://scholarsarchive.byu.edu/facpub/9711), [destinationCRM](https://www.destinationcrm.com/Articles/CRM-News/CRM-Featured-Articles/Can-I-Call-You-Back-Later-48699.aspx), [B2B Marketing](https://www.b2bmarketing.net/half-of-sales-leads-never-receive-personalised-response/), [mikedp](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored)); hotel sales over 25% ([Hospitality Upgrade](https://www.hospitalityupgrade.com/news/blowing-the-basics-hotel-sales-managers-fail-to-respond-to-customer-inquiries-more-than-25-of-the-time)); high end matches those; middle set below the 23% to 25% lower audits because paying advertisers and high-value enquiries are likely more attended (judgement); low end guessed |
| Spread of neglect between advertisers | some near 0% | | some near 50% | estimated: audits show firms from 5-minute replies to none on identical leads ([HBR](https://scholarsarchive.byu.edu/facpub/9711), [mikedp](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored)) |
| MICE / group enquiries with no reply (includes deliberate declines) | 25% | 40% | 55% | estimated: 25%+ hotel sales ([Hospitality Upgrade](https://www.hospitalityupgrade.com/news/blowing-the-basics-hotel-sales-managers-fail-to-respond-to-customer-inquiries-more-than-25-of-the-time)), 55% of RFPs ignored ([Hospitality Net](https://www.hospitalitynet.org/news/4118318.html), vendor); part is a quality decision, not neglect |
| Share of neglect that depends on how good the lead looks (rest is workload, weekends, staff) | 0% | 10% | 25% | guessed: audits point to firm behaviour; RFP declines and triage point to some quality link |
| Delay to first **Contact attempt**, median (among attempted leads) | 30 min | 4 h | 24 h | estimated: median 39 min in weekday-hours real estate audit ([mikedp](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored)); 48% of HBR responders within 1 h; operator advice 4 h to 48 h ([Responsible Travel](https://www.responsibletravel.com/copy/best-practice-for-converting-leads-into-bookings)) |
| Delay to first attempt, mean (among attempted leads) | 8 h | 30 h | 5 days | estimated: means 8 h 17 min ([mikedp](https://www.mikedp.com/articles/2024/8/13/secret-shopping-47-of-online-property-inquiries-are-ignored)), 38 h to 47 h ([B2B Marketing](https://www.b2bmarketing.net/half-of-sales-leads-never-receive-personalised-response/), [InsideSales](https://www.insidesales.com/responseaudit-research-aa-isp-2012/), [HBR](https://scholarsarchive.byu.edu/facpub/9711)); MICE RFPs about 5 days ([AltexSoft/Amadeus](https://www.altexsoft.com/travel-industry-news/hotels-risk-group-bookings-with-slow-replies/)) |
| Share of attempted leads first attempted after more than 24 h | 10% | 30% | 45% | estimated: 24/77 = 31% of HBR responders ([HBR](https://scholarsarchive.byu.edu/facpub/9711)); high end allows weekends and peak season (guessed) |
| Extra delay for leads submitted on a weekend or after hours | until next working morning | | until next working morning plus 1 day | guessed; supported qualitatively ([CM.com](https://www.cm.com/en-gb/press/almost-half-of-customer-enquires-to-leading-uk-travel-companies-fail-to-get-a-response/): 48% office hours only) |
| **Contact attempts** before giving up on a lead that never answers | 1 | 2 | 5 | estimated: mean 1.3 ([InsideSales](https://www.insidesales.com/responseaudit-research-aa-isp-2012/)); about half never get a second call ([Velocify](https://www.slideshare.net/Velocify/the-ultimate-contact-strategy), vendor); high end for diligent teams (guessed) |
| Share of first attempts by email (rest phone, messaging) | 60% | 80% | 95% | estimated: 87% of responses by email ([InsideSales](https://www.insidesales.com/responseaudit-research-aa-isp-2012/)); 77% of leads never phoned ([B2B Marketing](https://www.b2bmarketing.net/half-of-sales-leads-never-receive-personalised-response/)); general |
| Share of attempted leads who never reply to the advertiser | 10% | 20% | 35% | estimated middle (SafariBookings help centre, search snippet only, [link](https://help.safaribookings.com/hc/en-150/categories/16984062191645-Quote-Requests-Performance) (not read in full: 403 and Cloudflare check on 2026-10-01)); range guessed. This is the lead's behaviour, not neglect |
| Share of advertisers whose export records contact attempts at all (per-lead activity with dates) | 15% | 40% | 70% | guessed, informed by 47% of sellers using CRM regularly ([SalesTechStar](https://salestechstar.com/sales-marketing/new-study-66-of-sellers-would-rather-clean-the-bathroom-than-update-their-crm-system/)) and travel operators on spreadsheets and inboxes (qualitative) |
| Where attempts are logged, share of real attempts that appear | 25% | 50% | 80% | estimated: 24% to 52% observed with manual add-ins ([Weflow](https://www.weflow.ai/blog/half-your-salesforce-fields-are-empty), vendor); high end for automatic email capture (guessed) |
| Duplicate lead rows within one advertiser's export (same person, re-submitted or second channel) | 2% | 8% | 20% | estimated: CRM-wide 10% to 30% ([Landbase](https://www.landbase.com/blog/duplicate-record-rate-statistics), vendor, unsourced) covers all records, not only enquiries; enquiries alone likely lower (judgement) |
| Spam or bot rows that reach the export | 0.5% | 4% | 15% | estimated: invalid traffic 18% to 45% is an upper bound before filtering ([CHEQ](https://cheq.ai/wp-content/uploads/2024/03/State-of-Fake-Traffic-2024.pdf), [Travel Weekly/Imperva](https://travelweekly.co.uk/news/air/half-of-online-travel-traffic-automated-and-44-malicious)); fake-data rejects 5% to 10% after submission ([Financial Reporter](https://www.financialreporter.co.uk/consumers-inputting-fake-data-into-quote-forms-for-fear-of-becoming-a-lead.html)); middle and low guessed |
| Genuine leads with an invalid or mistyped email | 1% | 3% | 8% | estimated: Contact State 5% to 10% fake data (includes phones) ([Financial Reporter](https://www.financialreporter.co.uk/consumers-inputting-fake-data-into-quote-forms-for-fear-of-becoming-a-lead.html)); ZeroBounce 24% invalid is a biased upper bound ([ZeroBounce](https://zerobounce.net/email-list-decay)) |
| Genuine leads with an invalid phone (where a phone is given) | 2% | 6% | 15% | guessed, informed by Contact State 5% to 10% (general, financial quote forms) |
| Records with at least one key field inaccurate, incomplete or outdated | 15% | 30% | 50% | estimated: 32% by sales pros' own estimate ([PPC Land/Firmable](https://ppc.land/b2b-sales-teams-estimate-32-of-their-crm-data-is-flawed-firmable-finds/)); general, B2B |
| Won leads with no **Deal value** recorded | 2% | 10% | 30% | guessed |
| Lost leads with no **Loss reason** | 30% | 55% | 80% | guessed |
| Leads that advance and skip at least one **Stage** of the **Canonical ladder** in the export | 20% | 40% | 70% | guessed (no source found) |
| Stage changes entered late: lag between event and its recorded date | 0 days | 2 days | 14 days | guessed; bulk updating before reviews described qualitatively ([Attention](https://wf-origin.attention.com/blog-posts/sales-teams-hate-crm-data-entry-heres-how-to-make-it-effortless)) |
| Share of stage changes made in bulk (same timestamp as several others) | 5% | 20% | 40% | guessed |
| Dead leads left open at their last stage at export time (never set to Lost) | 10% | 30% | 60% | guessed; general signal of stale pipelines ([Coffee/Fullcast](https://www.coffee.ai/articles/sales-pipeline-mistakes-forecasting-accuracy), vendor, enterprise software) |

## Open questions

1. **Neglect and lead quality.** The audits suggest neglect is mostly the advertiser's behaviour, but RFP
   declines and inbox triage suggest some link to how a lead looks. How large a link should the profile plant?
   Decision 0002 says neglect never counts against the lead; a small planted link would test whether Emva
   stays fair when that assumption is slightly wrong. Also: field experiments elsewhere (e.g. housing) find
   reply rates differ by the enquirer's perceived traits; not researched here, but relevant to **Prohibited
   inputs** if neglect in the simulator ever depends on them.
2. **No safari-specific neglect data.** A small mystery-shop of real safari operators would answer this, but it
   means sending fake enquiries to real businesses. Is that acceptable, or should the profile keep the wide
   range? (Asking a pilot advertiser for their own neglect rate is the cleaner path.)
3. **MICE vs leisure.** Should corporate trips and events be a separate sub-profile? Their non-response is
   higher and partly deliberate, and their replies are slower (days, not hours).
4. **Which export shape is the default?** Activities logged, stage only, or spreadsheet with notes. The guessed
   40% middle for "records attempts at all" decides how often the first **Transition** is unobservable.
5. **Speed effect on the lead.** The MIT/InsideSales speed effect (100 times) comes from phone-led mortgage and
   insurance leads. For emailed safari enquiries it is likely far smaller; the strength of a planted
   "slow reply lowers the chance to engage" effect needs its own range (overlaps `what-predicts-a-booking.md`).
6. **Sources not read in full:** HBR 2011 article, Drift 2017 post, CHEQ 2024 PDF, Validity 2022 PDF,
   SafariBookings help pages, Plauti 2021 post. Figures from them came from search snippets or secondary pages
   and should be checked before the profile cites them as sourced.
