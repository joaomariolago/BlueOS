#! /usr/bin/env python3
import argparse
import asyncio
import logging

from commonwealth.utils.logs import InterceptHandler, init_logger
from loguru import logger
from uvicorn import Config, Server

from api import app
from config import SERVICE_NAME

# Set up logging
logging.basicConfig(handlers=[InterceptHandler()], level=0)
init_logger(SERVICE_NAME)

# Global Kraken control instance
from kraken import kraken_instance

# Application entry point

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger(SERVICE_NAME).setLevel(logging.DEBUG)

    logger.info("Releasing the Kraken service.")

    loop = asyncio.new_event_loop()

    config = Config(app=app, loop=loop, host="0.0.0.0", port=9134, log_config=None)
    server = Server(config)

    loop.create_task(kraken_instance.run())
    loop.run_until_complete(server.serve())
    loop.run_until_complete(kraken_instance.stop())
