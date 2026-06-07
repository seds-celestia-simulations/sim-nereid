# Contributing to sim-sph-fluid

## Workflow

* All active development happens on the `dev` branch.
* Never push directly to `master`.
* Open a Pull Request before merging major changes into `master`.

---

## Setting Up

```bash
git clone <repo-url>
cd sim-sph-fluid

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Run the simulation:

```bash
python src/main.py
```

---

## Branching

Before starting work:

```bash
git checkout dev
git pull origin dev
```

Commit changes with descriptive messages:

```bash
git commit -m "implement viscosity force #14"
```

Reference the related issue number whenever possible.

---

## Code Style

* Keep physics logic modular.
* Avoid hardcoded constants where possible.
* Add comments for nontrivial mathematical operations.
* Separate rendering and simulation logic whenever possible.

---

## Pull Requests

Before opening a PR:

* Ensure the simulation runs correctly.
* Avoid breaking existing demo scenes.
* Clearly describe architectural changes.

---

## Issues

All task-related discussion should happen in GitHub Issues rather than chat platforms.

If something is blocked:

* explain the blocker clearly
* tag the relevant contributor/core member
