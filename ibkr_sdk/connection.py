import logging
import random
import os
import socket
import time
from ib_insync import IB

logger = logging.getLogger(__name__)

class IBConnection:
    def __init__(self, host='127.0.0.1', port=7496):
        self.ib = IB()
        self.host = host
        self.port = port
        self.client_id = self._generate_new_client_id()
        logger.info(f"Initialized IBConnection with Client ID {self.client_id}")

    def _generate_new_client_id(self):
        base_random_id = random.randint(100_000, 999_999_999) 
        pid_component = os.getpid() % 997 
        new_id = base_random_id + pid_component
        if new_id == 0: 
            new_id = 1
        return new_id % 999_999_999 if new_id > 999_999_999 else new_id

    def check_health(self):
        logger.info(f"Checking TWS/Gateway health at {self.host}:{self.port}...")
        try:
            with socket.create_connection((self.host, self.port), timeout=2):
                return True
        except (socket.error, socket.timeout) as e:
            logger.error(f"TWS/Gateway NOT REACHABLE on {self.host}:{self.port}. Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during TWS/Gateway health check: {e}")
            return False

    def connect(self):
        if not self.check_health():
            return False

        max_retries = 3 
        for attempt in range(max_retries):
            try:
                if not self.ib.isConnected():
                    logger.info(f"Attempting connection {attempt + 1}/{max_retries} with Client ID {self.client_id}...")
                    self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=10)
                    logger.info(f"Connected to IBKR! (Client ID {self.client_id})")
                return True
            except Exception as e:
                error_msg = str(e).lower()
                logger.warning(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if "client id already in use" in error_msg or "326" in error_msg:
                     logger.warning("Error 326 (Client ID already in use) detected. Cycling client ID...")
                     self._force_disconnect()
                     self.client_id = self._generate_new_client_id()
                elif "timeout" in error_msg or isinstance(e, TimeoutError):
                    logger.warning("Connection TimeoutError detected. Cycling client ID...")
                    self._force_disconnect()
                    self.client_id = self._generate_new_client_id()
                elif "peer closed connection" in error_msg or isinstance(e, (ConnectionResetError, ConnectionAbortedError)):
                    logger.warning("Peer closed connection detected. Cycling client ID.")
                    self._force_disconnect()
                    self.client_id = self._generate_new_client_id()
                
                if attempt < max_retries - 1:
                    wait_time = min(15, 2 ** attempt)
                    time.sleep(wait_time)
        return False

    def _force_disconnect(self):
        try:
            if self.ib.isConnected():
                self.ib.disconnect()
        except Exception as e:
            logger.debug(f"Disconnect error: {e}")

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()
            logger.info("Disconnected from IBKR.")
