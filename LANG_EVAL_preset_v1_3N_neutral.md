# LANG_EVAL Preset (v1.3N — Neutral)
# Purpose: First-pass language analysis/triage for academic/scientific docs
# Neutral defaults so it can be applied to any client, any journal, any quotation request.
# Key neutrality changes vs v1.3:
# - language, client_tags, and citation style default to AUTO detection.
# - No MDPI/Harvard defaults baked in; rules/quality gates are conditional on detected style.
# - Numeric vs author–date is inferred; enforcement matches the detected/selected style.
# - Percent/numbering styles are AUTO; house styles can be passed via inputs when needed.

```dsl
define_preset LANG_EVAL {
  task="academic_language_analysis";
  version="1.3N";
  description="Neutral, journal-agnostic language analysis with auto detection for language variant and citation style; supports pre/post delta metrics and quotation categorisation.";

  # -------- Inputs (Neutral) --------
  inputs = {
    doc_path: "<required: path to .docx/.pdf/.md>",
    cover_letter_path: "<optional: path to cover letter>",
    instructions: "<optional: free-text editorial instructions from client>",
    client_tags: [],                              # neutral by default
    language="auto",                              # auto | en-GB | en-US | af-ZA | etc.
    language_variant="auto",                      # auto-detect en-GB vs en-US if language=en
    numeric_style="auto",                         # auto | namc_percent_symbol_nbsp | fao_percent_word
    wr_mode="001WRR-S",                           # 001WRR-S (section) or 001WRR-P (page)
    analysis_only=true,                           # analysis + examples only; no full rewrites

    # Citation style (neutral): auto-detect predominant in-text pattern
    # auto detection heuristics:
    #  - numeric (ACS-like): [1], [2–4], [1,3]
    #  - author_date (Chicago/Harvard-like): (Author 2010) or (Author, 2010)
    citation_style_target="auto",                 # auto | author_date | numeric
    author_date_flavour="auto",                   # auto | Harvard_comma | Chicago_no_comma

    # Before/After workflow
    phase="pre",                                  # pre | post
    save_baseline=true,                           # when phase=pre, export baseline metrics
    baseline_metrics_path="",                     # when phase=post, path to pre metrics (.json or .csv)
    section_heading_regex="^#{1,3}\\s|^(?:Abstract|Introduction|Methods|Methodology|Results|Discussion|Conclusion|References)\\b"
  };

  # -------- Style/Conventions (Neutral) --------
  spelling_variant_lock=(language != "auto");     # only lock variant when explicitly set
  typography = {
    spaces_around_percent = (numeric_style == "namc_percent_symbol_nbsp");
    percent_word = (numeric_style == "fao_percent_word");
  };

  # -------- Detectors --------
  detectors = {
    long_sentence_threshold=34;
    this_verb_openers=true;
    there_verb_openers=true;
    repetition_001WRR=true;
    mixed_english_variant=true;                   # if language=en and variant fixed; otherwise advisory
    article_determiner_omission=true;
    passive_voice_ratio=true;
    nominalisation_density=true;
    cohesion_markers_scan=true;
    tense_consistency=true;
    inline_citation_conformity=true;
    figure_table_caption_style=true;

    # Conditional detectors (style-aware)
    numeric_citation_detected = (citation_style_target == "numeric" 
                                 || (citation_style_target == "auto" && detect_numeric_citations()==true));
    author_date_detected = (citation_style_target == "author_date" 
                            || (citation_style_target == "auto" && detect_author_date_citations()==true));

    # Flag only when author–date is detected/selected
    square_bracketed_author_year = author_date_detected;
  };

  # -------- Scoring (0–10) --------
  scoring_axes = { grammar=0.30, structure=0.20, cohesion=0.20, tone_register=0.15, consistency=0.10, readability=0.05 };
  scoring_notes="Export both /10 and %; deltas computed when baseline provided.";

  # -------- Edit Intensity Mapping --------
  edit_intensity_map = [
    {score_min: 8.5, label: "Light",        lines_percent: "≤15%"},
    {score_min: 7.0, label: "Medium",       lines_percent: "20–40%"},
    {score_min: 5.5, label: "Medium-Heavy", lines_percent: "35–55%"},
    {score_min: 0.0, label: "Heavy",        lines_percent: "≥60%"}
  ];

  # -------- Quotation Category (permanent) --------
  quotation = {
    threshold_percent=85;
    label_high="Standard language editing";
    label_low="Intermediate–Heavy language editing";
    embed_in_report=true;
    report_line_template="Quotation category: ${label} (${score_percent}% ${operator} ${threshold_percent}%)";
  };

  # -------- Modules/Guards --------
  modules = {
    phase1="001NM1,001NM2,001NM3";
    phase2="001WRR,002ThV,001NM2B";
    paraphrase_sentence=false;
    rephrase_sentence=false;
    rephrase_phrase=true;
    genuine_error_rephrase=true;
  };

  # -------- Citation Rules (style-aware, Neutral) --------
  rules = [
    # Author–date must use parentheses (only if author–date detected/selected)
    {
      id: "CIT-AD-001",
      enabled: author_date_detected,
      description: "Author–date citations must use parentheses, not square brackets.",
      pattern: "\\[(?:[A-Z][A-Za-z\\-]+[^\\]]*?\\d{4}[a-z]?[^\\]]*?)\\]",
      exclude_if: "numeric_citation_detected",
      message: "Author–date citation detected in square brackets. Use parentheses for author–date.",
      suggest: "Replace […] with (…). Then harmonise commas per selected flavour."
    },
    # Chicago normaliser (only if author_date_flavour selected/detected as Chicago)
    {
      id: "CIT-AD-002",
      enabled: (author_date_detected && (author_date_flavour == "Chicago_no_comma")),
      description: "Chicago author–date (no comma).",
      pattern: "\\(([^()]+?),\\s*(\\d{4}[a-z]?)\\)",
      replace: "(\\1 \\2)",
      message: "Drop the comma between author and year for Chicago author–date."
    },
    # Harvard normaliser (only if author_date_flavour selected/detected as Harvard comma)
    {
      id: "CIT-AD-003",
      enabled: (author_date_detected && (author_date_flavour == "Harvard_comma")),
      description: "Harvard author–date (comma).",
      pattern: "\\(([^()]+?)\\s+(\\d{4}[a-z]?)\\)",
      replace: "(\\1, \\2)",
      message: "Insert a comma between author and year for Harvard author–date."
    },
    # Multi-citation harmoniser inside parentheses (author–date)
    {
      id: "CIT-AD-004",
      enabled: author_date_detected,
      description: "Unify multi-citations separator to '; '.",
      pattern: "\\)\\s*,\\s*\\(",
      replace: "; ",
      message: "Use '; ' between multiple citations inside the same parentheses."
    },
    # Page locator normaliser (author–date)
    {
      id: "CIT-AD-005",
      enabled: author_date_detected,
      description: "Normalise page locators: '(Author Year, 45–47)'.",
      pattern: "\\(([^()]+?),\\s*(\\d{4}[a-z]?)\\s*[:|,]\\s*([\\d–\\-]+)\\)",
      replace: "(\\1 \\2, \\3)",
      message: "Move page range after the year, separated by comma."
    }
    # No numeric-style enforcement rules here; numeric systems vary by journal.
  ];

  # -------- Outputs --------
  outputs = {
    report_md_path="LANG-EVAL_report.md";
    findings_csv_path="LANG-EVAL_findings.csv";
    compliance_tsv_path="LANG-EVAL_compliance.tsv";
    metrics_json_path="LANG-EVAL_metrics.json";        # baseline or current metrics snapshot
    metrics_csv_path="LANG-EVAL_metrics.csv";
    include_rules_checklist=true;
    include_scores_table=true;
    include_edit_intensity=true;
    include_quotation_category=true;
    include_citation_policy_note=true;

    # DELTA artefacts (generated when baseline provided)
    delta_csv_path="LANG-EVAL_delta.csv";
    delta_report_md_path="LANG-EVAL_delta.md";
  };

  # -------- Metrics Schema --------
  metrics_schema = [
    "overall_score_10","overall_score_percent","grammar","structure","cohesion","tone_register","consistency","readability",
    "sentences_total","mean_sentence_len","long_sentences_gt34","long_sentences_gt40",
    "this_there_openers","passive_flags","nominalisation_per100w","root_repetition_sentences",
    "mixed_en_variants_count","cohesion_paragraph_starters","figures","tables","bracket_citations_count",
    "quotation_category","edit_intensity_label","edit_lines_percent_est",
    "citation_style_detected","author_date_flavour_detected"
  ];

  # -------- Quality Gates (post-edit, Neutral/conditional) --------
  quality_gates = {
    min_overall_increase=0.5,
    max_long34_reduction=0.30,
    target_this_there=0,
    target_mixed_variants=0,
    nominalisation_delta=-0.5,
    citation_brackets_zero=(author_date_detected),   # only applies when author–date is in use
    pass_text="Ready to deliver ✔",
    fail_text="Needs another pass ✖"
  };

  # -------- Report Sections --------
  report_sections = [
    "1. Executive Summary",
    "2. Scores & Edit Intensity",
    "2a. Quotation category (auto-generated)",
    "3. Key Issues (ranked)",
    "4. Detailed Findings (with examples + fixes)",
    "5. Style/Convention Checks (auto-detected/overridable)",
    "6. Reviewer-alignment check (if cover_letter_path provided)",
    "7. Rules enforced (checklist) & next steps"
  ];

  # -------- Delta Report Sections --------
  delta_sections = [
    "A. Summary of improvements (score, intensity, quotation category)",
    "B. Metric deltas table (before → after → Δ)",
    "C. Issue reductions (long sentences, This/There, repetition, mixed variants)",
    "D. Quality gates result (pass/fail with reasons)",
    "E. Per-section highlights (optional, if headings detected)"
  ];

  # -------- Reviewer Alignment --------
  reviewer_alignment = {
    enabled=true,
    requires_cover_letter=true,
    checks=[
      "Claims addressed linguistically (clarity/transition)",
      "Abstract/objective clarity vs paper body",
      "Terminology harmonised post-revision"
    ]
  };

  # -------- Execution Behaviour --------
  behaviour = {
    limit_examples_per_issue=2;
    sample_fix_length="1–2 sentences";
    preserve_author_voice=true;
  };
}
```

run LANG_EVAL with { doc_path="2025.02.28.Article_Brazil_CAR (1).docx" }

action=check_style_adherence; document="2025.02.28.Article_Brazil_CAR (1).docx"; styleguide="cb8081en.pdf"; execute=true
