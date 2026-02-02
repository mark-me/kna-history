# Adding Health Check Endpoint to Flask App

The new Docker setup includes health checks. You need to add a `/health` endpoint to your Flask application.

## Quick Implementation

Add this to your `src/app.py`:

```python
@app.route("/health")
def health():
    """Health check endpoint for Docker"""
    try:
        # Optional: Check database connection
        # db_reader.check_connection()  # Implement if needed
        
        return {
            "status": "healthy",
            "version": os.getenv("APP_VERSION", "unknown")
        }, 200
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503
```

## Complete Example with Database Check

If you want to verify database connectivity:

```python
@app.route("/health")
def health():
    """Health check endpoint for Docker"""
    health_status = {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "unknown"),
        "checks": {}
    }
    status_code = 200
    
    # Check database connection
    try:
        # Example: Try a simple query
        # Replace with your actual database check
        db_reader.db.execute("SELECT 1").fetchone()
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = f"error: {str(e)}"
        status_code = 503
    
    # Check resources directory
    try:
        resources_dir = "/data/resources"
        if os.path.exists(resources_dir) and os.access(resources_dir, os.R_OK):
            health_status["checks"]["resources"] = "ok"
        else:
            health_status["status"] = "degraded"
            health_status["checks"]["resources"] = "not accessible"
            status_code = 503
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["resources"] = f"error: {str(e)}"
        status_code = 503
    
    return health_status, status_code
```

## Testing

After adding the endpoint:

```bash
# Test locally
curl http://localhost:5000/health

# Test in Docker
docker compose exec kna-historie curl http://localhost:5000/health

# Check Docker health status
docker compose ps kna-historie
```

## Why Health Checks?

1. **Automatic Recovery**: Docker can restart unhealthy containers
2. **Orchestration**: Ensures services start in correct order
3. **Load Balancing**: Health checks inform load balancers
4. **Monitoring**: External tools can monitor application health

## Alternative: Minimal Implementation

If you prefer minimal setup:

```python
@app.route("/health")
def health():
    """Minimal health check"""
    return "OK", 200
```

This is sufficient for basic Docker health checking, but doesn't verify database connectivity.
