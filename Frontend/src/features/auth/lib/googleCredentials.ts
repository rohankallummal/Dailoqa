import { getAppUrl, getGoogleClientId, getGoogleClientSecret } from "./env";

export type GoogleCredentials = {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
};

export function getGoogleCredentials(): GoogleCredentials {
  return {
    clientId: getGoogleClientId(),
    clientSecret: getGoogleClientSecret(),
    redirectUri: `${getAppUrl()}/api/auth/callback/google`,
  };
}
