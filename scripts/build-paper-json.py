# -*- coding: utf-8 -*-
import json, re, io, os

PAPER = "/home/nandan/Documents/survey-sampling-with-ads/paper"
JUL   = "survey-sampling-with-ads-Jul2026.tex"
JMR   = "JMR_submission_09152025.tex"
SSRN  = "SSRN_09152025.tex"

src = open(os.path.join(PAPER, JUL), encoding="utf-8").read()
abstract = re.search(r"\\begin\{abstract\}(.*?)\n\n", src, re.S).group(1).strip().replace("\\$", "$")

doc = {
  "_meta": {
    "generated": "2026-08-20",
    "generated_by": "workstream: mine the paper into a structured data file",
    "purpose": "Source data for the Papers page (D-016) and the Home validation section. Every value below is quoted from the manuscript. Nothing is computed, inferred or filled in unless the field says so explicitly.",
    "read_before_use": [
      "CLAIMS.md is still the authority on what may be published. This file records what the paper SAYS; it does not grant permission to print it.",
      "C-004 is unresolved-and-then-withdrawn: per Nandan (2026-08-20) no cost-per-question figure ships at all. cost_table below is faithful to the paper but its per-question column must not be rendered on the site. See notes.publication_constraints.",
      "The paper reports NO standard errors, confidence intervals or significance tests on any MAD. Do not draw intervals."
    ],
    "paper_directory_actual": "/home/nandan/Documents/survey-sampling-with-ads/paper",
    "paper_directory_as_recorded_in_CLAIMS_md": "../../survey-sampling-with-ads/paper (relative to vlab.digital) -> /home/nandan/Documents/vlab-research/survey-sampling-with-ads/paper -- THIS PATH DOES NOT EXIST. The repo sits at /home/nandan/Documents/survey-sampling-with-ads, i.e. ../../../survey-sampling-with-ads. See ws-paper.md drift D-1."
  },

  "editions": [
    {
      "id": "Jul2026",
      "file": "survey-sampling-with-ads-Jul2026.tex",
      "filename_implies_year": 2026,
      "latex_date_command": "September 15, 2025",
      "role": "Working manuscript. The edition CLAIMS.md cites. Identified in the paper repo's PLAN.md as 'source of truth for the manuscript (live)'.",
      "differs_from_submission_in": [
        "Adds the per-stratum variance sigma_h^2 to the allocation problem (submission assumed equal variance across strata); adds the KKT derivation and the cost-aware optimal allocation n_h*.",
        "Algorithm retitled 'Optimizing Stratified Recruitment with Unknown Costs and Variances' and gains variance estimation steps.",
        "Future-work section rewritten: two avenues become one (adaptive stratification-variable selection).",
        "Competing-interest wording anonymized to 'One author ...' (see disclosures).",
        "Author block with names and affiliations restored (absent from the JMR submission, which is blinded)."
      ],
      "identical_to_submission_in": [
        "title", "abstract", "keywords", "all MAD values", "all cost values",
        "benchmark sources and years", "IRB number", "international-deployment figures",
        "Prolific sample size and field dates"
      ]
    },
    {
      "id": "JMR_submission_09152025",
      "file": "JMR_submission_09152025.tex",
      "latex_date_command": "September 15, 2025",
      "role": "As submitted to the Journal of Marketing Research. Blinded: no author block, companion manuscript cited as '[citation omitted]'.",
      "journal_status_evidence": "The paper repo's PLAN.md line 14 states: manuscript JMR-25-0847, a 'risky' major revision with a six-month extension granted. Not accepted, not in press."
    },
    {
      "id": "SSRN_09152025",
      "file": "SSRN_09152025.tex",
      "latex_date_command": "September 15, 2025",
      "role": "SSRN edition. Byline present. Competing-interest note names both authors.",
      "ssrn_id_found": False,
      "ssrn_id_note": "No SSRN abstract ID, DOI or URL appears anywhere in this file, in any other edition, in the .bib files, or elsewhere in the paper repository. There is nothing publicly linkable recorded locally. See ws-paper.md, 'Citation year'."
    },
    {
      "id": "Jan2025",
      "file": "survey-sampling-with-ads-Jan2025.tex",
      "latex_date_command": "September 15, 2025",
      "role": "Fourth edition, present in the directory but not named in CLAIMS.md. Byte-different from SSRN_09152025.tex but carries the same named competing-interest wording. Recorded here only so a later agent does not think it is new.",
      "in_scope": False
    }
  ],

  "title": {
    "value": "Adaptive Survey Sampling via Ad Platforms",
    "source_edition": "Jul2026",
    "source_file": "survey-sampling-with-ads-Jul2026.tex",
    "source_line": 69,
    "verbatim_latex": "\\title{{\\Huge Adaptive Survey Sampling  via Ad Platforms}\\thanks{...}}",
    "transform_note": "The LaTeX has a double space between 'Sampling' and 'via'; normalized to one. \\Huge is a size command, dropped. Identical in all three editions."
  },

  "authors": [
    {
      "name": "Dante Donati",
      "affiliation": "Columbia Business School and CESifo",
      "email": "dd3137@gsb.columbia.edu",
      "source_edition": "Jul2026",
      "source_line": 74
    },
    {
      "name": "Nandan Rao",
      "affiliation": "Virtual Lab and Universitat Aut\u00f2noma de Barcelona",
      "email": "nandan@vlab.digital",
      "source_edition": "Jul2026",
      "source_line": 74
    }
  ],
  "authors_note": "Order as printed. Affiliations are the \\thanks footnotes attached to each name, verbatim. The JMR submission edition is blinded and carries no author block; SSRN and Jan2025 carry the same two lines as Jul2026.",

  "abstract": {
    "verbatim": abstract,
    "source_edition": "Jul2026",
    "source_file": "survey-sampling-with-ads-Jul2026.tex",
    "identical_in": ["Jul2026", "JMR_submission_09152025", "SSRN_09152025"],
    "transforms_applied": [
      "\\$ -> $ (LaTeX escaped dollar sign), one occurrence: '$0.30'.",
      "No other macro appears in the abstract body. No \\emph, \\textit, \\cite or math.",
      "U+2019 RIGHT SINGLE QUOTATION MARK in 'method\u2019s' is present in the source and is preserved as-is.",
      "Trailing LaTeX comment lines and \\vspace commands after the paragraph were not part of the abstract text and are excluded."
    ],
    "verbatim_warnings": [
      "'We obtain a mean absolute deviations of 6.1 percentage points' is a grammatical error IN THE SOURCE. Do not silently correct it -- CONTENT.md requires the abstract be quoted, not paraphrased. If it must be fixed, quote it with [sic] or ask the authors.",
      "The abstract says $0.30 per question per respondent. The paper's own cost table says $0.32. See cost_conflict."
    ],
    "keywords": ["Ad Platforms", "APIs", "Consumer Insights", "Online Sampling", "Survey Research"],
    "keywords_source": "\\textit{Keywords: ...} line, identical in all three editions."
  },

  "bibtex": {
    "status": "CONSTRUCTED -- NOT FOUND IN THE MANUSCRIPT",
    "found_in_manuscript": False,
    "search_performed": "grep for 'donati' across paper/bibs/*.bib and paper/*.bib; grep for 'ssrn|doi' across the paper repository. The bib files contain five other Donati/Rao works but no entry for this paper. No .bib entry, no DOI, no SSRN ID exists locally.",
    "entry": "@unpublished{donati_rao_adaptive,\n  author  = {Donati, Dante and Rao, Nandan},\n  title   = {Adaptive Survey Sampling via Ad Platforms},\n  note    = {Working paper},\n  year    = {2025}\n}",
    "entry_warning": "The year field is a PLACEHOLDER pending the citation-year decision (see ws-paper.md). Do not publish this BibTeX until the year and the venue/URL are settled. A BibTeX entry with no URL and a guessed year is worse than no BibTeX entry on a page whose whole proposition is verifiability.",
    "fields_we_cannot_fill": ["url", "doi", "eprint / SSRN abstract id", "journal", "volume", "number", "pages"]
  },

  "mad_comparison": {
    "what_it_is": "Mean absolute deviation from gold-standard benchmarks, aggregated across all outcome variables, for three sample sources.",
    "unit": "proportion (multiply by 100 for percentage points)",
    "source_edition": "Jul2026",
    "source": "Figure fig:MAD-comparison and the paragraph immediately following it.",
    "source_note": "CLAIMS.md's 'Refreshing' section says these come from 'Table 4'. THERE IS NO TABLE 4 CARRYING THEM. The comparison is a FIGURE (an included PDF, presentation/Figures/mad_grouped_meta_prolific_llm.pdf) and the numeric values exist only in the surrounding prose. See ws-paper.md drift D-2.",
    "identical_in_all_three_editions": True,
    "sources": [
      {"key": "meta",     "label_in_paper": "Meta",                      "site_label": "Virtual Lab", "weighted": 0.061, "unweighted": 0.062, "weighted_pp": 6.1, "unweighted_pp": 6.2},
      {"key": "prolific", "label_in_paper": "Prolific",                  "site_label": "Prolific",    "weighted": 0.071, "unweighted": 0.073, "weighted_pp": 7.1, "unweighted_pp": 7.3},
      {"key": "twins",    "label_in_paper": "LLM-based digital twins",   "site_label": "LLM digital twins", "weighted": 0.111, "unweighted": 0.120, "weighted_pp": 11.1, "unweighted_pp": 12.0}
    ],
    "relative_claims_verbatim": "In relative terms, Meta\u2019s accuracy is about 15% better than Prolific and more than 45% better than the LLM-generated twins.",
    "ceiling_sentence_verbatim": "These results indicate that our Meta-based methodology produces estimates that are at least as representative as Prolific participants and markedly closer to benchmarks than LLM-generated twins.",
    "uncertainty": {
      "intervals_reported": False,
      "standard_errors_reported": False,
      "significance_tests_reported": False,
      "evidence": "grep across all three editions for 'standard error', 'confidence interval', 'error bar', 'bootstrap', 'CI', 'p-value', 'significan' in a statistical sense returns zero hits on any MAD. Independently confirmed by the paper repo's PLAN.md line 14, which records the JMR reviewers' consensus that 'MAD comparisons have no inference'.",
      "consequence": "DESIGN.md motif M3 (Interval) is NOT PERMITTED for this figure -- 'Appears only where a real interval exists. Decorative use would be a lie.' assets/figures/mad-comparison.svg is drawn as M2 (bar + shared tick)."
    }
  },

  "mad_by_domain_meta_only": {
    "what_it_is": "MAD by outcome domain for the Meta (Virtual Lab) sample only.",
    "source_edition": "Jul2026",
    "source": "Table tab:mad_outcomes, 'Mean Absolute Deviations (MAD) by Domain'",
    "identical_in_all_three_editions": True,
    "unit": "proportion",
    "rows": [
      {"domain": "Overall (all outcomes)",        "unweighted": 0.0625, "weighted": 0.0608},
      {"domain": "Past Voting Behavior",          "unweighted": 0.0336, "weighted": 0.0326},
      {"domain": "Privacy Concerns",              "unweighted": 0.0457, "weighted": 0.0413},
      {"domain": "Life Satisfaction/Perceptions", "unweighted": 0.0541, "weighted": 0.0493},
      {"domain": "Socioeconomic Status",          "unweighted": 0.0482, "weighted": 0.0500},
      {"domain": "Attitudes on Social Issues",    "unweighted": 0.0692, "weighted": 0.0699},
      {"domain": "Internet Use",                  "unweighted": 0.0893, "weighted": 0.0876},
      {"domain": "Trust",                         "unweighted": 0.1063, "weighted": 0.1053}
    ],
    "note": "The table's 'Overall' row (0.0608 / 0.0625) is the same quantity the comparison figure rounds to 0.061 / 0.062. Table precision is four decimals; the comparison prose is three. Per DESIGN.md 'never round differently in two places' -- pick one precision for the site and keep it. Recommended: one decimal in p.p. (6.1)."
  },

  "mad_by_domain_three_way": {
    "what_it_is": "MAD by domain for all three sample sources. This is the per-domain breakdown CLAIMS.md's C-006/C-007 caveat rests on.",
    "source_edition": "Jul2026",
    "source": "Figure fig:MAD-categories-comparison and the paragraph preceding it, which states every value in prose.",
    "identical_in_all_three_editions": True,
    "unit": "proportion",
    "weighting": "weighted -- INFERRED, NOT STATED. The paper does not label the figure weighted or unweighted. Every Meta value here matches the WEIGHTED column of Table tab:mad_outcomes to the stated precision (0.033/0.0326, 0.041/0.0413, 0.050/0.0500, 0.049/0.0493, 0.070/0.0699, 0.088/0.0876, 0.105/0.1053) and several do not match the unweighted column. Flagged as an inference; confirm with an author before printing 'weighted' beside it.",
    "rows": [
      {"domain": "Past Voting Behavior",          "meta": 0.033, "prolific": 0.093, "twins": 0.095, "closest": "meta"},
      {"domain": "Privacy Concerns",              "meta": 0.041, "prolific": 0.057, "twins": 0.105, "closest": "meta"},
      {"domain": "Socioeconomic Status",          "meta": 0.050, "prolific": 0.059, "twins": 0.032, "closest": "twins"},
      {"domain": "Life Satisfaction/Perceptions", "meta": 0.049, "prolific": 0.064, "twins": 0.156, "closest": "meta"},
      {"domain": "Attitudes on Social Issues",    "meta": 0.070, "prolific": 0.062, "twins": 0.115, "closest": "prolific"},
      {"domain": "Internet Use",                  "meta": 0.088, "prolific": 0.067, "twins": 0.100, "closest": "prolific"},
      {"domain": "Trust",                         "meta": 0.105, "prolific": 0.107, "twins": 0.126, "closest": "meta"}
    ],
    "domains_where_we_are_not_closest": ["Socioeconomic Status (twins)", "Attitudes on Social Issues (prolific)", "Internet Use (prolific)"],
    "twins_ses_footnote_verbatim": "This likely reflects the fact that information on respondents\u2019 employment status\u2014an element of the socioeconomic status domain\u2014was directly incorporated into the construction of the digital twin personas.",
    "trust_note": "Trust is the weakest domain for every source: Meta 0.105, Prolific 0.107, twins 0.126. All exceed 0.10."
  },

  "cost_table": {
    "what_it_is": "Table 'costs' -- Comparison of Survey Costs Across Sampling Methods.",
    "source_edition": "Jul2026",
    "source": "Table \\label{costs}",
    "identical_in_all_three_editions": True,
    "unit": "USD, cost per question per respondent",
    "rows": [
      {"source": "Meta (ads + incentives)",           "cost_per_question_per_respondent_usd": 0.32},
      {"source": "GSS (traditional waves)",           "cost_per_question_per_respondent_usd": 3.00},
      {"source": "GSS (Follow-on, 2024 brochure)",    "cost_per_question_per_respondent_usd": 6.67},
      {"source": "Prolific",                          "cost_per_question_per_respondent_usd": 0.095}
    ],
    "supporting_figures_from_cost_considerations_text": {
      "advertising_cost_per_participant_usd": 6.3,
      "advertising_cost_per_participant_verbatim": "advertising costs per participant were $6.3",
      "advertising_cost_range_usd": {"low": 0.70, "low_stratum": "urban young medium-educated men", "high": 20.00, "high_stratum": "urban mid-age low-educated men"},
      "incentive_usd": 5.00,
      "incentive_form": "$5 Amazon gift cards upon completing the survey",
      "total_cost_per_final_participant_usd": 11.6,
      "prolific_cost_per_respondent_usd": 2.66,
      "prolific_cost_per_question_text": "about $0.10 per question per respondent",
      "multiple_verbatim": "the Meta sample was roughly 3 times more expensive than Prolific on a per-question basis, though still far more cost-effective than gold-standard probability surveys",
      "gss_followon_basis": "about $20,000 per survey minute, which equates to roughly $6.67 per question per respondent for a sample of 1,000 cases (norc2024gss)",
      "gss_traditional_basis": "around $3 per respondent per question (goel2015non)"
    },
    "number_of_questions_used_in_the_division": {
      "value": None,
      "status": "NOT STATED IN THE PAPER",
      "note": "The paper says $11.6 per participant 'corresponding to a cost per question per respondent of approximately $0.32' but never states the question count that divides it. $11.6/0.32 implies ~36 questions; $11.6/0.30 implies ~39. The instrument is described as 'a broad set of 20 substantive outcomes' plus eight demographic items = 28 items, which divides to $0.414. DO NOT PUBLISH ANY OF THESE ARITHMETIC RECONSTRUCTIONS. Recorded only as evidence for C-004."
    }
  },

  "cost_conflict": {
    "claims_row": "C-004",
    "status_in_claims_md": "STALE / unresolved, owner Nandan",
    "resolution_2026_08_20": "Nandan's answer is 'don't include that' -- no cost-per-question figure ships at all. See notes.publication_constraints.",
    "conflict_is_real": True,
    "conflict_is_exactly_as_claims_md_describes": True,
    "by_edition": [
      {"edition": "Jul2026",                  "abstract_says": "$0.30", "cost_table_says": "$0.32", "cost_text_says": "$0.32", "agree": False},
      {"edition": "JMR_submission_09152025",  "abstract_says": "$0.30", "cost_table_says": "$0.32", "cost_text_says": "$0.32", "agree": False},
      {"edition": "SSRN_09152025",            "abstract_says": "$0.30", "cost_table_says": "$0.32", "cost_text_says": "$0.32", "agree": False}
    ],
    "finding": "All three editions carry BYTE-IDENTICAL abstract and cost sections. The conflict is not an artifact of one edition and cannot be resolved by choosing an edition. It is a single unreconciled inconsistency propagated across all of them.",
    "extra_evidence": "A fourth, older abstract survives commented out at line 94 of every edition and reads 'a cost per question per respondent around $0.30', alongside 'mean absolute deviations ranging around 6.3 p.p.' Both are superseded prose. This suggests $0.30 is a survival from an earlier draft that the rewritten cost section (which computes $0.32 from $11.60) never updated.",
    "not_resolved_here": "This workstream was instructed not to resolve C-004 and has not."
  },

  "benchmarks": {
    "source_edition": "Jul2026",
    "source": "Benchmark data subsection, lines 474-475",
    "identical_in_all_three_editions": True,
    "claims_md_says": "GSS 2024, CPS 2024, Pew 2023",
    "paper_confirms": True,
    "entries": [
      {
        "name": "General Social Survey", "abbrev": "GSS", "year": 2024,
        "verbatim": "the General Social Survey (GSS 2024), a rigorous biennial survey conducted by NORC at the University of Chicago and widely regarded as a gold standard for measuring social attitudes and behaviors",
        "caveat": "NOT PURELY 2024. Verbatim: 'For items not collected in the 2024 wave, we use the most recent prior wave with identical wording.' The footnote names four items taken from GSS 2022: hours spent on the web, online health information search, perceived service quality in restaurants, and attitudes toward family life and women's full-time work. CLAIMS.md does not record this. A source line reading 'GSS 2024' is defensible; 'all benchmarks are 2024' is not."
      },
      {
        "name": "Current Population Survey", "abbrev": "CPS", "year": 2024,
        "verbatim": "the Current Population Survey (CPS 2024), the official U.S. labor force survey jointly conducted by the U.S. Census Bureau and the Bureau of Labor Statistics, which serves as the benchmark for socioeconomic measures"
      },
      {
        "name": "Pew Research Center", "abbrev": "Pew", "year": 2023,
        "verbatim": "recent Pew Research Center studies (2023), a probability-based national panel that provides reliable benchmarks for digital privacy, technology adoption, and platform policy attitudes"
      }
    ],
    "weighting_verbatim": "Benchmark means are always computed using each survey\u2019s official analysis weights (e.g., final person weights), following the protocols of the survey producers to ensure representativeness of the U.S. adult population (18+)."
  },

  "sample_sizes": {
    "us_validation_meta": {
      "value": 1500,
      "claims_row": "C-005",
      "source": "Abstract ('a 1,500-person U.S. study') and Introduction ('we recruit a sample of 1,500 Meta users in the United States').",
      "identical_in_all_three_editions": True
    },
    "prolific_comparison": {
      "value": 1197,
      "claims_row": "C-008",
      "verbatim": "Our Prolific sample consists of 1,197 respondents recruited and surveyed in June\u2013July 2025.",
      "fielded": "June\u2013July 2025",
      "stratification": "Sampling was stratified by age, gender, and race to ensure that the marginal distributions of these variables closely mirror the 2020 U.S. Census. However, apart from these characteristics, no further demographic controls were applied at the recruitment stage.",
      "identical_in_all_three_editions": True
    },
    "digital_twins": {
      "value": None,
      "status": "NOT STATED AS A NUMBER",
      "verbatim": "The digital twin dataset contains a similar number of synthetic respondents, generated to match the demographic distribution of the Prolific sample.",
      "dataset": "Twin-2K-500 (toubia2025twin)",
      "note": "Do not print an n for the twins arm. The paper gives none."
    },
    "weighting_battery_verbatim": "For both datasets, we apply post-stratification weighting techniques using the same battery of demographic and socioeconomic indicators employed in the Meta sample\u2014namely age, gender, education, settlement type, income, race, ethnicity, and marital status."
  },

  "instrument": {
    "substantive_outcomes": 20,
    "domains": ["Socioeconomic Status", "Life Satisfaction and Perceptions", "Privacy Concerns", "Attitudes on Social Issues", "Trust", "Internet Use", "Past Voting Behavior"],
    "demographic_items": ["gender", "age", "education", "settlement type", "income", "race", "country of birth", "marital status"],
    "verbatim": "Our survey instrument used a subset of items from the above-mentioned surveys and covered both demographic background variables and a broad set of 20 substantive outcomes.",
    "note": "Seven domains. The mad_by_domain tables have seven rows plus an overall row."
  },

  "disclosures": {
    "irb": {
      "claims_row": "C-054",
      "number": "AAAV1539",
      "body": "Columbia University IRB",
      "verbatim": "This research received ethical clearance from the Columbia University IRB (AAAV1539).",
      "location": "Title footnote (\\thanks on \\title), line 69",
      "identical_in_all_three_editions": True,
      "scope_warning": "The footnote says 'This research', i.e. the work described in the paper. CLAIMS.md C-054 is right that this does not generalize to all Virtual Lab work. Do not write 'IRB-approved' unscoped."
    },
    "competing_interest": {
      "location": "Title footnote (\\thanks on \\title), line 69",
      "wording_differs_by_edition": True,
      "Jul2026_and_JMR_verbatim": "One author declares no competing interests. One author  has ownership interests in Virtual Lab LLC, a company that applies the open-source methodology described in this paper to provide paid services.",
      "SSRN_and_Jan2025_verbatim": "Dante Donati declares no competing interests. Nandan Rao  has ownership interests in Virtual Lab LLC, a company that applies the open-source methodology described in this paper to provide paid services.",
      "transform_note": "The double space before 'has' is in the source and is preserved above. Normalize it when typesetting.",
      "which_to_quote": "Quote the SSRN/named wording if the site names Nandan (it is the same fact, stated unambiguously, and the site cannot pretend not to know which author). Quote the Jul2026 wording only if reproducing the working-manuscript footnote as a block.",
      "claims_md_says": "'one author holds ownership in Virtual Lab LLC' -- accurate for the Jul2026 edition."
    },
    "data_availability_verbatim": "All data and code underlying our analyses can be made available to ensure transparency and replicability.",
    "acknowledgements_verbatim": "The authors thank participants at the MIT Conference on Digital Experimentation (CODE), the Workshop on Frontiers in Measurement and Survey Methods, the Marketing Science Conference, the China India Insights Program, the AIML and Business Analytics Conference, and the MarkTech Conference for their valuable feedback."
  },

  "international_deployment": {
    "claims_rows": ["C-001", "C-002"],
    "source": "Applications in Other Countries section",
    "identical_in_all_three_editions": True,
    "studies": 33,
    "countries": 23,
    "people_reached_by_ads": 33073461,
    "optimized_respondents": 166535,
    "body_verbatim": "Our methodology was applied to conduct 33 studies across 23 countries, leveraging recruitment ads that reached 33,073,461 people and resulted in 166,535 optimized respondents.",
    "abstract_verbatim": "we provide evidence of success in over 33 studies across 23 countries",
    "over_33_note": "The abstract says 'over 33'; the body says '33'. CLAIMS.md C-001 already records this and caps publication at '33' or '33+'. Confirmed correct.",
    "appendix_detail": {
      "recruitment_cost_range_usd": {"low": 0.24, "low_country": "India", "high": 11.07, "high_country": "Gambia"},
      "share_below_4_usd": "80% of cases",
      "strata_range": {"low": 1, "low_country": "Serbia", "high": 200, "high_country": "Romania"},
      "max_ctr_note": "maximum CTRs exceeding 25% in some cases, such as Macedonia",
      "table": "Table country-results, Appendix"
    },
    "scope_warning": "These describe studies IN THE PAPER. Production shows 41 countries and (per Nandan, 2026-08-20) 175 studies. Do not cite the paper for operating scale."
  },

  "other_paper_figures_not_currently_in_claims_md": {
    "note": "Recorded so the Papers page can use them without a fresh trip to the .tex. None of these has a CLAIMS.md row yet; each would need one before publication.",
    "mad_stratification_variables_unweighted_pp": 3.5,
    "mad_stratification_plus_sociodemographic_unweighted_pp": 6.3,
    "mad_weighted_stratification_and_sociodemographic": "virtually zero (raking check, not a result)",
    "mad_at_100_participants": 0.103,
    "mad_at_1500_participants": 0.061,
    "improvement_pp": 4.2,
    "improvement_percent": 41,
    "mad_strata_at_first_100_participants_pp": "roughly 7",
    "mad_strata_stabilizes_at_pp": 3.5,
    "mad_strata_stabilizes_at_n": 900,
    "acquisition_cost_start_usd": 3,
    "acquisition_cost_end_usd": 9,
    "reoptimization_cadence": "every four hours",
    "direction_of_bias_verbatim": "Compared to benchmark surveys, Meta respondents spend more time on the internet and social media, report lower trust in others and less confidence in businesses and the press, express more conservative attitudes toward women and immigrants, perceive lower job security and financial satisfaction, and express less concern about privacy."
  },

  "notes": {
    "publication_constraints": [
      "C-004 withdrawn (Nandan, 2026-08-20): no cost-per-question figure ships. The cost_table above is per-question in EVERY row, so reproducing the paper's cost table on the Papers page prints the withheld $0.32. Either omit the table or render the comparison in per-participant units (advertising $6.30, total $11.60) which are independent of C-004.",
      "C-013's '~3x Prolific' is also stated per-question in the paper. The multiple itself ($11.60 vs $2.66 per respondent = 4.4x; per-question 0.32 vs 0.095 = 3.4x, paper says 'roughly 3 times') can be kept qualitatively without printing a per-question figure.",
      "Do not draw intervals on any MAD figure -- none exist.",
      "Do not print an n for the digital-twins arm -- none is stated.",
      "Do not print the number of questions -- it is not stated."
    ],
    "material_risk_flagged_for_nandan": "The paper repository's own PLAN.md (July 2026 research session) records that the Meta-vs-Prolific difference, computed with inference, is -0.62 p.p. with a 95% CI of [-1.24, +0.08] -- NOT SIGNIFICANT weighted. The manuscript's '15% better than Prolific' therefore has no inferential support and the authors know it. C-006 is the site's strongest asset and this is the strongest threat to it. See ws-paper.md, 'The C-006 problem'."
  }
}

out = "/home/nandan/Documents/vlab-research/vlab.digital/_data/paper.json"
with io.open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("wrote", out, os.path.getsize(out), "bytes")
