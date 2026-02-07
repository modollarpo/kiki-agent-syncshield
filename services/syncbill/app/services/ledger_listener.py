"""
SyncLedger Event Listener

Listens for settlement events from SyncLedger via periodic gRPC polling
(or future gRPC streaming implementation).

Event Flow:
1. SyncLedger completes monthly settlement calculation
2. SyncBill polls GetSettlementReport endpoint
3. Detect new settlements (not yet invoiced)
4. Generate Invoice record
5. Create Stripe invoice
6. Generate custom PDF
7. Mark settlement as invoiced in SyncLedger
"""

import asyncio
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

# Import generated protobuf stubs (will be generated via make proto)
try:
    from proto import cms_integration_pb2 as pb
    from proto import cms_integration_pb2_grpc as pb_grpc
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️  Protobuf stubs not found. Run 'make proto' to generate.")
    pb = None
    pb_grpc = None

from app.models import Invoice, InvoiceLineItem
from app.services.stripe_service import StripeService
from app.services.pdf_service import PDFService
from app.database import async_session_maker
from sqlalchemy import select

logger = logging.getLogger(__name__)


class LedgerEventListener:
    """
    Listens for SyncLedger settlement events and triggers invoice generation.
    """
    
    def __init__(
        self,
        ledger_host: str,
        ledger_port: int,
        stripe_service: StripeService,
        poll_interval: int = 300  # Poll every 5 minutes
    ):
        self.ledger_host = ledger_host
        self.ledger_port = ledger_port
        self.stripe_service = stripe_service
        self.pdf_service = PDFService()
        self.poll_interval = poll_interval
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[pb_grpc.SyncLedgerServiceStub] = None
        
    async def connect(self):
        """Establish gRPC connection to SyncLedger"""
        if not pb or not pb_grpc:
            raise ImportError("Protobuf stubs not generated. Run 'make proto'.")
        
        self.channel = grpc.aio.insecure_channel(
            f"{self.ledger_host}:{self.ledger_port}"
        )
        self.stub = pb_grpc.SyncLedgerServiceStub(self.channel)
        logger.info(f"✅ Connected to SyncLedger at {self.ledger_host}:{self.ledger_port}")
    
    async def close(self):
        """Close gRPC connection"""
        if self.channel:
            await self.channel.close()
            logger.info("👋 Disconnected from SyncLedger")
    
    async def listen_for_settlements(self):
        """
        Poll SyncLedger for new settlements.
        
        Checks for completed monthly settlements that haven't been invoiced yet.
        """
        if not self.stub:
            await self.connect()
        
        logger.info("👂 Listening for SyncLedger settlement events...")
        
        # Get list of all active stores (should be from database)
        # For now, we'll query recent settlements
        
        # Check last 2 months for new settlements
        current_date = datetime.utcnow()
        
        for months_ago in range(2):
            check_date = current_date - timedelta(days=30 * months_ago)
            year = check_date.year
            month = check_date.month
            
            # Query all stores (in production, maintain list of active stores)
            # For demo, check stores 1-1000
            for store_id in range(1, 100):  # Check first 100 stores
                try:
                    await self._process_store_settlement(store_id, year, month)
                except Exception as e:
                    logger.debug(f"Store {store_id} settlement check: {e}")
                    continue
        
        logger.info("✅ Settlement polling cycle complete")
        await asyncio.sleep(self.poll_interval)
    
    async def _process_store_settlement(
        self,
        store_id: int,
        year: int,
        month: int
    ):
        """
        Check if store has completed settlement for given period.
        If yes and not invoiced, generate invoice.
        """
        # Check if invoice already exists
        async with async_session_maker() as session:
            stmt = select(Invoice).where(
                Invoice.store_id == store_id,
                Invoice.billing_year == year,
                Invoice.billing_month == month
            )
            result = await session.execute(stmt)
            existing_invoice = result.scalar_one_or_none()
            
            if existing_invoice:
                logger.debug(f"Invoice already exists for store {store_id} - {year}-{month:02d}")
                return
        
        # Fetch settlement report from SyncLedger
        try:
            request = pb.SuccessFeeRequest(
                store_id=store_id,
                year=year,
                month=month
            )
            
            response: pb.SuccessFeeResponse = await self.stub.CalculateSuccessFee(request)
            
            if not response.success:
                logger.debug(f"No settlement data for store {store_id} - {year}-{month:02d}")
                return
            
            # Check if there's incremental revenue (success fee > 0)
            incremental_revenue = self._money_to_decimal(response.incremental_revenue)
            success_fee = self._money_to_decimal(response.success_fee_amount)
            
            if success_fee <= 0:
                logger.info(f"⚠️  Store {store_id} - {year}-{month:02d}: Zero fee (Zero-Risk Policy)")
                # Still create invoice showing $0 fee for transparency
            
            # Generate invoice
            await self._generate_invoice_from_settlement(
                store_id=store_id,
                year=year,
                month=month,
                settlement_data=response
            )
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                logger.debug(f"No settlement for store {store_id} - {year}-{month:02d}")
            else:
                logger.error(f"gRPC error fetching settlement: {e}")
    
    async def _generate_invoice_from_settlement(
        self,
        store_id: int,
        year: int,
        month: int,
        settlement_data: 'pb.SuccessFeeResponse'
    ):
        """
        Generate Invoice from SyncLedger settlement data.
        
        Steps:
        1. Create Invoice database record
        2. Create Stripe invoice
        3. Generate custom PDF
        4. Update database with Stripe references
        """
        logger.info(f"📄 Generating invoice for store {store_id} - {year}-{month:02d}")
        
        # Extract data from settlement (Net Profit Model)
        baseline_revenue = self._money_to_decimal(settlement_data.baseline_revenue)
        current_revenue = self._money_to_decimal(settlement_data.current_revenue)
        incremental_revenue = self._money_to_decimal(settlement_data.incremental_revenue)
        
        # Ad Spend data (NEW - Net Profit Model)
        baseline_ad_spend = self._money_to_decimal(getattr(settlement_data, 'baseline_ad_spend', pb.Money(amount=0)))
        actual_ad_spend = self._money_to_decimal(getattr(settlement_data, 'actual_ad_spend', pb.Money(amount=0)))
        incremental_ad_spend = actual_ad_spend - baseline_ad_spend
        
        # Net Profit Calculation
        baseline_profit = baseline_revenue - baseline_ad_spend
        actual_profit = current_revenue - actual_ad_spend
        net_profit_uplift = incremental_revenue - incremental_ad_spend
        
        # Success fee based on Net Profit Uplift (not gross revenue)
        success_fee = self._money_to_decimal(settlement_data.success_fee_amount)
        
        # Client value metrics
        client_net_gain = net_profit_uplift - success_fee
        client_roi = Decimal("0.0")
        if success_fee > 0:
            client_roi = client_net_gain / success_fee
        
        growth_percentage = Decimal(str(settlement_data.growth_percentage))
        
        # Calculate billing period dates
        billing_start = datetime(year, month, 1)
        if month == 12:
            billing_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            billing_end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Create invoice record (Net Profit Model)
        invoice = Invoice(
            invoice_number=f"KIKI-{year}{month:02d}-{store_id:06d}",
            store_id=store_id,
            platform="shopify",  # TODO: Get from store metadata
            customer_name=f"Store #{store_id}",  # TODO: Get actual name
            customer_email=f"store{store_id}@example.com",  # TODO: Get from database
            billing_month=month,
            billing_year=year,
            billing_period_start=billing_start,
            billing_period_end=billing_end,
            
            # Revenue metrics
            baseline_revenue=baseline_revenue,
            actual_revenue=current_revenue,
            incremental_revenue=incremental_revenue,
            uplift_percentage=growth_percentage,
            
            # Ad Spend metrics (Net Profit Model)
            baseline_ad_spend=baseline_ad_spend,
            actual_ad_spend=actual_ad_spend,
            incremental_ad_spend=incremental_ad_spend,
            ad_spend_uplift_percent=(incremental_ad_spend / baseline_ad_spend * 100) if baseline_ad_spend > 0 else Decimal("0.0"),
            
            # Net Profit metrics
            net_profit_uplift=net_profit_uplift,
            baseline_profit=baseline_profit,
            actual_profit=actual_profit,
            net_profit_uplift_percent=(net_profit_uplift / baseline_profit * 100) if baseline_profit > 0 else Decimal("0.0"),
            
            # Client value
            client_net_gain=client_net_gain,
            client_roi=client_roi,
            
            # Invoice amounts
            subtotal=success_fee,
            tax_rate=Decimal("0.0"),  # TODO: Calculate based on jurisdiction
            tax_amount=Decimal("0.0"),
            total_amount=success_fee,
            amount_due=success_fee,
            currency="USD",
            status="draft",
            payment_status="unpaid",
            issue_date=datetime.utcnow(),
            created_by="ledger_listener"
        )
        
        # Calculate due date (Net 30)
        invoice.calculate_due_date()
        
        # Extract XAI data from settlement
        if settlement_data.attribution_stats:
            invoice.attribution_stats = dict(settlement_data.attribution_stats)
        
        # Save to database
        async with async_session_maker() as session:
            session.add(invoice)
            await session.commit()
            await session.refresh(invoice)
            
            logger.info(f"✅ Invoice record created: {invoice.invoice_number} (ID: {invoice.id})")
        
        # Create Stripe invoice
        try:
            stripe_result = await self.stripe_service.create_invoice_from_settlement(invoice)
            
            # Update invoice with Stripe references
            async with async_session_maker() as session:
                stmt = select(Invoice).where(Invoice.id == invoice.id)
                result = await session.execute(stmt)
                inv = result.scalar_one()
                
                inv.stripe_invoice_id = stripe_result["stripe_invoice_id"]
                inv.stripe_customer_id = stripe_result["stripe_customer_id"]
                inv.hosted_invoice_url = stripe_result["hosted_invoice_url"]
                inv.invoice_pdf = stripe_result["invoice_pdf"]
                inv.status = "sent"
                inv.sent_at = datetime.utcnow()
                
                await session.commit()
                
            logger.info(f"✅ Stripe invoice created: {stripe_result['stripe_invoice_id']}")
            
        except Exception as e:
            logger.error(f"❌ Stripe invoice creation failed: {e}", exc_info=True)
            # Keep database record even if Stripe fails
        
        # Generate custom PDF (async background task)
        # asyncio.create_task(self.pdf_service.generate_invoice_pdf(invoice))
        
        logger.info(f"🎉 Invoice {invoice.invoice_number} successfully generated")
    
    @staticmethod
    def _money_to_decimal(money_pb) -> Decimal:
        """Convert protobuf Money to Decimal"""
        if not money_pb:
            return Decimal("0.00")
        return Decimal(str(money_pb.units)) + Decimal(str(money_pb.nanos)) / Decimal(1_000_000_000)
