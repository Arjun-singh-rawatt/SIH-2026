import React from 'react';

/**
 * Highlights exact evidence phrases extracted by AI/NLP from the raw field narrative
 */
export function EvidencePhrase({ rawText, evidencePhrases = [] }) {
  if (!rawText) return null;
  if (!evidencePhrases || evidencePhrases.length === 0) {
    return <p className="text-sm text-ink-primary leading-relaxed whitespace-pre-wrap">{rawText}</p>;
  }

  // Build a regex pattern matching any of the evidence phrases
  const escapedPhrases = evidencePhrases
    .filter(Boolean)
    .map((p) => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

  if (escapedPhrases.length === 0) {
    return <p className="text-sm text-ink-primary leading-relaxed whitespace-pre-wrap">{rawText}</p>;
  }

  const regex = new RegExp(`(${escapedPhrases.join('|')})`, 'gi');
  const parts = rawText.split(regex);

  return (
    <div className="text-sm sm:text-base text-ink-primary leading-relaxed font-sans bg-[#FAF7F2] p-5 sm:p-6 rounded-3xl border border-surface-border/80 shadow-spatial-xs">
      {parts.map((part, index) => {
        const isMatch = evidencePhrases.some(
          (ep) => ep.toLowerCase() === part.toLowerCase()
        );

        if (isMatch) {
          return (
            <mark
              key={index}
              className="bg-amber-100/90 text-amber-950 font-bold px-2 py-0.5 rounded-lg border border-amber-300 shadow-spatial-xs mx-0.5 inline-block"
              title="AI Evidence Phrase: Extracted safety precursor indicator"
            >
              {part}
            </mark>
          );
        }

        return <span key={index}>{part}</span>;
      })}
    </div>
  );
}
