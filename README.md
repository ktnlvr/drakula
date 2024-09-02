# drakula

A third-person single-player strategic vampire hunting game
loosely inspired by [Fury Of Dracula (Third/Fourth Edition)](https://boardgamegeek.com/boardgame/181279/fury-of-dracula-thirdfourth-edition).

## Installation

1. Clone the repository `git clone github.com/ktnlvr/drakula`
2. Enter the directory `cd drakula`
3. Install all the required packages using `pip install -r requirements.txt`
4. Install the module using `pip install -e .`
5. Run with `python -m drakula`

## Introduction

This document is meant for internal reference and public display. It contains information about both the requirements
to the product, and a listing of specific design decisions taken in the making of the game.

* [Vision](#vision)
  * [Inspiration](#inspiration)
  * [Theme](#theme)
  * [Goals](#goals)
  * [User Skills](#user-skills)
  * [Game Mechanics](#game-mechanics)
  * [Progression and Challenge](#progression-and-challenge)
  * [Loss and Win Conditions](#loss-and-win-conditions)
  * [Graphic Design](#graphic-design)
* [Functional Requirements](#functional-requirements)
  * [Target Platforms](#target-platforms)
  * [Configuration](#configuration)
* [Quality Requirements](#quality-requirements)
  * [Age Category](#age-category)
  * [Legal](#legal)

## Vision

### Inspiration

The conceptual idea of travelling to hunt down Dracula is taken from the boardgame Fury Of Dracula. However, to avoid plagiarism, none of the programmers involved are informed about the specific rules, mechanics or other game components.

### Theme

Like the inspiration, the game centers on catching count Dracula, which has gone on a rampage around the world destroying cities and turning people into vampires!

### Goals

Providing entertainment is the main design goal. Akin to other session games, it should be easy to run, play a couple of games and then exit.


### User Skills

The game is focused on testing the player's ability to strategize, handle resources, deal with hidden information and type on a keyboard.

### Game Mechanics

Since the main topic is flight, the main mechanic is flying.
The player is tasked with capturing Dracula. This is done by trapping an airport and waiting for Dracula to land in the trap.

This would be easy lest the position of the count was known. During the entire game, the actual position is never communicated explicitly.

The game loop is separated into turns. On their turn, the player chooses a location to fly to and optionally installs a
trap in the current airport.

### Progression and Challenge

### Loss and Win Conditions

### Graphic Design

## Functional Requirements

A player can move from one airport to another using typing.

The player can save and restore their progress to pick up a game later.

### Target Platforms

It is imperative that the game can run on `Linux` and `Windows 10/11` devices.

The recommended system requirements are as follows:
* 64 or 32-bit processor and an operating system.
* Windows 10 (64 or 32-bit), Windows 11, Linux (6.1.X)
* AMD FX-4300 (4 * 3800) or equivalent / Intel Core i3-3240 (2 * 3400) or equivalent
* 2 GB RAM
* Radeon HD 7750 (1024 VRAM) or equivalent / GeForce GT640 (2048 VRAM) or equivalent
* 2 GB of storage space

While minor improvements to adapt the code for other platforms can be done, they are not a priority.

The target Python version is 3.9, with all the subsequent Python3.X versions following as per Python's major
version compatibility policy.

All the dependencies are listed in the [requirements.txt](./requirements.txt) and should run as per their own compatibility policy.

The product also requires an active and running and accessable instance of MariaDB. The credentials, as well as the
port and the host should be configured following the [Configuration](#configuration) section.

### Configuration

Configuration is done via environmental variables. They can be both fetched from and environment and a `.env` file.
For more examples see [example.env](./example.env).

## Quality Requirements

### Age Category

The game should be appropriate for players of age 12 and more. As a guideline, the [PEGI 12](https://pegi.info/what-do-the-labels-mean) rating is used.

> Video games that show violence of a slightly more graphic nature towards fantasy characters or non-realistic violence towards human-like characters would fall in this age category. Sexual innuendo or sexual posturing can be present, while any bad language in this category must be mild.

### Legal

All of the assets used in game must be distributed under a public domain license by a third party or produced in house
following the licensing requirements of the active license (see [LICENSE.txt](./LICENSE.txt)).