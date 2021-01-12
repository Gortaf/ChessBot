# ChessBot
A discord bot that allows you to play Chess with your friends directly on discord

![game-screenshot](https://i.ibb.co/FHHCtkX/chessbot-demo.png)

### Adding this bot to your server
To add ChessBot to your server, simply click this link: https://discord.com/oauth2/authorize?client_id=797085070422441984&scope=bot&permissions=268479568 and select the server you'd like ChessBot to join

### How to use ChessBot

#### Starting a game
To start a game with someone, use the following command:

>$duel @someone

Where @someone is a mention of the user you wish to play with.
Then the other user must answer with:

>$accept

or

>$refuse

to accept or refuse the challenge. If the challenge is accepted, a new channel will be created where the game will play. This channel is only accessible to the 2 players, but any user who wishes to spectate the game can react with the "eye" emoji to the message announcing the game to gain acces to the channel (tho spectators cannot type in the channel)

Note that when dueling someone, you can add certain keywords to the end of the duel command for different effects:

-Adding the keyword "public" at the end of the duel command will make the duel channel accessible by anyone without the need to spectate

-Adding the keyword "private" at the end of the duel command will make it impossible to spectate. Nobody besides the duelists, the bot and the admins will have acess to the channel.

The channel will be removed after the game ends

#### Playing the game

To move their pieces on their turn, the players must use the $move, or $m command.

>$move [piece's_id] [new coordinates]

The piece's ID is written on the top left of the piece. So if I wanted to move my 3rd pawn (P3) to the c3 cell, I'd use:

>$move p3 c3

(note that the command isn't caps sensitive, I could have typed P3 or C3)

ChessBot won't allow illegal moves. However, it will not stop you from putting your king in harm's way (isn't it more fun this way? :D)

The game ends when a player loses their king, or when no messages have been sent for 10 minutes.


### Upcomming features

- "En passant" optional rule
- Maximum cumulative time optional rule
- Custom rulesets maybe?
