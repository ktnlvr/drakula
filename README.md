# drakula

## Installation

1. Clone the repository `git clone github.com/ktnlvr/drakula`
2. Enter the directory `cd drakula`
3. Install all the required packages using `pip install -r requirements.txt`
4. Install the module using `pip install -e .`
5. Run with `python -m drakula`

<h3 align="center">Flight Simulator Game</h3>
 <p align="center">
    <a href="" rel="noopener">
   <img width=325px height=220px 
    src="https://classroomclipart.com/image/content7/64941/thumb.gif" alt="Project logo"> 
    </a>
</p>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](    )
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](   )
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

# ✈️ Flight Simulator Game

## 📝 Table of Contents

- [Introduction](#introduction) 
- [Vision](#vision)
- [Functional Requirements](#functional)
- [Quality Requirements](#quality)
- [Built Using](#built)
- [Authors](#authors)
## Introduction <a name = "introduction"></a>

### 🎯 Purpose of this Document
The following document describes the development requirements for a flight simulator game. The main thought is the player after playing this game not only be satisfied with this true entertainment but also could learn some general sustainable development knowledge from it. <p>The main purpose of this document is to give a general overview of the game development process, and a reference guide for the developer, designer, project manager, tester, etc.</p>

### 👥 Target Audience
The game is designed for players who are above the 12+ age, especially suitable for students because it is strategic and educational. 

## Vision <a name = "vision"></a>

### 💡 General Idea of the Game
The game will combine with entertainment and sustainable development together to create a unique gaming experience with players. <p>The game focuses on simulating a real-world flight scenario for the player, the player could enjoy the game while learning about resource management, strategic decision-making and sustainable development during their playing.</p>

### 🎮 Purpose of the Game
- **Entertainment**:<p>The game players aim to escape or catch the computer-controlled opponent. we encourage players to engage in logical thinking and strategy development to win the game.</p>
- **Education**: <p>Players could learn some basic knowledge about sustainable development, and resource management, and make strategic decisions while they playing this fun game.</p>

### 🛫 Gameplay Flow
1. **Start Game**:<p>From the game starts, the player's airplane will displayed in a random airport on the map. The player uses initial money and resources to fly to the next airport.</p>
2. **Opponent-Computer**: <p>The computer acts as an opponent, it will control another airplane located in a different airport at the beginning of the game, and the computer will be invisible on the map during the game. But in some cases, like extra resources or spending some money, the player could know where the computer is for one time.</p>
3. **Strategic**: <p>Both the player and the computer just available to fly to the nearest airport on the map for the next step.</p><p>Flights could be within the same continent or between two continents, on the other hand between two continents the players will spend more money for it.</p><p>After every round of flights, the previous airport will not be available for each of them to land again.</p>
4. **Resource Management**: <p>The players need to carefully manage their limited budget and limited resources.  <p>There will be a chance for the player to collect props from each airport, but there are not always benefits, sometime, some props may even have traps or penalties, such as not being able to fly for one turn.</p><p>If the player's money or resources are not enough for the next flight they are done "GAME OVER".</p>
5. **Winning the Game**: <p>The player wins by successfully escaping: the computer's pursuit during time limits or after several rounds of flight the left airport is not available for them to meet each other.</p><p>The player wins by successfully catching:  The player successfully catches the computer.</p><p>The player wins a bonus: after the player wins, there is a hidden bonus for them. If the player doesn't reach the red line of the carbon footprint limits, there will be a bonus for them maybe extra money or a sustainability development trophy.</p>

## Functional Requirements <a name = "functional"></a>

### 🛩️ User Story 1
- **Role**: As a player
- **Action**: I can view all the nearest airports on the map and fly to the nearest airport from my current location for one flight.
- **Benefit**: I can move one step, and then use my genius strategy to consider both the distance and cost to make a perfect plan to escape or catch the computer.

### 🤖 User Story 2
- **Role**: As a player
- **Action**: I can collect one special prop at the airport I fly to.
- **Benefit**: This allows me to gain advantages such as flying twice or more in one turn, maybe I can get some extra money or special abilities that help me win the game. 

### 💰 User Story 3
- **Role**: As a player
- **Action**: I have the choice to plan my next airport where I fly to with a low carbon footprint
- **Benefit**: I can win a hidden bonus, maybe it's extra money or a sustainability development trophy.

### 🎁 User Story 4
- **Role**: As a player
- **Action**: I can use the props which I collect during my flight.
- **Benefit**: This allows me to influence the outcome of the game and increase my chances of winning by catching my opponents.

### 🎯 User Story 5
- **Role**: As a player
- **Action**: I can win the game by catching the opponent or successfully escaping during time limits or after several rounds of flight the left airport is not available for them to meet each other.
- **Benefit**: So that I can win the game.

### 🏆 User Story 6
- **Role**: As a player     
- **Action**: I can win a bonus at the end of the game, not just win the game.
- **Benefit**: After I win, there is a hidden bonus for me. there will be an extra money or a trophy.

### 🗺️ User Story 7
- **Role**: As a computer
- **Action**: The computer will have the same rules as the player.
- **Benefit**: To generate an equal and challenging gaming experience.

## Quality Requirements  <a name = "quality"></a>

### ⚡Performance Requirements

- **Intuitive Interface**: The user interface must display the player's information, current time remaining and the player's current money. To ensure that the player understands their options.
- **Cost and Distance Clarity**: The map must show the nearest airport, the cost to fly there and the carbon footprint to help players make quick decisions.
- **Stable Gameplay**: It must be ensured that not crash during gameplay. The game should have a progress save feature to save the player's current progress.
- **Error Handling**: The game should be able to show a prompt to warn the player if they try to make an action that does not follow the game’s rules (e.g., the selected airport is not the nearest airport).
- **Cross-Platform Compatibility**: The game should be compatible with Windows, macOS, and Linux, and should support playing with a keyboard.
## ⛏️ Built Using <a name = "built"></a>

- [Python](https://www.python.org/) - Programming
- [MariaDB](https://mariadb.org/) - Database
- [   ](    ) - Framework


## ✍️ Authors <a name = "authors"></a>

- 


