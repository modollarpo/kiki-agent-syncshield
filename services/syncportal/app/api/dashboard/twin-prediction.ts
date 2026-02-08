import { NextResponse } from 'next/server';
import { fetchTwinPredictionFromSyncTwin } from '../../../backend/grpc_clients';

export async function GET() {
  const prediction = await fetchTwinPredictionFromSyncTwin();
  return NextResponse.json(prediction);
}
