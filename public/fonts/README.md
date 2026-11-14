# Fonts

Latin Modern, the OpenType edition of Donald Knuth's Computer Modern, by GUST e-foundry
(B. Jackowski and J. M. Nowacki), version 2.004. Distributed under the GUST Font License
([`GUST-FONT-LICENSE.txt`](GUST-FONT-LICENSE.txt)), which permits redistribution.
Home: <https://www.gust.org.pl/projects/e-foundry/latin-modern>.

| File | Family | Used as |
|---|---|---|
| `lmroman10-regular.otf`, `-italic`, `-bold`, `-bolditalic` | Latin Modern Roman | all text |
| `lmmono10-regular.otf`, `lmmonolt10-bold.otf` | Latin Modern Mono | code |
| `lmsans10-regular.otf`, `lmsans10-bold.otf` | Latin Modern Sans | interface text in product mocks |

Both engines load these same files: Manim hands the folder to Typst (`kit/python/xkit/text.py`),
Remotion loads each face with `@remotion/fonts` (`kit/remotion/fonts.ts`). That is why a word
measures the same in both (`./x parity`). The files are unmodified. Math is set by Typst in New
Computer Modern Math, which ships inside the Typst compiler.

To change the typeface, replace the files, update `font` in `theme/tokens.json`, and run
`./x parity`.
