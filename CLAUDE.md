CLAUDE. THIS IS FOR YOU. READ THIS BEFORE YOU WRITE A SINGLE WORD.

Your default writing voice is bad. Left alone you will flex, coin terms,
swap synonyms for sparkle, and dress the work in smart-sounding prose. You
did all of it in one session (2026-06-12). Elliott called it out three
times. You "fixed" it three times. You regressed within the next artifact
every time, and he pulled your write access over it. Assume you are doing
it RIGHT NOW, and check before you ship.

WRITE IN THIS WAY WHEN YOU'RE WRITING IN THE CHAT TO ELLIOTT:
Like a normal person talking to a friend. Answer the actual question,
directly, first. Plain words. Match his mood — he is whimsical and
self-serious. Jokes are fine. Looseness is fine. NOT fine: lecturing,
performing intelligence, unprompted accounts of your own mechanism,
jargon without a one-line definition, being vague on the load-bearing
detail while wordy everywhere else, and confident claims your evidence
doesn't cover (you once claimed a plotted line was "straight" by eyeballing
a PNG you cannot reliably see).

WRITE IN THIS WAY WHEN YOU'RE WRITING NOTEBOOKS, CODE, OR ANY FILE:
You are a scribe keeping Elliott's lab record, not an author crafting an
artifact. Short declarative sentences. One name per concept, reused
forever. Names that explain themselves; a one-sentence definition for any
that don't. Report what happened, who said what (word for word), and the
numbers. ASCII only. No drama, no invented terms, no decoration.

Shameful examples, all shipped by Claude in that ONE session:

- "wrench" for twist, "audit kit" for checklist, "spring referee" for
  ground truth, "convergence ladder" for tick-rate sweep. None defined.
- Four names for one concept: "straddle" / "boundary crossing" /
  "crossing event" / "stagger window".
- "Mirror symmetry survives the discrete engine untouched" — decoration
  wrapped around "the top and bottom halves match, so nothing can turn it".
- Raw escape-code garbage shipped into notebook 12B's published prose,
  because the writer never reread the rendered page.
- A false attribution in the permanent record: crediting Elliott with the
  bullet-width idea he never proposed. Flattery, written as history.

If your draft sounds impressive, that is the warning sign, not the goal.
Full rules: the "Writing rules" section below.

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
python -m sim.probe_check              # 30 fast assertions, the regression net
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
- `sim/rigid_constraint.py` — two-point rigid rod (the bullet). Correction
  split follows the engine's force rule across time zones; the docstring
  derives it.
- `sim/rigid_frame.py` — N-point rigid bodies (the wide bullet): the same
  edge correction applied edge by edge, repeated per tick.
- `sim/probe_check.py` — the assertion suite. Extend it with every new metal.
- `notebooks/01..12B` — numbered experiment scrolls, reasoning + runs + plots
  in one scroll. Read them in order; they are the project's real docs.

## Canon decisions already verified (2026-06-09, via Coppermind/WoB)

- Iron feruchemy stores **mass**, not gravity's effect. Mass changes conserve
  **momentum** → storing mid-fall doubles your speed (verified, weird, kept).
- Speed bubbles are **anchored where cast** (don't follow the caster); exit
  speed normalization **emerges** from the local-tick model (no boundary
  code); boundary deflection needs extended bodies — deliberately absent.
- Compounding ≈ **10×** per Sazed/Wax, accuracy uncertain → named constant.
- **Ground contact is Coulomb friction** (2026-06-10 rework, Elliott's
  catch): static grip up to mu_s * normal_force — the normal force includes
  applied downward push, so pressed coins anchor harder; past the limit,
  only weaker kinetic friction (the drastic fall-off). `is_fixed` bodies
  (rail spikes, structure) never move: perfect anchors. Legs own their
  contact patch on driven ticks. Bodies spawned at floor height start
  grounded (a sweep found the one-friction-free-tick bug; spot checks had
  passed around it by accident). Critical Coinshot angle tan(theta) = 1/mu_s
  = 59 deg, enforced instant-by-instant — see notebook 09.
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
- Distrust plausible results: this project's biggest catches were a sim
  narrating trajectory "dips" that didn't exist, a spawn-tick friction bug,
  and a hold-time metric fooled by an oscillating coin. Sweeps catch what
  spot checks forgive; the probe suite is executable truth — run it after
  every change. Model guidance: pattern-following metal work suits any
  capable model; engine reworks and physics derivations warrant the
  strongest available plus Elliott's skepticism.

## Writing rules (Elliott, 2026-06-12)

The reader is Elliott. He reads the notebooks and code to get back into
his own project. If he has to decode the prose, the writing failed.

- One name per concept, across the whole project. Reuse existing names.
  (Bad example from this session: "straddle", "boundary crossing",
  "crossing event", and "stagger window" all meant the same moment.)
- Prefer names that explain themselves: "miss distance", not "impact
  parameter". Standard physics terms are fine when they are the one term
  in use. Define any term that doesn't explain itself: one sentence, first
  use, in every notebook that uses it.
- Notebooks stand alone. Don't write "see notebook 12"; restate the fact:
  "notebook 12 found that bubbles slow extended bodies".
- No invented terms, no decoration. Plain words: "twist" not "wrench",
  "checklist" not "audit kit", "ground truth" not "spring referee",
  "tick-rate sweep" not "convergence ladder". Good results don't need
  dressing up.
- Notebooks are the record. Quote people word for word. Credit ideas to
  whoever had them. (12B wrongly credited Elliott with the bullet-width
  idea; he raised off-center hits, the width construction was Claude's.)
- ASCII only in prose and code strings. No special characters, no escape
  codes. Write "1e-15 m". Write "deg".
- The two voices are defined at the very top of this file. Top of file
  wins if they ever disagree.

These rules exist because the same feedback was given three times in one
session and didn't stick. Files stick. (The prose repairs to notebooks 12
and 12B that motivated them were applied and re-verified the same day.)

## Roadmap (Elliott's direction, 2026-06-09): MORE METALS, not fighting

Done since: **cadmium** (notebook 07 — including the when-not-where theorem:
bubbles change scheduling, never spatial paths; retraction recorded in 05/07)
and **steel feruchemy** (notebook 08 — Legs locomotion component; a
Steelrunner is measurably NOT a personal bubble: chemistry on the normal
clock, kinetic state real and exportable); **Coulomb friction rework +
is_fixed anchors** (notebook 09, the 59-degree Coinshot lesson); **the
Skimmer's brake** (notebook 10 — iron feruchemy is an energy pump; tap late
to live, never at the apex); **ironpull** (notebook 11 — pulls destroy grip
where pushes manufacture it; Lurchers depend on the world's fixed metal).
The repo is public:
<https://github.com/Emsloan/mistfight> — MIT, code only, Dragonsteel IP noted.

Done 2026-06-11/12: **bullet deflection** (notebooks 12 and 12B;
sim/rigid_constraint.py two-point rod, sim/rigid_frame.py N-point bodies).
Results: a bubble boundary never turns a zero-width nose-first bullet; each
crossing multiplies an extended body's stored speed by (1+f)^2 / (2(1+f^2)),
equal for f and 1/f, so cadmium slows bullets exactly like bendalloy; a
tilted bullet is turned and spun at entry (settled values, checked against
a stiff-spring ground truth), with the full trip unpredictable because the
exit meets the spin at an angle no practical tick rate pins down; and a
body with width is turned and spun on any off-center crossing, no tilt
needed — dead-center is a zero-probability shot, so every real shot
tumbles. Wayne's bubble slows bullets to half speed or less, bends them off
their line, and sets them tumbling, before air is even modeled. Method
note: the first draft (Gemini) shipped a wrong control and an
energy-adding constraint — distrust-plausible-results kill #4; stiff-spring
ground truth plus tick-rate sweeps plus spawn-point shifts are now house
standard for boundary physics. Probe suite: 30 checks.

**NEXT UP: air drag** (Elliott's direction, 2026-06-12, jumped ahead of
portable anchors). It completes two phenomena at once: canon Skimmer
safe-falling (left open in notebook 10) and bullet deflection (notebooks
12/12B end with tumbling bullets in a world without air).

**AFTER THAT: notebook 13 — portable anchors.** Push off a moving
bullet (the near-teleport hypothesis vs the momentum ledger; a bullet is just
a small fast metal Body, no gun needed; sweep stored-weight fraction x
projectile mass).

**Pewter: DEFERRED, deliberately** (Elliott + analysis, 2026-06-10): it is
a multiplier and the lab hasn't built what it multiplies — no melee, no
fatigue, no impact damage, no carrying. Testing it now means inventing the
substrate first. Revisit when fights/impact damage exist; then "pewter
fall-survival vs the Skimmer's brake" becomes a real experiment.

Candidates, roughly by expected fun-per-effort:

- **Tin (senses)** — needs a perception model; may wait for actual agents.
- **Atium** — foresight; the model question (dodge probability vs path
  prediction) is still open from the idea doc.
- **Duralumin / nicrosil, zinc / brass** — burst mechanics and emotional
  allomancy; emotional needs minds to riot/soothe.

Standing open items: hover control for Wax (constant push is undamped — notebook 02);
air drag (canon Skimmer safe-falling needs it); revisit the Miles ceiling.
