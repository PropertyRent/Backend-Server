-- Migration script to add admin_reply fields to schedule_meetings table
-- Run this SQL script in your PostgreSQL database

-- Add admin_reply column
ALTER TABLE schedule_meetings 
ADD COLUMN IF NOT EXISTS admin_reply TEXT DEFAULT NULL;

-- Add admin_reply_date column  
ALTER TABLE schedule_meetings 
ADD COLUMN IF NOT EXISTS admin_reply_date TIMESTAMPTZ DEFAULT NULL;

-- Verify the columns were added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'schedule_meetings' 
AND column_name IN ('admin_reply', 'admin_reply_date');