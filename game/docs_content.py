from game import constants


PLAYING_SECTIONS = [
    {
        "key": "INTRO",
        "title": "Introduction",
        "content": [
            "This document details the actions that are available to you as you explore and progress through the wonderful worlds created in this app.",
            "You'll find as you play around with the adventures that there may be more than one way to refer to things when typing commands - e.g. locations, friends, items, enemies. This is because it's possible for authors to name a thing and then provide a list of alternative references to that thing. For example if an item was named 'The Sword of Destiny' they might also provide shorthand references like 'Sword'.",
        ],
    },
    {
        "key": constants.MOVE_COMMAND,
        "title": "Movement",
        "commands": constants.COMMAND_OPTIONS[constants.MOVE_COMMAND],
        "content": [
            "This is how you move between the locations of the world. There are two main ways movement works. You can either write the name of the room you're moving towards or you can write a direction you're moving in. This is dependant on the way the author of the adventure has set up the world so use the descriptions of the rooms you find yourself in to determine which methods you can use."
            "When in a room that only has one exit you can also use the 'Leave' or 'Exit' command with no room name and it will move you to the next room."
        ],
        "examples": ["Go East", "Move to the Forest", "Leave"],
    },
    {
        "key": constants.TAKE_COMMAND,
        "title": "Picking up Items",
        "commands": constants.COMMAND_OPTIONS[constants.TAKE_COMMAND],
        "content": [
            "This set of commands allows to to take the items that you might find in the world. Use a command word alongside the name of the item you want to pick up and you will add the item to your inventory."
        ],
        "examples": ["Take sword"],
    },
    {
        "key": constants.OPEN_COMMAND,
        "title": "Opening Containers",
        "commands": constants.COMMAND_OPTIONS[constants.OPEN_COMMAND],
        "content": [
            "Some items within the world will be containers. These can be picked up and then opened with this command. The contents of the container will then be added to your inventory."
        ],
        "examples": ["Open box"],
    },
    {
        "key": constants.USE_COMMAND,
        "title": "Using Items",
        "commands": constants.COMMAND_OPTIONS[constants.USE_COMMAND],
        "content": [
            "Currently the only items that have a 'use' function are keys. If you have a key in your inventory and use this command in the room that the key unlocks a door; the door will be unlocked."
        ],
        "examples": ["Use key"],
    },
    {
        "key": constants.INSPECT_COMMAND,
        "title": "Inspecting Items",
        "commands": constants.COMMAND_OPTIONS[constants.INSPECT_COMMAND],
        "content": [
            "Items you hold or are in the current room can be described. This might reveal extra information that is not contained within the description of the room with the item in it."
        ],
        "examples": ["Inspect the sword", "Describe the map"],
    },
    {
        "key": constants.FIGHT_COMMAND,
        "title": "Fighting Enemies",
        "commands": constants.COMMAND_OPTIONS[constants.FIGHT_COMMAND],
        "content": [
            "Enemies can be fought in the game. Usually when entering a room enemies will automatically attack you in which case you don't need to use this command. However it is possible for the creator of the game to allow you to decide whether or not you want to engage them in combat. If this is the case then the room's description will indicate there is an enemy that you could fight. Using the name of the enemy along with the fight command will engage them in combat."
        ],
        "examples": ["Fight thug", "attack bandit"],
    },
    {
        "key": constants.TALK_COMMAND,
        "title": "Talking to Friends",
        "commands": constants.COMMAND_OPTIONS[constants.TALK_COMMAND],
        "content": [
            "When you find a friend in a location you're in, you can usually engage them in conversation.",
            "There are two types of conversations that can occur. Sometimes a friend will only have one thing they can say, in which case they will say the thing and you will be able to enter another command immediately. On the other hand, they may allow you to respond to their speech in which case dialogue options will appear and you can interact with them until you wish to leave - by selecting 'Goodbye'.",
            "In some cases conversing with a friend might result in you gaining some items, when you exit conversation with such friends, you'll find those items in your inventory.",
        ],
        "examples": ["Talk to the queen"],
    },
    {
        "key": constants.GIVE_COMMAND,
        "title": "Giving Items to Friends",
        "commands": constants.COMMAND_OPTIONS[constants.GIVE_COMMAND],
        "content": [
            "Some friends will accept items you hold - this will usually be indicated by dialogue lines you can access by talking to them. If you use this command along with the name of the item in the location the friend is in, it will give them the item.",
            "You'll often find that giving items to friends provides you with different dialogue if you talk to them again.",
        ],
        "examples": ["Give gold"],
    },
]
