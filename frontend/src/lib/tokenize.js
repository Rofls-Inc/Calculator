/**
 * Lightweight tokenizer used only for presentation: syntax highlighting,
 * bracket counters and pointing at an unbalanced parenthesis. Evaluation
 * always happens on the backend.
 */

const OPERATORS = new Set(["+", "-", "*", "/"]);


export function tokenize(source) {
  const tokens = [];
  let i = 0;

  while (i < source.length) {
    const ch = source[i];
    const start = i;

    if (ch === " " || ch === "\t") {
      while (i < source.length && (source[i] === " " || source[i] === "\t")) i += 1;
      tokens.push({ type: "space", value: source.slice(start, i), start });
      continue;
    }

    if ((ch >= "0" && ch <= "9") || (ch === "." && source[i + 1] >= "0" && source[i + 1] <= "9")) {
      while (i < source.length && ((source[i] >= "0" && source[i] <= "9") || source[i] === ".")) i += 1;
      tokens.push({ type: "num", value: source.slice(start, i), start });
      continue;
    }

    i += 1;

    if (OPERATORS.has(ch)) {
      tokens.push({ type: "op", value: ch, start });
    } else if (ch === "(" || ch === ")") {
      tokens.push({ type: "paren", value: ch, start });
    } else {
      tokens.push({ type: "unknown", value: ch, start });
    }
  }

  return tokens;
}


/**
 * Count parentheses and locate the first problem: an extra ")" or a missing
 * ")" at the end of the expression. Positions are 1-based for display.
 */
export function bracketStats(tokens) {
  let open = 0;
  let close = 0;
  let depth = 0;
  let errorPos = null;
  let errorKind = null;

  for (const token of tokens) {
    if (token.type !== "paren") continue;

    if (token.value === "(") {
      open += 1;
      depth += 1;
    } else {
      close += 1;
      depth -= 1;
      if (depth < 0 && errorPos === null) {
        errorPos = token.start + 1;
        errorKind = "extra-close";
      }
    }
  }

  if (errorPos === null && depth > 0) {
    const last = tokens[tokens.length - 1];
    errorPos = last ? last.start + last.value.length + 1 : 1;
    errorKind = "missing-close";
  }

  return {
    open,
    close,
    total: Math.max(open, close),
    balanced: errorPos === null,
    errorPos,
    errorKind,
  };
}


export function countTokens(tokens) {
  return tokens.filter((token) => token.type !== "space").length;
}
