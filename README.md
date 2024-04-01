# Please you python3.12 with pip 24.0

# Install Packages (Recommended using the Virtul Env):

> pip install -r requirements.txt

# Run Server from CLI :

- Head into the TradingView directory and use python or python3
  and call `python mt5_socket_io.py`

# Run Server from VS Code :

- Open this project as you current working directory afterward open the `mt5_socket_io.py` file and hit `F5` to start the debugger.
  > Please make sure you have all the dependencies and python , pip correct versions !!

# Open Postman for testing

- Create a new socket io connection.
- Add the URL `http://localhost:8675`.
- Event Method name which you have to subscribe is `subscribeToMarketData`.
- And to listen the updated value you can add this event -> `touchline` to the listner.
