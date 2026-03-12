import { refreshAccessToken } from "./auth";

type AuthFetchOptions = {
  token?: string | null;
  retry?: boolean;
};

export async function authFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
  options: AuthFetchOptions = {}
): Promise<Response> {
  const { token, retry = true } = options;
  const accessToken = token ?? localStorage.getItem("access_token");
  const headers = new Headers(init.headers || {});

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(input, { ...init, headers });

  if (response.status !== 401 || !retry) {
    return response;
  }

  const refreshed = await refreshAccessToken();
  if (!refreshed) {
    return response;
  }

  headers.set("Authorization", `Bearer ${refreshed}`);
  return fetch(input, { ...init, headers });
}
