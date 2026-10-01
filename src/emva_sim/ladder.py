"""The Canonical ladder's Stage names, as CONTEXT.md and the profile's pipeline write them."""

SUBMITTED = "Submitted"
CONTACT_ATTEMPTED = "Contact attempted"
ENGAGED = "Engaged"
QUALIFIED = "Qualified"
PROPOSAL = "Proposal"
WON = "Won"
LOST = "Lost"

# The Stages after Contact attempted; the profile names each transition by its Stage, in lower case.
AFTER_CONTACT = (ENGAGED, QUALIFIED, PROPOSAL, WON)
