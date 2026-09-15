export interface AuthSession {
  userId: string;
  sessionId: string;
  accessToken: string;
  refreshToken: string;
}
