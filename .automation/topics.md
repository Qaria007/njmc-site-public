# Insights topic queue

The writer takes the **first topic whose slug has no matching file** at the
repository root. When a topic is used, its article exists, so it is skipped
automatically on the next run. No editing is required to advance the queue.

Refilling this list is the recurring human task. When fewer than four unused
topics remain, add more.

A topic belongs here only if it can be written **without stating a regulatory
figure and without any claim about NJMC**. If a topic can only be written well
by quoting a threshold, a fee or a timeline, it does not belong in this queue.

Every topic carries a **registered target query** (what a buyer types into a
search engine) and an **AEO question** (what a buyer asks an assistant, and the
exact H2 above the direct answer). A topic without both is not ready to write.
The order below is the writer's order. **Reordering it by live search data is
the weekly cycle's job, done from the Mac with Search Console access, not the
cloud writer's**, which has no network and must never guess at demand.

| # | Slug | Badge | Working title (EN) | Target query | AEO question (the direct-answer H2) |
|---|------|-------|--------------------|--------------|-------------------------------------|
| 16 | `insights-hospitals-sourcing-from-china` | Sourcing | How hospitals can source from Chinese suppliers | healthcare institutions sourcing china suppliers | How can a hospital source from Chinese suppliers and control the risk? |
| 17 | `insights-qualifying-excipient-suppliers` | Sourcing | Excipient sourcing: how to qualify the supplier, not only the material | excipient sourcing supplier qualification | How do you qualify an excipient supplier before the first order? |
| 18 | `insights-lot-records-receiving-materials` | Quality | What to record for each lot when APIs and excipients arrive | receiving api excipients lot number documentation | What should be recorded for each lot when APIs and excipients are received? |
| 11 | `insights-free-sale-certificates-legalisation` | Documentation | Free sale certificates, legalisation and the paperwork that delays a shipment | free sale certificate legalisation medical import | What is a free sale certificate and when does it need legalising? |
| 12 | `insights-change-control-supplier-changes` | Quality | When your supplier changes something, what reaches your filing | supplier change control pharmaceutical filing | When a supplier changes something, what reaches your regulatory filing? |
| 13 | `insights-cold-chain-medical-shipments` | Logistics | Temperature sensitive shipments: the qualification a buyer should ask about | cold chain qualification medical shipments | What qualification should you ask for on a temperature sensitive shipment? |
| 14 | `insights-packaging-labelling-pharma-imports` | Documentation | Packaging and labelling documents that customs and the regulator each want | pharmaceutical import packaging labelling documents | Which packaging and labelling documents do customs and the regulator each want? |
| 19 | `insights-verify-medical-supplier-china` | Sourcing | Checks to make on a medical supplier in China before paying | how to verify medical supplier china | How do you verify a medical supplier in China before paying? |
| 20 | `insights-checking-iso-13485-certificate` | Medical Devices | Reading an ISO 13485 certificate: does it cover your product? | how to verify iso 13485 certificate | How do you check that an ISO 13485 certificate is valid and covers your product? |
| 21 | `insights-choosing-medical-device-distributor` | Medical Devices | What a manufacturer should check before appointing a distributor | how to choose medical device distributor | What should a manufacturer check before appointing a medical device distributor? |
| 22 | `insights-exclusive-distribution-terms` | Sourcing | Exclusive distribution of medical products: the terms worth settling first | exclusive distribution agreement medical products | Which commercial and regulatory terms should be settled before agreeing exclusive distribution? |
| 23 | `insights-sample-evaluation-medical-consumables` | Medical Consumables | Evaluating a consumable sample before a bulk order | evaluate medical consumables samples before bulk order | What should you check in a medical consumable sample before a bulk order? |
| 24 | `insights-pre-shipment-inspection-medical-goods` | Logistics | What a pre-shipment inspection of medical goods should cover | pre shipment inspection medical devices | What should a pre-shipment inspection of medical goods cover? |
| 25 | `insights-lab-equipment-iq-oq-pq` | Quality | Installation, operational and performance qualification for lab equipment | iq oq pq laboratory equipment | What do IQ, OQ and PQ mean when you buy laboratory equipment? |
| 26 | `insights-quality-complaint-overseas-supplier` | Quality | When a shipment fails: raising a quality complaint with an overseas supplier | quality complaint overseas supplier capa | How do you raise a quality complaint with an overseas supplier and get a corrective action? |

Scope limits for the writer:

- Row 17: the supplier qualification process only; do not repeat `insights-excipient-gmp-ipec`.
- Row 18: the content of the receipt record only; do not repeat the checks in `insights-incoming-goods-inspection`; give no retention periods.
- Row 19: device and consumable suppliers only; do not repeat `insights-manufacturer-or-trader` or `insights-sourcing-apis-from-china-india`; no device class tiers, no deposit percentages.
- Rows 19, 24: do not quote NJMC fees, even those shown on the site.
- Row 22: business and regulatory terms only; state nothing about what any country's law requires; tell the reader to take local legal advice.

Rows 16 to 18 were put first on 7 Nov 2026 from Search Console impressions (15 Oct to 4 Nov). Apart from the brand name, the largest query was certificate of analysis vs conformance, already covered by a published article. Rows 16 to 18 rest on very small counts. Rows 19 to 26 follow the older rows.

Rows C1 to C3 were put first on 16 Oct 2026 at the owner's request: NJMC is now the front door for the PharmaTrust certificate check (njmcmedicsupp.com/certificate-check/), so certificate of analysis topics come first.

## Badges in use on the live site

`Active Pharmaceutical Ingredients`, `Documentation`, `Sourcing`, `Quality`,
`Medical Devices`, `Medical Consumables`, `Logistics`. Reuse an existing badge
rather than inventing a new one.

## Used

- `insights-api-impurity-profiles` — published 25 August 2026; query `api impurity profile certificate of analysis`; question "How do you read an API impurity profile against its specification?"
- `insights-api-polymorphism-particle-size` — published 4 September 2026; query `api polymorphic form particle size`; question "Why does the polymorphic form of an API matter if it meets the monograph?"
- `insights-reading-a-gmp-certificate` — published 8 September 2026; query `how to read a gmp certificate`; question "What does a GMP certificate actually prove?"
- `insights-manufacturer-or-trader` — published 15 September 2026; query `manufacturer vs trading company pharmaceutical`; question "How do you tell a manufacturer from a trading company before ordering?"
- `insights-quality-agreements-api-supply` — published 22 September 2026; query `quality agreement api supplier`; question "What should a quality agreement with an API supplier contain?"
- `insights-retest-date-and-expiry` — published 29 September 2026; query `api retest date vs expiry date`; question "What is the difference between a retest date and an expiry date?"
- `insights-incoming-goods-inspection` — published 6 October 2026; query `incoming goods inspection pharmaceutical`; question "What should you check when imported pharmaceutical material arrives?"
- `insights-residual-solvents-elemental-impurities` — published 13 October 2026; query `residual solvents elemental impurities api`; question "Why are residual solvents and elemental impurities controlled separately?"
- `insights-how-to-check-a-certificate-of-analysis`, published 16 October 2026; query `how to check a certificate of analysis`; question "How do you check a supplier's certificate of analysis before you buy?"
- `insights-what-a-certificate-of-analysis-must-contain`, published 16 October 2026; query `certificate of analysis requirements`; question "What must a certificate of analysis for an API or excipient contain?"
- `insights-certificate-of-analysis-vs-conformance`, published 16 October 2026; query `certificate of analysis vs certificate of conformance`; question "What is the difference between a certificate of analysis and a certificate of conformance?"
- `insights-device-technical-file`, published 20 October 2026; query `medical device technical file contents`; question "What is in a medical device technical file and what can a buyer see?"
- `insights-sterilisation-single-use-consumables`, published 27 October 2026; query `sterilisation methods single use medical consumables`; question "How are single use medical consumables sterilised and validated?"
- `insights-remote-supplier-audits`, published 3 November 2026; query `remote supplier audit limitations`; question "What can a remote supplier audit establish?"
