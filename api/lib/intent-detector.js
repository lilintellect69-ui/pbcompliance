// Intent detector — regex/keyword scoring (no LLM call) to classify the user's
// latest message into one of four output modes before invoking the model. This
// is per the design brief §4 (Output Modes). Detection runs in <1ms.
//
// Modes:
//   explain     — default; conversational with PB interpretation
//   procurement — emit external_safe_claim / external_safe_phrasing verbatim
//   audit       — emit documented_evidence + audit_methods + cadence + failure_modes
//   crosswalk   — traverse 1-hop crosswalk graph; produce comparison

const PATTERNS = {
  procurement: [
    /\bdraft\s+(a\s+)?(response|reply|boilerplate|statement)\b/i,
    /\b(rfp|rfi|rfq)\b/i,
    /\bprocurement\b/i,
    /\bexternal\s+claim\b/i,
    /\bfor\s+(the\s+)?(customer|client|buyer)\b/i,
    /\b(marketing|sales|trust\s+pack|trust\s+centre)\s+language\b/i,
    /\bcan\s+i\s+say\b/i,
    /\bwhat\s+can\s+we\s+(claim|say)\b/i,
    /\bpublic\s*(-|\s)?facing\b/i,
  ],
  audit: [
    /\b(documented|operational)?\s*evidence\b/i,
    /\bauditor\b/i,
    /\baudit(\s|-)?(ready|prep|preparation)\b/i,
    /\bhow\s+do\s+(i|we)\s+(prove|demonstrate|show)\b/i,
    /\btype\s+(i{1,2}|1|2)\b/i,
    /\bobservation\s+period\b/i,
    /\bartefact\b/i,
    /\bsampling\b/i,
    /\b(what\s+do\s+i\s+need|what\s+would\s+i\s+need)\b/i,
    /\b(audit\s+)?(test|testing|verification)\s+(method|approach)\b/i,
    /\binternal\s+audit\b/i,
  ],
  crosswalk: [
    /\bmap(s|ped|ping)?\s+to\b/i,
    /\bvs\s+(iso|nist|popia|king|soc|eu)\b/i,
    /\b(equivalent|analog(ue|ous))\b/i,
    /\bcross(\s|-)?walk\b/i,
    /\bcompare\s+(with|to|against)\b/i,
    /\bhow\s+does\s+this\s+relate\s+to\b/i,
    /\bdoes\s+this\s+overlap\s+with\b/i,
    /\b(parallel|analog)\s+in\b/i,
    /\b(corresponds?\s+to|mapping|mapped)\b/i,
  ],
};

const FRAMEWORK_MENTIONS = {
  'iso-27001': /\b(iso\s*27001|iso\/iec\s*27001|27001|isms)\b/i,
  'iso-27701': /\b(iso\s*27701|iso\/iec\s*27701|27701|pims)\b/i,
  'iso-42001': /\b(iso\s*42001|iso\/iec\s*42001|42001|aims)\b/i,
  'eu-ai-act': /\b(eu\s*ai\s*act|ai\s*act|regulation\s*2024\/1689|2024\/1689)\b/i,
  'popia': /\b(popia|protection\s+of\s+personal\s+information|act\s*4\s*of\s*2013)\b/i,
  'king-v': /\b(king\s*v|king\s*iv|iodsa)\b/i,
  'soc-2': /\b(soc\s*2|soc\s*ii|trust\s+services\s+criteria|tsc)\b/i,
  'nist': /\b(nist|ai\s*rmf|ssdf|800-218|sp\s*800-218|218a|genai\s*profile)\b/i,
};

const PROCEDURAL_HEDGES = [
  /\bwhat\s+if\b/i,
  /\bhow\s+do\s+i\s+(operationalise|operationalize|implement|set\s+up)\b/i,
  /\bblocks?\b/i,
  /\bpending\b/i,
];

export function detectMode(message) {
  if (!message || typeof message !== 'string') return 'explain';

  const scores = { explain: 0, procurement: 0, audit: 0, crosswalk: 0 };

  for (const [mode, patterns] of Object.entries(PATTERNS)) {
    for (const pattern of patterns) {
      if (pattern.test(message)) scores[mode] += 1;
    }
  }

  // Crosswalk trigger: any non-current framework name mentioned
  let frameworksMentioned = 0;
  for (const re of Object.values(FRAMEWORK_MENTIONS)) {
    if (re.test(message)) frameworksMentioned += 1;
  }
  if (frameworksMentioned >= 2) scores.crosswalk += 1;

  // Pick highest-scoring non-default; fall back to explain
  const ranked = Object.entries(scores)
    .filter(([m]) => m !== 'explain')
    .sort((a, b) => b[1] - a[1]);

  if (ranked[0][1] > 0) return ranked[0][0];
  return 'explain';
}

export function detectFrameworkMentions(message) {
  if (!message || typeof message !== 'string') return [];
  return Object.entries(FRAMEWORK_MENTIONS)
    .filter(([, re]) => re.test(message))
    .map(([fwId]) => fwId);
}

export function isProcedural(message) {
  if (!message || typeof message !== 'string') return false;
  return PROCEDURAL_HEDGES.some((re) => re.test(message));
}
