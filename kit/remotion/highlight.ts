// A small syntax highlighter that colours code from the house palette.
// Deliberately tiny: explainer code is a few lines, and colours have to follow the video's colour
// roles (pass `roles` to give `loss` the colour loss has everywhere else), which no stock theme does.
import { P } from "./theme";

export type Lang = "python" | "js" | "ts" | "bash" | "json" | "text";
export type TokenKind = "plain" | "keyword" | "string" | "number" | "comment" | "call" | "punct";
export type CodeToken = { text: string; kind: TokenKind; color: string; italic?: boolean };

const KEYWORDS: Record<Lang, string[]> = {
  python:
    "and as assert async await break class continue def del elif else except finally for from global if import in is lambda None nonlocal not or pass raise return True False try while with yield".split(" "),
  js: "async await break case catch class const continue default delete do else export extends false finally for from function if import in instanceof let new null of return static super switch this throw true try typeof undefined var void while yield".split(" "),
  ts: "abstract any as async await boolean break case catch class const continue declare default delete do else enum export extends false finally for from function if implements import in instanceof interface keyof let new null number of private protected public readonly return static string super switch this throw true try type typeof undefined unknown var void while yield".split(" "),
  bash: "if then else elif fi for in do done while case esac function return export local echo cd".split(" "),
  json: ["true", "false", "null"],
  text: [],
};

export const SYNTAX: Record<TokenKind, string> = {
  plain: P.white,
  keyword: P.purple,
  string: P.green,
  number: P.gold,
  comment: P.greyC,
  call: P.blueLight,
  punct: P.greyB,
};

const pattern = (lang: Lang): RegExp => {
  const comment = lang === "python" || lang === "bash" ? "#.*" : lang === "json" || lang === "text" ? "(?!)" : "//.*";
  return new RegExp(
    [
      `(?<comment>${comment})`,
      `(?<string>"(?:[^"\\\\]|\\\\.)*"|'(?:[^'\\\\]|\\\\.)*'|\`(?:[^\`\\\\]|\\\\.)*\`)`,
      `(?<number>\\b\\d[\\d_]*(?:\\.\\d+)?(?:e[+-]?\\d+)?\\b)`,
      `(?<word>[A-Za-z_$][\\w$]*)`,
      `(?<space>\\s+)`,
      `(?<punct>[^\\sA-Za-z_$\\d"'\`]+)`,
    ].join("|"),
    "gi",
  );
};

/** One line of code as coloured tokens. `roles` maps exact identifiers to colours. */
export const tokenize = (line: string, lang: Lang = "python", roles: Record<string, string> = {}): CodeToken[] => {
  if (lang === "text") return [{ text: line, kind: "plain", color: SYNTAX.plain }];
  const keywords = new Set(KEYWORDS[lang]);
  const out: CodeToken[] = [];
  const re = pattern(lang);
  let m: RegExpExecArray | null;
  while ((m = re.exec(line)) !== null) {
    const g = m.groups ?? {};
    const text = m[0];
    if (text === "") {
      re.lastIndex++;
      continue;
    }
    if (g.comment !== undefined) out.push({ text, kind: "comment", color: SYNTAX.comment, italic: true });
    else if (g.string !== undefined) out.push({ text, kind: "string", color: SYNTAX.string });
    else if (g.number !== undefined) out.push({ text, kind: "number", color: SYNTAX.number });
    else if (g.word !== undefined) {
      const next = line.slice(re.lastIndex).trimStart()[0];
      const kind: TokenKind = keywords.has(text) ? "keyword" : next === "(" ? "call" : "plain";
      out.push({ text, kind, color: roles[text] ?? SYNTAX[kind] });
    } else if (g.space !== undefined) out.push({ text, kind: "plain", color: SYNTAX.plain });
    else out.push({ text, kind: "punct", color: SYNTAX.punct });
  }
  return out;
};

/** The first `count` characters of a tokenised line (for code that types itself). */
export const sliceTokens = (tokens: CodeToken[], count: number): CodeToken[] => {
  const out: CodeToken[] = [];
  let left = count;
  for (const tok of tokens) {
    if (left <= 0) break;
    const chars = Array.from(tok.text);
    out.push(chars.length <= left ? tok : { ...tok, text: chars.slice(0, left).join("") });
    left -= chars.length;
  }
  return out;
};
