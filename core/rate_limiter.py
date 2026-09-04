"""
NeuroStudy Security, Rate Limiter & Cryptographic Verification Engine
Prevents API key abuse, DDoS, and enforces tamper-proof clinical signatures.
"""
import time
import hmac
import hashlib
import datetime
from core.db import get_connection

SECRET_SALT = "NEUROSTUDY_MED_VERIFY_SECRET_2026_EBM"

class RateLimiter:
    @staticmethod
    def check_and_increment(username, action="ai_generate", max_per_minute=10):
        """
        Enforces sliding window and daily quotas.
        Returns: (allowed: bool, message: str, remaining: int)
        """
        if username in ["dimas", "dr_dimas", "admin"]:
            return True, "Admin/Owner Access: Unlimited", 9999
            
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Check minute-level flood
        now_ts = datetime.datetime.now()
        one_min_ago = (now_ts - datetime.timedelta(minutes=1)).isoformat()
        
        cur.execute("""
        SELECT COUNT(*) as count FROM audit_logs 
        WHERE username = ? AND action = ? AND timestamp >= ?;
        """, (username, action, one_min_ago))
        min_count = cur.fetchone()["count"]
        
        if min_count >= max_per_minute:
            conn.close()
            return False, "Terlalu banyak permintaan! Harap tunggu 60 detik demi keamanan server.", 0
            
        # 2. Check daily quota
        today_str = datetime.date.today().isoformat()
        cur.execute("SELECT tier, daily_ai_requests, last_request_date FROM users WHERE username = ?;", (username,))
        row = cur.fetchone()
        
        tier = "free"
        daily_used = 0
        if row:
            tier = row["tier"] or "free"
            if row["last_request_date"] == today_str:
                daily_used = row["daily_ai_requests"] or 0
                
        daily_limit = 50 if tier == "pro" else 15
        if daily_used >= daily_limit:
            conn.close()
            return False, f"Batas kuota harian ({daily_limit} modul/hari untuk tier {tier.upper()}) tercapai.", 0
            
        # Log this request
        cur.execute("""
        INSERT INTO audit_logs (username, action, endpoint, status, timestamp)
        VALUES (?, ?, ?, 'allowed', ?);
        """, (username, action, action, now_ts.isoformat()))
        
        cur.execute("""
        UPDATE users SET daily_ai_requests = ?, last_request_date = ? WHERE username = ?;
        """, (daily_used + 1, today_str, username))
        
        conn.commit()
        conn.close()
        
        remaining = max(0, daily_limit - (daily_used + 1))
        return True, "OK", remaining

    @staticmethod
    def generate_clinical_signature(module_title, reviewer_name, license_str="STR-1994-EBM"):
        """Generate HMAC-SHA256 tamper-proof signature for verified clinical notes."""
        payload = f"{module_title}|{reviewer_name}|{license_str}|{datetime.date.today().isoformat()}"
        sig = hmac.new(SECRET_SALT.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return f"EBM-SIG-{sig[:16].upper()}"

    @staticmethod
    def verify_clinical_signature(module_title, reviewer_name, signature):
        if not signature or not signature.startswith("EBM-SIG-"):
            return False
        expected = RateLimiter.generate_clinical_signature(module_title, reviewer_name)
        return hmac.compare_digest(signature, expected)
