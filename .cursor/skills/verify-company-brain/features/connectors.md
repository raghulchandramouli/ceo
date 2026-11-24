# Connectors

Connectors is the page for Slack, Google Workspace, and Notion. It says sync status will show up here. It does not start an install or list a connection.

## Sub-features

- `connectors-from-header` opens Connectors from the header on `/` or `/brain`.
- `connectors-from-setup` opens Connectors via `Go to connectors` on the setup page.
- `connectors-direct` opens `http://127.0.0.1:3000/connectors`.

## How to get to it (user POV)

- Choose `Connectors` in the header on the home page or the brain page.
- Choose `Go to connectors` on the setup page.
- Open `http://127.0.0.1:3000/connectors`.

## Driving it with the Cursor browser

Preconditions:

- `verify.sh doctor` exits 0.
- No connector is installed. The page does not render a status row.

- **Header entry.** Open `/`, then choose `Connectors`. The heading is `Connectors`. The text says to install Slack and connect Google Workspace and Notion, and that sync status shows up here. The header remains visible.
- **Setup entry.** Open `/onboarding`, then choose `Go to connectors`. The heading is `Connectors`. The header is present after this navigation because the connectors page renders it.
- **Direct entry.** Navigate to `http://127.0.0.1:3000/connectors`. The same heading and sentence are present.
- **Proof.** Save the header-entry snapshot to `artifacts/connectors/opened.aria.txt` and the screenshot to `artifacts/connectors/opened.png`. Both show the heading `Connectors` and the Slack, Google Workspace, and Notion sentence.

## Gotchas

- There is no install button, OAuth redirect, or sync-status table. A journey that tries to connect Slack fails because those controls are not on the page.
- `Go to connectors` and the header link `Connectors` are different entry points. Verify both.
- The setup page itself has no header. The header appears only after the connectors page loads.
- Empty sync status is expected. Do not wait for a connector row.
