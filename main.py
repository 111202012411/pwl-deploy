#!/usr/bin/env python

import uvicorn

if str(__name__).upper() in ("__MAIN__",):

  uvicorn.run("server.api:app", host="0.0.0.0", port=5656, server_header=False, date_header=False, reload=True)

  
