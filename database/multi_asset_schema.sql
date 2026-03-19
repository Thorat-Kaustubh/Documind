-- Documind Elite: Multi-Asset Unified Schema
-- Supports Equity, Mutual Funds, IPOs, Commodities, and News

-- 1. MASTER ASSET REGISTRY
CREATE TABLE IF NOT EXISTS asset_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'EQUITY', 'COMMODITY', 'FOREX', 'IPOS', 'MUTUAL_FUND'
    sector TEXT,
    exchange TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. HIGH-FREQUENCY METRICS (Delayed/EOD)
CREATE TABLE IF NOT EXISTS market_quotes (
    id BIGSERIAL PRIMARY KEY,
    asset_id UUID REFERENCES asset_master(id),
    price DECIMAL(18, 4),
    change_percent DECIMAL(10, 4),
    volume BIGINT,
    market_cap TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. CORPORATE ANNOUNCEMENTS & NEWS (The 'Discovery' Layer)
CREATE TABLE IF NOT EXISTS intelligence_feed (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES asset_master(id),
    title TEXT NOT NULL,
    content TEXT,
    source TEXT, -- 'TAVILY', 'NSE', 'REUTERS'
    sentiment_score DECIMAL(3, 2),
    category TEXT, -- 'ANNOUNCEMENT', 'NEWS', 'REGULATORY'
    published_at TIMESTAMP WITH TIME ZONE,
    vector_id TEXT -- ID in ChromaDB for RAG lookup
);

-- 4. FUNDAMENTAL MASTERS (Historical)
CREATE TABLE IF NOT EXISTS financial_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES asset_master(id),
    fiscal_year INTEGER,
    quarter TEXT,
    revenue DECIMAL(24, 4),
    net_profit DECIMAL(24, 4),
    eps DECIMAL(10, 4),
    raw_json JSONB -- Stores the full scraped tables for RAG verification
);

-- 5. IPO WATCHLIST
CREATE TABLE IF NOT EXISTS ipo_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name TEXT NOT NULL,
    listing_date DATE,
    issue_price_range TEXT,
    lot_size INTEGER,
    status TEXT -- 'UPCOMING', 'OPEN', 'LISTED'
);
