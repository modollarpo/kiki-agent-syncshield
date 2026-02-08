import { NextResponse } from 'next/server';
import { fetchSummaryStatsFromKiki } from '../../../backend/grpc_clients';

export async function GET() {
  const stats = await fetchSummaryStatsFromKiki();
  return NextResponse.json(stats);
}
