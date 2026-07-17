import os
import httpx
from typing import Dict, Any, Optional

class StorageService:
    def __init__(self):
        # Fallbacks for local / test environments
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.bucket = os.getenv("SUPABASE_BUCKET", "assignments")
        
    def upload_file(self, path: str, content: bytes, content_type: str) -> Dict[str, Any]:
        """
        Uploads a file to Supabase Storage.
        If credentials are not present, simulate successful upload.
        """
        if not self.supabase_url or not self.supabase_key:
            # Mock simulation mode for testing / local development
            return {
                "storage_path": f"{self.bucket}/{path}",
                "file_url": f"https://mock-supabase.com/storage/v1/object/public/{self.bucket}/{path}"
            }
            
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{path}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": content_type
        }
        
        with httpx.Client() as client:
            resp = client.post(url, content=content, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Failed to upload to Supabase Storage: {resp.text}")
                
        return {
            "storage_path": f"{self.bucket}/{path}",
            "file_url": f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{path}"
        }
        
    def get_signed_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Generates a signed URL for a file in Supabase Storage.
        """
        parts = storage_path.split("/")
        if parts[0] == self.bucket:
            path_in_bucket = "/".join(parts[1:])
        else:
            path_in_bucket = storage_path
            
        if not self.supabase_url or not self.supabase_key:
            # Mock signed URL
            return f"https://mock-supabase.com/storage/v1/object/sign/{self.bucket}/{path_in_bucket}?token=mock_signed_token"
            
        url = f"{self.supabase_url}/storage/v1/object/sign/{self.bucket}/{path_in_bucket}"
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        body = {"expiresIn": expires_in}
        
        with httpx.Client() as client:
            resp = client.post(url, json=body, headers=headers)
            if resp.status_code != 200:
                # Fallback to public URL on error
                return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{path_in_bucket}"
            signed_url_path = resp.json().get("signedURL")
            return f"{self.supabase_url}{signed_url_path}"

storage_service = StorageService()
