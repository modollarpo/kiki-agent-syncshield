import { NextResponse } from 'next/server';
import { fetchExplainabilityFeedFromBroker } from '../../../backend/grpc_clients';

export async function GET() {
  const explainabilityEvents = await fetchExplainabilityFeedFromBroker();
  return NextResponse.json(explainabilityEvents);
}
