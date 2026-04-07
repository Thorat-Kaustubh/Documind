import os
import psycopg2
from dotenv import load_dotenv
import sys

def fix():
    load_dotenv()
    url = os.getenv('POSTGRES_URL')
    if not url:
        print("Error: No POSTGRES_URL found in .env")
        return
    
    # Ensure sslmode is used if connecting to Supabase pooler
    if "pooler.supabase.com" in url and "sslmode" not in url:
        if "?" in url:
            url += "&sslmode=require"
        else:
            url += "?sslmode=require"

    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        cur = conn.cursor()
        
        # 1. Hard-refresh the Profiles table schema
        print("Updating profiles table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.profiles (
                id UUID PRIMARY KEY,
                email TEXT,
                full_name TEXT,
                avatar_url TEXT,
                tier TEXT DEFAULT 'FREE',
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
        """)

        # 2. Inject Hyper-Resilient Trigger
        print("Injecting resilient trigger...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION public.handle_new_user() 
            RETURNS trigger AS $body$
            BEGIN
              INSERT INTO public.profiles (id, email, full_name, avatar_url)
              VALUES (
                new.id, 
                new.email, 
                COALESCE(new.raw_user_meta_data->>'full_name', split_part(new.email, '@', 1), 'Analyst'), 
                new.raw_user_meta_data->>'avatar_url'
              )
              ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                updated_at = NOW();
              RETURN new;
            EXCEPTION WHEN OTHERS THEN
              -- Log the error to profiles if possible or just exit safely
              INSERT INTO public.profiles (id, email, full_name) 
              VALUES (new.id, new.email, 'Recovery Profile') 
              ON CONFLICT (id) DO NOTHING;
              RETURN new;
            END;
            $body$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;
        """)

        # 3. Re-bind the trigger
        print("Binding trigger to auth.users...")
        cur.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;")
        cur.execute("""
            CREATE TRIGGER on_auth_user_created
              AFTER INSERT ON auth.users
              FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
        """)

        conn.commit()
        print("✅ [DATABASE] Mega-Resilient Sync Trigger Established.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix()
