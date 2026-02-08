import { NextResponse } from 'next/server';
import { fetchUpliftChartFromLedger } from '../../../backend/grpc_clients';

export async function GET() {
  const data = await fetchUpliftChartFromLedger();
  return NextResponse.json(data);
}
