"""Channel intersection with a DM fallback."""

from ceo_brain.acl.filter import is_visible


def allow_in_channel(
    *,
    document_tenant: str,
    document_principals: set[str],
    query_tenant: str,
    user_principals: set[str],
    channel_principals: set[str],
) -> bool:
    return is_visible(
        document_tenant=document_tenant,
        document_principals=document_principals,
        query_tenant=query_tenant,
        user_principals=user_principals,
        channel_principals=channel_principals,
    )
