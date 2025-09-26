"""
Supabase configuration for KRAI Engine
Includes database connection and storage bucket setup
"""

import os
import httpx
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent.parent / '.env')

class SupabaseConfig:
    """Supabase configuration manager"""
    
    def __init__(self):
        self.config = self._load_config()
        self.supabase_url = self.config['supabase_url']
        self.supabase_key = self.config['supabase_key']
        self.supabase_service_key = self.config['supabase_service_key']
    
    def _load_config(self) -> Dict:
        """Load Supabase configuration from environment variables"""
        return {
            'supabase_url': os.getenv('SUPABASE_URL'),
            'supabase_key': os.getenv('SUPABASE_ANON_KEY'),
            'supabase_service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            'supabase_password': os.getenv('SUPABASE_PASSWORD') or os.getenv('POSTGRES_PASSWORD'),
            'storage_bucket': os.getenv('SUPABASE_STORAGE_BUCKET', 'krai-documents'),
            'image_bucket': os.getenv('SUPABASE_IMAGE_BUCKET', 'krai-images')
        }
    
    def get_database_url(self) -> str:
        """Get PostgreSQL connection string for Supabase"""
        if not self.config['supabase_password']:
            raise ValueError("SUPABASE_PASSWORD or POSTGRES_PASSWORD environment variables must be set")
        
        # For local Supabase, use direct PostgreSQL connection
        if '127.0.0.1' in self.config['supabase_url'] or 'localhost' in self.config['supabase_url']:
            return f"postgresql://postgres:{self.config['supabase_password']}@127.0.0.1:54322/postgres"
        
        # For cloud Supabase, extract database info from URL
        db_host = self.config['supabase_url'].replace('https://', '').replace('.supabase.co', '')
        db_host = f"{db_host}.supabase.co"
        
        return f"postgresql://postgres:{self.config['supabase_password']}@{db_host}:5432/postgres"
    
    def get_storage_url(self) -> str:
        """Get Supabase storage URL"""
        return f"{self.config['supabase_url']}/storage/v1"
    
    def get_api_url(self) -> str:
        """Get Supabase API URL"""
        return f"{self.config['supabase_url']}/rest/v1"

class SupabaseStorage:
    """Supabase storage operations"""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.storage_url = config.get_storage_url()
        self.headers = {
            'Authorization': f'Bearer {config.supabase_service_key}',
            'Content-Type': 'application/json'
        }
    
    async def create_bucket(self, bucket_name: str, is_public: bool = True) -> bool:
        """Create a storage bucket"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.storage_url}/bucket",
                    headers=self.headers,
                    json={
                        'id': bucket_name,
                        'name': bucket_name,
                        'public': is_public,
                        'file_size_limit': 104857600,  # 100MB
                        'allowed_mime_types': [
                            'application/pdf',
                            'image/jpeg',
                            'image/png',
                            'image/gif',
                            'image/webp'
                        ]
                    }
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ Created bucket: {bucket_name}")
                    return True
                elif response.status_code == 409:
                    print(f"ℹ️ Bucket already exists: {bucket_name}")
                    return True
                else:
                    print(f"❌ Failed to create bucket {bucket_name}: {response.status_code} - {response.text}")
                    return False
        
        except Exception as e:
            print(f"❌ Error creating bucket {bucket_name}: {e}")
            return False
    
    async def upload_file(self, bucket_name: str, file_path: Path, 
                         file_content: bytes, content_type: str = None) -> Optional[str]:
        """Upload file to Supabase storage"""
        try:
            if not content_type:
                content_type = self._get_content_type(file_path)
            
            # Generate filename with hash for deduplication
            file_hash = self._calculate_file_hash(file_content)
            file_extension = file_path.suffix
            unique_filename = f"{file_hash}{file_extension}"
            
            upload_url = f"{self.storage_url}/object/{bucket_name}/{unique_filename}"
            
            headers = {
                'Authorization': f'Bearer {self.config.supabase_service_key}',
                'Content-Type': content_type
            }
            
            async with httpx.AsyncClient() as client:
                # First check if file already exists
                check_url = f"{self.storage_url}/object/{bucket_name}/{unique_filename}"
                check_response = await client.head(check_url, headers={'Authorization': f'Bearer {self.config.supabase_service_key}'})
                
                if check_response.status_code == 200:
                    # File already exists, return existing URL
                    storage_url = f"{self.config.supabase_url}/storage/v1/object/{bucket_name}/{unique_filename}"
                    print(f"⏭️ File already exists: {unique_filename}")
                    return storage_url
                
                # File doesn't exist, upload it
                response = await client.post(
                    upload_url,
                    headers=headers,
                    content=file_content
                )
                
                if response.status_code in [200, 201]:
                    # Return storage URL (not public since buckets are private)
                    storage_url = f"{self.config.supabase_url}/storage/v1/object/{bucket_name}/{unique_filename}"
                    print(f"✅ Uploaded file: {unique_filename}")
                    return storage_url
                else:
                    print(f"❌ Upload failed: {response.status_code} - {response.text}")
                    return None
        
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return None
    
    async def upload_image(self, image_path: Path, image_content: bytes, image_type: str = "error") -> Optional[Dict]:
        """Upload image to appropriate specialized bucket"""
        try:
            # Calculate image hash
            image_hash = self._calculate_file_hash(image_content)
            
            # Determine target bucket based on image type
            bucket_mapping = {
                "error": "krai-error-images",
                "manual": "krai-manual-images", 
                "parts": "krai-parts-images"
            }
            
            target_bucket = bucket_mapping.get(image_type, "krai-error-images")
            
            # Upload to specialized bucket
            public_url = await self.upload_file(
                target_bucket,
                image_path,
                image_content,
                'image/jpeg'
            )
            
            if public_url:
                return {
                    'url': public_url,
                    'hash': image_hash,
                    'size': len(image_content),
                    'content_type': 'image/jpeg',
                    'filename': image_path.name,
                    'bucket': target_bucket,
                    'image_type': image_type
                }
            
            return None
        
        except Exception as e:
            print(f"❌ Error uploading image to {image_type} bucket: {e}")
            return None
    
    async def upload_document(self, doc_path: Path, doc_content: bytes) -> Optional[Dict]:
        """Upload document with metadata"""
        try:
            # Calculate document hash
            doc_hash = self._calculate_file_hash(doc_content)
            
            # Upload to document bucket
            public_url = await self.upload_file(
                self.config.config['storage_bucket'],
                doc_path,
                doc_content,
                'application/pdf'
            )
            
            if public_url:
                return {
                    'url': public_url,
                    'hash': doc_hash,
                    'size': len(doc_content),
                    'content_type': 'application/pdf',
                    'filename': doc_path.name
                }
            
            return None
        
        except Exception as e:
            print(f"❌ Error uploading document: {e}")
            return None
    
    async def bucket_exists(self, bucket_name: str) -> bool:
        """Check if a storage bucket exists"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.storage_url}/bucket",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    buckets = response.json()
                    return any(bucket.get('id') == bucket_name for bucket in buckets)
                else:
                    return False
        
        except Exception as e:
            print(f"❌ Error checking bucket {bucket_name}: {e}")
            return False
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get content type based on file extension"""
        extension = file_path.suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def _calculate_file_hash(self, content: bytes) -> str:
        """Calculate SHA256 hash of file content"""
        import hashlib
        return hashlib.sha256(content).hexdigest()
    
    async def setup_storage_buckets(self) -> bool:
        """Setup required storage buckets with existence check"""
        try:
            print("🚀 Setting up specialized KR-AI-Engine storage buckets...")
            
            # Define the specialized buckets
            buckets = [
                "krai-error-images",
                "krai-manual-images", 
                "krai-parts-images"
            ]
            
            success_count = 0
            for bucket_name in buckets:
                # Check if bucket exists first
                exists = await self.bucket_exists(bucket_name)
                if exists:
                    print(f"ℹ️ Bucket already exists: {bucket_name}")
                    success_count += 1
                else:
                    # Create bucket if it doesn't exist
                    created = await self.create_bucket(bucket_name, is_public=True)
                    if created:
                        success_count += 1
            
            if success_count == len(buckets):
                print("✅ All specialized storage buckets ready")
                return True
            else:
                print(f"❌ {len(buckets) - success_count} buckets failed to setup")
                return False
        
        except Exception as e:
            print(f"❌ Storage setup failed: {e}")
            return False

# Global Supabase configuration
supabase_config = SupabaseConfig()
