import os
import pandas as pd
from datetime import date, timedelta
from jugaad_data.nse import bhavcopy_save
from database.vector_storage import VectorStorage
from database.postgres_sync import PostgresSync

class HistoricalIngestService:
    """
    Automated Historical Intelligence Ingestion.
    Downloads NSE Bhavcopies, parses them, and indexes them for RAG.
    """
    def __init__(self):
        self.vector_db = VectorStorage(collection_name="bhavcopy_intelligence")
        self.pg_db = PostgresSync()
        self.temp_dir = "temp_bhavcopies"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def ingest_range(self, days: int = 30):
        """Ingests the last N trading days of market activity."""
        today = date.today()
        for i in range(days):
            target_date = today - timedelta(days=i)
            # Skip weekends (NSE is closed)
            if target_date.weekday() >= 5:
                continue
                
            try:
                print(f"📅 Attempting to download Bhavcopy for {target_date}...")
                file_path = bhavcopy_save(target_date, self.temp_dir)
                if file_path:
                    print(f"✅ Downloaded: {file_path}. Processing...")
                    self._process_bhavcopy(file_path, target_date)
            except Exception as e:
                print(f"⚠️ Could not fetch for {target_date}: {e}")

    def _process_bhavcopy(self, file_path: str, report_date: date):
        """Parses CSV and indexes key high-volume movers."""
        try:
            df = pd.read_csv(file_path)
            # Focus on EQ series and top value movers
            equity_df = df[df['SERIES'] == 'EQ']
            top_movers = equity_df.nlargest(10, 'TOTTRDVAL')
            
            for _, row in top_movers.iterrows():
                symbol = row['SYMBOL']
                payload = (
                    f"Market Snapshot for {symbol} on {report_date}:\n"
                    f"Open: {row['OPEN']}, High: {row['HIGH']}, Low: {row['LOW']}, Close: {row['CLOSE']}\n"
                    f"Traded Value: {row['TOTTRDVAL']}, Volume: {row['TOTTRDQTY']}"
                )
                
                # Update Vector Memory
                self.vector_db.upsert_document(
                    text=payload,
                    metadata={
                        "symbol": symbol, 
                        "date": report_date.isoformat(), 
                        "type": "HISTORICAL_SNAP"
                    },
                    namespace=f"hist_{symbol}"
                )
                
                # Optional: Update Postgres for time-series charts
                self.pg_db.insert_market_quote(
                    symbol, 
                    float(row['CLOSE']), 
                    0.0, # Change PCT 
                    int(row['TOTTRDQTY']), 
                    str(row['TOTTRDVAL'])
                )
            
        except Exception as e:
            print(f"❌ Error processing bhavcopy {file_path}: {e}")
        finally:
            # Consistent with PDF Intelligence Engine logic (Cleanup even on failure)
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    service = HistoricalIngestService()
    # Ingest last 7 days as a warm-up
    service.ingest_range(days=7)
