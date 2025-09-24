-- =====================================
-- KRAI ENGINE - SYSTEM SCHEMA
-- System Operations: Queue, Monitoring, Audit
-- =====================================

-- =====================================
-- 1. PROCESSING QUEUE TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_system.processing_queue (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Task Definition
  task_type text CHECK (task_type IN (
    'pdf_extraction',                          -- PDF text extraction
    'embedding_generation',                    -- Generate vector embeddings
    'video_processing',                        -- Process instructional videos
    'document_indexing',                       -- Index document content
    'cpmd_parsing',                           -- Parse CPMD databases
    'relationship_mapping',                   -- Map document relationships
    'error_code_extraction',                  -- Extract error codes
    'image_analysis',                         -- Analyze images with AI
    'defect_detection'                        -- Detect print defects
  )),
  
  -- Target References
  document_id uuid REFERENCES krai_core.documents(id) ON DELETE CASCADE,
  chunk_id uuid REFERENCES krai_intelligence.chunks(id) ON DELETE CASCADE,
  video_id uuid REFERENCES krai_content.instructional_videos(id) ON DELETE CASCADE,
  image_id uuid REFERENCES krai_content.images(id) ON DELETE CASCADE,
  
  -- Task Status & Priority
  status text CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retry')) DEFAULT 'pending',
  priority integer CHECK (priority BETWEEN 1 AND 10) DEFAULT 5,  -- 1=highest, 10=lowest
  
  -- Retry Logic
  attempts integer DEFAULT 0,                  -- Retry attempts
  max_attempts integer DEFAULT 3,              -- Maximum retries
  error_message text,                          -- Failure details
  
  -- Processing Timestamps
  processing_started_at timestamp with time zone,
  processing_completed_at timestamp with time zone,
  
  -- Task Configuration
  task_metadata jsonb DEFAULT '{}'::jsonb,     -- Task-specific parameters
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for processing queue
CREATE INDEX IF NOT EXISTS idx_queue_status_priority ON krai_system.processing_queue(status, priority DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_queue_task_type ON krai_system.processing_queue(task_type);
CREATE INDEX IF NOT EXISTS idx_queue_document ON krai_system.processing_queue(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_queue_chunk ON krai_system.processing_queue(chunk_id) WHERE chunk_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_queue_pending ON krai_system.processing_queue(created_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_queue_failed ON krai_system.processing_queue(attempts, max_attempts) WHERE status = 'failed';

COMMENT ON TABLE krai_system.processing_queue IS 'Background processing queue for async document and content processing';
COMMENT ON COLUMN krai_system.processing_queue.priority IS 'Processing priority: 1=highest, 10=lowest';

-- =====================================
-- 2. PERFORMANCE METRICS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_system.performance_metrics (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Metric Information
  metric_name text NOT NULL,                    -- "query_response_time", "embedding_generation", "document_processing"
  metric_type text CHECK (metric_type IN ('query', 'processing', 'system', 'user_action')),
  
  -- Performance Data
  execution_time_ms integer,                    -- Execution time in milliseconds
  memory_usage_mb numeric,                      -- Memory usage in MB
  cpu_usage_percent numeric,                    -- CPU usage percentage
  
  -- Context Information
  query_text text,                              -- SQL query (for query metrics)
  parameters jsonb,                             -- Query or operation parameters
  user_id uuid,                                 -- User who triggered the operation
  
  -- Resource Information
  table_name text,                              -- Affected table (if applicable)
  schema_name text,                             -- Affected schema (if applicable)
  
  -- System Information
  server_hostname text,                         -- Server hostname
  database_name text,                           -- Database name
  
  -- Timestamps
  recorded_at timestamp with time zone DEFAULT now()
);

-- Indexes for performance metrics
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON krai_system.performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON krai_system.performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_execution_time ON krai_system.performance_metrics(execution_time_ms);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_recorded_at ON krai_system.performance_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_slow_queries ON krai_system.performance_metrics(execution_time_ms) WHERE execution_time_ms > 1000;

COMMENT ON TABLE krai_system.performance_metrics IS 'System performance monitoring and query execution metrics';
COMMENT ON COLUMN krai_system.performance_metrics.execution_time_ms IS 'Query or operation execution time in milliseconds';

-- =====================================
-- 3. AUDIT LOG TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_system.audit_log (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Audit Information
  table_name text NOT NULL,                     -- Affected table
  schema_name text NOT NULL,                    -- Affected schema
  operation text CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT')) NOT NULL,
  
  -- Data Changes
  old_data jsonb,                               -- Previous data (for UPDATE/DELETE)
  new_data jsonb,                               -- New data (for INSERT/UPDATE)
  
  -- User Information
  user_id uuid,                                 -- User who performed the operation
  user_role text,                               -- User role at time of operation
  session_id text,                              -- User session ID
  
  -- Request Information
  ip_address inet,                              -- Client IP address
  user_agent text,                              -- Client user agent
  request_id uuid,                              -- Request ID for tracing
  
  -- Additional Context
  reason text,                                  -- Reason for the operation
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional audit metadata
  
  -- Timestamps
  timestamp timestamp with time zone DEFAULT now()
);

-- Indexes for audit log
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON krai_system.audit_log(schema_name, table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON krai_system.audit_log(operation);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON krai_system.audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON krai_system.audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_session ON krai_system.audit_log(session_id);

COMMENT ON TABLE krai_system.audit_log IS 'Audit trail for all database operations and data changes';
COMMENT ON COLUMN krai_system.audit_log.operation IS 'Type of operation: INSERT, UPDATE, DELETE, SELECT';

-- =====================================
-- 4. SYSTEM HEALTH TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_system.system_health (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Health Check Information
  check_name text NOT NULL,                     -- "database_connection", "disk_space", "memory_usage"
  check_type text CHECK (check_type IN ('system', 'database', 'application', 'external')) NOT NULL,
  
  -- Health Status
  status text CHECK (status IN ('healthy', 'warning', 'critical', 'unknown')) NOT NULL,
  status_message text,                          -- Detailed status message
  
  -- Metrics
  response_time_ms integer,                     -- Response time for the check
  metric_value numeric,                         -- Numeric metric value
  metric_unit text,                             -- Unit of the metric
  
  -- Thresholds
  warning_threshold numeric,                    -- Warning threshold
  critical_threshold numeric,                   -- Critical threshold
  
  -- Additional Data
  check_data jsonb DEFAULT '{}'::jsonb,         -- Additional check-specific data
  
  -- Timestamps
  checked_at timestamp with time zone DEFAULT now()
);

-- Indexes for system health
CREATE INDEX IF NOT EXISTS idx_system_health_name ON krai_system.system_health(check_name);
CREATE INDEX IF NOT EXISTS idx_system_health_type ON krai_system.system_health(check_type);
CREATE INDEX IF NOT EXISTS idx_system_health_status ON krai_system.system_health(status);
CREATE INDEX IF NOT EXISTS idx_system_health_checked_at ON krai_system.system_health(checked_at);
CREATE INDEX IF NOT EXISTS idx_system_health_critical ON krai_system.system_health(checked_at) WHERE status = 'critical';

COMMENT ON TABLE krai_system.system_health IS 'System health monitoring and status checks';
COMMENT ON COLUMN krai_system.system_health.status IS 'Health status: healthy, warning, critical, unknown';

-- =====================================
-- 5. TRIGGERS FOR UPDATED_AT
-- =====================================

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_processing_queue_updated_at BEFORE UPDATE ON krai_system.processing_queue FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();

-- =====================================
-- 6. AUDIT TRIGGERS
-- =====================================

-- Function to create audit log entry
CREATE OR REPLACE FUNCTION krai_system.create_audit_entry()
RETURNS TRIGGER AS $$
BEGIN
  -- Insert audit log entry
  INSERT INTO krai_system.audit_log (
    table_name,
    schema_name,
    operation,
    old_data,
    new_data,
    user_id,
    user_role,
    session_id
  ) VALUES (
    TG_TABLE_NAME,
    TG_TABLE_SCHEMA,
    TG_OP,
    CASE WHEN TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN to_jsonb(OLD) ELSE NULL END,
    CASE WHEN TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN to_jsonb(NEW) ELSE NULL END,
    COALESCE(current_setting('app.current_user_id', true)::uuid, NULL),
    COALESCE(current_setting('app.current_user_role', true), 'unknown'),
    COALESCE(current_setting('app.session_id', true), NULL)
  );
  
  -- Return appropriate record
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- 7. SYSTEM FUNCTIONS
-- =====================================

-- Function: Get system health overview
CREATE OR REPLACE FUNCTION krai_system.get_system_health_overview()
RETURNS TABLE (
  check_name text,
  status text,
  response_time_ms integer,
  last_checked timestamptz
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    sh.check_name,
    sh.status,
    sh.response_time_ms,
    sh.checked_at
  FROM krai_system.system_health sh
  WHERE sh.checked_at = (
    SELECT MAX(checked_at) 
    FROM krai_system.system_health sh2 
    WHERE sh2.check_name = sh.check_name
  )
  ORDER BY 
    CASE sh.status 
      WHEN 'critical' THEN 1 
      WHEN 'warning' THEN 2 
      WHEN 'healthy' THEN 3 
      ELSE 4 
    END,
    sh.check_name;
END;
$$ LANGUAGE plpgsql;

-- Function: Get performance statistics
CREATE OR REPLACE FUNCTION krai_system.get_performance_stats(
  metric_name_filter text DEFAULT NULL,
  hours_back integer DEFAULT 24
)
RETURNS TABLE (
  metric_name text,
  avg_execution_time_ms numeric,
  max_execution_time_ms integer,
  min_execution_time_ms integer,
  total_executions bigint,
  slow_query_count bigint
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    pm.metric_name,
    AVG(pm.execution_time_ms)::numeric as avg_execution_time_ms,
    MAX(pm.execution_time_ms) as max_execution_time_ms,
    MIN(pm.execution_time_ms) as min_execution_time_ms,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE pm.execution_time_ms > 1000) as slow_query_count
  FROM krai_system.performance_metrics pm
  WHERE (metric_name_filter IS NULL OR pm.metric_name = metric_name_filter)
    AND pm.recorded_at >= now() - interval '1 hour' * hours_back
  GROUP BY pm.metric_name
  ORDER BY avg_execution_time_ms DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get processing queue status
CREATE OR REPLACE FUNCTION krai_system.get_queue_status()
RETURNS TABLE (
  task_type text,
  status text,
  count bigint,
  avg_processing_time_ms numeric,
  failed_count bigint
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    pq.task_type,
    pq.status,
    COUNT(*) as count,
    AVG(
      EXTRACT(EPOCH FROM (pq.processing_completed_at - pq.processing_started_at)) * 1000
    )::numeric as avg_processing_time_ms,
    COUNT(*) FILTER (WHERE pq.status = 'failed') as failed_count
  FROM krai_system.processing_queue pq
  WHERE pq.created_at >= now() - interval '24 hours'
  GROUP BY pq.task_type, pq.status
  ORDER BY pq.task_type, pq.status;
END;
$$ LANGUAGE plpgsql;

-- Function: Cleanup old records
CREATE OR REPLACE FUNCTION krai_system.cleanup_old_records()
RETURNS TABLE (
  table_name text,
  deleted_count bigint
) AS $$
DECLARE
  cleanup_date timestamptz := now() - interval '90 days';
BEGIN
  -- Cleanup old performance metrics
  DELETE FROM krai_system.performance_metrics 
  WHERE recorded_at < cleanup_date;
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN QUERY SELECT 'performance_metrics'::text, deleted_count;
  
  -- Cleanup old audit logs (keep only 30 days)
  DELETE FROM krai_system.audit_log 
  WHERE timestamp < now() - interval '30 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN QUERY SELECT 'audit_log'::text, deleted_count;
  
  -- Cleanup completed processing queue items (keep only 7 days)
  DELETE FROM krai_system.processing_queue 
  WHERE status = 'completed' 
    AND processing_completed_at < now() - interval '7 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN QUERY SELECT 'processing_queue'::text, deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON SCHEMA krai_system IS 'System operations, monitoring, audit, and background processing';
