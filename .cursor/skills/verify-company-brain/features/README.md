# Company Brain verification map

This directory is the maintained source for verifying the Company Brain control plane. Read the index before driving the app, then use the matching feature file as the recipe.

## Baseline preconditions

- Launch with `.cursor/skills/verify-company-brain/scripts/verify.sh launch`.
- The web console is `http://127.0.0.1:3000` and the API is `http://127.0.0.1:8000`.
- Run `.cursor/skills/verify-company-brain/scripts/verify.sh doctor` and require the printed pids to own those ports.
- There is no signed-in user, workspace, document, or connector. Do not invent one.
- Never drive an instance that was not started by this verification run.

## Driving conventions

- Start every recipe from the home page unless its preconditions say otherwise.
- Prefer accessible names from `browser_snapshot` over CSS selectors, coordinates, or tab order.
- Treat every link name as literal.
- Drive the browser with the Cursor browser tools named in the skill.
- Leave proof artifacts in `.cursor/skills/verify-company-brain/artifacts/`. Do not remove them during cleanup.

## Proof and skip reporting

- Capture the user action and the resulting state, not only the final screen.
- UI proof includes an accessibility snapshot and a screenshot that shows the page heading.
- Record the feature id and the entry point used with every artifact.
- Report an unreachable path with the attempted step and the unmet precondition.
- Do not report a skipped entry point as verified through a different path.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing the user-visible behavior. It then uses exactly four H2 sections in this order.

1. `Sub-features` lists short IDs with one line for each behavior.
2. `How to get to it (user POV)` lists every user entry point.
3. `Driving it with the Cursor browser` starts with `Preconditions:` and uses labeled bullets that pair each user action with a browser step and observable result.
4. `Gotchas` lists traps that can waste or invalidate a verification run.

## Features

- [Home](./home.md) covers the control-plane landing page and its links to login and onboarding.
- [Log in](./login.md) covers opening the login route and returning home.
- [Set up a workspace](./onboarding.md) covers the setup page and its link to connectors.
- [Brain](./brain.md) covers opening the brain page from the header.
- [Connectors](./connectors.md) covers opening the connectors page from the header.
