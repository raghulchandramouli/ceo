# Brain

Brain is the page for ACL-aware search. It shows that description. It does not accept a query or list documents.

## Sub-features

- `brain-from-header` opens Brain from the header on `/` or `/connectors`.
- `brain-direct` opens `http://127.0.0.1:3000/brain`.
- `brain-home` returns via the `Company Brain` header link.

## How to get to it (user POV)

- Choose `Brain` in the header on the home page or the connectors page.
- Open `http://127.0.0.1:3000/brain`.

## Driving it with the Cursor browser

Preconditions:

- `verify.sh doctor` exits 0.
- No documents are indexed. The page does not render a result list.

- **Header entry.** Open `/`, then choose `Brain` in the header. The heading is `Brain`. The text says ACL-aware search across the documents this user is allowed to see. The header still shows `Company Brain`, `Brain`, and `Connectors`.
- **Direct entry.** Navigate to `http://127.0.0.1:3000/brain`. The same heading and description are present.
- **Return.** Choose `Company Brain`. The heading is `Control plane`.
- **Proof.** Save the header-entry snapshot to `artifacts/brain/opened.aria.txt` and the screenshot to `artifacts/brain/opened.png`. Both show the heading `Brain` and the ACL-aware sentence. Save `artifacts/brain/home.aria.txt` after choosing `Company Brain`.

## Gotchas

- There is no search box, no result list, and no permission error to dismiss. A journey that types a query fails because the control is not on the page.
- An empty page is the current product, not a failed load. Do not wait for documents.
- The header link and the direct URL are separate entry points.
- This page is not linked from `/login` or `/onboarding`. Those pages have no header.
