import socket

"""
Server Messages
---------------
    Chat message:
    "b':wanshitongbot!wanshitongbot@wanshitongbot.tmi.twitch.tv PRIVMSG #wanshitongbot :my message here'"

    "b':<username>!<username>@<username>.tmi.twitch.tv PRIVMSG #<channel_name> :<chat_message>"

    Ping message:
    "b'PING :tmi.twitch.tv"

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
    https://dev.twitch.tv/docs/irc/guide
    """

    _IRC_CLIENT = "irc.twitch.tv"
    _IRC_PORT = 6667

    _socket = socket.socket()
    socket_bytes = 1024

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

        Reference
        ---------
        https://stackoverflow.com/a/15812738/11715889
        """
        return self._IRC_CLIENT

    @property
    def IRC_PORT(self):
        """
        Defines the getter method for IRC_PORT.

        Reference
        ---------
        https://stackoverflow.com/a/15812738/11715889
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
            client_message = "JOIN #" + channel + "\r\n"
            self._socket.send(bytes(client_message, "utf-8"))

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def listen(self):
        """
        Listens for responses from the server.
        """
        while True:
            for line in str(self._socket.recv(1024)).split('\\r\\n'):
                # for line in server_message.split('\\r\\n'):
                parts = line.split(':')

                print(parts)

                if len(parts) < 3:
                    continue

                if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                    message = parts[2][:len(parts[2])]

                usernamesplit = parts[1].split("!")
                username = usernamesplit[0]

                # print(username + ": " + message)
                if message == "Hey":
                    self.chat(self.username,
                              "Welcome to my stream, " + username)

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    def chat(self, channel, chat_message):
        """
        Sends a chat_message.
        """
        client_message = "PRIVMSG #" + channel + " :" + chat_message + "\r\n"
        self._socket.send(bytes(client_message, "utf-8"))
