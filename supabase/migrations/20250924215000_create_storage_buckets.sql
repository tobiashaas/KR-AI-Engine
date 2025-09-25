-- Create storage buckets for KRAI Engine
-- This migration creates the necessary storage buckets for documents and images

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types) VALUES 
    ('krai-documents', 'krai-documents', false, 104857600, ARRAY['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
    ('krai-images', 'krai-images', false, 52428800, ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/tiff'])
ON CONFLICT (id) DO NOTHING;

-- Create storage policies for krai-documents bucket (if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-documents-read' AND tablename = 'objects') THEN
        CREATE POLICY "krai-documents-read" ON storage.objects FOR SELECT USING (bucket_id = 'krai-documents' AND auth.role() = 'authenticated');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-documents-insert' AND tablename = 'objects') THEN
        CREATE POLICY "krai-documents-insert" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'krai-documents' AND auth.role() = 'authenticated');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-documents-update' AND tablename = 'objects') THEN
        CREATE POLICY "krai-documents-update" ON storage.objects FOR UPDATE USING (bucket_id = 'krai-documents' AND auth.role() = 'authenticated');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-documents-delete' AND tablename = 'objects') THEN
        CREATE POLICY "krai-documents-delete" ON storage.objects FOR DELETE USING (bucket_id = 'krai-documents' AND auth.role() = 'authenticated');
    END IF;
END
$$;

-- Create storage policies for krai-images bucket (if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-images-read' AND tablename = 'objects') THEN
        CREATE POLICY "krai-images-read" ON storage.objects FOR SELECT USING (bucket_id = 'krai-images' AND auth.role() = 'authenticated');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-images-insert' AND tablename = 'objects') THEN
        CREATE POLICY "krai-images-insert" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'krai-images' AND auth.role() = 'authenticated');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-images-update' AND tablename = 'objects') THEN
        CREATE POLICY "krai-images-update" ON storage.objects FOR UPDATE USING (bucket_id = 'krai-images' AND auth.role() = 'authenticated');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'krai-images-delete' AND tablename = 'objects') THEN
        CREATE POLICY "krai-images-delete" ON storage.objects FOR DELETE USING (bucket_id = 'krai-images' AND auth.role() = 'authenticated');
    END IF;
END
$$;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Storage buckets created successfully: krai-documents, krai-images';
END
$$;
