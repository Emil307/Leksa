import type { ReportUnexpectedResponse } from './apiClient.types';

export const reportUnexpectedResponse: ReportUnexpectedResponse = ({ path, status }) => {
  console.error({ path, status });
};
