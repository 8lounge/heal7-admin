#!/usr/bin/env python3
"""
HEAL7 Admin Backend Main Entry Point
Port: 8001 (admin.heal7.com)
"""

import sys
import os
import uvicorn
from admin_api_updated import app

if __name__ == "__main__":
    uvicorn.run(
        "admin_api_updated:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        workers=1
    )