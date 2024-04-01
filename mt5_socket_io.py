# Main Python Import
import asyncio
import json

# MetaTrader5 Import
import MetaTrader5 as mt

# Import SocketIO
import socketio

# Import Uvicorn 
import uvicorn

# Local Backend Imports
from config import settings
from custom_logging import logger


sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

# Dictionary to store symbol rooms
symbol_rooms = {}

async def initialize_mt5() -> None:
    try:
        mt.initialize()
        logger.info("Successfully Initialised the MetaTrader5")
    except Exception as e:
        logger.error("Could not Initialise the MetaTrader5")


async def login_mt5() -> None:
    try:
        mt.login(settings.login, settings.password, settings.server)
        logger.info("Successful Login into the MetaTrader5 Account")
    except Exception as e:
        logger.error("Could not Login into the MetaTrader5 account")
        

async def fetch_symbol_data(symbol) -> dict | None:
    try:
        symbol_data = mt.symbol_info(symbol)
        if symbol_data is not None:
            response = {"symbol": symbol,
                        "spread": symbol_data.spread,
                        "Bid": symbol_data.bid,
                        "High": symbol_data.bidhigh,
                        "Low": symbol_data.bidlow,
                        "Ask": symbol_data.ask,
                        "LTP": symbol_data.last,
                        "lotsize" : symbol_data.trade_contract_size,
                        "TotalVolume": symbol_data.session_volume,
                        "Open": symbol_data.session_open,
                        "Previous_Close": symbol_data.session_close,
                        "price_change" : symbol_data.price_change
                        }
            return response
    except Exception as e:
        logger.error(f"Exception while fetching symbol data - {str(e)}")

@sio.event
async def connect(sid, environ):
    try:
        await initialize_mt5()
        await login_mt5()
        logger.info(f'Client connected: {sid}')
    except Exception as e:
        logger.error(f"Could not connect the User to SocketIO - {str(e)}")

@sio.event
async def subscribeToMarketData(sid, data):
    try:
        symbols = data
        symbol_rooms[sid] = set(symbols)

        previous_data = {}  # Dictionary to store previous symbol data

        while sid in symbol_rooms and symbol_rooms[sid]:
            for symbol in symbol_rooms[sid]:
                symbol_info = await fetch_symbol_data(symbol)
                if symbol_info:
                    if symbol not in previous_data or symbol_info != previous_data[symbol]:
                        await sio.emit('touchline', symbol_info, room=sid)
                        logger.info(f"Current Symbol data - {symbol_info["symbol"]}")
                        previous_data[symbol] = symbol_info  
            await asyncio.sleep(1/3)
    except Exception as e:
        logger.error(f"Could not subscribe to the Event - {str(e)}")

@sio.event
async def disconnect(sid):
    try:
        logger.info(f'Client disconnected: {sid}')
        if sid in symbol_rooms:
            del symbol_rooms[sid]
    except Exception as e:
        logger.error(f"Could not disconnect the User - {str(e)}")


if __name__ == "__main__":
    try:
        uvicorn.run(app="mt5_socket_io:app",host="localhost",port=8675,reload=True)
        logger.info("Spin up the Uvicorn server!!!")
    except Exception as e:
        logger.error(f"Could not spin up the Uvicorn Server  - {str(e)}")