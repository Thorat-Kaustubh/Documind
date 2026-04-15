import os
import psycopg2
from dotenv import load_dotenv
import sys

def normalize_database():
    load_dotenv()
    url = os.getenv('POSTGRES_URL')
    if not url:
        print("Error: No POSTGRES_URL found in .env")
        return
    
    # Supabase connection fix
    if "pooler.supabase.com" in url and "sslmode" not in url:
        if "?" in url: url += "&sslmode=require"
        else: url += "?sslmode=require"

    print("Connecting to database for Multi-Provider Sync...")
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        
        # 1. Inject Unified Normalizer Function
        print("Injecting Unified Normalizer Function...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION public.handle_new_user() 
            RETURNS trigger AS $body$
            BEGIN
              INSERT INTO public.profiles (id, email, full_name, avatar_url)
              VALUES (
                new.id, 
                new.email, 
                COALESCE(
                    new.raw_user_meta_data->>'full_name', 
                    new.raw_user_meta_data->>'name', 
                    new.raw_user_meta_data->>'user_name', 
                    split_part(new.email, '@', 1),
                    'Analyst'
                ), 
                COALESCE(
                    new.raw_user_meta_data->>'avatar_url',
                    new.raw_user_meta_data->>'picture',
                    ''
                )
              )
              ON CONFLICT (id) DO UPDATE SET
                email = EXCLUDED.email,
                full_name = EXCLUDED.full_name,
                avatar_url = EXCLUDED.avatar_url,
                updated_at = NOW();
              RETURN new;
            END;
            $body$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;
        """)

        conn.commit()
        print("[DATABASE] Multi-Provider Normalization Rule Established.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    normalize_database()
