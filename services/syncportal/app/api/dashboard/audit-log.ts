import { NextResponse } from 'next/server';
import { fetchAuditLogFromSyncShield } from '../../../backend/grpc_clients';

export async function GET() {
  const logs = await fetchAuditLogFromSyncShield();
  return NextResponse.json(logs);
}
