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

-- 6. PERFORMANCE INDEXES (Optimized for Sub-10ms Hot Paths)
CREATE INDEX IF NOT EXISTS idx_asset_ticker ON asset_master(ticker);
CREATE INDEX IF NOT EXISTS idx_asset_sector ON asset_master(sector) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_quotes_asset_time ON market_quotes(asset_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_feed_asset_published ON intelligence_feed(asset_id, published_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_feed_category ON intelligence_feed(category);
CREATE INDEX IF NOT EXISTS idx_ipo_date ON ipo_registry(listing_date DESC NULLS LAST);

-- 📊 7. SECURITY HARDENING (Supabase Advisor Fixes)
-- RLS Enablement
ALTER TABLE IF EXISTS public.asset_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.market_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.market_metrics ENABLE ROW LEVEL SECURITY; -- Fix for reported issue
ALTER TABLE IF EXISTS public.intelligence_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.financial_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.ipo_registry ENABLE ROW LEVEL SECURITY;

-- Default Policies (Public Read, Authenticated Write)
DO $$ 
BEGIN 
    -- Asset Master
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'asset_master' AND policyname = 'Allow Public Read') THEN
        CREATE POLICY "Allow Public Read" ON public.asset_master FOR SELECT USING (true);
    END IF;

    -- Market Quotes
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_quotes' AND policyname = 'Allow Public Read') THEN
        CREATE POLICY "Allow Public Read" ON public.market_quotes FOR SELECT USING (true);
    END IF;
END $$;

-- Search Path Hardening (Fix for 'Function Search Path Mutable')
DO $$ 
BEGIN 
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'handle_new_user' AND pronamespace = 'public'::regnamespace) THEN
        ALTER FUNCTION public.handle_new_user() SET search_path = public;
    END IF;
END $$;

-- 👤 8. USER PROFILES & ACCESS CONTROL
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    tier TEXT DEFAULT 'FREE', -- 'FREE', 'PRO', 'ELITE'
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Profiles Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'profiles' AND policyname = 'Users can view their own profile') THEN
        CREATE POLICY "Users can view their own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'profiles' AND policyname = 'Users can update their own profile') THEN
        CREATE POLICY "Users can update their own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
    END IF;
END $$;

-- Automated Profile Creation Trigger
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    new.id, 
    new.email, 
    COALESCE(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1)), 
    new.raw_user_meta_data->>'avatar_url'
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    updated_at = NOW();
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 👤 10. USER WATCHLISTS (Personalized Tracking)
CREATE TABLE IF NOT EXISTS public.user_watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES asset_master(id) ON DELETE CASCADE,
    alert_threshold_low DECIMAL(10, 4),
    alert_threshold_high DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, asset_id)
);

-- 🔔 11. NOTIFICATIONS & SIGNALS (Sentiment/Price Alerts)
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT,
    type TEXT, -- 'SENTIMENT_SWING', 'PRICE_SHOCK', 'SYSTEM'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 📝 12. AUDIT LOGS (Financial Traceability)
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    action TEXT NOT NULL,
    resource TEXT,
    metadata JSONB,
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 🔍 13. FULL-TEXT SEARCH (Neural & Keyword Hybrid Discovery)
-- Add a search vector column to intelligence_feed
ALTER TABLE public.intelligence_feed ADD COLUMN IF NOT EXISTS fts_vector tsvector GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))
) STORED;

CREATE INDEX IF NOT EXISTS idx_feed_fts ON public.intelligence_feed USING GIN(fts_vector);

-- 📊 14. SECURITY HARDENING FOR NEW TABLES
ALTER TABLE public.user_watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN 
    -- Watchlists Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'user_watchlists' AND policyname = 'Users can manage their own watchlists') THEN
        CREATE POLICY "Users can manage their own watchlists" ON public.user_watchlists FOR ALL USING (auth.uid() = user_id);
    END IF;

    -- Notifications Policy
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'notifications' AND policyname = 'Users can view their own notifications') THEN
        CREATE POLICY "Users can view their own notifications" ON public.notifications FOR SELECT USING (auth.uid() = user_id);
    END IF;

    -- Audit Logs Policy (Admin/Self)
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'audit_logs' AND policyname = 'Users can view their own audit logs') THEN
        CREATE POLICY "Users can view their own audit logs" ON public.audit_logs FOR SELECT USING (auth.uid() = user_id);
    END IF;
END $$;
