import socket

"""
Server Message Examples
-----------------------
    Chat message:
    "b':wanshitongbot!wanshitongbot@wanshitongbot.tmi.twitch.tv PRIVMSG #wanshitongbot :my message here'"

    "b':<username>!<username>@<username>.tmi.twitch.tv PRIVMSG #<channel_name> :<chat_message>"

Conventions
-----------
    client_message   Message to send to Twitch IRC server
    server_message   Message received from Twitch IRC server

"""


class TwitchChatBot:
    """
    Instantiates a new Twitch chat bot.


    Parameters
    ----------
        username    Twitch username
        password    OAuth password, following the convention
                    "oauth: <OAUTH_TOKEN>"
        channels    List of Twitch channels to connect to


    Attributes
    ----------
        IRC_CLIENT  IRC client URI
        PORT        Port number for IRC client
        socket      Socket


    References
    ----------
    [Twitch IRC Guide](https://dev.twitch.tv/docs/irc/guide)
    """

    # Class constants
    _IRC_CLIENT = "irc.twitch.tv"
    _IRC_PORT = 6667

    # Class configurations
    _socket = socket.socket()
    socket_bytes = 1024

    # Instance-specific attributes
    username = ""
    __password = ""
    channels = []

    def __init__(self, username, password, channels):
        self.username = username
        self.__password = password
        self.channels = channels

    @property
    def IRC_CLIENT(self):
        """
        Defines the getter method for IRC_CLIENT.
        """
        return self._IRC_CLIENT

    @property
    def IRC_PORT(self):
        """
        Defines the getter method for IRC_PORT.
        """
        return self._IRC_PORT

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def connect(self):
        """
        Connects to Twitch's IRC client.

        References
        ----------
        https://dev.twitch.tv/docs/irc/guide#connecting-to-twitch-irc
        """

        # Connects to Twitch's IRC client.
        self._socket.connect((self.IRC_CLIENT, self.IRC_PORT))

        # Authenticates chat bot.
        self.authenticate()

        # Connects to all of the specified Twitch channels.
        self.join_channels()

        # Listens to the server's response.
        while True:
            line = self._socket.recv(self.socket_bytes).decode()

            # Stops listening when the following substring is found.
            if "End of /NAMES list" in line:
                break

        # Listens for responses from the server.
        self.listen()

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def authenticate(self):
        """
        Sends messages containing the bot's username and OAuth password to
        Twitch's IRC client.
        """
        self._socket.send(bytes("PASS " + self.__password + "\r\n", "utf-8"))
        self._socket.send(bytes("NICK " + self.username + "\r\n", "utf-8"))

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def join_channels(self):
        """
        Connects to all of the specified Twitch channels.
        """
        for channel in self.channels:
            client_message = f"JOIN #{channel}\r\n"
            self._socket.send(bytes(client_message, "utf-8"))

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def listen(self):
        """
        Listens for responses from the server.

        Server Message Keywords
        -----------------------
            NICK <username>                    Twitch username
            PASS oauth:<password>               Twitch OAuth password
            JOIN #<channel_name>                Joins a Twitch channel
            PART #<channel_name>                Leaves a Twitch channel
            PRIVMSG #<channel_name> :<message>  Sends a chat message

            PING :tmi.twitch.tv                 Ping from the server
            PONG :tmi.twitch.tv                 Client response to ping from
                                                the server

            https://dev.twitch.tv/docs/irc/guide#generic-irc-commands
        """
        while True:
            for line in self._socket.recv(self.socket_bytes).decode().split("\r\n"):

                # Sends a PONG message.
                if "PING" in line:
                    self.send_client_message("PONG :tmi.twitch.tv")

                # Responds to chat message.
                if "PRIVMSG" in line:
                    server_message_details = self.parse_private_message(line)
                    self.chat(server_message_details)

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def send_client_message(self, client_message):
        """
        Sends a message to the server.

        Parameters
        ----------
            client_message (string):
            Message to send to the server
        """
        self._socket.send(bytes(client_message, "utf-8"))

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def chat(self, server_message_details):
        """
        Sends a chat message.

        Parameters
        ----------
            server_message_details (dict):
            {
                "channel": <channel_name>,
                "username": <twitch_username>,
                "message": <chat_message>
            }
        """
        keys = ("channel", "username", "message")
        channel, username, message = [server_message_details[k] for k in keys]

        if self.username in message.lower():
            client_message = f"PRIVMSG #{channel} :@{username}, welcome to my stream.\r\n"
            self.send_client_message(client_message)

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def parse_private_message(self, server_message):
        """
        Parses the private

        Example
        -------
            ":wanshitongbot!wanshitongbot@wanshitongbot.tmi.twitch.tv
            PRIVMSG #wanshitongbot :my message here"

            ":<username>!<username>@<username>.tmi.twitch.tv PRIVMSG
            # <channel_name> :<chat_message>"

        Parameters
        ----------
            server_message (string):
            Message from the server

        Returns
        -------
            {
                "channel": <channel_name>,
                "username": <twitch_username>,
                "message": <chat_message>
            }

        """
        # Creates a dictionary containing parse information about the private
        # message.

        _, server_message_details, message = server_message.split(":")
        username, details = server_message_details.split("!")
        _, channel = details.split("#")

        return {
            "channel": channel,
            "username": username,
            "message": message
        }
