### We're building a fighting simulator with a backend to support it.
We'll be representing the leaderboard via a persistent table that will be constantly updated as battles progress. Entrants will be randomly generated and added to the participants or fighter table as needed. A backend API will pull participants and simulate a fight between the two. The loser dies, the winner gets ELO and rises in the leaderboards. 

We plan to add more functionality like a seperate weapons table from which participants can acquire weapons.

### Generating Entrants
Entrants will be generated when a certain threshold is met (for example, if there are less than 10 entrants in the pool). Entrant generation will be done randomly through an API call to OpenAI's GPT-4o-mini. Each entrant will have stats generated according to their characteristics.
Entrant stat fields:
- Base health
- Base damage
- Strength multiplier
- Critical hit chance
- Mercy chance
- and more
  
### Battles
Battles will be turn based and dependent on each characters stats. A sequence of probabilistic events will determine the winner. The sequence of events as well as the end-result are passed to GPT-4o-mini to generate a random story for how the fight played out. 

### Potential added functionality
- Acquiring weapons to boost stats. Winners collect losers weapons.
- Potentially a basic front-end UI to display the leaderboard and battles.
- Gang battles. If a winner spares a loser, there is a chance for the two to team up. A graph database could be used to manage fighter relationships. Gangs on opposite ends of the graph might seek each other out which could create some interesting scenerios.
- Sponsors. Users can sponsor fighters in real-time and increase their chances of winning.

#### MVP:
- add entrants
- simulate fighting
- maintain a leaderboard

### Contributers
- David Voronov
- Aiden King
- Ian Ang
- Swayam Chidrawar
