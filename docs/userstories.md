|  | User Story | Exception |
| ----- | ----- | ----- |
| 1 | As a user, I want to be able to login with an email | Exception: Email doesn’t exist Solution: Prompt user to create a username as well |
| 2 | As a user, I want to choose a creative username | Exception: User provides an inappropriate username Solution: Filter it out inappropriate words Exception: The user name already exists Solution: Prompt the user to choose a different user name (maybe suggest a different one?) |
| 3 | As a user, I want to bet on potential winners | Exception: User bids more money than they have Solution: give error remind user how much money they have |
| 4 | As a user, I want to be able to view the battles in real time | Exception: A user may view the result before another. Solution: Make sure all users receive results simultaneously. |
| 5 | As a user, I want to be able to change my username | Exception: The new username already exists Solution: Prompt the user for a new name. |
| 6 | As a user, I want to be able to have a means of earning money if I have none left. | Exception: User doesn’t receive money during start of next game.  Solution: Ensure all users are at the correct state before starting the game. |
| 7 | As a user I would like to be able to see a representation of the fights that are occurring. | Exception: AI image generator uses an inappropriate image Solution: use an API that has guardrails for the generation Exception: AI refuses to generate the image Solution: Provide filler text: “AI threw a tantrum and refused to generate this image” |
| 8 | As a modest user, I would like to be able to play the game without worrying another user will write hate speech | Exception: a user adds an inappropriate word Solution: have a database of blacklisted words to check when users upload names. If name is blacklisted, flag it and give the user an error, prompting a new input |
| 9 | As a user, I would like the ability to save money rather than betting on either contestant | Exception: User still loses money even without betting on a contestant.  Solution: Keep track of those who placed bets and only deduct their bets for them. |
| 10 | As a user, I want to be able to view past battles and results | Exception: No history of previous battles Exception: User sees the wrong history Solution: Ensure that users only see histories of games they’ve participated in. |
| 11 | As a front-end developer, I want to be able to plug in my own interface to this API. | Exception: No API documentation. Solution: Provide API documentation. |
| 12 | As a user, I want to be able to play this game with my friends and compete with them | Exception: User data gets scrambled with other users Solution: Give all users unique ids and only refer to ids in the backend |

