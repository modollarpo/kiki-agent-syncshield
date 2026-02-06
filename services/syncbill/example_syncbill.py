"""
Example script demonstrating SyncBill usage

Calculates settlements and generates QBR reports for demo clients.
"""

import asyncio
import httpx
from datetime import datetime


SYNCBILL_URL = "http://localhost:8008"


async def example_calculate_settlement():
    """Example: Calculate settlement with positive uplift"""
    print("=" * 70)
    print("Example 1: Settlement Calculation (Positive Uplift)")
    print("=" * 70)
    
    revenue_data = {
        "client_id": "client_acme_corp",
        "billing_cycle": "Q1 2026",
        "total_revenue": 250000.0,
        "baseline_revenue": 180000.0,
        "attribution_source": "syncvalue"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SYNCBILL_URL}/api/v1/settlement/calculate",
            json=revenue_data
        )
        
        if response.status_code == 200:
            settlement = response.json()
            
            print(f"\n✅ Settlement Calculated: {settlement['settlement_id']}")
            print(f"\nClient: {settlement['client_id']}")
            print(f"Billing Cycle: {settlement['billing_cycle']}")
            print(f"\n{'Financial Summary':-^50}")
            print(f"Total Revenue:       ${settlement['total_revenue']:>15,.2f}")
            print(f"Baseline Revenue:    ${settlement['baseline_revenue']:>15,.2f}")
            print(f"{'-' * 50}")
            print(f"Attributed Uplift:   ${settlement['attributed_uplift']:>15,.2f}")
            print(f"Success Fee Rate:    {settlement['success_fee_rate']*100:>14.0f}%")
            print(f"KIKI Success Fee:    ${settlement['kiki_success_fee']:>15,.2f}")
            print(f"Client Net Benefit:  ${settlement['client_net_benefit']:>15,.2f}")
            print(f"\nStatus: {settlement['status']}")
            print(f"Calculated At: {settlement['calculated_at']}")
            
            return settlement
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None


async def example_calculate_settlement_no_uplift():
    """Example: Calculate settlement with no uplift (zero fee)"""
    print("\n" + "=" * 70)
    print("Example 2: Settlement Calculation (No Uplift)")
    print("=" * 70)
    
    revenue_data = {
        "client_id": "client_beta_inc",
        "billing_cycle": "Q1 2026",
        "total_revenue": 90000.0,
        "baseline_revenue": 100000.0,
        "attribution_source": "manual"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SYNCBILL_URL}/api/v1/settlement/calculate",
            json=revenue_data
        )
        
        if response.status_code == 200:
            settlement = response.json()
            
            print(f"\n✅ Settlement Calculated: {settlement['settlement_id']}")
            print(f"\nClient: {settlement['client_id']}")
            print(f"Billing Cycle: {settlement['billing_cycle']}")
            print(f"\n{'Financial Summary':-^50}")
            print(f"Total Revenue:       ${settlement['total_revenue']:>15,.2f}")
            print(f"Baseline Revenue:    ${settlement['baseline_revenue']:>15,.2f}")
            print(f"{'-' * 50}")
            print(f"Attributed Uplift:   ${settlement['attributed_uplift']:>15,.2f}")
            print(f"\n⚠️  No Uplift Detected - Zero Fee Applied")
            print(f"KIKI Success Fee:    ${settlement['kiki_success_fee']:>15,.2f}")
            print(f"Client Net Benefit:  ${settlement['client_net_benefit']:>15,.2f}")
            print(f"\nStatus: {settlement['status']}")
            
            return settlement
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None


async def example_list_settlements():
    """Example: List all settlements"""
    print("\n" + "=" * 70)
    print("Example 3: List All Settlements")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{SYNCBILL_URL}/api/v1/settlements")
        
        if response.status_code == 200:
            settlements = response.json()
            
            print(f"\n✅ Found {len(settlements)} settlement(s)")
            
            for settlement in settlements:
                print(f"\n{'-' * 50}")
                print(f"ID: {settlement['settlement_id']}")
                print(f"Client: {settlement['client_id']}")
                print(f"Cycle: {settlement['billing_cycle']}")
                print(f"Uplift: ${settlement['attributed_uplift']:,.2f}")
                print(f"Fee: ${settlement['kiki_success_fee']:,.2f}")
                print(f"Status: {settlement['status']}")
        else:
            print(f"❌ Error: {response.status_code}")


async def example_generate_qbr(client_id: str = "client_acme_corp"):
    """Example: Generate QBR report"""
    print("\n" + "=" * 70)
    print("Example 4: Generate QBR Report")
    print("=" * 70)
    
    qbr_request = {
        "client_name": "Acme Corporation",
        "client_id": client_id,
        "period": "Q1 2026",
        "include_metrics": True
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SYNCBILL_URL}/api/v1/qbr/generate",
            json=qbr_request
        )
        
        if response.status_code == 200:
            qbr = response.json()
            
            print(f"\n✅ QBR Report Generated: {qbr['report_id']}")
            print(f"\nClient: {qbr['client_name']}")
            print(f"Period: {qbr['period']}")
            print(f"File Path: {qbr['file_path']}")
            print(f"Download URL: {qbr['download_url']}")
            print(f"Generated At: {qbr['generated_at']}")
            print(f"Expires At: {qbr['expires_at']}")
            
            print(f"\n📥 To download the report, visit:")
            print(f"   {SYNCBILL_URL}{qbr['download_url']}")
            
            return qbr
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None


async def example_health_check():
    """Example: Check service health"""
    print("\n" + "=" * 70)
    print("Example 5: Health Check")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{SYNCBILL_URL}/health")
        
        if response.status_code == 200:
            health = response.json()
            
            print(f"\n✅ Service is {health['status']}")
            print(f"\nService: {health['service']}")
            print(f"Version: {health['version']}")
            
            if 'metrics' in health:
                print(f"\nMetrics:")
                for key, value in health['metrics'].items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Service unhealthy: {response.status_code}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("SyncBill Service - Example Demonstrations")
    print("=" * 70)
    print("\nEnsure SyncBill service is running on http://localhost:8008")
    print("Start with: python services/syncbill/app/main.py")
    
    try:
        # Check health first
        await example_health_check()
        
        # Calculate settlements
        settlement1 = await example_calculate_settlement()
        settlement2 = await example_calculate_settlement_no_uplift()
        
        # List all settlements
        await example_list_settlements()
        
        # Generate QBR report (requires settlement to exist)
        if settlement1:
            await example_generate_qbr(settlement1['client_id'])
        
        print("\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("=" * 70)
        
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to SyncBill service")
        print("Ensure the service is running on http://localhost:8008")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
