// Provider IDs contain "/"; route segments cannot. Keep the original ID in JSON.
export function modelSlug(id: string): string {
  return id.replaceAll("/", "--");
}

export function modelHref(id: string, challenge?: string): string {
  return `/models/${modelSlug(id)}${challenge ? `/${challenge}` : ""}`;
}
