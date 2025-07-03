#!/usr/bin/env python
"""
Optimized startup script for the FastAPI application.

This script configures uvicorn with optimized settings for development and testing:
- Disables debug mode by default for faster startup
- Uses simple logging for quicker startup
- Sets process count to make better use of system resources
"""

import os
import argparse
import uvicorn
import platform
import multiprocessing

def main():
    """Run the FastAPI application with optimized uvicorn settings."""
    # Create command-line argument parser
    parser = argparse.ArgumentParser(description="Run the FastAPI application with optimized settings")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (slower startup)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (slower startup)")
    parser.add_argument("--port", type=int, default=8090, help="Port to run the server on")
    parser.add_argument("--workers", type=int, default=0, 
                       help="Number of worker processes (0 for auto-detection)")
    args = parser.parse_args()
    
    # Determine number of workers based on CPU cores if not specified
    workers = args.workers
    if workers <= 0:
        workers = min(multiprocessing.cpu_count(), 4)  # Use up to 4 workers
    
    # Set log level based on debug flag
    log_level = "info" if not args.debug else "debug"
    
    # Configure uvicorn settings
    uvicorn_config = {
        "app": "app:app",
        "host": "0.0.0.0",
        "port": args.port,
        "log_level": log_level,
        "workers": 1 if args.reload else workers,  # Only 1 worker when reload is enabled
        "reload": args.reload,
        "loop": "uvloop" if not platform.system() == "Windows" else "asyncio",
        "http": "httptools",
        "ws": "websockets",
        "use_colors": True,
        "access_log": args.debug,  # Only log access in debug mode
    }
    
    print(f"Starting server with {uvicorn_config['workers']} worker(s)")
    print(f"Debug mode: {args.debug}")
    print(f"Auto-reload: {args.reload}")
    print(f"Visit: http://localhost:{args.port}")
    
    # Run the server
    uvicorn.run(**uvicorn_config)

if __name__ == "__main__":
    main()
