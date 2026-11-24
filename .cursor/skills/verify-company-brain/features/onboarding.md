# Set up a workspace

Setup explains that a workspace is created here, the Slack app is installed, and the first source is connected. The only action is a link to connectors. The page does not create a workspace.

## Sub-features

- `onboarding-from-home` opens setup from the home page.
- `onboarding-direct` opens `http://127.0.0.1:3000/onboarding`.
- `onboarding-connectors` follows `Go to connectors`.

## How to get to it (user POV)

- Choose `Set up a workspace` on the home page.
- Open `http://127.0.0.1:3000/onboarding`.

## Driving it with the Cursor browser

Preconditions:

- `verify.sh doctor` exits 0.
- No workspace exists. The page does not list one.

- **Home entry.** Open `/`, then choose `Set up a workspace`. The heading is `Set up a workspace`. The text mentions the Slack app and the first source. The link `Go to connectors` is present.
- **Direct entry.** Navigate to `http://127.0.0.1:3000/onboarding`. The same heading and link are present.
- **Continue.** Choose `Go to connectors`. The heading is `Connectors`.
- **Proof.** Save the setup snapshot to `artifacts/onboarding/opened.aria.txt` and the screenshot to `artifacts/onboarding/opened.png` before the continue click. After the click, save `artifacts/onboarding/connectors.aria.txt` showing the heading `Connectors`.

## Gotchas

- Nothing on this page writes a tenant. Arrival here is not proof that a workspace was created.
- The header is absent, so `Connectors` in the header is not this entry point. The link name is `Go to connectors`.
- The document title is `Set up · Company Brain`. The heading to assert is `Set up a workspace`.
- Proving the home link does not prove the direct `/onboarding` URL.
