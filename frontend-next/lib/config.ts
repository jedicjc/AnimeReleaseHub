function isLocalApiUrl(value: string | undefined): boolean {
  if (!value) {
    return false;
  }

  return /127\.0\.0\.1|localhost/.test(value);
}

const explicitApiUrl = process.env.NEXT_PUBLIC_API_URL;
const explicitApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

export const API_URL =
  explicitApiBaseUrl && isLocalApiUrl(explicitApiUrl)
    ? explicitApiBaseUrl
    : explicitApiUrl ??
      explicitApiBaseUrl ??
      "https://maple-backend-0t01.onrender.com";
