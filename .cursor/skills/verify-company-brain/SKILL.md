---
name: verify-company-brain
description: Drive the Company Brain web console in the browser and check its local API. Use when verifying the control plane, login, onboarding, brain, or connectors pages, or when proving a UI change the way a user would see it.
---

# Verify Company Brain

The user-facing surface is the Next.js control plane. The FastAPI process is the local API behind it. Slack, Temporal workers, Postgres, Redis, and MinIO are not part of this verification: none of the current pages read them.

Ports are fixed. Two instances cannot run side by side. If port 3000 or 8000 is already taken, stop. Do not kill that process and do not drive it. Doctor only accepts the processes this skill started.

## Launch

From the repo root:

```bash
.cursor/skills/verify-company-brain/scripts/verify.sh launch
```

Launch starts, in a fresh `/tmp/ceo-verify` directory:

- `uv run uvicorn ceo_api.main:app --host 127.0.0.1 --port 8000`
- `apps/web/node_modules/.bin/next dev --hostname 127.0.0.1 --port 3000`

Ready means both of these are true, not merely that a socket accepts connections:

- `GET http://127.0.0.1:8000/health` returns a JSON body containing `"status":"ok"`
- `GET http://127.0.0.1:3000/` returns HTML containing `Control plane`

There is no database and no seed data. The current pages do not query one. Do not run `just up`, `just migrate`, or the Temporal worker for these journeys.

Launch refuses when either port is already owned, or when `/tmp/ceo-verify` already holds a live pid. A failed launch stops whatever it started.

If `web.log` contains `unable to start FSEvent stream`, Next exited during startup. The port may accept a connection for a moment and then die. That instance is not usable. Rerun launch in an environment that can watch the workspace filesystem. Do not drive it.

These local steps are not what `just dev` does, and they were the ones used to prove this skill:

- Docker is not started, so Postgres, Redis, Temporal, and MinIO stay down.
- Alembic is not run.
- `ceo_workers` is not started.
- `.env` is not loaded. The API uses its built-in local defaults, and the pages do not read them.

## Doctor

Run this before driving, and again whenever a page looks wrong:

```bash
.cursor/skills/verify-company-brain/scripts/verify.sh doctor
```

Doctor is read-only. It exits 0 only when all of these hold:

- `/tmp/ceo-verify/api.pid` and `web.pid` are alive
- pid listening on 8000 is that API process or its child
- pid listening on 3000 is that web process or its child
- health JSON contains `"status":"ok"`
- the home page contains `Control plane`

Doctor prints `web_url`, `api_url`, both pids, the listener pids, `api_health`, and `state_dir`. If it fails, do not drive. Do not kill an unrelated listener to make it pass.

## Drive

Use the Cursor browser tools. Refs come from the latest `browser_snapshot` for that tab. Match controls by their accessible name, never by a remembered ref, coordinates, or tab order.

1. `browser_tabs` with `action` `list`.
2. `browser_navigate` to `http://127.0.0.1:3000` plus the feature path. Omit `position`.
3. `browser_lock` with `action` `lock`.
4. `browser_snapshot`. Find the link or heading named in the feature file.
5. `browser_click` with that `ref` and an `element` string of the accessible name.
6. `browser_snapshot` again and confirm the URL and heading. The snapshot returned by `browser_click` can still show the page you clicked. Do not record proof from that snapshot.
7. `browser_lock` with `action` `unlock` when the journey is finished.

Direct URLs are a second entry only when the feature file lists them. A header link and a typed URL are different entry points. Passing one does not verify the other.

The home page heading is `Control plane`. Header links, present on `/`, `/brain`, and `/connectors`, are `Company Brain`, `Brain`, and `Connectors`. `/login` and `/onboarding` have no header.

## Evidence

Write proof under `.cursor/skills/verify-company-brain/artifacts/<feature-id>/`. Cleanup must not delete that directory.

For each journey record the feature id, the entry point used, the action, and the state after the action:

- Save the accessibility snapshot that shows the resulting heading to `<feature-id>/<step>.aria.txt`.
- Take `browser_take_screenshot` and copy the image file to `<feature-id>/<step>.png`. The screenshot must show the page heading.
- A snapshot of the final screen alone is not proof. Also keep the snapshot from the step that performed the action.

Do not call an unlisted test endpoint, change React state from the console, or treat `curl` of the HTML as a substitute for the click. `curl` of `/health` belongs to doctor only.

There is no dry-run mode. These pages do not write rows, files, or messages. If a later journey claims a side effect, prove it with a second user-visible read. Do not claim a workspace, session, document, or connector exists. Those controls are not on the pages.

## Cleanup

```bash
.cursor/skills/verify-company-brain/scripts/verify.sh cleanup
```

Cleanup reads `/tmp/ceo-verify/api.pid` and `web.pid`, signals those process groups, and deletes `/tmp/ceo-verify`. It does not signal processes by name (`next`, `node`, `uvicorn`, `uv`). It does not remove `.cursor/skills/verify-company-brain/artifacts/`.

Run cleanup after a failed launch too, so a half-started pair does not keep the ports.

## Helpers

`.cursor/skills/verify-company-brain/scripts/verify.sh` is the only helper. It is executable.

```bash
.cursor/skills/verify-company-brain/scripts/verify.sh launch
.cursor/skills/verify-company-brain/scripts/verify.sh doctor
.cursor/skills/verify-company-brain/scripts/verify.sh paths
.cursor/skills/verify-company-brain/scripts/verify.sh cleanup
```

`paths` prints `web_url`, `api_url`, `state_dir`, and `artifacts_dir`.
