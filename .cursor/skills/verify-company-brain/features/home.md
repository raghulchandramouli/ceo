# Home

Home is the control-plane landing page. It introduces the product and links to login and workspace setup. The header also links to Brain and Connectors.

## Sub-features

- `home-open` shows the `Control plane` heading and the product description.
- `home-login` follows `Log in` and can return home.
- `home-onboarding` follows `Set up a workspace`.

## How to get to it (user POV)

- Open `http://127.0.0.1:3000/`.
- Choose the `Company Brain` header link from `/brain` or `/connectors`.
- Choose `Back home` on the login page.

## Driving it with the Cursor browser

Preconditions:

- `verify.sh doctor` exits 0 for `http://127.0.0.1:3000`.
- Start from a fresh navigation to `/`, not from a leftover `/login` or `/onboarding` tab.

- **Open home.** Navigate to `http://127.0.0.1:3000/`. The heading is `Control plane`. The page includes links named `Log in`, `Set up a workspace`, `Company Brain`, `Brain`, and `Connectors`. The description mentions Slack, Drive, and Notion.
- **Open login.** Choose `Log in`. The heading becomes `Log in`. The header links `Brain` and `Connectors` are absent.
- **Return.** Choose `Back home`. The heading is `Control plane` again.
- **Open setup.** From home, choose `Set up a workspace`. The heading is `Set up a workspace`.
- **Proof.** After returning home, save the snapshot to `artifacts/home/returned.aria.txt` and the screenshot to `artifacts/home/returned.png`. Both show the heading `Control plane`. Also keep the snapshot taken on the login page, before the return click, as `artifacts/home/login.aria.txt`.

## Gotchas

- `Company Brain` and the browser tab title are not the page heading. Assert `Control plane`.
- Login and onboarding do not render the header. A missing `Brain` link there is expected.
- There is no account to sign in with and no workspace to create from this page. Do not treat arrival on those routes as a completed signup.
- Following `Log in` does not verify the direct `/login` entry. That entry is in the login feature.
- The snapshot attached to the click can still show `/` or `/login` with the link focused. Wait for a later snapshot whose URL and heading match the step.
