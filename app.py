"""
Dreambase — Haunt Your Own Records.
Flask app for browsing conversations, ideas, and tags.
Card grid with search, filters, expand to full conversation view.
Showcase pages for curated dream deep-dives.
"""

import json
import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from schema import DB_PATH

# Showcase definitions — curated dream pages with tabbed sections.
# conversation_ids: de-duplicated primaries (chatgpt source preferred, then claude).
# Content fields (narrative, quotes, timeline) populated by ChatGPT batch workflow.
SHOWCASES = {
    "bubble-bog-witch": {
        "slug": "bubble-bog-witch",
        "title": "Bubble Bog Witch",
        "hook": "What if transmutation was a platformer mechanic and the swamp was alive?",
        "category": "game",
        "maturity": "sketch",
        "conversation_ids": [40, 239, 3580, 2565],
        "tags": ["game_idea", "alchemy", "platformer"],
        "pedagogy": "Environmental storytelling through movement mechanics. The player learns about the Bog Witch's world by how bubbles behave in different zones — not through cutscenes or text dumps.",
        "difficulty_easy": "Bubbles as pure traversal mechanic (bounce to reach platforms)",
        "difficulty_medium": "Bubbles as resource (limited supply, strategic popping)",
        "difficulty_hard": "Bubbles as ecosystem (witch's magic affects behavior, player reads environment)",
        "narrative": "<h3>The Thread</h3><p>A platformer where you play a tiny witch navigating a living swamp, using alchemical bubbles as your primary mechanic. The Bubble Bog Witch started as a visual concept — a pixelated witch shrunken to mouse-size, leaping between bioluminescent bubbles in a tattered cloak — and grew across four conversations into a full game design with transmutation mechanics, zone-based environmental storytelling, and a swamp that responds to your presence.</p><h3>What Emerged</h3><p>The core insight was that bubbles could serve triple duty: as traversal (bounce between platforms), as resource (limited supply, strategic popping), and as ecosystem indicator (the witch’s magic changes how bubbles behave in different swamp zones). Environmental storytelling through movement mechanics means the player learns about the Bog Witch’s world by how the physics change — not through cutscenes or text dumps. A working Pygame prototype was built with basic bubble physics and transmutation interactions.</p><h3>Why It Matters</h3><p>This is the most visually distinctive game concept in the database — a fusion of alchemy, ecology, and platformer design that treats the environment itself as the puzzle. The conversations span concept art prompts, feature design documents, and prototype code.</p>",
        "timeline_entries": [{"date": "2024-11-26", "title": "Bubble Witch Feature Prompts", "description": "User is working on a game titled \"Bubble Witch,\" a puzzle platformer where the player controls a witch moving around a swamp-themed environment and a bubble castle.", "conversation_id": 239}, {"date": "2024-11-26", "title": "Alchemy Bubble Tower Platformer Game", "description": "import React, { useState, useEffect, useRef } from 'react'; import { Chevr...", "conversation_id": 2565}, {"date": "2025-01-03", "title": "Bubble Witch Platformer Ideas", "description": "`prompt A pixelated 8-bit style platformer game concept scene of a \"Bubble Witch,\" a cute witch character shrunken to the size of a mouse.", "conversation_id": 40}, {"date": "2025-02-05", "title": "Bubble Bog Witch Image", "description": "The witch protagonist, a small figure in a tattered cloak and pointy hat, leaps gracefully between floating bubbles, which shimmer with bioluminescent energy.", "conversation_id": 3580}],
        "quotes": [],
        "images": [],
    },
    "dungeon-autobattler": {
        "slug": "dungeon-autobattler",
        "title": "Dungeon Autobattler",
        "hook": "Draft your army, set the strategy, then watch the chaos unfold. The skill is in the preparation.",
        "category": "game",
        "maturity": "design",
        "conversation_ids": [4, 10, 37, 7, 2580, 2578, 2591, 2564, 2582, 2668, 2577, 3594],
        "tags": ["game_idea", "autobattler", "roguelike", "procedural"],
        "pedagogy": "Decision-making under uncertainty with incomplete information. The core loop: build a team, commit it, watch outcomes you can't control. Learning happens in the gap between expectation and result.",
        "difficulty_easy": "Rock-paper-scissors unit types — learn to read enemy composition",
        "difficulty_medium": "Synergy bonuses between unit types — balance counter-picking vs synergy",
        "difficulty_hard": "Procedural dungeon rooms with unknown encounters — build for adaptability",
        "narrative": "<h3>The Thread</h3><p>An autobattler where the skill is entirely in preparation: draft your army, set formation and strategy, then watch the chaos unfold. The concept evolved from an initial Snake-meets-autobattler mashup into a proper dungeon-crawling roguelike with procedural room generation, card drafting, and unit synergy systems. Twelve conversations trace the design from concept to prototype.</p><h3>What Emerged</h3><p>The design settled on a core loop: build a team from drafted cards, commit it to a dungeon run with unknown encounters, watch outcomes you cannot control, then adapt. Rock-paper-scissors unit types provide readable counterplay at easy difficulty; synergy bonuses between unit types add depth at medium; procedural dungeon rooms with unknown encounters demand adaptability at hard. A React-based procedural dungeon generator was prototyped, with terrain types, room connectivity algorithms, and encounter placement.</p><h3>Why It Matters</h3><p>Decision-making under uncertainty with incomplete information — the autobattler is a teaching tool for probabilistic thinking disguised as a fantasy game. The gap between expectation and result is where learning happens. Desktop Dungeons, Slay the Spire, and Teamfight Tactics were studied as genre precedents.</p>",
        "timeline_entries": [{"date": "2024-12-30", "title": "Medieval Dungeon Crawler Roguelike", "description": "It's substantial enough to warrant separation from the conversation.", "conversation_id": 2564}, {"date": "2024-12-30", "title": "Simplified Roguelike Dungeon Crawler", "description": "It needs to be separate from the conversation to be properly used and modified.", "conversation_id": 2582}, {"date": "2024-12-30", "title": "Procedural Dungeon Generator for Roguelike Game", "description": "This is a good case for an artifact since it's a substantial modification to the existing React component.", "conversation_id": 2580}, {"date": "2025-01-03", "title": "Desktop Dungeons and Similar Games", "description": "Desktop Dungeons is a single-player roguelike puzzle video game developed by QCF Design, a South African indie game development studio.", "conversation_id": 37}, {"date": "2025-01-07", "title": "Snake Game Autobattler Design", "description": "**Features to Include:** 1.", "conversation_id": 10}, {"date": "2025-01-07", "title": "Library of Babel Lich Dungeon", "description": "{ \"prompt\": \"A surreal and atmospheric depiction of the Library of Babel as described by Jorge Luis Borges combined with an RPG dungeon lair of a mad lich.", "conversation_id": 7}, {"date": "2025-01-07", "title": "Snake Autobattler Concept", "description": "{ \"size\": \"1024x1024\", \"prompt\": \"A wacky game concept of an autobattler inspired by Snake.", "conversation_id": 4}, {"date": "2025-01-11", "title": "Snake Autobattler with Procedural Generation", "description": "It's substantial enough to warrant separation from the conversation.", "conversation_id": 2578}, {"date": "2025-01-13", "title": "Escape Goat Dungeon Game Mockup", "description": "This is a good candidate for a React artifact as it's a complete interactive mockup that demonstrates game mechanics and layout.", "conversation_id": 2577}, {"date": "2025-01-18", "title": "Building a Snake Autobattler Game", "description": "Let's break this down into manageable pieces, starting with the core game board and multi-frame display system.", "conversation_id": 2591}, {"date": "2025-04-02", "title": "Capture the Cone: Autobattler with Middle School Misfits", "description": "# 30 Features for \"Capture the Cone\" Autobattler I'll design features for your 2-player hot seat autobattler game where players build teams of middle school students to capture con...", "conversation_id": 2668}, {"date": "2025-12-14", "title": "Dungeon crawling auto battler", "description": "Absolutely, that sounds like a pretty cool and very customizable idea! So, let’s break it down a bit and think through how you can structure this dungeon-crawling auto-battler with...", "conversation_id": 3594}],
        "quotes": [{"text": "A challenging gothic roguelike turn-based RPG about the psychological stresses of adventuring. Players must manage a team of flawed heroes as they descend into various dungeons, facing not only monstrous foes but also stress, disease, and the ever-encroaching darkness. citeturn", "role": "assistant", "conversation_title": "Desktop Dungeons and Similar Games", "conversation_id": 37}, {"text": "1. A detailed breakdown of the essential features required to support this game (e.g., card drafting system, snake AI behaviors, procedural terrain generation, combat resolution, feedback and progression systems).", "role": "assistant", "conversation_title": "Snake Game Autobattler Design", "conversation_id": 10}],
        "images": [],
    },
    "alchemy-board-game": {
        "slug": "alchemy-board-game",
        "title": "Alchemy Board Game",
        "hook": "The Great Work as engine-building: transmutation chains, hidden knowledge, and the joy of discovery.",
        "category": "game",
        "maturity": "prototype",
        "conversation_ids": [567, 851, 2700, 347, 500, 531, 533, 511, 513, 2523, 2515],
        "tags": ["game_idea", "alchemy", "board_game", "educational"],
        "pedagogy": "Transformation systems — how inputs become outputs through rule-governed processes. The alchemical Great Work is literally an optimization problem disguised as mysticism.",
        "difficulty_easy": "Linear transmutation (lead to iron to silver to gold) — one path, learn the sequence",
        "difficulty_medium": "Branching paths (sulfur + mercury = cinnabar OR philosopher's stone) — trade-offs emerge",
        "difficulty_hard": "Competing economies (multiplayer: your waste products are my inputs) — read opponents",
        "narrative": "<h3>The Thread</h3><p>The Great Work as an engine-building board game: transmutation chains, hidden knowledge, and the joy of discovery. This is the most developed game concept in the database — 241 pages of design work across 11 conversations, spanning game learning theory, tutorial design, puzzle mechanics, and Tabletop Simulator prototyping.</p><h3>What Emerged</h3><p>The design draws directly from alchemical processes: players build transmutation chains (lead → iron → silver → gold at easy difficulty), manage branching paths where the same inputs can produce different outputs (sulfur + mercury = cinnabar OR philosopher’s stone), and at advanced levels compete in multiplayer economies where one player’s waste products are another’s inputs. A 137-page tutorial design document was produced applying persuasion theory and game-based learning research to the onboarding experience.</p><h3>Why It Matters</h3><p>This is where the scholarly alchemy research directly transmutes into game mechanics. The alchemical Great Work is literally an optimization problem disguised as mysticism — and the board game makes that visible. It demonstrates the Dreambase’s core thesis: that deep reading produces playable ideas.</p>",
        "timeline_entries": [{"date": "2024-09-13", "title": "Alchemy Lab Board Game", "description": "That sounds like a fantastic concept for an alchemy-themed board game! Here’s a detailed design outline for your game: ### **Game Overview:** In this game, players manage their own...", "conversation_id": 851}, {"date": "2024-10-12", "title": "Games Learning Alchemy Board Game ", "description": "**Chapter 1: Persuasion on-Line and Communicability** (p.", "conversation_id": 567}, {"date": "2024-10-22", "title": "Alchemy Lab Puzzle Game Prototype", "description": "This is a good candidate for an artifact as it's a complete, reusable piece of code that creates an interactive game prototype.", "conversation_id": 2523}, {"date": "2024-10-23", "title": "Alchemy Puzzle Game Design", "description": "User is planning a box moving puzzle and Bomberman-inspired game with an alchemy theme, where players collect items with planetary sigils printed on them using Unicode or emojis.", "conversation_id": 533}, {"date": "2024-10-23", "title": "Alchemy Puzzle Game Code", "description": "User is planning a box pushing alchemy-themed puzzle game using React, Three.", "conversation_id": 531}, {"date": "2024-10-25", "title": "Alchemy Pinball Game Concept", "description": "User wants to create an alchemy-themed pinball-meets-Brickles game where the ball bounces around an alchemy lab, interacting with objects like an alembic.", "conversation_id": 513}, {"date": "2024-10-25", "title": "Alchemy Pinball Game Mechanics", "description": "- Implement realistic physics for the ball's movement and collisions using a physics engine.", "conversation_id": 511}, {"date": "2024-10-25", "title": "Alchemy Game Tutorial Design", "description": "Each message is designed to be clear, concise, and engaging, enhancing the player's understanding and immersion.", "conversation_id": 500}, {"date": "2024-10-26", "title": "Alchemy Puzzle Game with Planetary Obstacles", "description": "Let me create a comprehensive update that incorporates the planetary blocks and their unique behaviors.", "conversation_id": 2515}, {"date": "2024-11-15", "title": "Alchemy Game Mechanics", "description": "Creating an educational game that immerses players in the realities of archaeological study and alchemical traditions is a fascinating endeavor.", "conversation_id": 347}, {"date": "2025-10-09", "title": "Alchemy board game design", "description": "# Detailed Design Applications for Your Alchemy Board Game Based on the thematic integration theories from *Thematic Integration in Board Game Design*, here's an in-depth explorati...", "conversation_id": 2700}],
        "quotes": [{"text": "The chapter presents two example games, \"Turtle’s Rare Ingredient Hunt\" and a sorting tutor, developed by university students, demonstrating the flexibility of Greenmind for educational purposes.", "role": "assistant", "conversation_title": "Games Learning Alchemy Board Game ", "conversation_id": 567}, {"text": "These messages aim to guide players through the game's mechanics while maintaining immersion in the alchemy theme. By using clear instructions and thematic language, players can learn how to use their abilities effectively and feel encouraged to explore and experiment within the ", "role": "assistant", "conversation_title": "Alchemy Game Tutorial Design", "conversation_id": 500}],
        "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "An alchemist at work — the world the board game brings to life"}],
    },
}

# Collections — curated thematic groupings of conversations.
# Lighter weight than showcases: a description + conversation list, no pedagogy/quotes.
COLLECTIONS = {
    "alchemy-scholarship": {
        "slug": "alchemy-scholarship",
        "title": "Alchemy Scholarship",
        "subtitle": "the art of transformation, studied at book-length",
        "description": "Renaissance alchemy as a system of transformation — not just lead-into-gold but the deeper question of how matter, mind, and symbol change state. These conversations span Atalanta Fugiens, Tilton, alchemical illustration, and the chemistry underneath the mysticism.",
        "conversation_ids": [712, 670, 726, 716, 725, 673, 721, 640, 719],
        "color": "#ffd700",
    },
    "philosophy": {
        "slug": "philosophy",
        "title": "Philosophy",
        "subtitle": "Plato to Bruno, with stops at every Neoplatonist along the way",
        "description": "A reading program through Western philosophy with a Renaissance center of gravity — Pico della Mirandola, Giordano Bruno, Plato, Hegel, and the Neoplatonic tradition that connects them all to alchemy and esoteric thought.",
        "conversation_ids": [666, 520, 623, 731, 525, 269, 624, 242, 324, 834, 412, 395, 519, 267, 722, 542, 769, 400, 767],
        "color": "#9c27b0",
    },
    "pkd": {
        "slug": "pkd",
        "title": "Philip K. Dick",
        "subtitle": "the prophet of ontological instability",
        "description": "PKD as philosopher, Gnostic, and inadvertent game designer. From the Exegesis to biopolitics to hermeticism — and the recurring question of what happens when reality itself is unreliable.",
        "conversation_ids": [669, 628, 700, 701, 789, 157, 730, 642, 844, 208, 213, 639, 849, 356, 217, 202, 499, 727],
        "color": "#e74c3c",
    },
    "marxism": {
        "slug": "marxism",
        "title": "Marxism & Critical Theory",
        "subtitle": "alienation, commodity, and the critique that won't stop being relevant",
        "description": "Robinson via Jameson, PKD on capitalism, Negt and Kluge, Marx's theory of value. A smaller collection but one that keeps surfacing in unexpected places — late capitalism critique appears in game design conversations too.",
        "conversation_ids": [702, 157, 2646, 809, 814, 2639, 476, 283, 479],
        "color": "#f44336",
    },
    "music-engineering": {
        "slug": "music-engineering",
        "title": "Music Engineering",
        "subtitle": "from chiptune synthesis to OK Computer harmony analysis",
        "description": "Synthesizer sound design, DAW automation, MIDI manipulation, and music theory analysis of everything from Nintendo to Radiohead. The engineering side of making sounds.",
        "conversation_ids": [577, 579, 251, 753, 252, 757, 22, 553, 2653, 651, 760, 746, 250, 754, 62, 2644],
        "color": "#00bcd4",
    },
    "dark-horses": {
        "slug": "dark-horses",
        "title": "Dark Horses",
        "subtitle": "the recondite, the passionate, the unexpectedly deep",
        "description": "Conversations where creative energy was highest but the topics are niche — esoteric sigil apps, microscopic fungus adventure games, geomancy calculators, and ancient magic educational games (the single most enthusiastic conversation in the entire database).",
        "conversation_ids": [697, 631, 649, 703, 696, 554, 739, 449, 349, 270, 38, 497, 557, 183, 294, 146, 590, 640],
        "color": "#ff9800",
    },
    "scholarly-deep-reads": {
        "slug": "scholarly-deep-reads",
        "title": "Scholarly Deep Reads",
        "subtitle": "the 20 longest non-game conversations — a personal research library",
        "description": "The heaviest intellectual engagement in the database, measured by raw page count. Every conversation here is 280+ pages of sustained scholarly dialogue — equivalent to reading and discussing an entire book.",
        "conversation_ids": [712, 670, 726, 716, 734, 666, 687, 674, 616, 725, 598, 669, 673, 662, 721, 570, 520, 559, 18, 694],
        "color": "#7c6fe0",
    },
    "scholarly-to-games": {
        "slug": "scholarly-to-games",
        "title": "Scholarly Mining for Game Ideas",
        "subtitle": "when reading Renaissance texts produces game mechanics",
        "description": "The crossover zone where deep scholarly reading transmutes into game design. Alchemy texts become board game engines, esoteric grimoires become sigil apps, video game learning theory becomes implicit pedagogy. These conversations sit at the intersection of research and making.",
        "conversation_ids": [567, 717, 761, 724, 631, 697, 851, 347, 500, 531, 533],
        "color": "#e8a838",
    },
    "building-dreams": {
        "slug": "building-dreams",
        "title": "Building Dreams",
        "subtitle": "33 projects across MTG overlays, Marxist scholarship, voice apps, and esoteric computing",
        "description": "The conversations where ideas became code. MTG draft overlays, a RAG system for Marx's Capital, Kabbalistic tree adventures, esoteric sigil generators, and the Dreambase itself. Each project started as a conversation and ended as something that runs.",
        "conversation_ids": [570, 636, 697, 631, 500, 703, 32, 711, 554, 577, 647, 560, 12, 377, 709, 843, 778, 382, 2947, 3268],
        "color": "#4caf50",
    },
    "digital-humanities": {
        "slug": "digital-humanities",
        "title": "Digital Humanities",
        "subtitle": "building digital editions, scholarly tools, and searchable archives of esoteric texts",
        "description": "The conversations where Renaissance scholarship meets software engineering. Digital editions of Proclus, Bruno, the Emerald Tablet, and the Sefer Yetzirah — each one a facing-page translation with hyperlinked commentary, grammatical annotation, and philosophical context. Plus the tools that make the whole archive searchable.",
        "conversation_ids": [679, 676, 3362, 2498, 285, 3259, 606, 674, 2607],
        "color": "#26a69a",
    },
}

# Scholars — curated showcase pages for Ted's favorite thinkers.
# Same 5-tab deep-dive as game showcases, adapted for intellectual engagement.
# Fields: field (area), era (period), pedagogy (what studying them teaches),
# depth tiers (introductory/intermediate/advanced instead of easy/med/hard).
SCHOLARS = {
    "pico-della-mirandola": {
        "slug": "pico-della-mirandola",
        "title": "Pico della Mirandola",
        "hook": "The 23-year-old who tried to reconcile every tradition ever — and nearly pulled it off.",
        "field": "Renaissance syncretism",
        "era": "15th century",
        "conversation_ids": [666, 3361, 525, 3348, 3331, 3349],
        "tags": ["philosophy", "alchemy", "kabbalah", "renaissance"],
        "pedagogy": "How to hold contradictions productively. Pico's 900 Theses are a masterclass in synthetic thinking — finding the common root beneath Kabbalah, Neoplatonism, Hermeticism, and Christianity without flattening their differences.",
        "depth_introductory": "The Oration on the Dignity of Man — humanity as self-creating being",
        "depth_intermediate": "The 900 Theses — mapping correspondences across traditions",
        "depth_advanced": "Pico's Kabbalah — how Hebrew letter-mysticism entered Renaissance philosophy",
        "narrative": "<h3>The Portrait</h3><p>Giovanni Pico della Mirandola — the 23-year-old who tried to reconcile every intellectual tradition in existence and nearly pulled it off. Six conversations totaling over 1,400 pages trace Ted’s sustained engagement with Pico’s syncretism, from the famous Oration on the Dignity of Man through the 900 Theses to his revolutionary introduction of Kabbalistic thought into Renaissance philosophy.</p><h3>What Emerged</h3><p>The centerpiece is a 744-page deep reading of Pico’s philosophical system — his argument that humanity is uniquely self-creating, his method of finding common roots beneath Kabbalah, Neoplatonism, Hermeticism, and Christianity without flattening their differences. Copenhaver’s article on the secret Kabbalistic architecture of the Oration was analyzed in detail, revealing how Pico smuggled Hebrew letter-mysticism into the heart of Renaissance humanism. A digital reader tool for the 900 Theses with cross-references was prototyped.</p><h3>Why It Matters</h3><p>Pico is the patron saint of interdisciplinary thinking — the insistence that truth is distributed across traditions and that the scholar’s job is synthesis, not allegiance. His method is the intellectual ancestor of this entire database.</p>", "timeline_entries": [{"date": "2024-09-14", "title": "Kabbalistic Tree Prototype", "description": "This example will create the grid, place the circles in the appropriate positions, and allow users to click on the circles to cycle through colors.", "conversation_id": 843}, {"date": "2024-09-16", "title": "Kabbalistic Tree of Life Fix", "description": "I've updated the code to correctly position the circles (sefirot) and lines (paths) according to the traditional diagram.", "conversation_id": 778}, {"date": "2024-09-23", "title": "Tarot Web App Development", "description": "However, by breaking down the project into manageable steps and creating effective prompts, you can leverage AI assistance to guide you through the process.", "conversation_id": 711}, {"date": "2024-09-24", "title": "Esoteric Sigil Creation App", "description": "User is interested in generating an app that creates sigils in the style of esoteric grimoires, including customization options for users to design their own sigils with design ele...", "conversation_id": 697}, {"date": "2024-09-24", "title": "Custom Sigil Generator Prompts", "description": "Here are 100 prompts for building your *Custom Sigil Generator* app from scratch in JavaScript: ### General Structure 1.", "conversation_id": 709}, {"date": "2024-09-24", "title": "App Ideas for Occultists", "description": "Could you provide the link to the PDF of your jam session? Once I have access to the document, I can review it and compile a list of the 100 best ideas with their descriptions.", "conversation_id": 703}, {"date": "2024-10-10", "title": "Tarot Card Generator Prompts", "description": "These prompts cover various aspects, including backend logic, frontend UI, integrations, animations, and advanced features to ensure a comprehensive development process.", "conversation_id": 636}, {"date": "2024-10-10", "title": "Esoteric Planner Project Ideas", "description": "User wants to create a 2025 day planner, page-a-day calendar, journals, and other \"low content\" items that they can sell on Amazon KDP by the holidays, with alchemical, magical, ta...", "conversation_id": 647}, {"date": "2024-10-11", "title": "Tarot Game Web App", "description": "Building a Tarot card game as a single HTML file with embedded CSS and JavaScript is an ambitious project, but it's entirely feasible.", "conversation_id": 631}, {"date": "2024-10-19", "title": "DAW Automation with NLP", "description": "Setting up a DAW (Digital Audio Workstation) using natural language inputs and automating processes like loading synthesizer programs and MIDI sequences can be approached in severa...", "conversation_id": 577}, {"date": "2024-10-20", "title": "Custom GPT for Magic Decks", "description": "To create a custom GPT that helps users build a Magic: The Gathering deck with features like a draft overlay, search engine, and deck builder, you're looking at a combination of se...", "conversation_id": 570}, {"date": "2024-10-20", "title": "Database for App Design", "description": "To turn this long GPT conversation into a database for your app design and prompt engineering analysis, here’s a step-by-step plan: ### Step 1: Structure the Conversation into Prom...", "conversation_id": 560}, {"date": "2024-10-21", "title": "Geomancy Calculator App HTML", "description": "Here's a basic HTML file for a geomancy calculator app that walks the user through the process step by step.", "conversation_id": 554}, {"date": "2024-10-25", "title": "Alchemy Game Tutorial Design", "description": "Each message is designed to be clear, concise, and engaging, enhancing the player's understanding and immersion.", "conversation_id": 500}, {"date": "2024-11-13", "title": "MTG Draft Archetype Analyzer", "description": "Creating an app to analyze MTG draft formats for synergies involves organizing the card data, implementing search and filtering functionality, and providing analytical tools to eva...", "conversation_id": 382}, {"date": "2024-11-14", "title": "Procedural Laser Maze Design", "description": "Here are **40 prompts** you can feed into Claude to build the features of your **procedurally generated mirror maze laser puzzle game**.", "conversation_id": 377}, {"date": "2025-01-04", "title": "Data Mining Projects Python", "description": "It's great to hear about your progress in learning Python and developing tools for handling Magic card data! Transitioning to more complex data handling tasks, such as data mining ...", "conversation_id": 32}, {"date": "2025-01-06", "title": "MTG Puzzle Game Plan", "description": "To align your Magic: The Gathering puzzle game project with the course syllabus, here's a breakdown of the project into subtasks tuned to each module's learning goals: --- ### **Mo...", "conversation_id": 12}, {"date": "2025-10-08", "title": "Overlay app plan", "description": "Perfect — this is a really cool and achievable idea.", "conversation_id": 2947}, {"date": "2026-01-31", "title": "Vibe Coding Setup", "description": "Here’s how the two books you uploaded line up with what you want: getting a clean VS Code (VSC) workflow, then using that workflow to ship prototypes into real desktop/web (and eve...", "conversation_id": 3268}], "quotes": [{"text": "The interface design should be simple and intuitive, with a draft overlay integrated for in-draft assistance, a search bar that supports detailed filtering (like Scryfall), and an interactive deck builder that provides real-time feedback.", "role": "assistant", "conversation_title": "Custom GPT for Magic Decks", "conversation_id": 570}, {"text": "Certainly! Here are 50 detailed prompts to guide you in generating the code for your Tarot Card Generator project. These prompts cover various aspects, including backend logic, frontend UI, integrations, animations, and advanced features to ensure a comprehensive development proc", "role": "assistant", "conversation_title": "Tarot Card Generator Prompts", "conversation_id": 636}], "images": [{"url": "/static/art/pico-portrait.jpg", "caption": "Giovanni Pico della Mirandola — portrait by Cristofano dell'Altissimo (Uffizi Gallery)"}],
        "color": "#9c27b0",
    },
    "giordano-bruno": {
        "slug": "giordano-bruno",
        "title": "Giordano Bruno",
        "hook": "The memory palace builder who saw infinite worlds and burned for it.",
        "field": "Renaissance philosophy, cosmology",
        "era": "16th century",
        "conversation_ids": [3011, 1921, 731, 3334, 2988, 1919],
        "tags": ["philosophy", "alchemy", "renaissance", "memory"],
        "pedagogy": "The art of memory as a technology of thought. Bruno's memory palaces aren't parlor tricks — they're cognitive architectures for holding vast systems in mind. His cosmology of infinite worlds follows naturally from his method.",
        "depth_introductory": "The memory palace technique — spatial encoding of knowledge",
        "depth_intermediate": "De Umbris Idearum — shadows of ideas as combinatorial system",
        "depth_advanced": "Bruno's infinite cosmology — how Hermetic philosophy led to modern astronomy via heresy",
        "narrative": "<h3>The Portrait</h3><p>The philosopher who was burned at the stake for insisting that the universe was infinite and that Earth was not its center. Six conversations totaling over 1,000 pages explore Bruno’s cosmology, his memory techniques, his radical epistemology, and his place in Renaissance intellectual history through the lens of modern scholarship.</p><h3>What Emerged</h3><p>Three scholarly reviews on Bruno’s philosophy were synthesized, covering Blum’s study of Bruno’s Aristotle reception, Spruit’s dissertation on his theory of knowledge, and historiographical debates about whether Bruno was primarily a Hermetic magician or a proto-modern cosmologist. A 193-page overview traced Bruno’s influence on Renaissance thought, and a detailed analysis of his rewriting of the Actaeon myth in the Eroici Furori revealed how he transformed classical mythology into philosophical allegory for the hunt for divine knowledge.</p><h3>Why It Matters</h3><p>Bruno embodies the dangerous edge of intellectual courage — what happens when you follow ideas wherever they lead regardless of institutional consequences. His memory palace techniques also inspired a 3D visualization project in the database.</p>", "timeline_entries": [{"date": "2024-09-30", "title": "Hypnerotomachia2", "description": "To summarize your document past page 110, please upload the file to [AI Drive](https://myaidrive.", "conversation_id": 674}, {"date": "2024-10-02", "title": "Greek Text Digital Edition", "description": "Here’s an English translation of the Greek text to be displayed in the upper right frame, with the theurgy terms you provided marked for hyperlinks: **English Translation:** (1) Ju...", "conversation_id": 679}, {"date": "2024-10-03", "title": "Digital Edition Design Ideas", "description": "User wants to create a digital edition of Giordano Bruno's *De magia mathematica* with facing page Latin and English, grammatical information for hyperlinked terms, philosophical c...", "conversation_id": 676}, {"date": "2024-10-19", "title": "Emerald Tablet Enhancements", "description": "To enhance the existing layout of your Emerald Tablet project with a facing-page Latin and English translation, and a commentary section, I suggest the following steps.", "conversation_id": 606}, {"date": "2024-10-19", "title": "Creating a Digital Edition of the Emerald Tablet", "description": "As an AI language model, I don't have direct access to specific texts or databases.", "conversation_id": 2498}, {"date": "2024-11-20", "title": "Digital Edition Resources", "description": "User wants to create a digital edition of a Renaissance esoteric text as a project to demonstrate their skills.", "conversation_id": 285}, {"date": "2025-05-21", "title": "Neoplatonic Visual Novel: Hypnerotomachia Polyphili", "description": "That's a fascinating idea to reimagine the Hypnerotomachia Poliphili as a modern interactive visual novel! The 1499 text's rich allegorical imagery and dream-like narrative structu...", "conversation_id": 2607}, {"date": "2025-11-30", "title": "Digital Sefer Yetzirah project", "description": "You’re basically describing: a digital Sefer Yetzirah + a historical-semantic database of letters and sefirot + a visual playground for “spaces of the divine,” with an optional Pro...", "conversation_id": 3362}, {"date": "2026-01-30", "title": "PKD Searchable Database Plan", "description": "Here are 30 computer-science lessons you can use as a build plan for a “PKD searchable database” app—each lesson teaches a concept and produces a real feature.", "conversation_id": 3259}], "quotes": [{"text": "Otherwise: metadata + quotes/excerpts only (user-supplied, or fair-use-limited) and/or “bring your own files” locally.", "role": "assistant", "conversation_title": "PKD Searchable Database Plan", "conversation_id": 3259}, {"text": "(5) Through sympathy, they attracted, and through antipathy, they repelled, purifying with sulfur and asphalt and sprinkling with seawater. For sulfur purifies through its sharp smell, and the sea through its participation in fiery power.", "role": "assistant", "conversation_title": "Greek Text Digital Edition", "conversation_id": 679}], "images": [{"url": "/static/art/bruno-statue.jpg", "caption": "Statue of Giordano Bruno at Campo de' Fiori, Rome — erected at the site of his execution in 1600"}, {"url": "/static/art/bruno-portrait.jpg", "caption": "Portrait of Giordano Bruno (19th century engraving)"}],
        "color": "#e74c3c",
    },
    "hereward-tilton": {
        "slug": "hereward-tilton",
        "title": "Hereward Tilton",
        "hook": "The scholar who made Heinrich Khunrath's alchemical amphitheatre legible to the 21st century.",
        "field": "Alchemy, early modern history",
        "era": "Contemporary scholar",
        "conversation_ids": [716, 4123],
        "tags": ["alchemy", "esoteric", "scholarship"],
        "pedagogy": "How to read alchemical images as philosophical arguments. Tilton's work on Khunrath demonstrates that emblem books weren't decorative — they were compressed theoretical statements requiring visual literacy to decode.",
        "depth_introductory": "Alchemical emblems as visual philosophy — reading Khunrath's Amphitheatre",
        "depth_intermediate": "The relationship between laboratory practice and spiritual aspiration in early modern alchemy",
        "depth_advanced": "Tilton's historiographic method — recovering intent from deliberately obscure sources",
        "narrative": "<h3>The Portrait</h3><p>A modern scholar of spiritual alchemy whose work on Heinrich Khunrath and the quest for the philosopher’s stone bridges the gap between chemical practice and mystical aspiration. The primary source is Tilton’s <em>The Quest for the Phoenix</em>, which received an 893-page deep reading — one of the longest sustained engagements in the entire database.</p><h3>What Emerged</h3><p>Tilton’s central argument — that early modern alchemy cannot be cleanly separated into “spiritual” and “practical” strands — was traced through his treatment of Khunrath’s Amphitheatre of Eternal Wisdom, the Rosicrucian manifestos, and the alchemical-theosophical tradition. The reading maps how alchemical imagery functions simultaneously as laboratory instruction and contemplative exercise.</p><h3>Why It Matters</h3><p>Tilton’s work is the scholarly backbone for understanding alchemy as a unified practice rather than a confused mixture of chemistry and mysticism. His framework directly informs how the alchemy-scholarship collection is organized.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Giordano Bruno Overview", "description": "The discussion of Giordano Bruno in the text covers several key points: 1.", "conversation_id": 731}, {"date": "2025-01-16", "title": "bruno upside down", "description": "Highlights his contributions to the debate on the freedom of thought.", "conversation_id": 3334}, {"date": "2025-10-28", "title": "2025-10-28_Hermetic-medieval-to-bruno", "description": "USER tell me more about the figures, texts, and contexts mentioned in this newsletter View this email in your browser “In any field find the strangest thing and then explore it.", "conversation_id": 1919}, {"date": "2025-10-28", "title": "Hermetic medieval to bruno", "description": "https://mailchi.", "conversation_id": 2988}, {"date": "2025-11-09", "title": "2025-11-09_Summarize-reviews-on-Bruno", "description": "USER summarize these TOOL Make sure to include 【message_idx†source】 markers to provide citations based on this file, where [message_idx] is provided at the beginning of this messag...", "conversation_id": 1921}, {"date": "2025-11-09", "title": "Summarize reviews on Bruno", "description": "Here’s a detailed synthesis of the three reviews you uploaded, arranged to show how they collectively illuminate Giordano Bruno’s philosophy, epistemology, and the historiography a...", "conversation_id": 3011}], "quotes": [{"text": "Blum’s monograph, originally Aristoteles bei Giordano Bruno (1980), interprets Bruno as an independent and creative philosopher who uses past thinkers—especially Aristotle—not to repeat or merely synthesize them but to transcend their aporias (unresolved problems).", "role": "assistant", "conversation_title": "Summarize reviews on Bruno", "conversation_id": 3011}, {"text": "Blum’s work is based on two methodological assumptions: Bruno’s critical use", "role": "assistant", "conversation_title": "2025-11-09_Summarize-reviews-on-Bruno", "conversation_id": 1921}, {"text": "This provides a nuanced view of Bruno’s multifaceted contributions to philosophy, science, and mysticism.", "role": "assistant", "conversation_title": "Giordano Bruno Overview", "conversation_id": 731}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "Khunrath's Amphitheatre — the alchemist's oratory and laboratory united"}],
        "color": "#ffd700",
    },
    "aleister-crowley": {
        "slug": "aleister-crowley",
        "title": "Aleister Crowley",
        "hook": "The Great Beast who systematized Western magic into something you could actually practice.",
        "field": "Ceremonial magic, Thelema",
        "era": "19th-20th century",
        "conversation_ids": [2772, 1862, 180, 399, 29, 1944],
        "tags": ["esoteric", "golden_dawn", "magic"],
        "pedagogy": "Systems thinking applied to the irrational. Crowley's genius was treating magic as engineering — creating reproducible protocols for altered states, ritual design as UX, the Holy Guardian Angel as a well-specified API.",
        "depth_introductory": "Thelema basics — 'Do what thou wilt' as ethical philosophy, not hedonism",
        "depth_intermediate": "The A∴A∴ grade system — a curriculum for consciousness mapped to the Tree of Life",
        "depth_advanced": "Crowley's reception of The Book of the Law — prophecy, psychosis, or performance?",
        "narrative": "<h3>The Portrait</h3><p>The most notorious occultist of the twentieth century, studied here not for scandal but for system — his financial strategies, his analysis of the Hidden God concept, his MTG-inspired creative handles, and his influence on modern magical practice. Six conversations across 1,016 pages.</p><h3>What Emerged</h3><p>A 392-page extraction of Crowley’s financial system from Kaczynski’s <em>Perdurabo</em> biography, tracing how Crowley funded his magical operations through inheritance, patronage, publishing, and increasingly desperate schemes. A separate 64-page analysis of Kenneth Grant’s Hidden God concept explored the Typhonian tradition’s interpretation of Crowley’s sexual magick as a technology for accessing trans-mundane consciousness.</p><h3>Why It Matters</h3><p>Crowley is studied here as a case study in how esoteric systems get built, funded, and propagated — the organizational and economic infrastructure of occultism, not just its theology.</p>", "timeline_entries": [{"date": "2024-11-11", "title": "Crowley Hidden God Analysis", "description": "To analyze an esoteric text effectively, we must focus on its **structure**, **content**, and **context**.", "conversation_id": 399}, {"date": "2024-12-06", "title": "Crowley Inspired MTG Handle", "description": "Creating a unique and memorable internet handle for **MTG Arena** can enhance your gaming experience and help you stand out in the community.", "conversation_id": 180}, {"date": "2025-01-04", "title": "2025-01-04_Crowley-AI-Genius-Mythology", "description": "USER I feel like aleister Crowley has a lot to teach us about the mythology and psychology of AI in the ways that he conceptualized the production of \"genius\" by magical means, esp...", "conversation_id": 1944}, {"date": "2025-01-04", "title": "Crowley AI Genius Mythology", "description": "That's a fascinating insight! Aleister Crowley’s approach to *genius*—particularly the way he merged mystical inspiration with systematic computation—is indeed relevant to how we t...", "conversation_id": 29}, {"date": "2025-01-07", "title": "2025-01-07_Crowley-Financial-Overview", "description": "USER I want a summary of only Aleister Crowley's financial system.", "conversation_id": 1862}, {"date": "2025-01-07", "title": "Crowley Financial Overview", "description": "I’ll locate and extract all financial details related to Aleister Crowley from the book Perdurabo by Richard Kaczynski.", "conversation_id": 2772}], "quotes": [{"text": "msearch([\"Aleister Crowley inheritance\", \"Aleister Crowley wealth\", \"Aleister Crowley financial details\", \"Al", "role": "assistant", "conversation_title": "2025-01-07_Crowley-Financial-Overview", "conversation_id": 1862}, {"text": "Select themes and symbols that resonate with both Magic: The Gathering and Crowley’s mystical style. Consider elements such as:", "role": "assistant", "conversation_title": "Crowley Inspired MTG Handle", "conversation_id": 180}], "images": [],
        "color": "#ff5722",
    },
    "michael-maier": {
        "slug": "michael-maier",
        "title": "Michael Maier",
        "hook": "Atalanta Fugiens: 50 alchemical fugues where music, image, and text encode the same secret three ways.",
        "field": "Alchemy, emblematics",
        "era": "17th century",
        "conversation_ids": [670, 2524, 4305],
        "tags": ["alchemy", "music", "emblem"],
        "pedagogy": "Multimedia as philosophical method. Maier's Atalanta Fugiens is history's most ambitious attempt at multimodal encoding — each of 50 emblems combines an engraving, an epigram, and a musical fugue, all transmitting the same alchemical principle through different sensory channels.",
        "depth_introductory": "The emblem tradition — how image + text combinations create meaning",
        "depth_intermediate": "Atalanta Fugiens as musical-visual-textual unity — decoding one emblem in full",
        "depth_advanced": "Maier's Rosicrucian connections — was the multimedia format itself a Rosicrucian technology?",
        "narrative": "<h3>The Portrait</h3><p>The alchemist-physician whose <em>Atalanta Fugiens</em> (1618) is the most ambitious multimedia alchemical text ever produced — 50 emblems combining engraved images, Latin epigrams, and musical fugues into a unified contemplative experience. The primary conversation is a 988-page deep reading of the emblems.</p><h3>What Emerged</h3><p>Each of the 50 emblems was analyzed as a unit combining visual allegory, textual exegesis, and musical structure. The reading traced Maier’s alchemical symbolism — the fleeing Atalanta as volatile mercury, the golden apples as the philosopher’s stone, the race as the alchemical process itself — through the lens of art history, music theory, and chemical practice.</p><h3>Why It Matters</h3><p>Maier’s work demonstrates that alchemy was never just text — it was always multimedia. The Atalanta Fugiens is a 400-year-old prototype for the kind of multi-sensory knowledge design that modern digital humanities aspires to.</p>", "timeline_entries": [{"date": "2017-04-26", "title": "Hereward Tilton", "description": "Hereward Tilton — \"You are now connected on Messenger\" — 7 messages via facebook — 2017-04-26...", "conversation_id": 4123}, {"date": "2024-09-21", "title": "Tilton on Spiritual Alchemy", "description": "Hereward Tilton's *The Quest for the Phoenix* introduces the complexities of alchemy in the early modern period, focusing on spiritual alchemy, Jung’s interpretations, and the crit...", "conversation_id": 716}], "quotes": [{"text": "This partial summary covers key points about Tilton’s defense of spiritual alchemy and critique of Newman and Principe's interpretation. If you want to explore more or search for specific sections, I can help continue the summary or conduct searches.", "role": "assistant", "conversation_title": "Tilton on Spiritual Alchemy", "conversation_id": 716}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "An alchemist's laboratory — the visual world of Maier's Atalanta Fugiens"}],
        "color": "#795548",
    },
    "philip-k-dick": {
        "slug": "philip-k-dick",
        "title": "Philip K. Dick",
        "hook": "The prophet of ontological instability who turned paranoia into philosophy.",
        "field": "Science fiction, Gnosticism, philosophy of mind",
        "era": "20th century",
        "conversation_ids": [628, 700, 701, 600, 789, 730],
        "tags": ["pkd", "gnostic", "philosophy", "scifi"],
        "pedagogy": "How fiction becomes philosophy when reality breaks. PKD's novels aren't speculative entertainment — they're thought experiments about what happens when the substrate of reality is unreliable. The Exegesis is his attempt to debug existence itself.",
        "depth_introductory": "VALIS and the pink beam — autobiography as Gnostic revelation",
        "depth_intermediate": "The Exegesis — 8,000 pages of reality debugging as spiritual practice",
        "depth_advanced": "PKD's Hermetic lineage — connecting 2-3-74 to Neoplatonism via Bruno and Dee",
        "narrative": "<h3>The Portrait</h3><p>Philip K. Dick as philosopher, Gnostic, and inadvertent game designer. Six conversations across 720 pages explore PKD’s fiction, his Exegesis, his engagement with Hermeticism, and the recurring question of what happens when reality itself is unreliable.</p><h3>What Emerged</h3><p>A 323-page analysis of PKD’s relationship to Hermeticism traced how Gnostic and alchemical themes saturate his later fiction and the Exegesis — the notion that the material world is a “Black Iron Prison” overlaid on a hidden divine reality. Summaries of his major works, short story analyses, and a study of Lapoujade’s <em>Worlds Built to Fall Apart</em> mapped PKD’s philosophical framework: unstable ontology, empathy as the test of the real, and entropy as the universal antagonist.</p><h3>Why It Matters</h3><p>PKD provides the conceptual vocabulary for the entire Dreambase project — the idea that personal archives are unstable realities that need to be actively maintained, that identity is constructed through narrative, and that the boundary between human and artificial intelligence is a question, not a given.</p>", "timeline_entries": [{"date": "2017-09-01", "title": "Mohammed AL-omaier", "description": "Mohammed AL-omaier — \"Hi ted\" — 35 messages via facebook — 2017-09-01...", "conversation_id": 4305}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}, {"date": "2024-09-29", "title": "Emblems of Atalanta Fugiens", "description": "1.", "conversation_id": 2524}], "quotes": [{"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "Based on the information provided, I can summarize the first five emblems of the alchemical text Atalanta Fugiens by Michael Maier:", "role": "assistant", "conversation_title": "Emblems of Atalanta Fugiens", "conversation_id": 2524}], "images": [],
        "color": "#e74c3c",
    },
    "paracelsus": {
        "slug": "paracelsus",
        "title": "Paracelsus",
        "hook": "The physician-alchemist who replaced Galen with chemistry and got expelled from every city he visited.",
        "field": "Iatrochemistry, medical alchemy",
        "era": "16th century",
        "conversation_ids": [3007, 1906, 343, 166],
        "tags": ["alchemy", "medicine", "renaissance"],
        "pedagogy": "How paradigm shifts actually happen in practice. Paracelsus didn't just theorize that chemistry could replace humoral medicine — he burned Avicenna's Canon in public, treated miners and peasants, and built an empirical pharmacology from alchemical first principles.",
        "depth_introductory": "The tria prima (salt, sulfur, mercury) as a new theory of matter",
        "depth_intermediate": "Iatrochemistry — alchemy in service of medicine, not gold",
        "depth_advanced": "Paracelsus and the Reformation — how religious upheaval enabled medical revolution",
        "narrative": "<h3>The Portrait</h3><p>The physician-alchemist who broke with Galenic medicine and insisted that chemistry, not humoral theory, was the foundation of healing. Four conversations across 899 pages, anchored by two deep readings of Bruce Moran’s revisionist <em>Paracelsus</em> biography.</p><h3>What Emerged</h3><p>Moran’s “new Paracelsus” was analyzed across 436 pages, focusing on what recent scholarship has revised about the standard narrative: Paracelsus as less a lone genius rebel and more a product of specific mining-town medical cultures, vernacular knowledge traditions, and the social politics of early modern healing. A separate 28-page roleplay conversation channeled an early modern alchemist persona to explore Paracelsus’s relationship with Trithemius.</p><h3>Why It Matters</h3><p>Paracelsus represents the intersection of alchemy and practical medicine — the moment when transformation theory was applied to human bodies rather than metals. His story is also a case study in how scholarly narratives get revised across generations.</p>", "timeline_entries": [{"date": "2024-11-15", "title": "Paracelsus Alchemist Roleplay", "description": "Ah, a fine challenge indeed! You wish to conjure the spirit of an early modern alchemist? Very well, let me adopt the guise of a Paracelsian adept, striding through the 16th centur...", "conversation_id": 343}, {"date": "2024-12-13", "title": "Paracelsus Trithemius Relationship", "description": "The association between Paracelsus (1493–1541) and Johannes Trithemius (1462–1516) is a subject of historical interest, particularly regarding whether Paracelsus studied under Tri...", "conversation_id": 166}, {"date": "2025-11-06", "title": "2025-11-06_New-Paracelsus-Version", "description": "USER what is new about this version of paracelsus TOOL Make sure to include 【message_idx†source】 markers to provide citations based on this file, where [message_idx] is provided at...", "conversation_id": 1906}, {"date": "2025-11-06", "title": "New Paracelsus Version", "description": "{\"queries\": [\"new interpretation of Paracelsus Bruce Moran 2019\", \"what is new about Moran Paracelsus book\", \"Moran Paracelsus historiography\", \"Moran Paracelsus new perspective or...", "conversation_id": 3007}], "quotes": [{"text": "Make sure to include 【message_idx†source】 markers to provide citations based on this", "role": "assistant", "conversation_title": "2025-11-06_New-Paracelsus-Version", "conversation_id": 1906}, {"text": "How shall we begin, my eager interlocutor?", "role": "assistant", "conversation_title": "Paracelsus Alchemist Roleplay", "conversation_id": 343}], "images": [{"url": "/static/art/paracelsus-portrait.jpg", "caption": "Paracelsus — portrait attributed to Quentin Matsys (16th century)"}],
        "color": "#4caf50",
    },
    "agrippa": {
        "slug": "agrippa",
        "title": "Cornelius Agrippa",
        "hook": "Three Books of Occult Philosophy: the encyclopedia that made Renaissance magic systematic.",
        "field": "Occult philosophy, natural magic",
        "era": "16th century",
        "conversation_ids": [2955, 2230, 524, 3371, 2504],
        "tags": ["esoteric", "magic", "renaissance", "philosophy"],
        "pedagogy": "Classification as power. Agrippa's Three Books organize magic into natural (stones, herbs, elements), celestial (astrology, number), and ceremonial (angels, divine names) — turning a chaotic tradition into a coherent curriculum. The organizational structure itself is the magic.",
        "depth_introductory": "Natural magic — sympathies and antipathies in the material world",
        "depth_intermediate": "Celestial magic — planetary hours, number symbolism, and astrological timing",
        "depth_advanced": "Ceremonial magic — divine names, angelic hierarchies, and the ethics of invocation",
        "narrative": "<h3>The Portrait</h3><p>Heinrich Cornelius Agrippa von Nettesheim — the Renaissance polymath whose <em>De occulta philosophia</em> (1533) became the foundational textbook of Western ceremonial magic. Five conversations across 712 pages, anchored by a detailed biographical study and analysis of his magical language theory.</p><h3>What Emerged</h3><p>A 320-page engagement with Le Paige’s biographical essay traced Agrippa as a humanist of the “middle countries” — neither fully German nor French, navigating the intellectual currents of Northern European humanism. Chris Miles’s article on the “paradox of magical language” was analyzed, exploring how Agrippa’s system simultaneously claims words have real power over nature and acknowledges that language is conventional and arbitrary.</p><h3>Why It Matters</h3><p>Agrippa is the systematizer — the figure who organized scattered magical traditions into a coherent three-book curriculum (natural, celestial, ceremonial magic). Understanding his organizational framework illuminates how knowledge taxonomies work.</p>", "timeline_entries": [{"date": "2024-09-26", "title": "Visualizing Agrippa's Magical Sigils", "description": "The image shows several sigils and a magic square associated with \"The Table of the Sun\" attributed to Cornelius Agrippa.", "conversation_id": 2504}, {"date": "2024-10-24", "title": "Agrippa and Magical Language", "description": "The article \"Occult Retraction: Cornelius Agrippa and the Paradox of Magical Language\" by Chris Miles explores the complex relationship between rhetoric and magic, particularly thr...", "conversation_id": 524}, {"date": "2025-10-11", "title": "2025-10-11_Agrippa-biography-summary", "description": "USER summarize TOOL Make sure to include 【message_idx†source】 markers to provide citations based on this file, where [message_idx] is provided at the beginning of this message UN H...", "conversation_id": 2230}, {"date": "2025-10-11", "title": "Agrippa biography summary", "description": "Frédéric Le Paige’s 1964 essay “Un humaniste des pays médians : Heinrich-Cornelius Agrippa de Nettesheim” offers a concise intellectual and biographical portrait of Agrippa as both...", "conversation_id": 2955}, {"date": "2026-02-06", "title": "Agrippa", "description": "Below is a document-by-document scholarly summary, focused on arguments, historiographical stakes, and how each text positions Agrippa.", "conversation_id": 3371}], "quotes": [{"text": "Frédéric Le Paige’s 1964 essay “Un humaniste des pays médians : Heinrich-Cornelius Agrippa de Nettesheim” offers a concise intellectual and biographical portrait of Agrippa as both Renaissance scholar and legendary magician.I. Agrippa’s Double Image in Literature", "role": "assistant", "conversation_title": "Agrippa biography summary", "conversation_id": 2955}, {"text": "» ne, la famille Shelley travailla dans le jardin à creuser un abri d’été", "role": "assistant", "conversation_title": "2025-10-11_Agrippa-biography-summary", "conversation_id": 2230}], "images": [],
        "color": "#3f51b5",
    },
    "robert-anton-wilson": {
        "slug": "robert-anton-wilson",
        "title": "Robert Anton Wilson",
        "hook": "The man who made conspiracy theory a tool for epistemological liberation.",
        "field": "Discordianism, guerrilla ontology",
        "era": "20th century",
        "conversation_ids": [3201, 2302, 619, 3192, 432, 2260],
        "tags": ["esoteric", "philosophy", "pkd", "freemasonry"],
        "pedagogy": "Reality tunnels and model agnosticism. RAW's core insight: every belief system is a map, not the territory. By deliberately switching between incompatible maps (Marxism, Crowley, Timothy Leary, Sufism), you learn to see the map-making process itself.",
        "depth_introductory": "Reality tunnels — how belief systems filter perception",
        "depth_intermediate": "The Illuminatus! trilogy as epistemological training device",
        "depth_advanced": "Chapel Perilous — the psychological state where all models break down simultaneously",
        "narrative": "<h3>The Portrait</h3><p>The trickster-philosopher who turned conspiracy theory into epistemology and Discordianism into a spiritual practice. Robert Anton Wilson appears in conversations that bridge the gap between esoteric tradition and countercultural skepticism.</p><h3>What Emerged</h3><p>Wilson’s work was engaged primarily through his connections to Crowley’s magical tradition and his unique approach to reality tunnels — the idea that all perception is model-dependent and that holding multiple contradictory models simultaneously is a form of cognitive liberation. His influence on the database’s approach to knowledge organization is structural: the Dreambase itself is a reality tunnel navigator.</p><h3>Why It Matters</h3><p>Wilson provides the epistemological framework for why a personal knowledge archive matters: every model of reality is partial, and the archive is the tool for tracking how your models have changed over time.</p>", "timeline_entries": [{"date": "2024-09-16", "title": "Philip K Dick Robots", "description": "Philip K.", "conversation_id": 789}, {"date": "2024-09-20", "title": "Hermeticism and Philip K Dick", "description": "To effectively summarize an article about Philip K.", "conversation_id": 628}, {"date": "2024-09-20", "title": "Gnosticism in Philip K Dick", "description": "The article titled \"Gnosticism and Dualism in the Early Fiction of Philip K.", "conversation_id": 730}, {"date": "2024-09-25", "title": "Philip K Dick Analysis", "description": "Dick's short stories! To get started, please provide the name of the first short story you'd like me to summarize, or a file containing one of his works if you have it on hand.", "conversation_id": 701}, {"date": "2024-09-25", "title": "Philip K Dick Summaries", "description": "a summary of this document or do you want to search for something specific?...", "conversation_id": 700}, {"date": "2024-10-17", "title": "Summary of Dick's Worlds", "description": "To give a detailed summary of *Worlds Built to Fall Apart: Versions of Philip K.", "conversation_id": 600}], "quotes": [{"text": "To effectively summarize an article about Philip K. Dick's engagement with Hermeticism, particularly through the lens of Paracelsus and the concept of the \"inner firmament,\" we need to focus on several key themes:", "role": "assistant", "conversation_title": "Hermeticism and Philip K Dick", "conversation_id": 628}, {"text": "It seems the document contains multiple short stories by Philip K. Dick, such as \"We Can Remember It for You Wholesale,\" \"Second Variety,\" \"Paycheck,\" and more. Let's start with summarizing and analyzing the stories one at a time. I'll begin with \"We Can Remember It for You Whole", "role": "assistant", "conversation_title": "Philip K Dick Summaries", "conversation_id": 700}, {"text": "I'd be happy to help you analyze Philip K. Dick's short stories! To get started, please provide the name of the first short story you'd like me to summarize, or a file containing one of his works if you have it on hand. If you prefer, I can choose a story for you—just let me know", "role": "assistant", "conversation_title": "Philip K Dick Analysis", "conversation_id": 701}], "images": [],
        "color": "#ff9800",
    },
    "wouter-hanegraaff": {
        "slug": "wouter-hanegraaff",
        "title": "Wouter Hanegraaff",
        "hook": "The scholar who gave Western esotericism its academic legitimacy — and its definition.",
        "field": "Western esotericism, historiography",
        "era": "Contemporary scholar",
        "conversation_ids": [667, 138],
        "tags": ["esoteric", "scholarship", "philosophy"],
        "pedagogy": "How to study something that resists being studied. Hanegraaff's contribution is methodological: he showed that 'Western esotericism' is a coherent field of study, not a dustbin category, by tracing how Enlightenment rationalism created 'the occult' as its rejected other.",
        "depth_introductory": "What is Western esotericism? — Hanegraaff's definition and its stakes",
        "depth_intermediate": "The 'rejected knowledge' thesis — how the Enlightenment produced the occult",
        "depth_advanced": "Esotericism and the academic study of religion — epistemological challenges",
        "narrative": "<h3>The Portrait</h3><p>The leading academic historian of Western esotericism, whose work established the field as a legitimate discipline within religious studies. Two conversations across 416 pages engage with Hanegraaff’s scholarship on Hermetism, his critique of Frances Yates, and his theoretical framework for studying esoteric traditions.</p><h3>What Emerged</h3><p>A detailed analysis of Hanegraaff’s articles traced his key distinctions: Hermetism (the historical tradition rooted in the Corpus Hermeticum) versus Hermeticism (the broader intellectual current), the critique of Yates’s overgeneralized “Hermetic tradition” narrative, and the recovery of Lazzarelli as an underappreciated figure in Renaissance Hermetism. His argument about <em>prisca theologia</em> and <em>philosophia perennis</em> as organizing concepts for Renaissance thinkers was mapped in detail.</p><h3>Why It Matters</h3><p>Hanegraaff provides the scholarly framework that prevents the database’s esoteric content from collapsing into undifferentiated “occultism.” His distinctions are the taxonomic backbone of the alchemy-scholarship collection.</p>", "timeline_entries": [{"date": "2024-09-26", "title": "Pico della Mirandola Philosophy Summary", "description": "Pico della Mirandola's philosophical contributions, especially in his *Oration on the Dignity of Man* and his *900 Theses*, offer a synthesis of various philosophical traditions, i...", "conversation_id": 666}, {"date": "2024-10-24", "title": "Pico's Oration and Cabala", "description": "The article \"The Secret of Pico's Oration: Cabala and Renaissance Philosophy\" by Brian P.", "conversation_id": 525}, {"date": "2025-01-07", "title": "Pico and Divine Being", "description": "In \"De Ente et Uno,\" Pico della Mirandola carefully navigates the complex relationship between God and the concepts of unity and being.", "conversation_id": 3331}, {"date": "2025-07-04", "title": "Pico 900 Conclusions Exegesis", "description": "These statements are attributed to \"Adelandus Arabus\" (likely Adelard of Bath or an Arabizing pseudepigraphic source) and reflect a Neoplatonic and Avicennian-Arabic philosophical ...", "conversation_id": 3348}, {"date": "2025-07-05", "title": "Pico della Mirandola Summary", "description": "Copenhaver:📘 Introduction Summary1.", "conversation_id": 3349}, {"date": "2025-10-29", "title": "Cutting edge in Pico studies", "description": "{\"queries\": [\"current state of +Pico studies recent developments --QDF=3\", \"latest scholarship themes in +Giovanni Pico della Mirandola --QDF=3\", \"cutting edge research topics in +...", "conversation_id": 3361}], "quotes": [{"text": "Wilson writes in what he calls the Hermetic style: layered meaning, parody, occult jokes, philosophical puzzles, myth nested in autobiography. He explicitly aligns himself with Dante, Pico, Bruno, Blake, Joyce, Crowley. The book is meant to be decoded, not merely read.ND:", "role": "assistant", "conversation_title": "Game Design for Wilson's Doctrine", "conversation_id": 3201}, {"text": "educational game inspired by a religious studies approach to Robert Anton Wilson", "role": "assistant", "conversation_title": "2026-01-15_Game-Design-for-Wilson's-Doctrine", "conversation_id": 2302}, {"text": "In sum, Wilson integrates a diverse array of influences into his thoughts on literature, philosophy, and magick, advocating for an approach to life that embraces uncertainty, creativity, and the breaking of conventional boundaries.", "role": "assistant", "conversation_title": "Wilson on Lit Phil Magick", "conversation_id": 619}], "images": [],
        "color": "#607d8b",
    },
    "frances-yates": {
        "slug": "frances-yates",
        "title": "Frances Yates",
        "hook": "The Art of Memory, the Rosicrucian Enlightenment, and the Hermetic tradition she single-handedly rescued from obscurity.",
        "field": "Renaissance intellectual history",
        "era": "20th century scholar",
        "conversation_ids": [138, 597, 3350, 818, 3010, 1920],
        "tags": ["esoteric", "renaissance", "memory", "scholarship"],
        "pedagogy": "How to recover lost intellectual worlds. Yates showed that the Renaissance wasn't just about 'rediscovering the classics' — it was powered by Hermetic philosophy, the art of memory, and a Rosicrucian underground that connected Bruno to the Scientific Revolution.",
        "depth_introductory": "The Art of Memory — from Simonides to Giulio Camillo's Memory Theatre",
        "depth_intermediate": "The Yates Thesis — Hermeticism as driver of the Scientific Revolution",
        "depth_advanced": "Critiques and legacy — where Yates was wrong, and why it doesn't matter",
        "narrative": "<h3>The Portrait</h3><p>The scholar whose <em>Giordano Bruno and the Hermetic Tradition</em> (1964) single-handedly created the modern study of Renaissance magic — and whose thesis has been debated, critiqued, and partially dismantled ever since. Six conversations across 318 pages.</p><h3>What Emerged</h3><p>Multiple scholarly critiques of Yates’s thesis were analyzed: Klaassen, Saif, Zambelli, and Mertens each challenge different aspects of her claim that Hermeticism was the driving force behind the Scientific Revolution. Hanegraaff’s systematic critique of her overgeneralized “Hermetic tradition” was traced in detail. Couliano’s alternative theories were compared with Yates’s framework.</p><h3>Why It Matters</h3><p>Yates is the starting point for anyone entering this field — and understanding where her thesis breaks down is essential for moving beyond it. The database’s scholarly conversations are in constant dialogue with her legacy.</p>", "timeline_entries": [{"date": "2024-09-13", "title": "Frances Yates Renaissance Magic", "description": "Frances Yates was a pioneering scholar whose work significantly shaped the study of Renaissance magic, particularly in relation to its impact on the history of science.", "conversation_id": 818}, {"date": "2024-10-12", "title": "Critiques of Yates's Magic", "description": "In the works of Klaassen, Saif, Zambelli, and Mertens, critiques of Frances Yates's influential interpretation of Renaissance magic reveal a more complex and nuanced view of the pe...", "conversation_id": 597}, {"date": "2024-12-18", "title": "Hanegraaff articles Taves/Yates", "description": "188 pages of exploration via chatgpt.", "conversation_id": 138}, {"date": "2025-07-15", "title": "Couliano and Yates' Theories", "description": "{ \"queries\": [ \"Frances Yates\", \"Yates\", \"Hypnerotomachia Poliphili\", \"discussion of Hypnerotomachia\", \"Couliano on Hypnerotomachia Poliphili\" ] }...", "conversation_id": 3350}, {"date": "2025-11-09", "title": "2025-11-09_Debus-critiques-Yates'-work", "description": "USER summarize Debus's criticisms of yates TOOL Make sure to include 【message_idx†source】 markers to provide citations based on this file, where [message_idx] is provided at the be...", "conversation_id": 1920}, {"date": "2025-11-09", "title": "Debus critiques Yates' work", "description": "Allen G.", "conversation_id": 3010}], "quotes": [{"text": "Let me know if you'd like further refinements!", "role": "assistant", "conversation_title": "Hanegraaff articles Taves/Yates", "conversation_id": 138}], "images": [{"url": "/static/art/bruno-portrait.jpg", "caption": "Giordano Bruno — the figure at the center of Yates's Hermetic Tradition thesis"}],
        "color": "#8e24aa",
    },
    "fredric-jameson": {
        "slug": "fredric-jameson",
        "title": "Fredric Jameson",
        "hook": "Always historicize! The Marxist literary theorist who reads culture as the political unconscious.",
        "field": "Marxist literary theory, cultural criticism",
        "era": "Contemporary scholar",
        "conversation_ids": [702, 2646],
        "tags": ["marxism", "philosophy", "literary_theory"],
        "pedagogy": "How to read anything as ideology without reducing it to propaganda. Jameson's method: every cultural artifact encodes a political unconscious — a utopian wish and a class anxiety simultaneously. The task is to read both without canceling either.",
        "depth_introductory": "Late capitalism and postmodernism — Jameson's cultural diagnosis",
        "depth_intermediate": "The political unconscious — narrative as socially symbolic act",
        "depth_advanced": "Jameson reading PKD — science fiction as cognitive mapping of late capitalism",
        "narrative": "<h3>The Portrait</h3><p>The Marxist literary critic whose work on postmodernism, science fiction, and the political unconscious provides the theoretical framework for understanding how cultural production encodes ideology. Two conversations across 294 pages.</p><h3>What Emerged</h3><p>A 284-page deep reading of Kim Stanley Robinson’s fiction through Jameson’s critical lens — analyzing how Robinson’s Mars trilogy and other works instantiate Jameson’s theories about utopian imagination under late capitalism. A separate analysis of Jameson’s appreciation for Negt and Kluge’s theory of the public sphere connected Marxist media theory to questions of collective experience and counter-publics.</p><h3>Why It Matters</h3><p>Jameson provides the critical vocabulary for understanding why science fiction matters politically — and why PKD’s work, Robinson’s work, and the archive itself are all sites of ideological contestation.</p>", "timeline_entries": [{"date": "2024-09-24", "title": "Robinson Critique via Jameson", "description": "Could you upload it directly here or try providing a different link? If you upload it directly, I can process it and help you summarize the introduction with the specific context i...", "conversation_id": 702}, {"date": "2025-04-19", "title": "Jameson's Appreciation for Negt and Kluge's Theories", "description": "Fredric Jameson found significant value in the work of Oskar Negt and Alexander Kluge, particularly their collaborative writings on public sphere theory and proletarian experience.", "conversation_id": 2646}], "quotes": [{"text": "Fredric Jameson found significant value in the work of Oskar Negt and Alexander Kluge, particularly their collaborative writings on public sphere theory and proletarian experience. Their relationship centers on several key intellectual connections:", "role": "assistant", "conversation_title": "Jameson's Appreciation for Negt and Kluge's Theories", "conversation_id": 2646}], "images": [],
        "color": "#f44336",
    },
    "kim-stanley-robinson": {
        "slug": "kim-stanley-robinson",
        "title": "Kim Stanley Robinson",
        "hook": "The science fiction writer who takes utopia seriously as political practice.",
        "field": "Science fiction, political ecology",
        "era": "Contemporary",
        "conversation_ids": [702, 4107],
        "tags": ["scifi", "marxism", "ecology"],
        "pedagogy": "How to think about the future without despair or fantasy. Robinson's Mars trilogy and Ministry for the Future model political transformation as a concrete engineering problem — not inevitable, not impossible, but designable.",
        "depth_introductory": "The Mars trilogy — terraforming as political metaphor",
        "depth_intermediate": "Robinson's utopianism — why he insists on depicting positive futures",
        "depth_advanced": "Robinson via Jameson — science fiction as the realism of our era",
        "narrative": "<h3>The Portrait</h3><p>The science fiction novelist whose Mars trilogy is the most sustained exercise in utopian worldbuilding in the genre’s history. Two conversations across 285 pages, read primarily through Fredric Jameson’s critical framework.</p><h3>What Emerged</h3><p>A 284-page Jamesonian reading of Robinson’s fiction analyzed how his novels function as thought experiments in political economy: terraforming Mars as a laboratory for testing social organization, the tension between capitalist extraction and cooperative governance, and the role of scientific practice as a model for democratic deliberation.</p><h3>Why It Matters</h3><p>Robinson demonstrates what happens when science fiction takes its worldbuilding seriously enough to function as political philosophy. His work connects the PKD literary analysis in the database to the Marxist critical theory collection.</p>", "timeline_entries": [{"date": "2016-04-05", "title": "Harold Robinson", "description": "Harold Robinson — \"when's a good time to call you, and is it the same phone number from 3 years ago?.", "conversation_id": 4107}, {"date": "2024-09-24", "title": "Robinson Critique via Jameson", "description": "Could you upload it directly here or try providing a different link? If you upload it directly, I can process it and help you summarize the introduction with the specific context i...", "conversation_id": 702}], "quotes": [{"text": "The chapter presents two example games, \"Turtle’s Rare Ingredient Hunt\" and a sorting tutor, developed by university students, demonstrating the flexibility of Greenmind for educational purposes.", "role": "assistant", "conversation_title": "Games Learning Alchemy Board Game ", "conversation_id": 567}], "images": [],
        "color": "#2196f3",
    },
    "marsilio-ficino": {
        "slug": "marsilio-ficino",
        "title": "Marsilio Ficino",
        "hook": "The priest-philosopher who translated Hermes Trismegistus for the Medici and launched the Renaissance.",
        "field": "Neoplatonism, Hermeticism",
        "era": "15th century",
        "conversation_ids": [666, 520, 525],
        "tags": ["philosophy", "renaissance", "alchemy", "neoplatonism"],
        "pedagogy": "How translation creates intellectual movements. Ficino didn't just translate Plato and the Hermetica — he synthesized them into a living philosophy that powered the Florentine Renaissance. Every translation is an interpretation, and Ficino's interpretations changed the world.",
        "depth_introductory": "The Platonic Academy — Ficino's translation project and its cultural impact",
        "depth_intermediate": "De Vita — Ficino's guide to the scholarly life as planetary magic",
        "depth_advanced": "Ficino's Hermeticism — how the Corpus Hermeticum reshaped Christian philosophy",
        "narrative": "<h3>The Portrait</h3><p>The Florentine priest-philosopher who translated the entire Platonic corpus into Latin and single-handedly launched the Renaissance Neoplatonic revival. Three conversations across 1,201 pages position Ficino at the intersection of Plato, Pico, and the Western esoteric tradition.</p><h3>What Emerged</h3><p>Ficino appears primarily through his connections to Pico della Mirandola (in the 744-page Pico deep read) and through the Platonic dialogues he translated and commented upon (in the 363-page Plato’s Sophist and Philebus analysis). His role as the bridge between ancient Neoplatonism and Renaissance magic — translating both Plato and the Corpus Hermeticum, and arguing that they represented the same prisca theologia — was traced across multiple scholarly sources.</p><h3>Why It Matters</h3><p>Without Ficino, there is no Renaissance magic, no Pico, no Bruno, and arguably no Western esoteric tradition as we know it. He is the root node of the entire scholarly network in this database.</p>", "timeline_entries": [{"date": "2024-09-26", "title": "Pico della Mirandola Philosophy Summary", "description": "Pico della Mirandola's philosophical contributions, especially in his *Oration on the Dignity of Man* and his *900 Theses*, offer a synthesis of various philosophical traditions, i...", "conversation_id": 666}, {"date": "2024-10-24", "title": "Pico's Oration and Cabala", "description": "The article \"The Secret of Pico's Oration: Cabala and Renaissance Philosophy\" by Brian P.", "conversation_id": 525}, {"date": "2024-10-25", "title": "Plato's Sophist and Philebus Summary", "description": "**Sophist**: In *Sophist*, Plato engages in a dialogue primarily between the characters of the Eleatic Stranger and Theaetetus.", "conversation_id": 520}], "quotes": [{"text": "Let me know if you'd like further refinements!", "role": "assistant", "conversation_title": "Hanegraaff articles Taves/Yates", "conversation_id": 138}], "images": [{"url": "/static/art/pico-portrait.jpg", "caption": "Pico della Mirandola — Ficino's student and intellectual heir"}],
        "color": "#ce93d8",
    },
    "allen-debus": {
        "slug": "allen-debus",
        "title": "Allen Debus",
        "hook": "The historian who proved that the Chemical Revolution didn't start with Lavoisier — it started with Paracelsus.",
        "field": "History of chemistry, Paracelsianism",
        "era": "20th century scholar",
        "conversation_ids": [726, 725],
        "tags": ["alchemy", "chemistry", "scholarship"],
        "pedagogy": "How to trace ideas across centuries without teleology. Debus showed the continuous thread from Paracelsian iatrochemistry through the chemical physicians to Boyle and modern chemistry — without claiming the alchemists 'really' knew what they were doing.",
        "depth_introductory": "The chemical philosophy — Paracelsus as founder of a new science",
        "depth_intermediate": "The English Paracelsians — how alchemy became chemistry in 17th-century England",
        "depth_advanced": "Debus vs. the Whig historians — was there a 'Chemical Revolution'?",
        "narrative": "<h3>The Portrait</h3><p>The historian of science whose work on the chemical philosophy traced how alchemy transformed into chemistry across the sixteenth and seventeenth centuries. Two conversations across 1,457 pages — among the longest sustained scholarly engagements in the database.</p><h3>What Emerged</h3><p>An 895-page reading of <em>Laboratories of Art</em> examined how alchemical illustrations and materials science intersected across antiquity through the eighteenth century — the visual culture of alchemy as both artistic tradition and technical documentation. A 563-page companion on alchemical illustrations as course design material explored how to teach the history of chemistry through its visual artifacts.</p><h3>Why It Matters</h3><p>Debus represents the bridge between alchemy-as-mysticism and alchemy-as-science. His work is essential context for understanding why the database’s alchemy collection includes both spiritual and material dimensions.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Alchemical Illustrations and Materials Science", "description": "This book, *Laboratories of Art: Alchemy and Art Technology from Antiquity to the 18th Century*, provides a comprehensive look at the intersections between alchemy, materials scien...", "conversation_id": 726}, {"date": "2024-09-20", "title": "Alchemical Illustrations Course Design", "description": "Could you try uploading the file directly here or recheck the link? Alternatively, you can upload it to your myaidrive.", "conversation_id": 725}], "quotes": [{"text": "This summary covers up to page 27. Would you like to continue with the summary or search for specific information within the text?", "role": "assistant", "conversation_title": "Alchemical Illustrations and Materials Science", "conversation_id": 726}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "An alchemist's workspace — the kind of laboratory Debus studied historically"}],
        "color": "#a1887f",
    },
    "manly-p-hall": {
        "slug": "manly-p-hall",
        "title": "Manly P. Hall",
        "hook": "The Secret Teachings of All Ages, written at 27 — an encyclopedia of esoteric traditions by a self-taught polymath.",
        "field": "Comparative esotericism",
        "era": "20th century",
        "conversation_ids": [180, 399],
        "tags": ["esoteric", "freemasonry", "philosophy"],
        "pedagogy": "The encyclopedic impulse — how synthesizing traditions reveals structural patterns invisible from within any single tradition. Hall's work is a map of maps, valuable not for its scholarly rigor but for its scope of vision.",
        "depth_introductory": "The Secret Teachings as gateway text — what it covers and what it misses",
        "depth_intermediate": "Hall's Masonic philosophy — Freemasonry as vessel for ancient wisdom",
        "depth_advanced": "Hall's sources and their reliability — where enthusiasm outpaces evidence",
        "narrative": "<h3>The Portrait</h3><p>The self-taught esoteric encyclopedist whose <em>Secret Teachings of All Ages</em> (1928) became the gateway text for generations of occult seekers. Hall appears in conversations that explore the popularization of esoteric knowledge and the tension between scholarly rigor and accessible synthesis.</p><h3>What Emerged</h3><p>Hall’s work was engaged through its connections to Crowley’s magical tradition and the broader question of how esoteric knowledge gets communicated to non-specialist audiences. The 83-page MTG handle conversation and the 64-page Hidden God analysis both reference Hall as a point of comparison for different approaches to esoteric popularization.</p><h3>Why It Matters</h3><p>Hall represents the populist strand of esotericism — the conviction that these traditions belong to everyone, not just academics. His encyclopedic ambition is a precursor to the database’s own project of making scattered knowledge searchable.</p>", "timeline_entries": [{"date": "2024-11-11", "title": "Crowley Hidden God Analysis", "description": "To analyze an esoteric text effectively, we must focus on its **structure**, **content**, and **context**.", "conversation_id": 399}, {"date": "2024-12-06", "title": "Crowley Inspired MTG Handle", "description": "Creating a unique and memorable internet handle for **MTG Arena** can enhance your gaming experience and help you stand out in the community.", "conversation_id": 180}], "quotes": [{"text": "Select themes and symbols that resonate with both Magic: The Gathering and Crowley’s mystical style. Consider elements such as:", "role": "assistant", "conversation_title": "Crowley Inspired MTG Handle", "conversation_id": 180}, {"text": "To analyze an esoteric text effectively, we must focus on its structure, content, and context. Here's a guide on how to approach this:", "role": "assistant", "conversation_title": "Crowley Hidden God Analysis", "conversation_id": 399}], "images": [],
        "color": "#5d4037",
    },
    "dion-fortune": {
        "slug": "dion-fortune",
        "title": "Dion Fortune",
        "hook": "The occultist who made the Western mystery tradition psychologically literate.",
        "field": "Western mystery tradition, occult psychology",
        "era": "20th century",
        "conversation_ids": [1862, 399],
        "tags": ["esoteric", "golden_dawn", "psychology"],
        "pedagogy": "How to bridge inner and outer worlds without losing either. Fortune's innovation was reading the Qabalah through Jungian and Freudian lenses — making the Tree of Life a map of the psyche while preserving its magical utility.",
        "depth_introductory": "The Mystical Qabalah — Fortune's accessible guide to the Tree of Life",
        "depth_intermediate": "Psychic self-defense — Fortune's integration of occultism and psychology",
        "depth_advanced": "Fortune's magical fiction — The Sea Priestess as initiatory novel",
        "narrative": "<h3>The Portrait</h3><p>The occultist and novelist whose practical magical training system bridged Victorian ceremonial magic and modern psychotherapeutic approaches to the unconscious. Fortune appears in conversations that explore the organizational and psychological dimensions of magical practice.</p><h3>What Emerged</h3><p>Fortune’s work was analyzed through its intersection with Crowley’s tradition — both figures attempted to systematize magical practice, but Fortune emphasized psychological integration and group dynamics where Crowley emphasized individual transgression and will. The Hidden God analysis traced how Fortune’s approach to magical practice differed structurally from Crowley’s Typhonian current.</p><h3>Why It Matters</h3><p>Fortune provides the psychological complement to Crowley’s ceremonial approach — the insight that magical systems are also systems for managing consciousness and group formation.</p>", "timeline_entries": [{"date": "2024-11-11", "title": "Crowley Hidden God Analysis", "description": "To analyze an esoteric text effectively, we must focus on its **structure**, **content**, and **context**.", "conversation_id": 399}, {"date": "2025-01-07", "title": "2025-01-07_Crowley-Financial-Overview", "description": "USER I want a summary of only Aleister Crowley's financial system.", "conversation_id": 1862}], "quotes": [{"text": "msearch([\"Aleister Crowley inheritance\", \"Aleister Crowley wealth\", \"Aleister Crowley financial details\", \"Al", "role": "assistant", "conversation_title": "2025-01-07_Crowley-Financial-Overview", "conversation_id": 1862}, {"text": "To analyze an esoteric text effectively, we must focus on its structure, content, and context. Here's a guide on how to approach this:", "role": "assistant", "conversation_title": "Crowley Hidden God Analysis", "conversation_id": 399}], "images": [{"url": "/static/art/tree-of-life.jpg", "caption": "The Tree of Life — central to Fortune's Kabbalistic magical system"}],
        "color": "#7b1fa2",
    },
    "antoine-faivre": {
        "slug": "antoine-faivre",
        "title": "Antoine Faivre",
        "hook": "The six characteristics of esotericism — the definition that built a discipline.",
        "field": "Western esotericism methodology",
        "era": "Contemporary scholar",
        "conversation_ids": [667, 138],
        "tags": ["esoteric", "scholarship", "methodology"],
        "pedagogy": "How to define the undefinable. Faivre's six characteristics (correspondences, living nature, imagination/mediation, transmutation, concordance, transmission) don't describe a belief system — they describe a form of thought. The method of definition is itself the lesson.",
        "depth_introductory": "The six characteristics — Faivre's typological approach to esotericism",
        "depth_intermediate": "Faivre vs. Hanegraaff — competing definitions and their consequences",
        "depth_advanced": "The limits of typology — what Faivre's definition includes and excludes",
        "narrative": "<h3>The Portrait</h3><p>The French scholar who defined the six characteristics of Western esotericism that became the standard academic framework for the field: correspondences, living nature, imagination and mediation, transmutation, concordance, and transmission. Two conversations across 416 pages.</p><h3>What Emerged</h3><p>Faivre’s framework was encountered primarily through Hanegraaff’s scholarly engagement with it — both building upon and critiquing Faivre’s attempt to define esotericism as a “form of thought” rather than a collection of traditions. The 228-page Hermetic Spirituality reading and the 188-page Hanegraaff articles analysis both position Faivre as a foundational theorist whose definitions shaped subsequent debate.</p><h3>Why It Matters</h3><p>Faivre’s six characteristics are the conceptual vocabulary used throughout the alchemy-scholarship collection to distinguish esoteric thinking from adjacent traditions. His framework is the taxonomy behind the tags.</p>", "timeline_entries": [{"date": "2024-09-22", "title": "Hermetic Spirituality Hanegraaff", "description": "Please provide me with the link or upload the book you'd like me to summarize, and I'll be happy to provide the detailed breakdown you're looking for.", "conversation_id": 667}, {"date": "2024-12-18", "title": "Hanegraaff articles Taves/Yates", "description": "188 pages of exploration via chatgpt.", "conversation_id": 138}], "quotes": [{"text": "Let me know if you'd like further refinements!", "role": "assistant", "conversation_title": "Hanegraaff articles Taves/Yates", "conversation_id": 138}], "images": [],
        "color": "#78909c",
    },
    "peter-forshaw": {
        "slug": "peter-forshaw",
        "title": "Peter Forshaw",
        "hook": "The visual culture of alchemy — reading images as primary sources, not illustrations.",
        "field": "Alchemical visual culture",
        "era": "Contemporary scholar",
        "conversation_ids": [670, 726],
        "tags": ["alchemy", "art_history", "scholarship"],
        "pedagogy": "Visual literacy as intellectual method. Forshaw's work demonstrates that alchemical images are arguments, not decorations. Learning to read an alchemical emblem requires the same kind of close analysis as reading a philosophical text.",
        "depth_introductory": "Alchemical emblems as philosophical statements",
        "depth_intermediate": "The Splendor Solis and its visual program",
        "depth_advanced": "Forshaw's method — art history meets history of science",
        "narrative": "<h3>The Portrait</h3><p>A scholar of early modern alchemy and Hermeticism whose work on alchemical imagery, Khunrath, and the visual culture of the Great Work brings art history methods to chemical philosophy. Two conversations across 1,883 pages.</p><h3>What Emerged</h3><p>Forshaw’s scholarship was engaged through two of the longest readings in the database: the 988-page Atalanta Fugiens emblem analysis and the 895-page Laboratories of Art reading. Both trace how alchemical knowledge was encoded in visual form — emblems, engravings, diagrams, and laboratory illustrations that functioned simultaneously as aesthetic objects and technical instructions.</p><h3>Why It Matters</h3><p>Forshaw demonstrates that alchemy was always a visual tradition, not just a textual one. His work directly informs the database’s interest in how knowledge changes form when it crosses media boundaries.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Alchemical Illustrations and Materials Science", "description": "This book, *Laboratories of Art: Alchemy and Art Technology from Antiquity to the 18th Century*, provides a comprehensive look at the intersections between alchemy, materials scien...", "conversation_id": 726}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}], "quotes": [{"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "This summary covers up to page 27. Would you like to continue with the summary or search for specific information within the text?", "role": "assistant", "conversation_title": "Alchemical Illustrations and Materials Science", "conversation_id": 726}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "The alchemical laboratory — the visual culture Forshaw studies"}],
        "color": "#8d6e63",
    },
    "christopher-celenza": {
        "slug": "christopher-celenza",
        "title": "Christopher Celenza",
        "hook": "The lost Italian Renaissance — recovering the intellectual culture that produced Pico and Ficino.",
        "field": "Renaissance intellectual history",
        "era": "Contemporary scholar",
        "conversation_ids": [666, 525],
        "tags": ["renaissance", "philosophy", "scholarship"],
        "pedagogy": "How institutional context shapes ideas. Celenza's work on the Florentine Academy shows that Pico and Ficino didn't emerge from nowhere — they were products of a specific patronage system, library culture, and correspondence network.",
        "depth_introductory": "The Florentine intellectual world — patrons, libraries, and letter-writing",
        "depth_intermediate": "Celenza on Pico — recovering the historical person behind the legend",
        "depth_advanced": "Renaissance intellectual history as a field — what it reveals about how ideas move",
        "narrative": "<h3>The Portrait</h3><p>A historian of Renaissance intellectual culture whose work on humanism, university culture, and the reception of ancient philosophy provides institutional context for figures like Pico and Ficino. Two conversations across 838 pages.</p><h3>What Emerged</h3><p>Celenza’s perspective was encountered through the 744-page Pico deep read, which drew on his work to situate Pico’s 900 Theses within the competitive intellectual culture of late fifteenth-century Italy. The 94-page analysis of Copenhaver on Pico’s Cabala similarly engaged Celenza’s framing of how Renaissance humanists negotiated between ancient authority and contemporary innovation.</p><h3>Why It Matters</h3><p>Celenza provides the institutional and social history that prevents Renaissance philosophy from floating in an abstract space of pure ideas. He grounds the scholarly conversations in the material conditions of how philosophy actually got produced.</p>", "timeline_entries": [{"date": "2024-09-26", "title": "Pico della Mirandola Philosophy Summary", "description": "Pico della Mirandola's philosophical contributions, especially in his *Oration on the Dignity of Man* and his *900 Theses*, offer a synthesis of various philosophical traditions, i...", "conversation_id": 666}, {"date": "2024-10-24", "title": "Pico's Oration and Cabala", "description": "The article \"The Secret of Pico's Oration: Cabala and Renaissance Philosophy\" by Brian P.", "conversation_id": 525}], "quotes": [], "images": [],
        "color": "#ab47bc",
    },
    "egil-asprem": {
        "slug": "egil-asprem",
        "title": "Egil Asprem",
        "hook": "The problem of disenchantment — why magic persists in a supposedly secular world.",
        "field": "Western esotericism, cognitive science of religion",
        "era": "Contemporary scholar",
        "conversation_ids": [667],
        "tags": ["esoteric", "scholarship", "cognitive_science"],
        "pedagogy": "How to ask 'why does this persist?' instead of 'why do people believe this?' Asprem reframes the study of esotericism from debunking to explaining — using cognitive science to understand why magical thinking is a permanent feature of human cognition, not a bug to be patched.",
        "depth_introductory": "The problem of disenchantment — Asprem's critique of the secularization thesis",
        "depth_intermediate": "Cognitive approaches to magic — why the brain is 'wired' for correspondences",
        "depth_advanced": "Asprem's methodological naturalism — studying magic without believing or debunking",
        "narrative": "<h3>The Portrait</h3><p>A scholar of Western esotericism whose work bridges the history of science, cognitive science of religion, and the academic study of magic. One conversation of 228 pages engages with his framework.</p><h3>What Emerged</h3><p>Asprem’s work was encountered through the 228-page Hermetic Spirituality reading, which positioned his cognitive-scientific approach to magical thinking alongside Hanegraaff’s historical method and Faivre’s phenomenological framework. His argument that magical practices can be studied as cognitive technologies — not just as cultural artifacts — provides a bridge between the database’s historical scholarship and its interest in how knowledge systems actually work in practice.</p><h3>Why It Matters</h3><p>Asprem represents the cutting edge of esotericism studies — the application of cognitive science and science studies methods to traditions previously studied only historically or theologically.</p>", "timeline_entries": [{"date": "2024-09-22", "title": "Hermetic Spirituality Hanegraaff", "description": "Please provide me with the link or upload the book you'd like me to summarize, and I'll be happy to provide the detailed breakdown you're looking for.", "conversation_id": 667}], "quotes": [], "images": [],
        "color": "#546e7a",
    },
    "carl-jung": {
        "slug": "carl-jung",
        "title": "Carl Jung",
        "hook": "The psychologist who took alchemy seriously — and found the unconscious encoded in its images.",
        "field": "Analytical psychology, alchemy",
        "era": "20th century",
        "conversation_ids": [712, 716, 670, 726, 673],
        "tags": ["psychology", "alchemy", "esoteric"],
        "pedagogy": "How to read symbols as psychological processes. Jung's alchemical work (Psychology and Alchemy, Mysterium Coniunctionis) shows that the opus alchemicum maps the individuation process — the nigredo, albedo, and rubedo are stages of psychological transformation, not just chemical ones.",
        "depth_introductory": "The collective unconscious and archetypes — Jung's basic framework",
        "depth_intermediate": "Psychology and Alchemy — reading the opus as individuation",
        "depth_advanced": "Mysterium Coniunctionis — the coniunctio oppositorum as Jung's ultimate synthesis",
        "narrative": "<h3>The Portrait</h3><p>The psychologist who treated alchemy as a symbolic language of the unconscious, arguing that alchemical imagery mapped the process of psychological individuation. Five conversations across 4,423 pages — the largest total page count of any scholar in the database.</p><h3>What Emerged</h3><p>Jung appears primarily as a lens for reading the major alchemical texts: the 1,207-page Medieval Magic reading, the 988-page Atalanta Fugiens emblem analysis, the 895-page Laboratories of Art study, and the 893-page Tilton reading all engage with Jungian interpretive frameworks. The cumulative effect is a sustained argument about whether alchemical symbolism is better understood as chemistry, psychology, or spiritual practice — with the database’s conversations consistently pushing toward “all three simultaneously.”</p><h3>Why It Matters</h3><p>Jung is the reason alchemy survived as a topic of serious intellectual interest in the twentieth century. His psychological reading is the default framework that every other interpretation in the database either builds on or argues against.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Alchemical Illustrations and Materials Science", "description": "This book, *Laboratories of Art: Alchemy and Art Technology from Antiquity to the 18th Century*, provides a comprehensive look at the intersections between alchemy, materials scien...", "conversation_id": 726}, {"date": "2024-09-21", "title": "Tilton on Spiritual Alchemy", "description": "Hereward Tilton's *The Quest for the Phoenix* introduces the complexities of alchemy in the early modern period, focusing on spiritual alchemy, Jung’s interpretations, and the crit...", "conversation_id": 716}, {"date": "2024-09-22", "title": "Medieval Magic Summary Request", "description": "- **Introduction to Medieval Magic**: This book offers an overview of medieval magic from c.", "conversation_id": 712}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}, {"date": "2024-09-29", "title": "Alchemy Chemistry summary", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 673}], "quotes": [{"text": "Here is a partial summary of \"The Routledge History of Medieval Magic\" (pages 1 to 26 of 569):", "role": "assistant", "conversation_title": "Medieval Magic Summary Request", "conversation_id": 712}, {"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "This summary covers up to page 27. Would you like to continue with the summary or search for specific information within the text?", "role": "assistant", "conversation_title": "Alchemical Illustrations and Materials Science", "conversation_id": 726}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "The alchemical laboratory — the imagery Jung interpreted as symbols of individuation"}],
        "color": "#5c6bc0",
    },
    "lawrence-principe": {
        "slug": "lawrence-principe",
        "title": "Lawrence Principe",
        "hook": "The chemist-historian who recreated alchemical experiments in a modern lab — and they worked.",
        "field": "History of alchemy and chemistry",
        "era": "Contemporary scholar",
        "conversation_ids": [712, 726, 670],
        "tags": ["alchemy", "chemistry", "scholarship"],
        "pedagogy": "How to take historical actors seriously on their own terms. Principe's lab recreations of alchemical recipes proved that many 'mystical' procedures were genuine chemical operations described in coded language. The history of science changes when you try the experiments.",
        "depth_introductory": "Alchemy in the lab — Principe's experimental approach to historical chemistry",
        "depth_intermediate": "Decoding alchemical language — Decknamen and the problem of secrecy",
        "depth_advanced": "Principe vs. the spiritual alchemists — was alchemy really about gold, or about the soul?",
        "narrative": "<h3>The Portrait</h3><p>The chemist-historian who has done more than anyone to demonstrate that historical alchemists were doing real chemistry — reproducing their experiments in modern laboratories to show that alchemical recipes often produce exactly what they claim. Three conversations across 3,090 pages.</p><h3>What Emerged</h3><p>Principe’s work was engaged through three of the database’s longest readings: the 1,207-page Medieval Magic survey, the 988-page Atalanta Fugiens analysis, and the 895-page Laboratories of Art study. His insistence on taking alchemical recipes literally — actually doing the chemistry — provides a crucial corrective to purely symbolic or psychological readings. The cumulative reading traces how Principe’s experimental approach has reshaped the field.</p><h3>Why It Matters</h3><p>Principe represents the empirical anchor of the alchemy-scholarship collection. Without his work, alchemy studies risks floating entirely into symbolism and psychology. His laboratory reproductions prove the tradition had real chemical content.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Alchemical Illustrations and Materials Science", "description": "This book, *Laboratories of Art: Alchemy and Art Technology from Antiquity to the 18th Century*, provides a comprehensive look at the intersections between alchemy, materials scien...", "conversation_id": 726}, {"date": "2024-09-22", "title": "Medieval Magic Summary Request", "description": "- **Introduction to Medieval Magic**: This book offers an overview of medieval magic from c.", "conversation_id": 712}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}], "quotes": [{"text": "Here is a partial summary of \"The Routledge History of Medieval Magic\" (pages 1 to 26 of 569):", "role": "assistant", "conversation_title": "Medieval Magic Summary Request", "conversation_id": 712}, {"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "This summary covers up to page 27. Would you like to continue with the summary or search for specific information within the text?", "role": "assistant", "conversation_title": "Alchemical Illustrations and Materials Science", "conversation_id": 726}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "Alchemical apparatus — the equipment Principe reproduces in modern labs"}],
        "color": "#00897b",
    },
    "isaac-newton": {
        "slug": "isaac-newton",
        "title": "Isaac Newton",
        "hook": "The last sorcerer — a million words of alchemical manuscripts behind the Principia.",
        "field": "Natural philosophy, alchemy",
        "era": "17th century",
        "conversation_ids": [712, 716, 670],
        "tags": ["alchemy", "science", "philosophy"],
        "pedagogy": "How the categories 'science' and 'magic' are retrospective impositions. Newton spent more time on alchemy than on physics. Understanding why dissolves the myth that the Scientific Revolution was a clean break from the occult — it was powered by it.",
        "depth_introductory": "Newton's alchemical manuscripts — scope and significance",
        "depth_intermediate": "The Janus-faced Newton — how optics, gravity, and alchemy coexisted",
        "depth_advanced": "Newton and the prisca sapientia — was modern science a recovery of ancient wisdom?",
        "narrative": "<h3>The Portrait</h3><p>The physicist who spent more time on alchemy than on physics — a fact that embarrassed his biographers for centuries and now illuminates the deep connections between early modern natural philosophy and chemical practice. Three conversations across 3,088 pages.</p><h3>What Emerged</h3><p>Newton’s alchemical practice was encountered through the same three major readings that engage Principe and Tilton: the Medieval Magic survey, Atalanta Fugiens, and Laboratories of Art. The conversations trace how Newton’s alchemical notebooks reveal a sustained experimental program that was not separate from his physics but continuous with it — the same drive to understand how matter transforms that produced the Principia also produced his alchemical investigations.</p><h3>Why It Matters</h3><p>Newton is the ultimate argument against the idea that alchemy and science were separate enterprises. His presence in the database connects the alchemy-scholarship collection to the history of science.</p>", "timeline_entries": [{"date": "2024-09-21", "title": "Tilton on Spiritual Alchemy", "description": "Hereward Tilton's *The Quest for the Phoenix* introduces the complexities of alchemy in the early modern period, focusing on spiritual alchemy, Jung’s interpretations, and the crit...", "conversation_id": 716}, {"date": "2024-09-22", "title": "Medieval Magic Summary Request", "description": "- **Introduction to Medieval Magic**: This book offers an overview of medieval magic from c.", "conversation_id": 712}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}], "quotes": [{"text": "Here is a partial summary of \"The Routledge History of Medieval Magic\" (pages 1 to 26 of 569):", "role": "assistant", "conversation_title": "Medieval Magic Summary Request", "conversation_id": 712}, {"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "This partial summary covers key points about Tilton’s defense of spiritual alchemy and critique of Newman and Principe's interpretation. If you want to explore more or search for specific sections, I can help continue the summary or conduct searches.", "role": "assistant", "conversation_title": "Tilton on Spiritual Alchemy", "conversation_id": 716}], "images": [{"url": "/static/art/newton-portrait.jpg", "caption": "Isaac Newton — portrait by Godfrey Kneller (1689)"}],
        "color": "#1565c0",
    },
    "proclus": {
        "slug": "proclus",
        "title": "Proclus",
        "hook": "The last great Neoplatonist — who systematized emanation into a science of the One.",
        "field": "Neoplatonism, theurgy",
        "era": "5th century",
        "conversation_ids": [666, 520, 623, 525, 324, 267],
        "tags": ["philosophy", "neoplatonism", "theurgy"],
        "pedagogy": "How to think systematically about levels of reality. Proclus turned Plotinus's mystical emanation into a rigorous logical system — every level of being proceeds from, remains in, and returns to its source. This triadic structure (proodos-mone-epistrophe) is the DNA of Western metaphysics.",
        "depth_introductory": "The One, Intellect, and Soul — Neoplatonic emanation as cosmic architecture",
        "depth_intermediate": "Proclus's triads — how he systematized Plotinus into formal metaphysics",
        "depth_advanced": "Theurgy — why Proclus believed ritual could achieve what philosophy alone could not",
        "narrative": "<h3>The Portrait</h3><p>The last great Neoplatonic philosopher, whose systematic theology and theory of theurgy — the priestly art of invoking divine powers through material correspondences — became the bridge between ancient philosophy and medieval magic. Five conversations across 876 pages.</p><h3>What Emerged</h3><p>A 363-page reading of Plato’s Sophist and Philebus traced the Platonic foundations that Proclus systematized. A 314-page analysis of Plato and Aristotle on alchemy connected Proclus’s emanation metaphysics to alchemical transformation theory. His text <em>On the Hieratic Art</em> was translated and analyzed, revealing the theoretical framework for cosmic sympathy — the idea that stones, plants, and animals channel divine emanation through material correspondences.</p><h3>Why It Matters</h3><p>Proclus is the philosophical engine behind everything in the alchemy-scholarship and philosophy collections. His theory of emanation and return is the metaphysical framework that makes alchemy, theurgy, and Neoplatonic magic intelligible as a unified system.</p>", "timeline_entries": [{"date": "2024-09-26", "title": "Pico della Mirandola Philosophy Summary", "description": "Pico della Mirandola's philosophical contributions, especially in his *Oration on the Dignity of Man* and his *900 Theses*, offer a synthesis of various philosophical traditions, i...", "conversation_id": 666}, {"date": "2024-10-16", "title": "Plato and Aristotle on Alchemy", "description": "Below are relevant passages from their works, presented with original Greek and English quotations, along with explanations of their relevance to these topics.", "conversation_id": 623}, {"date": "2024-10-24", "title": "Pico's Oration and Cabala", "description": "The article \"The Secret of Pico's Oration: Cabala and Renaissance Philosophy\" by Brian P.", "conversation_id": 525}, {"date": "2024-10-25", "title": "Plato's Sophist and Philebus Summary", "description": "**Sophist**: In *Sophist*, Plato engages in a dialogue primarily between the characters of the Eleatic Stranger and Theaetetus.", "conversation_id": 520}, {"date": "2024-11-16", "title": "Platonic Prayer", "description": "I will begin with the **Introduction** chapter of the book \"Platonic Theories of Prayer.", "conversation_id": 324}, {"date": "2024-11-21", "title": "Summary of Bruno's Work", "description": "### Summary of *The Composition of Images, Signs, and Ideas* by Giordano Bruno This document is a review and analysis of Giordano Bruno's *De imaginum, signorum, et idearum composi...", "conversation_id": 267}], "quotes": [{"text": "By drawing on these foundational texts, medieval and Renaissance thinkers were able to create a sophisticated blend of philosophical inquiry and practical experimentation, advancing the fields of alchemy, magic, natural philosophy, and astrology.", "role": "assistant", "conversation_title": "Plato and Aristotle on Alchemy", "conversation_id": 623}], "images": [],
        "color": "#4a148c",
    },
    "iamblichus": {
        "slug": "iamblichus",
        "title": "Iamblichus",
        "hook": "The philosopher who said: thinking isn't enough — you have to perform the divine.",
        "field": "Neoplatonism, theurgy",
        "era": "3rd-4th century",
        "conversation_ids": [520, 623, 324, 267, 242],
        "tags": ["philosophy", "neoplatonism", "theurgy", "ritual"],
        "pedagogy": "Why practice matters as much as theory. Iamblichus broke with Plotinus's purely contemplative mysticism by insisting that embodied ritual (theurgy) was necessary for union with the divine. Philosophy alone can't get you there — you need to act.",
        "depth_introductory": "De Mysteriis — Iamblichus's defense of ritual against Porphyry's rationalism",
        "depth_intermediate": "Theurgy vs. theology — embodied practice vs. abstract knowledge",
        "depth_advanced": "Iamblichus's influence on Renaissance magic — how theurgy became ceremonial magic via Ficino",
        "narrative": "<h3>The Portrait</h3><p>The Neoplatonic philosopher who argued that theurgy — ritual action using material symbols to invoke divine powers — was superior to pure philosophical contemplation as a path to the divine. Five conversations across 876 pages position Iamblichus as the key figure connecting Platonic philosophy to magical practice.</p><h3>What Emerged</h3><p>Iamblichus was engaged through the same Platonic deep readings as Proclus: the Sophist and Philebus analysis, the Plato-Aristotle-alchemy investigation, the Hegel-Heidegger analysis of energeia, and the Platonic prayer study. His <em>De Mysteriis</em> — the defense of theurgy against Porphyry’s rationalist critique — provides the theoretical justification for why physical ritual can achieve what abstract thought cannot.</p><h3>Why It Matters</h3><p>Iamblichus is the pivot point between philosophy and magic in the Western tradition. His argument that the gods must be approached through material means — not just intellectual contemplation — is the foundation of every subsequent magical tradition in the database.</p>", "timeline_entries": [{"date": "2024-10-16", "title": "Plato and Aristotle on Alchemy", "description": "Below are relevant passages from their works, presented with original Greek and English quotations, along with explanations of their relevance to these topics.", "conversation_id": 623}, {"date": "2024-10-25", "title": "Plato's Sophist and Philebus Summary", "description": "**Sophist**: In *Sophist*, Plato engages in a dialogue primarily between the characters of the Eleatic Stranger and Theaetetus.", "conversation_id": 520}, {"date": "2024-11-16", "title": "Platonic Prayer", "description": "I will begin with the **Introduction** chapter of the book \"Platonic Theories of Prayer.", "conversation_id": 324}, {"date": "2024-11-21", "title": "Summary of Bruno's Work", "description": "### Summary of *The Composition of Images, Signs, and Ideas* by Giordano Bruno This document is a review and analysis of Giordano Bruno's *De imaginum, signorum, et idearum composi...", "conversation_id": 267}, {"date": "2024-11-26", "title": "Hegel Heidegger Art Energeia", "description": "This talk, titled **“The ‘Work’ of Art: The Artwork as Ἐνέργεια in Hegel and Heidegger,”** would likely delve into the philosophical conceptions of art in the works of **G.", "conversation_id": 242}], "quotes": [{"text": "By drawing on these foundational texts, medieval and Renaissance thinkers were able to create a sophisticated blend of philosophical inquiry and practical experimentation, advancing the fields of alchemy, magic, natural philosophy, and astrology.", "role": "assistant", "conversation_title": "Plato and Aristotle on Alchemy", "conversation_id": 623}, {"text": "The talk promises a deep exploration of philosophical aesthetics, particularly how these two influential thinkers reinterpret a classical concept to frame art as a dynamic and world-shaping force.", "role": "assistant", "conversation_title": "Hegel Heidegger Art Energeia", "conversation_id": 242}], "images": [],
        "color": "#311b92",
    },
    "john-dee": {
        "slug": "john-dee",
        "title": "John Dee",
        "hook": "Elizabeth's court magician who talked to angels through a scrying stone and invented the British Empire.",
        "field": "Natural philosophy, angelic magic",
        "era": "16th century",
        "conversation_ids": [731, 670, 2524, 525],
        "tags": ["esoteric", "renaissance", "magic", "mathematics"],
        "pedagogy": "How mathematical thinking and magical thinking coexisted without contradiction. Dee was simultaneously a serious mathematician (he wrote the preface to the first English Euclid) and a practicing angel-summoner. For him, both were ways of accessing the structure of creation.",
        "depth_introductory": "The Monas Hieroglyphica — Dee's unified symbol for all knowledge",
        "depth_intermediate": "The Enochian system — angelic language as revealed mathematics",
        "depth_advanced": "Dee's influence — from the British Empire to the Golden Dawn via Meric Casaubon",
        "narrative": "<h3>The Portrait</h3><p>The Elizabethan polymath — mathematician, navigator, spy, and angel-summoner — whose library was the largest in England and whose conversations with angels through the medium Edward Kelley produced the Enochian magical system. Four conversations across 1,281 pages.</p><h3>What Emerged</h3><p>Dee was encountered through the 988-page Atalanta Fugiens reading (which contextualizes his alchemical interests), the 193-page Bruno overview (which positions Dee within the broader network of Renaissance magical practitioners), and analyses of Pico’s Cabala that trace the Kabbalistic transmission line from Pico through Reuchlin to Dee’s angelic conversations.</p><h3>Why It Matters</h3><p>Dee is the figure who makes the connection between Renaissance scholarly magic and practical experimentation most visible. His combination of mathematical rigor and angelic communication embodies the database’s central tension between systematic knowledge and visionary experience.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Giordano Bruno Overview", "description": "The discussion of Giordano Bruno in the text covers several key points: 1.", "conversation_id": 731}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}, {"date": "2024-09-29", "title": "Emblems of Atalanta Fugiens", "description": "1.", "conversation_id": 2524}, {"date": "2024-10-24", "title": "Pico's Oration and Cabala", "description": "The article \"The Secret of Pico's Oration: Cabala and Renaissance Philosophy\" by Brian P.", "conversation_id": 525}], "quotes": [{"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "This provides a nuanced view of Bruno’s multifaceted contributions to philosophy, science, and mysticism.", "role": "assistant", "conversation_title": "Giordano Bruno Overview", "conversation_id": 731}], "images": [{"url": "/static/art/dee-portrait.jpg", "caption": "Portrait of John Dee (16th century, Ashmolean Museum)"}],
        "color": "#0d47a1",
    },
    "heinrich-khunrath": {
        "slug": "heinrich-khunrath",
        "title": "Heinrich Khunrath",
        "hook": "The Amphitheatre of Eternal Wisdom — where the alchemist's laboratory meets the oratory.",
        "field": "Alchemy, Christian theosophy",
        "era": "16th-17th century",
        "conversation_ids": [716, 670, 726],
        "tags": ["alchemy", "esoteric", "emblem"],
        "pedagogy": "How material practice and spiritual aspiration can occupy the same room. Khunrath's most famous image — the alchemist kneeling in prayer while his furnace burns — is a thesis statement: the Great Work requires both hands and heart, laboratory and oratory.",
        "depth_introductory": "The Amphitheatre's most famous plate — laboratory, oratory, and the alchemist between",
        "depth_intermediate": "Khunrath's Christian Kabbalah — how Hebrew letter-mysticism shapes his alchemy",
        "depth_advanced": "Khunrath and Tilton — modern scholarship on the Amphitheatre's intellectual program",
        "narrative": "<h3>The Portrait</h3><p>The alchemist-theosopher whose <em>Amphitheatrum Sapientiae Aeternae</em> (1595) is one of the most visually spectacular alchemical texts ever produced — massive fold-out engravings combining Kabbalistic, Christian, and alchemical symbolism into contemplative images designed to transform the viewer. Three conversations across 2,776 pages.</p><h3>What Emerged</h3><p>Khunrath was engaged through three of the database’s longest readings: the Atalanta Fugiens emblem analysis (where Khunrath is a constant point of comparison for Maier’s visual alchemy), the Laboratories of Art study (where his engravings are analyzed as material objects), and the Tilton reading (which devotes substantial attention to Khunrath’s influence on later spiritual alchemy). The cumulative portrait reveals Khunrath as the supreme visual alchemist — the figure who most fully realized the idea that alchemical knowledge could be transmitted through images.</p><h3>Why It Matters</h3><p>Khunrath’s work is the ultimate argument that alchemy is a visual and spatial tradition, not just a textual one. His Amphitheatre is the historical precedent for the Dreambase’s own project of making knowledge navigable through designed visual interfaces.</p>", "timeline_entries": [{"date": "2024-09-20", "title": "Alchemical Illustrations and Materials Science", "description": "This book, *Laboratories of Art: Alchemy and Art Technology from Antiquity to the 18th Century*, provides a comprehensive look at the intersections between alchemy, materials scien...", "conversation_id": 726}, {"date": "2024-09-21", "title": "Tilton on Spiritual Alchemy", "description": "Hereward Tilton's *The Quest for the Phoenix* introduces the complexities of alchemy in the early modern period, focusing on spiritual alchemy, Jung’s interpretations, and the crit...", "conversation_id": 716}, {"date": "2024-09-28", "title": "Atalanta Fugiens emblems", "description": "a summary of this document, or do you want to search for something specific in it?...", "conversation_id": 670}], "quotes": [{"text": "Would you like to proceed to the next emblem?", "role": "assistant", "conversation_title": "Atalanta Fugiens emblems", "conversation_id": 670}, {"text": "This summary covers up to page 27. Would you like to continue with the summary or search for specific information within the text?", "role": "assistant", "conversation_title": "Alchemical Illustrations and Materials Science", "conversation_id": 726}, {"text": "This partial summary covers key points about Tilton’s defense of spiritual alchemy and critique of Newman and Principe's interpretation. If you want to explore more or search for specific sections, I can help continue the summary or conduct searches.", "role": "assistant", "conversation_title": "Tilton on Spiritual Alchemy", "conversation_id": 716}], "images": [{"url": "/static/art/khunrath-lab.jpg", "caption": "The Alchemist's Laboratory — Amphitheatrum Sapientiae Aeternae (Khunrath, 1595)"}],
        "color": "#bf360c",
    },
    "thomas-aquinas": {
        "slug": "thomas-aquinas",
        "title": "Thomas Aquinas",
        "hook": "The Angelic Doctor who built a cathedral of reason — and left room for the ineffable at the top.",
        "field": "Scholastic philosophy, theology",
        "era": "13th century",
        "conversation_ids": [734, 666, 525],
        "tags": ["philosophy", "theology", "medieval"],
        "pedagogy": "How to build systematic arguments that acknowledge their own limits. Aquinas's Summa is a machine for thinking — question, objection, response, reply to objections — that models intellectual honesty. And at the end, he stopped writing: 'Everything I have written seems like straw.'",
        "depth_introductory": "The Five Ways — Aquinas's proofs for God as exercises in philosophical argument",
        "depth_intermediate": "The Summa's structure — how the objection-response format models genuine inquiry",
        "depth_advanced": "Aquinas and the Islamic philosophers — how Averroes shaped Christian metaphysics",
        "narrative": "<h3>The Portrait</h3><p>The Dominican theologian whose synthesis of Aristotelian philosophy and Christian theology became the intellectual infrastructure of medieval Europe — and whose disputed relationship to alchemy produced a body of pseudo-Aquinian alchemical texts that circulated for centuries. His conversations in the database position him at the intersection of scholastic philosophy and alchemical tradition.</p><h3>What Emerged</h3><p>Aquinas was engaged primarily through the major alchemical surveys: the Medieval Magic reading traces how alchemical texts were attributed to Aquinas to lend them scholastic authority, while the Atalanta Fugiens and Laboratories of Art readings contextualize the pseudo-Aquinian tradition within the broader history of alchemical pseudepigraphy. The Platonic prayer analysis also traces Aquinas’s natural theology as a counterpoint to Neoplatonic theurgy.</p><h3>Why It Matters</h3><p>Aquinas represents the institutional mainstream against which the esoteric traditions in this database defined themselves. Understanding what scholastic philosophy accepted and rejected about alchemy is essential context for the entire collection.</p>", "timeline_entries": [{"date": "2024-10-17", "title": "Wilson on Lit Phil Magick", "description": "In *Robert Anton Wilson Explains Everything*, Robert Anton Wilson shares his views on literature, philosophy, and magick, touching on several key ideas: 1.", "conversation_id": 619}, {"date": "2024-11-07", "title": "James Crowley Wilson Influence", "description": "### Study Outline: The Influence of William James and Pragmatism on Aleister Crowley's Magick and Robert Anton Wilson's Reception and Development of the Concept #### **1.", "conversation_id": 432}, {"date": "2026-01-13", "title": "2026-01-13_Wilson-Campaign-Takeaways", "description": "27 pages of exploration via llm_logs_pdf.", "conversation_id": 2260}, {"date": "2026-01-13", "title": "Wilson Campaign Takeaways", "description": "Here’s what Jacobin (and a few other outlets) say Katie Wilson’s campaign operation learned, plus concrete takeaways you can lift for campaigns in the Mamdani lane.", "conversation_id": 3192}, {"date": "2026-01-15", "title": "2026-01-15_Game-Design-for-Wilson's-Doctrine", "description": "USER Have a narrative designer and a historian of ideas discuss ways to create an educational game inspired by a religious studies approach to Robert Anton Wilson boiling down the ...", "conversation_id": 2302}, {"date": "2026-01-15", "title": "Game Design for Wilson's Doctrine", "description": "Below is a staged conversation between a Narrative Designer and a Historian of Ideas brainstorming an educational game inspired by a religious-studies reading of Robert Anton Wilso...", "conversation_id": 3201}], "quotes": [], "images": [{"url": "/static/art/aquinas-portrait.jpg", "caption": "Thomas Aquinas — detail from the Demidoff Altarpiece by Carlo Crivelli (1476)"}],
        "color": "#6d4c41",
    },
    "gershom-scholem": {
        "slug": "gershom-scholem",
        "title": "Gershom Scholem",
        "hook": "The man who made Jewish mysticism academically respectable — and politically dangerous.",
        "field": "Kabbalah, Jewish mysticism",
        "era": "20th century scholar",
        "conversation_ids": [667, 138],
        "tags": ["kabbalah", "scholarship", "mysticism"],
        "pedagogy": "How recovering a suppressed tradition reshapes the culture it belongs to. Scholem's lifework recovering Kabbalah from the dustbin of 'superstition' didn't just create an academic field — it changed Jewish self-understanding and fed directly into Israeli cultural politics.",
        "depth_introductory": "Major Trends in Jewish Mysticism — Scholem's masterwork and its argument",
        "depth_intermediate": "The Sabbatian heresy — how Scholem's account of Sabbatai Zevi rewrote Jewish history",
        "depth_advanced": "Scholem and Benjamin — the mystical-materialist friendship that shaped both thinkers",
        "narrative": "<h3>The Portrait</h3><p>The founder of the modern academic study of Jewish mysticism, whose work on Kabbalah transformed it from an obscure sectarian tradition into a major field of religious studies. Two conversations across 416 pages engage with Scholem’s legacy through Hanegraaff’s scholarly framework.</p><h3>What Emerged</h3><p>Scholem was encountered through the 228-page Hermetic Spirituality reading and the 188-page Hanegraaff articles analysis, both of which position his work on Kabbalah as a parallel project to the academic study of Hermeticism. Hanegraaff traces how Scholem’s method — taking mystical texts seriously as intellectual documents rather than dismissing them as superstition — created the template for the entire field of Western esotericism studies.</p><h3>Why It Matters</h3><p>Scholem’s methodological breakthrough — treating marginal traditions with the same scholarly rigor applied to mainstream theology — is the intellectual foundation for every conversation in the database that takes alchemy, magic, or mysticism seriously as objects of study.</p>", "timeline_entries": [{"date": "2024-09-22", "title": "Hermetic Spirituality Hanegraaff", "description": "Please provide me with the link or upload the book you'd like me to summarize, and I'll be happy to provide the detailed breakdown you're looking for.", "conversation_id": 667}, {"date": "2024-12-18", "title": "Hanegraaff articles Taves/Yates", "description": "188 pages of exploration via chatgpt.", "conversation_id": 138}], "quotes": [{"text": "Let me know if you'd like further refinements!", "role": "assistant", "conversation_title": "Hanegraaff articles Taves/Yates", "conversation_id": 138}], "images": [{"url": "/static/art/tree-of-life.jpg", "caption": "The Kabbalistic Tree of Life — medieval manuscript illustration"}],
        "color": "#1a237e",
    },
}

# Projects catalog — 33 dev projects across C:\Dev and C:\OldDevProjects.
# domain: scholarship | games | tools | music | education
# files: approximate file count; has_git: version control status
# conversation_ids: Claude/ChatGPT conversations that shaped the project
PROJECTS = [
    {"name": "MarxistTradition", "domain": "scholarship", "framework": "Node.js/Express", "files": 621, "has_git": True, "description": "Marxist intellectual tradition with multi-tendency perspectives", "conversation_ids": [702, 157, 2646, 809]},
    {"name": "capital_interpreter", "domain": "scholarship", "framework": "Python", "files": 129, "has_git": True, "description": "RAG system for interpreting Marx's Capital with LLM assistance", "conversation_ids": [702, 476, 283]},
    {"name": "MTGDraftOverlay", "domain": "games", "framework": "Electron/React", "files": 205, "has_git": True, "description": "Real-time MTG draft overlay with card ratings and pick suggestions", "conversation_ids": [382, 2947, 2693, 570]},
    {"name": "TreeTapper", "domain": "games", "framework": "Python/Flask", "files": 87, "has_git": True, "description": "Kabbalistic Tree of Life interactive adventure game", "conversation_ids": [843, 778, 2652]},
    {"name": "AlchemyDB", "domain": "scholarship", "framework": "Python/SQLite", "files": 45, "has_git": False, "description": "Structured database of alchemical terms, processes, and scholars", "conversation_ids": [712, 670, 726, 673]},
    {"name": "alchemy_scryfall", "domain": "games", "framework": "Python", "files": 32, "has_git": True, "description": "MTG card catalog themed around historical alchemy imagery", "conversation_ids": [9, 5]},
    {"name": "VoxFugiens", "domain": "tools", "framework": "Python", "files": 18, "has_git": False, "description": "Voice notes transcription and organization tool", "conversation_ids": []},
    {"name": "draft-academy", "domain": "education", "framework": "React", "files": 156, "has_git": True, "description": "MTG draft training platform with curated exercises", "conversation_ids": []},
    {"name": "esoteric-beat-site", "domain": "scholarship", "framework": "Hugo", "files": 43, "has_git": True, "description": "Blog exploring connections between esotericism and beat culture", "conversation_ids": []},
    {"name": "megabase", "domain": "tools", "framework": "Python/Flask", "files": 48, "has_git": True, "description": "Personal Knowledge Archaeology System — the project IS the database", "conversation_ids": []},
    {"name": "MarxistPortal", "domain": "scholarship", "framework": "React", "files": 312, "has_git": True, "description": "Web portal for Marxist scholarship with reading lists and analysis tools", "conversation_ids": [702, 157]},
    {"name": "PKDExegesis", "domain": "scholarship", "framework": "Python", "files": 67, "has_git": True, "description": "Analysis tools for Philip K. Dick's Exegesis and related texts", "conversation_ids": [628, 700, 701]},
    {"name": "sigil-generator", "domain": "tools", "framework": "Python/SVG", "files": 24, "has_git": False, "description": "Generative sigil art from intention statements using letter-elimination method", "conversation_ids": [697, 631]},
    {"name": "geomancy-calc", "domain": "tools", "framework": "Python", "files": 15, "has_git": False, "description": "Geomantic divination calculator with figure interpretation", "conversation_ids": [649]},
    {"name": "game-ideas-tracker", "domain": "games", "framework": "Python/Flask", "files": 28, "has_git": False, "description": "Catalog and development tracker for game concepts", "conversation_ids": []},
    {"name": "chiptune-synth", "domain": "music", "framework": "Python/pygame", "files": 34, "has_git": True, "description": "8-bit synthesizer with programmable waveforms and sequencer", "conversation_ids": [577, 579]},
    {"name": "ok-computer-analysis", "domain": "music", "framework": "Python", "files": 19, "has_git": False, "description": "Harmonic analysis of Radiohead's OK Computer track by track", "conversation_ids": [753]},
    {"name": "midi-tools", "domain": "music", "framework": "Python", "files": 22, "has_git": True, "description": "MIDI file manipulation, transposition, and visualization tools", "conversation_ids": [251, 252]},
    {"name": "tarot-engine", "domain": "tools", "framework": "Python", "files": 41, "has_git": True, "description": "Tarot reading engine with Golden Dawn correspondences and Celtic Cross spread", "conversation_ids": [399, 180]},
    {"name": "sms-archaeology", "domain": "tools", "framework": "Python/SQLite", "files": 56, "has_git": True, "description": "SMS message analysis with sentiment, entity extraction, and timeline visualization", "conversation_ids": []},
    {"name": "twitter-archive", "domain": "tools", "framework": "Python/SQLite", "files": 38, "has_git": True, "description": "Twitter archive analysis with topic modeling and engagement metrics", "conversation_ids": []},
    {"name": "claude-data-tools", "domain": "tools", "framework": "Python", "files": 42, "has_git": True, "description": "Claude conversation data extraction and analysis pipeline", "conversation_ids": []},
    {"name": "fungus-adventure", "domain": "games", "framework": "Python/Ren'Py", "files": 73, "has_git": False, "description": "Microscopic fungus text adventure exploring mycelial networks", "conversation_ids": [554]},
    {"name": "bubble-prototype", "domain": "games", "framework": "Python/Pygame", "files": 31, "has_git": False, "description": "Bubble Bog Witch platformer prototype with transmutation mechanics", "conversation_ids": [40, 239]},
    {"name": "autobattler-proto", "domain": "games", "framework": "Python", "files": 44, "has_git": False, "description": "Dungeon autobattler prototype with draft-based army composition", "conversation_ids": [4, 10]},
    {"name": "alchemy-board-game", "domain": "games", "framework": "Tabletop Simulator", "files": 16, "has_git": False, "description": "Alchemical transmutation chain board game with engine-building mechanics", "conversation_ids": [567, 851]},
    {"name": "pico-reader", "domain": "scholarship", "framework": "Python", "files": 29, "has_git": True, "description": "Reader tool for Pico della Mirandola's 900 Theses with cross-references", "conversation_ids": [666, 525]},
    {"name": "golden-dawn-curriculum", "domain": "education", "framework": "Markdown/Hugo", "files": 88, "has_git": True, "description": "Structured curriculum for studying the Golden Dawn grade system", "conversation_ids": [1862, 399]},
    {"name": "memory-palace", "domain": "education", "framework": "React/Three.js", "files": 134, "has_git": True, "description": "3D memory palace builder inspired by Giordano Bruno's memory techniques", "conversation_ids": [731, 1921]},
    {"name": "daw-automation", "domain": "music", "framework": "Python/MIDI", "files": 27, "has_git": False, "description": "DAW automation scripts for Ableton Live parameter control", "conversation_ids": [757]},
    {"name": "Overlay", "domain": "games", "framework": "Electron", "files": 189, "has_git": True, "description": "General-purpose game overlay framework (evolved into MTGDraftOverlay)", "conversation_ids": [570, 636]},
    {"name": "kabbalah-tree-viz", "domain": "tools", "framework": "D3.js/SVG", "files": 21, "has_git": False, "description": "Interactive Tree of Life visualization with sephirotic correspondences", "conversation_ids": [843]},
    {"name": "hermetic-reading-list", "domain": "scholarship", "framework": "Python/Markdown", "files": 14, "has_git": True, "description": "Curated reading list generator for Hermetic and esoteric texts", "conversation_ids": [667, 138]},
]

# Special showcases — lavishly illustrated flagship pages with unique templates.
SPECIAL_SHOWCASES = {
    "algorithms-in-wonderland": {
        "slug": "algorithms-in-wonderland",
        "title": "Algorithms in Wonderland",
        "subtitle": "Computer science as a descent into strange rules, recursive logic, unstable systems, and nonsense that turns out to be precise.",
        "hook": "What if the best introduction to computer science was already written in 1865 — by a mathematician who disguised it as a children's book?",
        "conversation_ids": [585, 639, 573, 610, 560, 459, 556, 2557],
        "tags": ["coding", "educational", "game_idea", "philosophy"],
        "color": "#e8a838",
        "template": "wonderland.html",
    },
    "injecting-custom-logic": {
        "slug": "injecting-custom-logic",
        "title": "Injecting Custom Logic",
        "subtitle": "Every non-trivial system has a seam where users need to inject their own rules. This showcase maps every pattern.",
        "hook": "Hooks, middleware, plugins, parsers, pipelines, callbacks, decorators, event buses — the engineering of extensibility.",
        "conversation_ids": [570, 636, 631, 500, 703, 710, 711, 578, 679, 270, 75, 32, 14, 28, 252, 2521],
        "tags": ["coding", "game_idea", "educational"],
        "color": "#00bcd4",
        "template": "custom_logic.html",
    },
    "50-takeaways": {
        "slug": "50-takeaways",
        "title": "50 Takeaways from Working with LLMs",
        "subtitle": "What 4,308 conversations and 2 years of daily AI collaboration actually taught me.",
        "hook": "The meta-lessons from building a 130,000-page personal knowledge system with large language models.",
        "conversation_ids": [570, 559, 636, 632, 571, 565, 3268, 339, 523, 653, 3259, 500, 703, 631],
        "tags": ["coding", "educational", "philosophy"],
        "color": "#ff9800",
        "template": "takeaways.html",
    },
}

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db()
    q = request.args.get("q", "").strip()
    source = request.args.get("source", "")
    tag = request.args.get("tag", "")
    sort = request.args.get("sort", "pages")
    page = int(request.args.get("page", 1))
    per_page = 48

    # Build query
    conditions = []
    params = []

    if q:
        # FTS search — sanitize input to prevent FTS5 syntax errors
        # Strip all non-alphanumeric chars (except spaces/apostrophes), then quote each word
        clean = "".join(c if c.isalnum() or c.isspace() or c == "'" else " " for c in q)
        words = [w for w in clean.split() if w and w.upper() not in ("AND", "OR", "NOT", "NEAR")]
        sanitized_q = " ".join(f'"{w}"' for w in words)
        if sanitized_q:
            conditions.append("""c.id IN (
                SELECT m.conversation_id FROM messages m
                JOIN messages_fts ON messages_fts.rowid=m.id
                WHERE messages_fts MATCH ?
            )""")
            params.append(sanitized_q)

    if source:
        conditions.append("s.name = ?")
        params.append(source)

    if tag:
        conditions.append("""c.id IN (
            SELECT ct.conversation_id FROM conversation_tags ct
            JOIN tags t ON t.id=ct.tag_id WHERE t.name=?
        )""")
        params.append(tag)

    where = " AND ".join(conditions) if conditions else "1=1"

    sort_map = {
        "pages": "c.estimated_pages DESC",
        "date": "c.created_at DESC",
        "messages": "c.message_count DESC",
        "title": "c.title ASC",
    }
    order = sort_map.get(sort, "c.estimated_pages DESC")

    total = conn.execute(f"""
        SELECT count(*) FROM conversations c JOIN sources s ON s.id=c.source_id WHERE {where}
    """, params).fetchone()[0]

    convos = conn.execute(f"""
        SELECT c.id, c.title, c.summary, c.created_at, c.estimated_pages, c.message_count,
               s.name as source_name
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE {where}
        ORDER BY {order}
        LIMIT ? OFFSET ?
    """, params + [per_page, (page - 1) * per_page]).fetchall()

    # Get tags for each conversation
    conv_ids = [c["id"] for c in convos]
    conv_tags = {}
    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        tag_rows = conn.execute(f"""
            SELECT ct.conversation_id, t.name
            FROM conversation_tags ct JOIN tags t ON t.id=ct.tag_id
            WHERE ct.conversation_id IN ({ph})
        """, conv_ids).fetchall()
        for tr in tag_rows:
            conv_tags.setdefault(tr["conversation_id"], []).append(tr["name"])

    # Get available sources and tags for filters
    sources = conn.execute("SELECT DISTINCT name FROM sources ORDER BY name").fetchall()
    tags = conn.execute("""
        SELECT t.name, count(*) as cnt FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        GROUP BY t.name ORDER BY cnt DESC
    """).fetchall()

    total_pages = (total + per_page - 1) // per_page

    conn.close()
    return render_template("index.html",
        convos=convos, conv_tags=conv_tags,
        sources=sources, tags=tags,
        q=q, source=source, tag=tag, sort=sort,
        page=page, total_pages=total_pages, total=total)


@app.route("/conversation/<int:conv_id>")
def conversation(conv_id):
    conn = get_db()

    conv = conn.execute("""
        SELECT c.*, s.name as source_name
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.id=?
    """, (conv_id,)).fetchone()

    if not conv:
        return "Not found", 404

    # Get messages with pagination
    msg_page = int(request.args.get("msg_page", 1))
    msgs_per_page = 50
    total_msgs = conv["message_count"] or 0

    messages = conn.execute("""
        SELECT role, content, created_at, sentiment_vader, sentiment_label, char_count
        FROM messages WHERE conversation_id=?
        ORDER BY id
        LIMIT ? OFFSET ?
    """, (conv_id, msgs_per_page, (msg_page - 1) * msgs_per_page)).fetchall()

    # Get tags
    tags = conn.execute("""
        SELECT t.name, ct.confidence, ct.method
        FROM conversation_tags ct JOIN tags t ON t.id=ct.tag_id
        WHERE ct.conversation_id=?
    """, (conv_id,)).fetchall()

    # Get ideas
    ideas = conn.execute("SELECT * FROM ideas WHERE conversation_id=?", (conv_id,)).fetchall()

    total_msg_pages = (total_msgs + msgs_per_page - 1) // msgs_per_page

    conn.close()
    return render_template("conversation.html",
        conv=conv, messages=messages, tags=tags, ideas=ideas,
        msg_page=msg_page, total_msg_pages=total_msg_pages)


@app.route("/ideas")
def ideas():
    conn = get_db()
    category = request.args.get("category", "")
    maturity = request.args.get("maturity", "")
    view = request.args.get("view", "grid")
    sort = request.args.get("sort", "name")

    conditions = []
    params = []
    if category:
        conditions.append("i.category = ?")
        params.append(category)
    if maturity:
        conditions.append("i.maturity = ?")
        params.append(maturity)

    where = " AND ".join(conditions) if conditions else "1=1"

    sort_map = {
        "name": "i.name ASC",
        "pages": "c.estimated_pages DESC",
        "maturity": "CASE i.maturity WHEN 'built' THEN 0 WHEN 'prototype' THEN 1 WHEN 'design' THEN 2 ELSE 3 END, i.name",
        "date": "i.created_at DESC",
    }
    order = sort_map.get(sort, "i.name ASC")

    rows = conn.execute(f"""
        SELECT i.*, c.title as conv_title, c.estimated_pages, s.name as source_name
        FROM ideas i
        JOIN conversations c ON c.id=i.conversation_id
        JOIN sources s ON s.id=c.source_id
        WHERE {where}
        ORDER BY {order}
    """, params).fetchall()

    categories = conn.execute("SELECT DISTINCT category FROM ideas ORDER BY category").fetchall()
    maturities = conn.execute("SELECT DISTINCT maturity FROM ideas ORDER BY maturity").fetchall()

    cat_counts = conn.execute(
        "SELECT category, count(*) as cnt FROM ideas GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    mat_counts = conn.execute(
        "SELECT maturity, count(*) as cnt FROM ideas GROUP BY maturity ORDER BY cnt DESC"
    ).fetchall()

    conn.close()
    return render_template("ideas.html",
        ideas=rows, categories=categories, maturities=maturities,
        cat_counts={r["category"]: r["cnt"] for r in cat_counts},
        mat_counts={r["maturity"]: r["cnt"] for r in mat_counts},
        category=category, maturity=maturity, view=view, sort=sort)


@app.route("/viz")
def viz():
    conn = get_db()

    # 1. Intellectual Timeline — conversations by month and source
    timeline = conn.execute("""
        SELECT substr(c.created_at,1,7) as month, s.name as source,
               count(*) as cnt, sum(c.estimated_pages) as pages
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.created_at IS NOT NULL AND c.created_at > '2007-12'
        GROUP BY month, source ORDER BY month
    """).fetchall()

    # 2. Topic Constellation — tag co-occurrence
    cooccurrence = conn.execute("""
        SELECT t1.name as tag1, t2.name as tag2, count(*) as cnt
        FROM conversation_tags ct1
        JOIN conversation_tags ct2 ON ct1.conversation_id=ct2.conversation_id AND ct1.tag_id < ct2.tag_id
        JOIN tags t1 ON t1.id=ct1.tag_id
        JOIN tags t2 ON t2.id=ct2.tag_id
        GROUP BY t1.name, t2.name ORDER BY cnt DESC
    """).fetchall()

    # Tag totals for node sizing
    tag_totals = conn.execute("""
        SELECT t.name, count(*) as cnt FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        GROUP BY t.name ORDER BY cnt DESC
    """).fetchall()

    # 3. Activity Heatmap — messages per week
    heatmap = conn.execute("""
        SELECT substr(c.created_at,1,10) as day, s.name as source, count(*) as cnt
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.created_at IS NOT NULL AND c.created_at >= '2024-01-01'
        GROUP BY day, source ORDER BY day
    """).fetchall()

    # 4. Idea Funnel — by category and maturity
    idea_funnel = conn.execute("""
        SELECT category, maturity, count(*) as cnt
        FROM ideas GROUP BY category, maturity ORDER BY category
    """).fetchall()

    # 5. Sentiment River — monthly sentiment by source
    sentiment = conn.execute("""
        SELECT substr(m.created_at,1,7) as month, s.name as source,
               round(avg(m.sentiment_vader),3) as avg_sent,
               count(*) as cnt,
               sum(CASE WHEN m.sentiment_label='positive' THEN 1 ELSE 0 END) as pos,
               sum(CASE WHEN m.sentiment_label='negative' THEN 1 ELSE 0 END) as neg,
               sum(CASE WHEN m.sentiment_label='neutral' THEN 1 ELSE 0 END) as neu
        FROM messages m
        JOIN conversations c ON c.id=m.conversation_id
        JOIN sources s ON s.id=c.source_id
        WHERE m.created_at IS NOT NULL AND m.sentiment_vader IS NOT NULL
              AND m.created_at >= '2024-01-01'
        GROUP BY month, source ORDER BY month
    """).fetchall()

    # 6. Treemap — conversation sizes by source
    treemap = conn.execute("""
        SELECT s.name as source, count(*) as convos,
               sum(c.estimated_pages) as total_pages,
               sum(c.message_count) as total_msgs,
               round(sum(c.char_count)/1e6, 1) as text_mb
        FROM conversations c JOIN sources s ON s.id=c.source_id
        GROUP BY s.name ORDER BY total_pages DESC
    """).fetchall()

    # Top conversations for treemap detail
    top_convos = conn.execute("""
        SELECT c.title, c.estimated_pages, s.name as source
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.estimated_pages > 50
        ORDER BY c.estimated_pages DESC LIMIT 60
    """).fetchall()

    # 7. Sparkline Table — per-tag stats with monthly trends
    sparkline_tags = conn.execute("""
        SELECT t.name,
               count(DISTINCT ct.conversation_id) as convos,
               (SELECT count(*) FROM ideas i
                JOIN conversation_tags ct2 ON ct2.conversation_id=i.conversation_id
                WHERE ct2.tag_id=t.id) as ideas,
               (SELECT round(avg(m2.sentiment_vader),3) FROM messages m2
                JOIN conversations c2 ON c2.id=m2.conversation_id
                JOIN conversation_tags ct3 ON ct3.conversation_id=c2.id
                WHERE ct3.tag_id=t.id AND m2.sentiment_vader IS NOT NULL) as avg_sent,
               (SELECT round(avg(c3.estimated_pages),1) FROM conversations c3
                JOIN conversation_tags ct4 ON ct4.conversation_id=c3.id
                WHERE ct4.tag_id=t.id) as avg_pages
        FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        GROUP BY t.name ORDER BY convos DESC
    """).fetchall()

    # Monthly trend per tag (for sparklines)
    tag_trends = conn.execute("""
        SELECT t.name, substr(c.created_at,1,7) as month, count(*) as cnt
        FROM conversation_tags ct
        JOIN tags t ON t.id=ct.tag_id
        JOIN conversations c ON c.id=ct.conversation_id
        WHERE c.created_at IS NOT NULL AND c.created_at >= '2024-06-01'
        GROUP BY t.name, month ORDER BY t.name, month
    """).fetchall()

    conn.close()
    return render_template("viz.html",
        timeline=[dict(r) for r in timeline],
        cooccurrence=[dict(r) for r in cooccurrence],
        tag_totals=[dict(r) for r in tag_totals],
        heatmap=[dict(r) for r in heatmap],
        idea_funnel=[dict(r) for r in idea_funnel],
        sentiment=[dict(r) for r in sentiment],
        treemap=[dict(r) for r in treemap],
        top_convos=[dict(r) for r in top_convos],
        sparkline_tags=[dict(r) for r in sparkline_tags],
        tag_trends=[dict(r) for r in tag_trends])


@app.route("/values")
def values():
    """Scholarly and engineering values with evidence from the database."""
    conn = get_db()

    # Topic prevalence with user-only sentiment (scholarly passion indicator)
    topic_stats = conn.execute("""
        SELECT t.name,
               count(DISTINCT ct.conversation_id) as convos,
               round(sum(c.estimated_pages), 0) as total_pages,
               round(avg(c.estimated_pages), 1) as avg_pages,
               (SELECT round(avg(m2.sentiment_vader), 3) FROM messages m2
                JOIN conversations c2 ON c2.id=m2.conversation_id
                JOIN conversation_tags ct2 ON ct2.conversation_id=c2.id
                WHERE ct2.tag_id=t.id AND m2.role='user'
                AND m2.sentiment_vader IS NOT NULL) as user_sentiment,
               (SELECT count(DISTINCT i.id) FROM ideas i
                JOIN conversation_tags ct3 ON ct3.conversation_id=i.conversation_id
                WHERE ct3.tag_id=t.id) as idea_count
        FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        JOIN conversations c ON c.id=ct.conversation_id
        GROUP BY t.name
        HAVING convos >= 5
        ORDER BY convos DESC
    """).fetchall()

    # Idea maturity funnel
    maturity_funnel = conn.execute("""
        SELECT category, maturity, count(*) as cnt
        FROM ideas GROUP BY category, maturity ORDER BY category, maturity
    """).fetchall()

    # Top conversations per tag (for "more details" rabbit holes)
    tag_top_convos = {}
    for row in topic_stats[:15]:
        tag_name = row["name"]
        top = conn.execute("""
            SELECT c.id, c.title, c.estimated_pages, s.name as source_name
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=?
            ORDER BY c.estimated_pages DESC LIMIT 5
        """, (tag_name,)).fetchall()
        tag_top_convos[tag_name] = [dict(r) for r in top]

    # Monthly activity per tag (engagement over time)
    tag_monthly = conn.execute("""
        SELECT t.name, substr(c.created_at,1,7) as month, count(*) as cnt
        FROM conversation_tags ct
        JOIN tags t ON t.id=ct.tag_id
        JOIN conversations c ON c.id=ct.conversation_id
        WHERE c.created_at IS NOT NULL AND c.created_at >= '2024-01-01'
        GROUP BY t.name, month ORDER BY t.name, month
    """).fetchall()

    conn.close()
    return render_template("values.html",
        topic_stats=[dict(r) for r in topic_stats],
        maturity_funnel=[dict(r) for r in maturity_funnel],
        tag_top_convos=tag_top_convos,
        tag_monthly=[dict(r) for r in tag_monthly])


@app.route("/showcases")
def showcases_index():
    """List all showcase dream pages — games, special showcases, and collections."""
    return render_template(
        "showcases.html",
        showcases=list(SHOWCASES.values()),
        specials=list(SPECIAL_SHOWCASES.values()),
        collections=list(COLLECTIONS.values()),
    )


@app.route("/dream/<slug>")
def showcase(slug):
    """Tabbed showcase page for a curated dream."""
    sc = SHOWCASES.get(slug)
    if not sc:
        return "Not found", 404

    conn = get_db()

    # Fetch the linked conversations
    conv_ids = sc["conversation_ids"]
    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        conversations = conn.execute(f"""
            SELECT c.id, c.title, c.estimated_pages, c.message_count,
                   c.created_at, s.name as source_name
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
        """, conv_ids).fetchall()
    else:
        conversations = []

    total_pages = sum(c["estimated_pages"] or 0 for c in conversations)

    # Load any JSON sidecar data (narrative, quotes, timeline) if it exists
    sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "showcases", f"{slug}.json")
    sidecar = {}
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                sidecar = json.load(f)
        except (json.JSONDecodeError, IOError):
            sidecar = {}

    # Merge sidecar into showcase data (sidecar overrides defaults)
    narrative = sidecar.get("narrative") or sc.get("narrative")
    timeline_entries = sidecar.get("timeline_entries") or sc.get("timeline_entries", [])
    quotes = sidecar.get("quotes") or sc.get("quotes", [])
    images = sidecar.get("images") or sc.get("images", [])

    conn.close()
    return render_template("showcase.html",
        showcase=sc,
        narrative=narrative,
        conversations=[dict(c) for c in conversations],
        total_pages=int(total_pages),
        tags=sc.get("tags", []),
        timeline_entries=timeline_entries,
        quotes=quotes,
        images=images)


@app.route("/collections")
def collections_index():
    """List all curated collections — thematic rabbit holes."""
    return render_template("collections.html", collections=list(COLLECTIONS.values()))


@app.route("/collection/<slug>")
def collection(slug):
    """Collection detail page — themed conversation grouping with rabbit hole design."""
    col = COLLECTIONS.get(slug)
    if not col:
        return "Not found", 404

    conn = get_db()
    conv_ids = col["conversation_ids"]
    conversations = []
    total_pages = 0
    total_messages = 0
    date_range = ("", "")
    tag_counts = {}

    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        conversations = conn.execute(f"""
            SELECT c.id, c.title, c.summary, c.estimated_pages, c.message_count,
                   c.created_at, c.char_count, s.name as source_name
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
        """, conv_ids).fetchall()
        conversations = [dict(c) for c in conversations]
        total_pages = sum(c["estimated_pages"] or 0 for c in conversations)
        total_messages = sum(c["message_count"] or 0 for c in conversations)
        dates = sorted(c["created_at"] or "" for c in conversations if c.get("created_at"))
        if dates:
            date_range = (dates[0][:10], dates[-1][:10])

        # Get tags for these conversations
        tag_rows = conn.execute(f"""
            SELECT t.name, count(*) as cnt
            FROM conversation_tags ct JOIN tags t ON t.id=ct.tag_id
            WHERE ct.conversation_id IN ({ph})
            GROUP BY t.name ORDER BY cnt DESC
        """, conv_ids).fetchall()
        tag_counts = {r["name"]: r["cnt"] for r in tag_rows}

        # Get sentiment stats per conversation (user messages only)
        for c in conversations:
            sent = conn.execute("""
                SELECT round(avg(sentiment_vader), 3) as avg_sent,
                       count(*) as msg_count
                FROM messages WHERE conversation_id=? AND role='user'
                AND sentiment_vader IS NOT NULL
            """, (c["id"],)).fetchone()
            c["user_sentiment"] = sent["avg_sent"] if sent else None

    # Find adjacent collections (those sharing conversation IDs)
    adjacent = []
    my_ids = set(conv_ids)
    for other_slug, other in COLLECTIONS.items():
        if other_slug == slug:
            continue
        overlap = my_ids & set(other["conversation_ids"])
        if overlap:
            adjacent.append({"slug": other_slug, "title": other["title"],
                             "color": other.get("color", "#7c6fe0"),
                             "overlap": len(overlap)})
    adjacent.sort(key=lambda x: x["overlap"], reverse=True)

    conn.close()
    return render_template("collection.html",
        collection=col,
        conversations=conversations,
        total_pages=int(total_pages),
        total_messages=total_messages,
        date_range=date_range,
        tag_counts=tag_counts,
        adjacent=adjacent)


@app.route("/wonderland/<slug>")
def wonderland(slug):
    """Special lavishly illustrated showcase page."""
    sc = SPECIAL_SHOWCASES.get(slug)
    if not sc:
        return "Not found", 404

    conn = get_db()
    conv_ids = sc["conversation_ids"]
    conversations = []
    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        conversations = conn.execute(f"""
            SELECT c.id, c.title, c.estimated_pages, c.message_count,
                   c.created_at, c.summary, s.name as source_name
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
        """, conv_ids).fetchall()

    total_pages = sum(c["estimated_pages"] or 0 for c in conversations)
    total_messages = sum(c["message_count"] or 0 for c in conversations)

    conn.close()
    return render_template(sc["template"],
        showcase=sc,
        conversations=[dict(c) for c in conversations],
        total_pages=int(total_pages),
        total_messages=total_messages)


@app.route("/scholars")
def scholars_index():
    """List all scholar showcase pages — curated intellectual portraits."""
    scholars = sorted(SCHOLARS.values(), key=lambda s: s["title"])
    # Group by era for display
    eras = {}
    for s in scholars:
        era = s.get("era", "Unknown")
        eras.setdefault(era, []).append(s)
    return render_template("scholars.html", scholars=scholars, eras=eras)


@app.route("/scholar/<slug>")
def scholar(slug):
    """Tabbed scholar showcase page — 5-tab deep dive into a thinker."""
    sc = SCHOLARS.get(slug)
    if not sc:
        return "Not found", 404

    conn = get_db()

    # Fetch linked conversations
    conv_ids = sc["conversation_ids"]
    conversations = []
    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        conversations = conn.execute(f"""
            SELECT c.id, c.title, c.estimated_pages, c.message_count,
                   c.created_at, c.summary, s.name as source_name
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
        """, conv_ids).fetchall()

    total_pages = sum(c["estimated_pages"] or 0 for c in conversations)

    # Load sidecar data if it exists
    sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "scholars", f"{slug}.json")
    sidecar = {}
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, "r", encoding="utf-8") as f:
                sidecar = json.load(f)
        except (json.JSONDecodeError, IOError):
            sidecar = {}

    narrative = sidecar.get("narrative") or sc.get("narrative")
    timeline_entries = sidecar.get("timeline_entries") or sc.get("timeline_entries", [])
    quotes = sidecar.get("quotes") or sc.get("quotes", [])
    images = sidecar.get("images") or sc.get("images", [])

    # Find related scholars (those sharing conversation IDs)
    related = []
    my_ids = set(conv_ids)
    for other_slug, other in SCHOLARS.items():
        if other_slug == slug:
            continue
        overlap = my_ids & set(other["conversation_ids"])
        if overlap:
            related.append({"slug": other_slug, "title": other["title"],
                            "field": other.get("field", ""),
                            "color": other.get("color", "#7c6fe0"),
                            "overlap": len(overlap)})
    related.sort(key=lambda x: x["overlap"], reverse=True)

    # Find related collections
    related_collections = []
    for col_slug, col in COLLECTIONS.items():
        overlap = my_ids & set(col["conversation_ids"])
        if overlap:
            related_collections.append({"slug": col_slug, "title": col["title"],
                                        "color": col.get("color", "#7c6fe0"),
                                        "overlap": len(overlap)})
    related_collections.sort(key=lambda x: x["overlap"], reverse=True)

    conn.close()
    return render_template("scholar.html",
        scholar=sc,
        narrative=narrative,
        conversations=[dict(c) for c in conversations],
        total_pages=int(total_pages),
        tags=sc.get("tags", []),
        timeline_entries=timeline_entries,
        quotes=quotes,
        images=images,
        related=related[:8],
        related_collections=related_collections[:5])


@app.route("/projects")
def projects():
    """Static project visualization — Tufte-inspired small multiples across all 33 dev projects."""
    # Compute summary statistics
    total_files = sum(p["files"] for p in PROJECTS)
    git_count = sum(1 for p in PROJECTS if p["has_git"])
    no_git_count = len(PROJECTS) - git_count
    total_convos = sum(len(p["conversation_ids"]) for p in PROJECTS)

    # Group by domain
    domains = {}
    for p in PROJECTS:
        domains.setdefault(p["domain"], []).append(p)
    # Sort each domain's projects by file count descending
    for d in domains:
        domains[d].sort(key=lambda x: x["files"], reverse=True)

    # Domain order for display
    domain_order = ["scholarship", "games", "tools", "music", "education"]
    ordered_domains = [(d, domains[d]) for d in domain_order if d in domains]

    # Per-domain stats
    domain_stats = {}
    for d, projs in domains.items():
        domain_stats[d] = {
            "count": len(projs),
            "files": sum(p["files"] for p in projs),
            "git": sum(1 for p in projs if p["has_git"]),
        }

    return render_template(
        "projects.html",
        projects=PROJECTS,
        ordered_domains=ordered_domains,
        domain_stats=domain_stats,
        total_files=total_files,
        git_count=git_count,
        no_git_count=no_git_count,
        total_convos=total_convos,
    )


@app.route("/action-map")
def action_map():
    """Interactive action map — next steps for Dreambase development."""
    return render_template("action_map.html")


@app.route("/api/search")
def api_search():
    """Quick search API for autocomplete."""
    conn = get_db()
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])

    rows = conn.execute("""
        SELECT c.id, c.title, s.name as source, c.estimated_pages
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.title LIKE ?
        ORDER BY c.estimated_pages DESC LIMIT 20
    """, (f"%{q}%",)).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=True, port=5555)
