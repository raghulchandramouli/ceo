"""Decide whether a document may be shown for a tenant, user, and channel."""

from __future__ import annotations


def is_visible(
    *,
    document_tenant: str,
    document_principals: set[str],
    query_tenant: str,
    user_principals: set[str],
    channel_principals: set[str] | None,
) -> bool:
    """Return whether the document can be included in this answer.

    A channel answer is visible only when the asking user can see it and every
    channel member can see it too. A DM uses the asking user alone.
    """
    if document_tenant != query_tenant:
        return False
    if "workspace_public" in document_principals:
        return True
    if channel_principals is None:
        return bool(document_principals & user_principals)
    if not (document_principals & user_principals):
        return False
    return channel_principals <= document_principals
