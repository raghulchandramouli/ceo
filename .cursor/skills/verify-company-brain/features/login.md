# Log in

Log in is the route where workspace sign-in will land. The page names that purpose and links back home. It does not collect credentials.

## Sub-features

- `login-from-home` opens the page from the home link.
- `login-direct` opens `http://127.0.0.1:3000/login`.
- `login-return` follows `Back home` to the control plane.

## How to get to it (user POV)

- Choose `Log in` on the home page.
- Open `http://127.0.0.1:3000/login`.

## Driving it with the Cursor browser

Preconditions:

- `verify.sh doctor` exits 0.
- No session cookie is required. None is set.

- **Home entry.** Open `/`, then choose `Log in`. The heading is `Log in`. The text says workspace sign-in and the provider callback land on this route. `Back home` is present. `Brain` and `Connectors` are absent.
- **Direct entry.** Navigate to `http://127.0.0.1:3000/login` in the same tab. The same heading and `Back home` link are present.
- **Return.** Choose `Back home`. The heading is `Control plane`.
- **Proof.** Save the direct-entry snapshot to `artifacts/login/opened.aria.txt` and the screenshot to `artifacts/login/opened.png`. Both show the heading `Log in`. Save the post-return snapshot to `artifacts/login/returned.aria.txt`.

## Gotchas

- There is no email field, password field, or submit button. A journey that tries to sign in fails because those controls are not on the page. Do not skip the assertion and call the route verified as authentication.
- The document title is `Log in · Company Brain`. The heading to assert is `Log in`.
- Proving the home link does not prove the direct URL. Drive both entry points.
