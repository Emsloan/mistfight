# Captured Ideas

The holding pen for tangents, future experiments, and direction-changing
thoughts — written down so nothing gets lost between sessions. Date each
entry; move things out when they become notebooks or design docs.

## 2026-06-10

### Era-3 Metallic Arts sports (direction-changing — friend's idea)

Elliott's friend: "era 3 should certainly have metallic arts sports. You
could do some really cool shit here." Elliott: "you may have just changed
what this game could be WAY for the better... Twinborn players? nasty.
imagine the paychecks."

Potentially reframes the eventual game from combat to athletics — or adds a
whole mode. The lab supports it directly: every balance question becomes a
league-design question (what Twinborn combos get banned? what's the metal
salary cap?). The long-jump experiment in notebook 08 is *already*
accidentally a track-and-field event. Candidate events: coinshot vertical
ascent, Steelrunner sprints (grip-limited!), bubble-relay races, full-contact
something. Rules questions are balance questions are sim questions.

### Bullet-surfing (friend's idea — future experiment, needs fired projectiles)

Store weight until lighter than feels-right, steelpush off a *moving*
bullet — "shoot at himself and damn near teleport." Comically dangerous,
canon-Wax never tried it.

Sim prediction to test (reasoning, unverified): momentum bookkeeping is
against it. The harvestable impulse from a bullet is bounded by roughly
twice the bullet's momentum (~0.01 kg × 800 m/s × 2 ≈ 16 kg·m/s — the same
reason recoil doesn't knock shooters over). Even at 8 kg (90% stored), that's
~2 m/s of Wax, not teleportation. BUT: light-Wax + repeated pushes off a
*stream* of bullets, or off heavy artillery shells, scales differently. The
experiment: implement fired projectiles, sweep stored-weight fraction and
projectile mass, find where (if anywhere) bullet-surfing beats coin-jumping.
Either way the answer is a finding: the sim settles a fan debate.

### Cadmium-feruchemy breath tactics

Storing breath enables hiding underwater or under earth, drawing on stored
breaths — ambush/infiltration tactics, staggering implications. Sims like
Miles' gold budget did: breath as a logistics resource. Needs a suffocation
model (trivial: like Poison). Pairs weirdly with bubbles: breath spent
inside a cadmium bubble lasts longer in external time — a buried pulser is
a *very* patient ambush.

### Dense-Wax durability — PENDING LORE VERIFICATION

Question (Elliott, via friend discussion): do the books imply that
weight-tapping Wax is also *denser and more durable*? **Status: web search
quota blocked the Coppermind check (resets 2026-06-10 ~1:20pm); verify
before modeling.** Physics-only analysis (labeled reasoning, not lore):

- More mass at fixed volume = more density, but durability lives in bond
  strength, not weight. Two real effects pull opposite directions:
  - FREE WIN (already emergent via F = ma): more inertia means a punch or
    bullet imparts less velocity change — heavy Wax is a worse target to
    knock around, no new code needed.
  - COST: when heavy Wax hits a wall at speed v, his own tissues must
    transmit proportionally more stopping force — same Δv hurts MORE at
    higher mass unless toughness is magically granted.
- So if canon grants toughness, it's a separate lore grant to model
  explicitly (damage-resistance scaling while tapping), distinct from the
  inertia effect we get free. Keep the two effects separated in the model.

### Friction rework rationale (decided 2026-06-10, implemented in notebook 09)

Elliott's catch: the every-tick velocity-zeroing ground was a hack — Wax has
no zero-friction coins, but canon also has genuinely *fixed* anchors (rail
spikes, building bones). Replaced with Coulomb static/kinetic friction
("stronger until overwhelmed, then drastically falls off" — Elliott) plus
`is_fixed` bodies. Predicted emergent wins: pushed-down coins anchor harder
(normal force grows), shallow pushes skitter, Steelrunner acceleration
becomes grip-limited.
