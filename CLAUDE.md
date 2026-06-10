# CLAUDE.md — mistfight

Mistborn powers laboratory. Python + Jupyter notebooks, not (yet) a game.
Born 2026-06-09 from `~/Ideas/mistborn-fighting-game.md` — treat that doc as
a lossy transcription of Elliott's idea, not a spec. The long arc is a real
game (likely Godot; `~/demojam` is the sibling project to steal patterns
from when porting), but the current phase is **powers-first**: implement
each metal honestly, test whether book behavior emerges.

## The founding rule — emergence or it isn't a sim

Never special-case a character or outcome. Wayne's fast healing comes from
ordinary health code plus ordinary bubble time — zero Wayne-specific lines.
If a desired result has to be hard-coded, the model is wrong; fix the model.
Corollary: every modeling choice that ISN'T canon gets stated in the module
docstring and the notebook prose (linear push falloff, storing floor at
1 HP, compounding burns only what it delivers, etc.).

## How to run

```sh
# from this folder (sessions should be LAUNCHED from this folder —
# .claude/settings.local.json sets bypassPermissions here)
python -m sim.probe_check              # 17 fast assertions, the regression net
python notebooks\execute_notebooks.py  # run all notebooks, embed outputs
```

Notebooks open rendered in VS Code (Jupyter extension installed). If one
opens as raw JSON text: right-click → Open With → Jupyter Notebook editor.

## Architecture

- `sim/world.py` — fixed-tick (1/240 s default) deterministic 2D side-view
  world; computes each body's LOCAL tick (time bubbles) before anything else;
  ground at y = 0 acts as infinite static friction (that's what makes coins
  anchors).
- `sim/bodies.py` — point masses. `change_mass` conserves MOMENTUM (canon).
- `sim/steelpush.py` — force pair along center line, Newton's third law,
  linear falloff to zero at max range (falloff shape is our choice).
- `sim/feruchemy.py` — `IronFeruchemy` (mass) and `GoldFeruchemy` (health):
  three states (storing / tapping / neither), continuous flow, zero-sum.
  Storing makes you actively diminished the whole time.
- `sim/health.py` — `Health` and `Poison`. Deliberately simple; flesh-bound
  processes run on the body's local clock (so bubbles accelerate your poison
  along with your healing).
- `sim/bubbles.py` — `SpeedBubble`: fixed circular region scaling local
  time. The ONLY bubble mechanism; nothing else knows bubbles exist.
- `sim/compounding.py` — `GoldCompounding`, the zero-sum breaker (10×,
  canon-cited, tunable). Metal grams are Miles' only true budget.
- `sim/recording.py` — full per-tick history, plots, inline animations.
- `sim/probe_check.py` — the assertion suite. Extend it with every new metal.
- `notebooks/01..06` — numbered experiment scrolls, reasoning + runs + plots
  in one scroll. Read them in order; they are the project's real docs.

## Canon decisions already verified (2026-06-09, via Coppermind/WoB)

- Iron feruchemy stores **mass**, not gravity's effect. Mass changes conserve
  **momentum** → storing mid-fall doubles your speed (verified, weird, kept).
- Speed bubbles are **anchored where cast** (don't follow the caster); exit
  speed normalization **emerges** from the local-tick model (no boundary
  code); boundary deflection needs extended bodies — deliberately absent.
- Compounding ≈ **10×** per Sazed/Wax, accuracy uncertain → named constant.
- **Miles has no canon healing ceiling** (Elliott): the books show him
  surviving monstrous damage and dying exactly once — firing squad, after
  his metalminds were stripped. `max_burn_charge_per_second` creates a
  non-canon throughput kill; for canon-Miles set it high enough that only
  metal exhaustion can end him. (Notebook 06 finding 3 records this.)

Research notes: Coppermind is the source of truth for lore questions, but it
Cloudflare-blocks WebFetch and curl — use WebSearch and 17th Shard results
instead. Verify before modeling; cite in the notebook prose.

## Working style (project-specific)

- One knob per experiment, or an explicit 2D grid. Paper prediction before
  the run where possible; the sim correcting the paper is a result worth
  reporting (it caught a forgotten storing-drain feedback in notebook 06B).
- New metal = module (or addition to feruchemy.py) + probe checks + a
  numbered notebook. Keep the engine ignorant of characters.
- Full descriptive names, flat loops, comments say why. Elliott reads code
  as prose; that's load-bearing.

## Roadmap (Elliott's direction, 2026-06-09): MORE METALS, not fighting

Done since: **cadmium** (notebook 07 — including the when-not-where theorem:
bubbles change scheduling, never spatial paths; retraction recorded in 05/07)
and **steel feruchemy** (notebook 08 — Legs locomotion component; a
Steelrunner is measurably NOT a personal bubble: chemistry on the normal
clock, kinetic state real and exportable). The repo is public:
<https://github.com/Emsloan/mistfight> — MIT, code only, Dragonsteel IP noted.

Candidates, roughly by expected fun-per-effort:

- **Pewter (allomantic strength/durability)** — needs a damage-resistance or
  exertion model; keep it as simple as Health.
- **Tin (senses)** — needs a perception model; may wait for actual agents.
- **Atium** — foresight; the model question (dodge probability vs path
  prediction) is still open from the idea doc.
- **Duralumin / nicrosil, zinc / brass** — burst mechanics and emotional
  allomancy; emotional needs minds to riot/soothe.

Standing open items: two-point rigid bullet → emergent bubble boundary
deflection; hover control for Wax (constant push is undamped — notebook 02);
air drag (canon Skimmer safe-falling needs it); revisit the Miles ceiling.
