# Cinesis Good Fit Test

**Extraction (Part A):** `extract_profile.py` calls Claude with a structured-JSON prompt against the raw transcript, since the role is explicitly about LLM-based extraction from messy conversation. Current location (Dallas) and minimum rate ($2/mile) are stated directly. Home base (San Antonio) comes from the dispatcher's question, which the driver confirms. Equipment is stated directly as "hotshot gooseneck trailer," interpreted as excluding flatbed and van even though both came up earlier in the call as related categories. Weight capacity (16,000 lb) is not stated, it is inferred from typical non-CDL hotshot/gooseneck limits and used only as a generous filter ceiling, it does not bind any load in this dataset.

**Missing rows (Part B):** L06 (missing price) and L07 (missing destination) cannot produce a valid effective-rate calculation, so they are skipped and logged with a reason rather than guessed at or silently dropped.

**Rejected high-rate load:** L05 (Waco to San Antonio, Flatbed, $640) produces a strong 2.514 $/mile, high enough to outrank L02 on rate alone. It is excluded because the driver runs hotshot/gooseneck only, not flatbed. Ranking on rate before filtering on equipment would have put a non-matching trailer type in the top 3.


