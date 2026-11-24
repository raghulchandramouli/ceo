export type Session = {
  userId: string;
  tenantId: string;
  role: "admin" | "member" | "viewer";
};

/** Session from the auth provider. Returns null until WorkOS or Clerk is wired. */
export async function getSession(): Promise<Session | null> {
  return null;
}
