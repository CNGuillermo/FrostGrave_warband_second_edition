#!/usr/bin/env python3
"""
Frostgrave 2ª Edición — Constructor de Warband
Basado en las reglas de Joseph A. McCullough (Osprey Games, 2020)
"""

import json
import os

# Siempre guardar en la misma carpeta que el .py, sin importar desde dónde se ejecute
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
#  DATOS DEL JUEGO
# ─────────────────────────────────────────────

WIZARD_TYPES = [
    "Chronomancer",
    "Elementalist",
    "Enchanter",
    "Illusionist",
    "Necromancer",
    "Sigilist",
    "Soothsayer",
    "Summoner",
    "Thaumaturge",
    "Witch",
]

# Relaciones entre escuelas: +0 propia, +2 alineada, +4 neutral, +6 opuesta
# (nunca se puede elegir la opuesta al inicio)
SCHOOL_RELATIONS = {
    "Chronomancer": {
        "own":      ["Chronomancer"],
        "aligned":  ["Elementalist", "Necromancer", "Soothsayer"],
        "neutral":  ["Illusionist", "Sigilist", "Summoner", "Thaumaturge", "Witch"],
        "opposed":  ["Enchanter"],
    },
    "Elementalist": {
        "own":      ["Elementalist"],
        "aligned":  ["Chronomancer", "Enchanter", "Summoner"],
        "neutral":  ["Necromancer", "Sigilist", "Soothsayer", "Thaumaturge", "Witch"],
        "opposed":  ["Illusionist"],
    },
    "Enchanter": {
        "own":      ["Enchanter"],
        "aligned":  ["Elementalist", "Sigilist", "Witch"],
        "neutral":  ["Illusionist", "Necromancer", "Soothsayer", "Summoner", "Thaumaturge"],
        "opposed":  ["Chronomancer"],
    },
    "Illusionist": {
        "own":      ["Illusionist"],
        "aligned":  ["Sigilist", "Soothsayer", "Thaumaturge"],
        "neutral":  ["Chronomancer", "Enchanter", "Necromancer", "Summoner", "Witch"],
        "opposed":  ["Elementalist"],
    },
    "Necromancer": {
        "own":      ["Necromancer"],
        "aligned":  ["Chronomancer", "Summoner", "Witch"],
        "neutral":  ["Elementalist", "Enchanter", "Illusionist", "Sigilist", "Soothsayer"],
        "opposed":  ["Thaumaturge"],
    },
    "Sigilist": {
        "own":      ["Sigilist"],
        "aligned":  ["Enchanter", "Illusionist", "Thaumaturge"],
        "neutral":  ["Chronomancer", "Elementalist", "Necromancer", "Soothsayer", "Witch"],
        "opposed":  ["Summoner"],
    },
    "Soothsayer": {
        "own":      ["Soothsayer"],
        "aligned":  ["Chronomancer", "Illusionist", "Thaumaturge"],
        "neutral":  ["Elementalist", "Enchanter", "Necromancer", "Sigilist", "Summoner"],
        "opposed":  ["Witch"],
    },
    "Summoner": {
        "own":      ["Summoner"],
        "aligned":  ["Elementalist", "Necromancer", "Witch"],
        "neutral":  ["Chronomancer", "Enchanter", "Illusionist", "Soothsayer", "Thaumaturge"],
        "opposed":  ["Sigilist"],
    },
    "Thaumaturge": {
        "own":      ["Thaumaturge"],
        "aligned":  ["Illusionist", "Sigilist", "Soothsayer"],
        "neutral":  ["Chronomancer", "Elementalist", "Enchanter", "Summoner", "Witch"],
        "opposed":  ["Necromancer"],
    },
    "Witch": {
        "own":      ["Witch"],
        "aligned":  ["Enchanter", "Necromancer", "Summoner"],
        "neutral":  ["Chronomancer", "Elementalist", "Illusionist", "Sigilist", "Thaumaturge"],
        "opposed":  ["Soothsayer"],
    },
}

SCHOOL_PENALTY = {"own": 0, "aligned": 2, "neutral": 4, "opposed": 6}

# Todos los hechizos: {nombre: {school, base_cast, category}}
SPELLS = {
    "Absorb Knowledge":    {"school": "Sigilist",     "base": 12, "category": "Out of Game (A)"},
    "Animal Companion":    {"school": "Witch",        "base": 10, "category": "Out of Game (B)"},
    "Animate Construct":   {"school": "Enchanter",    "base": 10, "category": "Out of Game (B)"},
    "Animate Skull":       {"school": "Necromancer",  "base":  8, "category": "Line of Sight"},
    "Awareness":           {"school": "Soothsayer",   "base": 12, "category": "Out of Game (B)"},
    "Banish":              {"school": "Thaumaturge",  "base": 10, "category": "Line of Sight"},
    "Beauty":              {"school": "Illusionist",  "base": 10, "category": "Self Only"},
    "Blinding Light":      {"school": "Thaumaturge",  "base":  8, "category": "Line of Sight"},
    "Blink":               {"school": "Illusionist",  "base": 12, "category": "Line of Sight"},
    "Bone Dart":           {"school": "Necromancer",  "base": 10, "category": "Line of Sight"},
    "Bones of the Earth":  {"school": "Necromancer",  "base": 10, "category": "Line of Sight"},
    "Brew Potion":         {"school": "Witch",        "base": 12, "category": "Out of Game (B)"},
    "Bridge":              {"school": "Sigilist",     "base": 10, "category": "Line of Sight"},
    "Call Storm":          {"school": "Elementalist", "base": 12, "category": "Area Effect"},
    "Circle of Protection":{"school": "Thaumaturge",  "base": 12, "category": "Touch"},
    "Combat Awareness":    {"school": "Soothsayer",   "base": 12, "category": "Touch"},
    "Control Animal":      {"school": "Witch",        "base": 12, "category": "Line of Sight"},
    "Control Construct":   {"school": "Enchanter",    "base": 12, "category": "Line of Sight"},
    "Control Demon":       {"school": "Summoner",     "base": 10, "category": "Line of Sight"},
    "Control Undead":      {"school": "Necromancer",  "base": 12, "category": "Line of Sight"},
    "Crumble":             {"school": "Chronomancer", "base": 10, "category": "Line of Sight"},
    "Curse":               {"school": "Witch",        "base":  8, "category": "Line of Sight"},
    "Decay":               {"school": "Chronomancer", "base": 12, "category": "Line of Sight"},
    "Destroy Undead":      {"school": "Thaumaturge",  "base": 10, "category": "Line of Sight"},
    "Destructive Sphere":  {"school": "Elementalist", "base": 12, "category": "Area Effect"},
    "Dispel":              {"school": "Thaumaturge",  "base": 12, "category": "Line of Sight"},
    "Draining Word":       {"school": "Sigilist",     "base": 14, "category": "Area Effect"},
    "Elemental Ball":      {"school": "Elementalist", "base": 12, "category": "Line of Sight"},
    "Elemental Bolt":      {"school": "Elementalist", "base": 12, "category": "Line of Sight"},
    "Elemental Hammer":    {"school": "Elementalist", "base": 10, "category": "Line of Sight"},
    "Elemental Shield":    {"school": "Elementalist", "base": 10, "category": "Self Only"},
    "Embed Enchantment":   {"school": "Enchanter",    "base": 14, "category": "Out of Game (A)"},
    "Enchant Armour":      {"school": "Enchanter",    "base":  8, "category": "Line of Sight"},
    "Enchant Weapon":      {"school": "Enchanter",    "base":  8, "category": "Line of Sight"},
    "Explosive Rune":      {"school": "Sigilist",     "base": 10, "category": "Line of Sight"},
    "Familiar":            {"school": "Witch",        "base": 10, "category": "Out of Game (B)"},
    "Fast Act":            {"school": "Chronomancer", "base":  8, "category": "Line of Sight"},
    "Fleet Feet":          {"school": "Chronomancer", "base": 10, "category": "Line of Sight"},
    "Fog":                 {"school": "Witch",        "base":  8, "category": "Line of Sight"},
    "Fool's Gold":         {"school": "Illusionist",  "base": 10, "category": "Line of Sight"},
    "Furious Quill":       {"school": "Sigilist",     "base": 10, "category": "Line of Sight"},
    "Glow":                {"school": "Illusionist",  "base": 10, "category": "Line of Sight"},
    "Grenade":             {"school": "Enchanter",    "base": 10, "category": "Line of Sight"},
    "Heal":                {"school": "Thaumaturge",  "base":  8, "category": "Line of Sight"},
    "Illusionary Soldier": {"school": "Illusionist",  "base": 12, "category": "Out of Game (B) / Touch"},
    "Imp":                 {"school": "Summoner",     "base": 10, "category": "Line of Sight"},
    "Invisibility":        {"school": "Illusionist",  "base": 12, "category": "Touch"},
    "Leap":                {"school": "Summoner",     "base":  8, "category": "Line of Sight"},
    "Mind Control":        {"school": "Soothsayer",   "base": 12, "category": "Line of Sight"},
    "Mind Lock":           {"school": "Soothsayer",   "base": 12, "category": "Line of Sight"},
    "Miraculous Cure":     {"school": "Thaumaturge",  "base": 16, "category": "Out of Game (A)"},
    "Mud":                 {"school": "Witch",        "base": 10, "category": "Line of Sight"},
    "Petrify":             {"school": "Chronomancer", "base": 10, "category": "Line of Sight"},
    "Plague of Insects":   {"school": "Summoner",     "base": 10, "category": "Line of Sight"},
    "Planar Tear":         {"school": "Summoner",     "base": 12, "category": "Line of Sight"},
    "Plane Walk":          {"school": "Summoner",     "base": 10, "category": "Self Only"},
    "Poison Dart":         {"school": "Witch",        "base": 10, "category": "Line of Sight"},
    "Possess":             {"school": "Summoner",     "base": 12, "category": "Line of Sight"},
    "Power Word":          {"school": "Sigilist",     "base": 14, "category": "Area Effect"},
    "Push":                {"school": "Sigilist",     "base":  8, "category": "Line of Sight"},
    "Raise Zombie":        {"school": "Necromancer",  "base": 10, "category": "Out of Game (B) / Touch"},
    "Reveal Secret":       {"school": "Soothsayer",   "base": 12, "category": "Out of Game (B)"},
    "Scatter Shot":        {"school": "Elementalist", "base": 12, "category": "Area Effect"},
    "Shield":              {"school": "Thaumaturge",  "base": 10, "category": "Line of Sight"},
    "Slow":                {"school": "Chronomancer", "base": 10, "category": "Line of Sight"},
    "Spell Eater":         {"school": "Necromancer",  "base": 12, "category": "Line of Sight"},
    "Steal Health":        {"school": "Necromancer",  "base": 10, "category": "Line of Sight"},
    "Strength":            {"school": "Enchanter",    "base": 10, "category": "Line of Sight"},
    "Strike Dead":         {"school": "Necromancer",  "base": 18, "category": "Line of Sight"},
    "Suggestion":          {"school": "Soothsayer",   "base": 12, "category": "Line of Sight"},
    "Summon Demon":        {"school": "Summoner",     "base": 12, "category": "Touch"},
    "Telekinesis":         {"school": "Enchanter",    "base": 10, "category": "Line of Sight"},
    "Teleport":            {"school": "Illusionist",  "base": 10, "category": "Self Only"},
    "Time Store":          {"school": "Chronomancer", "base": 14, "category": "Self Only"},
    "Time Walk":           {"school": "Chronomancer", "base": 14, "category": "Self Only"},
    "Transpose":           {"school": "Illusionist",  "base": 12, "category": "Line of Sight"},
    "True Sight":          {"school": "Soothsayer",   "base": 10, "category": "Self Only"},
    "Wall":                {"school": "Elementalist", "base": 10, "category": "Line of Sight"},
    "Wizard Eye":          {"school": "Soothsayer",   "base":  8, "category": "Line of Sight"},
    "Write Scroll":        {"school": "Sigilist",     "base": 12, "category": "Out of Game (A)"},
}

# Descripción completa de cada hechizo (extraída del manual, 2ª ed.)
SPELL_DESCRIPTIONS = {
    "Absorb Knowledge": "Wizard only. This spell allows a wizard to absorb the knowledge from a written work without having to read it. A wizard immediately gains 40 experience points for casting this spell to represent the speed with which they can gain knowledge. This experience does not count against the maximum that can be earned in one game. This spell may only be cast after a game in which the wizard was not reduced to 0 Health.",
    "Animal Companion": "The spellcaster summons an animal companion of their choice from the following options to become a permanent member of their warband: bear, ice toad, snow leopard, or wolf. All Animal Companions count as standard soldiers. Animal companions are more strong-willed than wild examples of their species and receive a permanent +3 Will. A spellcaster may only have one animal companion at any time.",
    "Animate Construct": "It is assumed that the spellcaster has built a construct prior to using this spell to animate it. If the spell is successfully cast, the construct immediately becomes a permanent member of the warband, taking the place of a soldier. A spellcaster must declare the size of construct they are attempting to animate (small, medium or large) before rolling to cast the spell. The larger the construct, the harder it is to animate: Small -0, Medium -3, Large -6. Large constructs count as specialist soldiers, the others as standard soldiers.",
    "Animate Skull": "The spellcaster fills a skull with magic malice and throws it at an opponent. Place one animated skull within 6\" of the spellcaster. It can be placed directly into combat. This skull is an uncontrolled creature. The spellcaster may not cast this spell again until this creature is removed from the table, but may spend an action to cancel the spell.",
    "Awareness": "If this spellcaster is on the table, its warband may add +2 to its Initiative Rolls for the purposes of determining the primary player only. This bonus stacks so, if both the wizard and the apprentice have cast this spell and are both on the table, the player may add +4 to their Initiative Rolls. The maximum possible bonus is +4.",
    "Banish": "All demons within line of sight of the spellcaster must pass an immediate Will Roll with a Target Number equal to the Casting Roll. If a demon fails the roll and its current Will is +4 or less, it is immediately reduced to 0 Health and removed from the table. If its current Will is +5 or higher, it suffers damage equal to three times the amount by which it failed the Will Roll.",
    "Beauty": "This spell causes anyone who looks on the spellcaster to see a paragon of beauty. Any member of an opposing warband must make a Will Roll (TN = Casting Roll) if they wish to: move into combat with the spellcaster, make a shooting attack that could potentially hit the spellcaster, or cast any spell that targets the spellcaster. A figure may only attempt such a Will Roll once per turn. This spell has no effect on creatures or war hounds.",
    "Blinding Light": "The target must make an immediate Will Roll with a Target Number equal to the Casting Roll. If it fails, it may not attack, shoot, or cast Line of Sight spells. Its Fight stat is reduced to +0 and its Move to 1. At the end of each turn, the figure may attempt another Will Roll with the same Target Number to cancel the spell.",
    "Blink": "This spell may target any figure within 12\". Move that figure 4\" in a random direction. A figure may make a Will Roll with a Target Number equal to the Casting Roll in order to resist this spell. Uncontrolled creatures will always attempt this Will Roll.",
    "Bone Dart": "This spell fires a small, sharp shard of bone. The spellcaster makes a +5 shooting attack against any figure within line of sight and 12\". This does not count as a magic attack.",
    "Bones of the Earth": "A skeletal hand reaches out of the ground and grabs the target's ankle. The figure may not take any move actions until it escapes. The only way to escape is to fight the hand (Fight +0, Health 1). If the hand wins the fight, it does damage as normal. This spell may only be cast against a target standing on the ground. Large creatures are unaffected. Maximum range: 18\".",
    "Brew Potion": "The spellcaster creates one Lesser Potion of their choice that may be sold, stored in the wizard's vault, or given to a member of the warband. A wizard (only) may use this spell to create a Greater Potion by paying the ingredients cost and applying a -4 to the Casting Roll.",
    "Bridge": "The spellcaster creates a temporary bridge, ramp, or staircase: 6\" long and 2\" wide, placed anywhere completely in line of sight. Figures may move along it at normal movement rate. Each spellcaster may only have one bridge in play at a time. Roll a die at the end of every turn: on a 1–2 the bridge vanishes.",
    "Call Storm": "All bow and crossbow attacks are made with -1 Shoot for the rest of the game. This spell may be cast multiple times (and by multiple spellcasters), with each additional casting increasing the penalty by a further -1, up to a maximum of -5.",
    "Circle of Protection": "Creates a circle with a 3\" diameter which no demon or undead creature can enter or pass through. A spellcaster may only have one active circle of protection at a time, but does not have to remain within it. Roll a die at the end of every turn: on a 1–3 the spell is cancelled.",
    "Combat Awareness": "This spell gives the target a magic insight into the moves their opponent will attempt in a fight. It grants the target +1 Fight and +1 Armour for the remainder of the game. Multiple castings of this spell on the same target have no effect.",
    "Control Animal": "The target animal must make an immediate Will Roll with a Target Number equal to the Casting Roll. If the roll fails, the animal becomes a temporary member of the spellcaster's warband for the rest of the game or until the spell is cancelled. A spellcaster may only control one animal at a time.",
    "Control Construct": "The target construct must make an immediate Will Roll with a Target Number equal to the Casting Roll. If the roll fails, the construct becomes a temporary member of the spellcaster's warband for the rest of the game or until the spell is cancelled. A spellcaster may only control one construct at a time.",
    "Control Demon": "The target demon must make an immediate Will Roll with a Target Number equal to the Casting Roll. If it fails, it becomes a temporary member of the spellcaster's warband for the rest of the game or until the spell is cancelled. A spellcaster may only control one demon at a time.",
    "Control Undead": "The target undead creature must make an immediate Will Roll with a Target Number equal to the Casting Roll. If the roll fails, the undead creature becomes a temporary member of the spellcaster's warband for the rest of the game or until the spell is cancelled. A spellcaster may only control one undead creature at a time.",
    "Crumble": "This spell can only target inanimate structures such as buildings and walls. The spellcaster rapidly speeds up the passing of time in a small area, causing it to collapse — creating a doorway-sized hole through any wall. Can also collapse a section of floor beneath a figure standing on a level above the ground (Move Roll TN22 or fall). If cast on a Wall spell, it is completely destroyed.",
    "Curse": "The target suffers -2 to all die rolls. At the end of each turn, the target may make a Will Roll with the Target Number equal to the Casting Roll (at -2). If successful, this spell is cancelled. Curse cannot be cast on a figure already suffering the effects of a Curse spell.",
    "Decay": "The spellcaster selects and attacks a target's weapon, causing it to decay and fall apart, rendering it useless for the rest of the game. This spell has no effect on magic weapons (even those only temporarily enchanted), nor on creatures (unless specifically equipped with a weapon from the General Arms and Armour List).",
    "Destroy Undead": "The target undead creature must make a Will Roll with a Target Number equal to the Casting Roll. If the undead creature fails the roll and its current Will is +2 or less, it is immediately reduced to 0 Health and removed from the table. If its current Will is +3 or higher, it suffers damage equal to three times the amount by which it failed the Will Roll.",
    "Destructive Sphere": "Every figure within 3\" of the spellcaster (but not counting the spellcaster itself) suffers a +5 elemental magic attack.",
    "Dispel": "Immediately cancels the ongoing effect of any one casting of any one spell. It cannot unsummon a creature, but it can cancel the control of a creature that is a temporary member of a warband.",
    "Draining Word": "This spell draws a bright rune of power in the sky. The spellcaster may choose one spell for Draining Word to affect. All rolls to attempt to cast that particular spell are at -3 for the rest of the game. A spellcaster may only have one Draining Word spell in effect at a time.",
    "Elemental Ball": "The spellcaster selects an enemy figure within 16\" and line of sight and hurls a ball of destructive elemental energy at it. The target and every figure within 1\" and line of sight of the target immediately suffers a +5 elemental magic shooting attack (rolled separately for each figure). This spell may not target an enemy figure that is even partially obscured by another figure.",
    "Elemental Bolt": "The spellcaster makes a +7 elemental magic shooting attack against a target figure within 16\" and line of sight.",
    "Elemental Hammer": "This spell is cast upon a weapon. The next time the figure wielding this weapon wins a round of combat and does at least 1 point of damage, this weapon inflicts an additional 5 points of elemental magic damage. If cast on a bow or crossbow the spell only applies to the next attack.",
    "Elemental Shield": "The spellcaster forms a floating shield that absorbs the next 3 points of damage the spellcaster would normally suffer in combat or from a shooting attack. Once 3 points have been absorbed the spell is cancelled. A spellcaster may only have one Elemental Shield active at any time.",
    "Embed Enchantment": "This spell causes any one Enchant Armour or Enchant Weapon spell that is still active at the end of a game to become permanent, and the weapon or armour in question to become a magic weapon or armour. The newly created magic weapon or armour takes up an item slot as normal.",
    "Enchant Armour": "This spell may only be cast on a figure wearing armour. The armour worn by the target now counts as magic armour and grants +1 Armour for the rest of the game. Multiple castings of this spell on the same target have no effect.",
    "Enchant Weapon": "This spell targets a weapon of the spellcaster's choosing. If cast on a melee weapon, this weapon counts as a magic weapon with +1 Fight. Bows and crossbows count as magic weapons with +1 Shoot (but the attacks do not count as magic). This spell may only be cast once on each weapon.",
    "Explosive Rune": "The spellcaster draws a bright, glowing rune of power anywhere within 4\" and line of sight. If any character or creature not part of the spellcaster's warband moves within 1\" of the rune, it explodes — every figure within 2\" suffers an immediate +5 magic attack. A spellcaster may have up to three such runes in play at any time.",
    "Familiar": "The spellcaster gains a familiar, which can take the form of any small creature. A spellcaster with a familiar gains +2 Health (written as a split stat). If the spellcaster is ever reduced to 1 Health or less, the familiar is destroyed. At the start of the next game, the spellcaster reverts to their normal Health unless another Familiar spell is successfully cast.",
    "Fast Act": "This spell may only be cast on a member of the spellcaster's warband or an uncontrolled creature. This figure will activate at the end of the current phase instead of in its normal phase. Spellcasters may not cast this spell on themselves, nor on a figure that has already activated in the current turn.",
    "Fleet Feet": "The target receives +2 Move for the rest of the game. Multiple castings of Fleet Feet on the same target have no effect.",
    "Fog": "Place a line of fog, 6\" long, 3\" high, and 1\" thick anywhere on the table (some part must be in line of sight of the spellcaster, all within 24\"). Figures can move through the fog with no penalty, but line of sight may not be drawn through it. At the start of each new turn, roll a die: on a 1–4 the fog dissipates.",
    "Fool's Gold": "This spell may only be cast on a figure carrying a treasure token. That figure must make an immediate Will Roll with a Target Number equal to the Casting Roll. If it fails, the spellcaster may take the treasure token from the figure and move it up to 4\" in any direction, provided the final spot is within line of sight of the spellcaster.",
    "Furious Quill": "The target is attacked by a sharp animated quill. Although the quill does no damage, it is highly irritating and extremely distracting. While under attack, the target suffers -1 Move, -2 Fight, -4 Shoot, and -2 to all Casting Rolls. Whenever the target is activated, it may make a Will Roll (TN = Casting Roll) — if successful, the quill is caught and destroyed. Multiple castings against the same target have no effect.",
    "Glow": "A brightly glowing light surrounds the target figure. For the rest of the game, all shooting attacks against this figure from any source are at +3. Multiple castings of Glow on the same target have no effect.",
    "Grenade": "The spellcaster imbues an object with magic energy and throws it at a target point within 14\". Every figure (including allies) within 1.5\" of that point immediately suffers a +3 magic shooting attack.",
    "Heal": "This spell restores up to 5 points of lost Health to a target figure within 6\". This spell cannot take a model above its starting Health. This spell has no effect on undead or constructs.",
    "Illusionary Soldier": "An illusionary soldier becomes a temporary member of the warband for the next battle (if cast Out of Game) or until the end of the game (if cast during a battle). This soldier can be of any type except an apothecary. This soldier cannot pick up treasure, nor can it deal damage, but otherwise counts as a regular soldier. If the illusionary soldier ever suffers damage of any type, it is removed. A warband may only have one illusionary soldier at any given time.",
    "Imp": "The spellcaster places an imp on the table anywhere within line of sight, but no closer than 3\" to any other figure. The imp follows the normal rules for uncontrolled creatures and will activate in the next Creature phase. If the spellcaster casts this spell a second time, the first imp immediately vanishes.",
    "Invisibility": "The target figure becomes invisible. No figure may move into combat with the invisible figure, nor target it with any attack or spell (although it may still be affected by area effects). If the invisible figure moves into combat, casts a spell, or picks up a treasure token, the Invisibility spell is cancelled.",
    "Leap": "This spell may only be cast on a member of the spellcaster's warband. Immediately move the target figure up to 10\" in any direction, including vertically (straight line or arc). If the target is carrying treasure, this move is reduced to 5\". This move may not take a figure off the table or into combat. The target may take no other actions this turn.",
    "Mind Control": "The target figure must make an immediate Will Roll (TN = Casting Roll). If it fails, the target temporarily joins the spellcaster's warband. After the figure activates each turn, it must make another Will Roll to regain its normal allegiance. A spellcaster may only have one active Mind Control spell at a time. This spell has no effect on spellcasters.",
    "Mind Lock": "The target of this spell becomes immune to Mind Control and Suggestion spells for the rest of the game, and any current Mind Control spells on the figure are cancelled. The figure gains +2 Will for the rest of the game.",
    "Miraculous Cure": "Wizard only. A successful casting will remove all permanent injuries from one figure. Or, it may be cast on a Badly Wounded figure to allow them to participate in the next game with no penalty. Finally, it may be used to attempt to bring a figure back from the dead (figure must have died in the game just played, with a -4 penalty to the Casting Roll). If Miraculous Cure is cast using a scroll, it cannot be used to resurrect the dead.",
    "Mud": "All ground within 3\" of a target point becomes rough ground.",
    "Petrify": "The target figure must make an immediate Will Roll with a Target Number equal to the Casting Roll. If it fails, it receives no actions in its next activation. Furthermore, the figure suffers -3 Fight (minimum +0) and may not have Leap cast upon it until after it makes its next move action. Large creatures receive +8 to their Will Roll to resist this spell.",
    "Plague of Insects": "The target figure is attacked by a cloud of stinging or biting insects. The cloud has a 1\" radius centred on and moving with the target figure. Affected figures have -4 Fight, -4 Shoot (minimum +0) and -2 to Casting Rolls. After the target activates each turn, it may make a Will Roll (TN = Casting Roll) to cancel the spell. Large creatures, undead, and constructs are immune to this spell.",
    "Planar Tear": "The spellcaster creates a small tear in the fabric of the universe. The spellcaster selects a target point. All figures within 2\" of that point must make a Will Roll (TN = Casting Roll) or suffer 2 points of damage. Demons that fail the Will Roll take damage equal to the Casting Roll.",
    "Plane Walk": "Although the spellcaster remains in the same physical location, they move briefly between planes of existence. For the rest of this turn, they can ignore all terrain when moving, cannot be targeted by attacks or spells, and will never be in combat. However, they may not pick up treasure or affect other figures or terrain. If casting this spell in a second consecutive turn, they suffer a -5 modifier to their Casting Roll (-10 for three in a row, -15 beyond that).",
    "Poison Dart": "Make an immediate +3 poisoned shooting attack against the target figure. This is a non-magic attack.",
    "Possess": "This spell may only be cast on a permanent or temporary member of the spellcaster's own warband (except the wizard, apprentice, or demons). The target gains +2 Fight, +1 Armour, and -2 Will and counts as a demon. This figure may not be part of a group activation. A spellcaster may only have one Possess spell active at a time.",
    "Power Word": "This spell draws a bright rune of power in the sky. The spellcaster may pick one spell for the Power Word to affect. All rolls to cast that particular spell are at +3 for every spellcaster for the rest of the game. A spellcaster may only have one Power Word spell in effect at a time.",
    "Push": "The target suffers an immediate +10 attack. Instead of taking damage, the target is moved 1\" directly away from the spellcaster for every point of damage they would have taken. If pushed into a table edge or terrain over ½\" high, they stop immediately. If pushed up or off a height, the target suffers falling damage. This spell can push a figure out of combat.",
    "Raise Zombie": "The spellcaster adds one zombie to their warband as a temporary member. If the spell is cast before the game, the zombie can be deployed normally; if during a game, it appears in base contact with the spellcaster. A warband may only have one raised zombie at any one time. If the zombie is killed or exits the table, Raise Zombie can be cast again.",
    "Reveal Secret": "This spell imparts knowledge on some lost treasure. Every successful casting of this spell before a game allows the player to make two rolls for a single treasure token (other than the central treasure) after the game and choose which one to take.",
    "Scatter Shot": "The spellcaster makes a +0 elemental magic shooting attack against every enemy figure (either from an opposing warband or uncontrolled creature) within 12\" and line of sight. Normal rules for shooting into combat apply.",
    "Shield": "The target receives +2 Armour for the rest of the game. The maximum armour rule still applies. Multiple castings of Shield on the same target have no effect.",
    "Slow": "The target is reduced to a maximum of one action per activation (which can be any action, not necessarily movement). It may make a Will Roll versus the Casting Roll at the end of each of its activations. If successful the spell is cancelled.",
    "Spell Eater": "Casting this spell causes the spellcaster to immediately take 1 point of damage. When this spell is cast, it cancels the effects of a single casting of any one spell currently in play. This spell cannot unsummon a creature, but it can cancel the control of a creature.",
    "Steal Health": "The target must make an immediate Will Roll with a Target Number equal to the Casting Roll. If failed, the target immediately loses 3 Health and the spellcaster regains 3 Health. This may not take the spellcaster above their starting Health. This spell has no effect on undead or constructs.",
    "Strength": "The target receives +2 Fight. Multiple Strength spells on the same target have no effect.",
    "Strike Dead": "This spell targets a figure within 8\". The target must make a Will Roll (TN = Casting Roll) or be immediately reduced to 0 Health. All figures may empower their Will Roll to resist this spell, even non-spellcasters. The spellcaster immediately loses 1 Health upon attempting this spell, regardless of success. This spell has no effect on undead or constructs.",
    "Suggestion": "The target of this spell immediately drops any treasure tokens it is carrying. The spellcaster may move the figure up to 3\" in any direction provided this does not move the figure into combat or cause immediate damage. The target may make a Will Roll (TN = Casting Roll) to resist — if successful, the spell has no effect.",
    "Summon Demon": "Immediately place a demon on the table within 1\" of the spellcaster (not in combat). This demon is considered to be under the effects of a Control Demon spell. The type of demon depends on the margin of success: 0–5 imp, 6–12 minor demon, 13+ major demon. If a spellcaster rolls a 1 while attempting this spell, they summon an uncontrolled demon in combat with the spellcaster.",
    "Telekinesis": "The spellcaster may move any treasure token within 16\" by up to 6\" in any direction, so long as it remains in line of sight. This spell has no effect on a treasure token being carried by a figure, nor on the central treasure until after it has been picked up for the first time.",
    "Teleport": "The spellcaster immediately moves to any location within line of sight, but may take no other actions this turn after casting this spell. This spell may not be used to enter combat or to move off the table.",
    "Time Store": "The spellcaster captures a fragment of their own present to save for future use. They must spend their first action casting Time Store — if successful, the second action is lost. The spellcaster gains a stored 'extra action' that they may use in a future turn, potentially allowing three actions in one activation.",
    "Time Walk": "Wizard only. The wizard will activate again in the Apprentice phase and the Soldier phase (one action each). They may not activate additional soldiers or be part of a group activation in these phases. If the wizard moved in a previous activation, additional move actions are at half rate. If a wizard casts this spell in consecutive turns, they immediately suffer 8 points of damage.",
    "Transpose": "This spell switches the position of two figures on the table. Both figures must be within line of sight of the spellcaster and within 12\" of one another. Members of opposing warbands may make a Will Roll (TN = Casting Roll) to attempt to resist the spell — if successful, the spell is cancelled. Friendly figures and uncontrolled creatures will not make such Will Rolls.",
    "True Sight": "The spellcaster, and all friendly figures within 6\" of the spellcaster, can see invisible figures and are immune to the effects of the Beauty spell. Furthermore, if an invisible figure is within 6\" of the spellcaster, the Invisibility spell is cancelled. If an Illusionary Soldier is within 6\" of the spellcaster, it is immediately removed from the table.",
    "Wall": "This spell creates a 6\"-long, 3\"-high wall, part of which must be within 10\" and line of sight of the spellcaster. This wall can be climbed as normal. At the end of each turn after the turn in which the spell was cast, roll a die: on a 1–4 the wall vanishes.",
    "Wizard Eye": "This spell may be cast on any terrain feature within 12\" that has a flat side. Place a token on or next to the terrain feature to represent the Wizard Eye. For the rest of the game, the caster may choose to draw line of sight from the Wizard Eye when casting spells. The Wizard Eye has 180-degree field of vision. A spellcaster may only maintain one Wizard Eye at a time.",
    "Write Scroll": "This spell creates one scroll. The scroll must be of a spell that the spellcaster either knows or for which they own the grimoire. The scroll may be sold, given to a figure, or stored in the wizard's vault.",
}

# Stats del wizard inicial
WIZARD_BASE_STATS = {
    "Move": 6, "Fight": "+2", "Shoot": "+0", "Armour": 10, "Will": "+4", "Health": 14,
}

APPRENTICE_BASE_STATS = {
    "Move": 6, "Fight": "+0", "Shoot": "+0", "Armour": 10, "Will": "+2", "Health": 12,
}

APPRENTICE_COST = 100

STANDARD_SOLDIERS = {
    "Thug":        {"Move":6,"Fight":"+2","Shoot":"+0","Armour":10,"Will":"-1","Health":10,"Cost":0,  "Notes":"Hand Weapon","Specialist":False},
    "Thief":       {"Move":7,"Fight":"+1","Shoot":"+0","Armour":10,"Will":"+0","Health":10,"Cost":0,  "Notes":"Dagger","Specialist":False},
    "War Hound":   {"Move":8,"Fight":"+1","Shoot":"+0","Armour":10,"Will":"-2","Health":8, "Cost":10, "Notes":"Animal — no puede llevar objetos ni recoger tesoros","Specialist":False},
    "Infantryman": {"Move":6,"Fight":"+3","Shoot":"+0","Armour":11,"Will":"+0","Health":10,"Cost":50, "Notes":"Two-Handed Weapon, Light Armour","Specialist":False},
    "Man-at-Arms": {"Move":6,"Fight":"+3","Shoot":"+0","Armour":12,"Will":"+1","Health":12,"Cost":75, "Notes":"Hand Weapon, Shield, Light Armour","Specialist":False},
    "Apothecary":  {"Move":6,"Fight":"+1","Shoot":"+0","Armour":10,"Will":"+3","Health":12,"Cost":75, "Notes":"Staff, Healing Potion","Specialist":False},
}

SPECIALIST_SOLDIERS = {
    "Archer":          {"Move":6,"Fight":"+1","Shoot":"+2","Armour":11,"Will":"+0","Health":10,"Cost":75, "Notes":"Bow, Quiver, Dagger, Light Armour","Specialist":True},
    "Crossbowman":     {"Move":6,"Fight":"+1","Shoot":"+2","Armour":11,"Will":"+0","Health":10,"Cost":75, "Notes":"Crossbow, Quiver, Dagger, Light Armour","Specialist":True},
    "Treasure Hunter": {"Move":7,"Fight":"+3","Shoot":"+0","Armour":11,"Will":"+2","Health":12,"Cost":100,"Notes":"Hand Weapon, Dagger, Light Armour","Specialist":True},
    "Tracker":         {"Move":7,"Fight":"+1","Shoot":"+2","Armour":11,"Will":"+1","Health":12,"Cost":100,"Notes":"Staff, Bow, Quiver, Light Armour","Specialist":True},
    "Knight":          {"Move":5,"Fight":"+4","Shoot":"+0","Armour":13,"Will":"+1","Health":12,"Cost":125,"Notes":"Hand Weapon, Dagger, Shield, Heavy Armour","Specialist":True},
    "Templar":         {"Move":5,"Fight":"+4","Shoot":"+0","Armour":12,"Will":"+1","Health":12,"Cost":125,"Notes":"Two-Handed Weapon, Heavy Armour","Specialist":True},
    "Ranger":          {"Move":7,"Fight":"+2","Shoot":"+2","Armour":11,"Will":"+2","Health":12,"Cost":125,"Notes":"Bow, Quiver, Hand Weapon, Light Armour","Specialist":True},
    "Barbarian":       {"Move":6,"Fight":"+4","Shoot":"+0","Armour":10,"Will":"+3","Health":14,"Cost":125,"Notes":"Two-Handed Weapon, Dagger","Specialist":True},
    "Marksman":        {"Move":5,"Fight":"+2","Shoot":"+2","Armour":12,"Will":"+1","Health":12,"Cost":125,"Notes":"Crossbow, Quiver, Hand Weapon, Heavy Armour","Specialist":True},
}

ALL_SOLDIERS = {**STANDARD_SOLDIERS, **SPECIALIST_SOLDIERS}

STARTING_GOLD = 400
MAX_SOLDIERS  = 8
MAX_SPECIALISTS = 4

# Reglas de selección de hechizos al inicio:
# 3 propios, 1 de cada escuela alineada (3 en total), 2 de escuelas neutrales distintas
# Total: 8 hechizos, de 6 escuelas distintas (propia + 3 alineadas + 2 neutrales)
SPELL_SELECTION_RULES = {
    "own":     3,  # exactamente 3 de la propia escuela
    "aligned": 1,  # exactamente 1 de cada una de las 3 escuelas alineadas
    "neutral": 2,  # 2 de neutrales, de escuelas distintas
    "total":   8,
}


# ─────────────────────────────────────────────
#  HELPERS DE HECHIZOS
# ─────────────────────────────────────────────

def get_relation(wizard_type: str, spell_school: str) -> str:
    """Devuelve 'own'/'aligned'/'neutral'/'opposed' de un hechizo para un wizard."""
    rel = SCHOOL_RELATIONS[wizard_type]
    if spell_school in rel["own"]:      return "own"
    if spell_school in rel["aligned"]:  return "aligned"
    if spell_school in rel["neutral"]:  return "neutral"
    return "opposed"

def casting_number(wizard_type: str, spell_name: str) -> int:
    """Número de conjuro efectivo = base + penalización por escuela."""
    spell = SPELLS[spell_name]
    relation = get_relation(wizard_type, spell["school"])
    return spell["base"] + SCHOOL_PENALTY[relation]

def spells_by_school(school: str) -> list[str]:
    return sorted(s for s, d in SPELLS.items() if d["school"] == school)

def validate_spell_selection(wizard_type: str, selected: list[str]) -> list[str]:
    """
    Valida que la selección de hechizos cumpla las reglas de inicio.
    Devuelve lista de errores (vacía = OK).
    """
    errors = []
    rel = SCHOOL_RELATIONS[wizard_type]

    # Contar por relación y por escuela neutral
    counts = {"own": 0, "aligned": 0, "neutral": 0, "opposed": 0}
    neutral_schools_used = set()
    aligned_schools_used = {}

    for spell_name in selected:
        if spell_name not in SPELLS:
            errors.append(f"Hechizo desconocido: '{spell_name}'")
            continue
        school = SPELLS[spell_name]["school"]
        relation = get_relation(wizard_type, school)
        counts[relation] += 1
        if relation == "neutral":
            neutral_schools_used.add(school)
        if relation == "aligned":
            aligned_schools_used[school] = aligned_schools_used.get(school, 0) + 1

    if counts["opposed"] > 0:
        errors.append("No podés elegir hechizos de la escuela opuesta al inicio.")
    if counts["own"] != 3:
        errors.append(f"Necesitás exactamente 3 hechizos de tu propia escuela (tenés {counts['own']}).")
    if counts["aligned"] != 3:
        errors.append(f"Necesitás exactamente 1 hechizo de cada escuela alineada, 3 en total (tenés {counts['aligned']}).")
    else:
        for school, cnt in aligned_schools_used.items():
            if cnt > 1:
                errors.append(f"Solo podés elegir 1 hechizo de {school} (es alineada).")
        for school in rel["aligned"]:
            if school not in aligned_schools_used:
                errors.append(f"Falta elegir 1 hechizo de {school} (escuela alineada).")
    if counts["neutral"] != 2:
        errors.append(f"Necesitás exactamente 2 hechizos de escuelas neutrales (tenés {counts['neutral']}).")
    elif len(neutral_schools_used) < 2:
        errors.append("Los 2 hechizos neutrales deben ser de escuelas distintas.")
    if len(selected) != 8:
        errors.append(f"Necesitás exactamente 8 hechizos (tenés {len(selected)}).")

    return errors


# ─────────────────────────────────────────────
#  CLASE WARBAND
# ─────────────────────────────────────────────

class Warband:
    def __init__(self):
        self.wizard_name: str = ""
        self.wizard_type: str = ""
        self.has_apprentice: bool = False
        self.soldiers: list[dict] = []
        self.gold_spent: int = 0
        self.spells: list[str] = []  # nombres de hechizos seleccionados

    @property
    def gold_remaining(self) -> int:
        return STARTING_GOLD - self.gold_spent

    @property
    def specialist_count(self) -> int:
        return sum(1 for s in self.soldiers if ALL_SOLDIERS[s["type"]]["Specialist"])

    @property
    def total_figures(self) -> int:
        return 1 + (1 if self.has_apprentice else 0) + len(self.soldiers)

    def set_wizard(self, name: str, wtype: str):
        self.wizard_name = name
        self.wizard_type = wtype
        self.spells = []  # resetear hechizos si cambia tipo

    def hire_apprentice(self) -> tuple[bool, str]:
        if self.has_apprentice:
            return False, "Ya tenés un aprendiz."
        if self.gold_remaining < APPRENTICE_COST:
            return False, f"Oro insuficiente ({APPRENTICE_COST} gc necesarios, {self.gold_remaining} gc disponibles)."
        self.has_apprentice = True
        self.gold_spent += APPRENTICE_COST
        return True, f"Aprendiz contratado por {APPRENTICE_COST} gc."

    def fire_apprentice(self) -> tuple[bool, str]:
        if not self.has_apprentice:
            return False, "No tenés aprendiz."
        self.has_apprentice = False
        self.gold_spent -= APPRENTICE_COST
        return True, "Aprendiz despedido."

    def add_soldier(self, soldier_type: str, name: str = "") -> tuple[bool, str]:
        if soldier_type not in ALL_SOLDIERS:
            return False, f"Tipo de soldado desconocido: '{soldier_type}'."
        if len(self.soldiers) >= MAX_SOLDIERS:
            return False, f"Límite de soldados alcanzado ({MAX_SOLDIERS} máximo)."
        data = ALL_SOLDIERS[soldier_type]
        if data["Specialist"] and self.specialist_count >= MAX_SPECIALISTS:
            return False, f"Límite de especialistas alcanzado ({MAX_SPECIALISTS} máximo)."
        cost = data["Cost"]
        if self.gold_remaining < cost:
            return False, f"Oro insuficiente ({cost} gc necesarios, {self.gold_remaining} gc disponibles)."
        self.soldiers.append({"type": soldier_type, "name": name})
        self.gold_spent += cost
        label = f" ({name})" if name else ""
        return True, f"{soldier_type}{label} reclutado por {cost} gc."

    def remove_soldier(self, index: int) -> tuple[bool, str]:
        if index < 0 or index >= len(self.soldiers):
            return False, "Índice de soldado inválido."
        removed = self.soldiers.pop(index)
        cost = ALL_SOLDIERS[removed["type"]]["Cost"]
        self.gold_spent -= cost
        label = f" ({removed['name']})" if removed["name"] else ""
        return True, f"{removed['type']}{label} despedido. +{cost} gc devueltos."

    def add_spell(self, spell_name: str) -> tuple[bool, str]:
        if not self.wizard_type:
            return False, "Primero configurá el tipo de wizard."
        if spell_name not in SPELLS:
            return False, f"Hechizo desconocido: '{spell_name}'."
        if spell_name in self.spells:
            return False, f"'{spell_name}' ya está en tu lista."
        if len(self.spells) >= 8:
            return False, "Ya tenés 8 hechizos (máximo para wizard inicial)."
        relation = get_relation(self.wizard_type, SPELLS[spell_name]["school"])
        if relation == "opposed":
            return False, f"No podés elegir hechizos de la escuela opuesta ({SPELLS[spell_name]['school']}) al inicio."
        self.spells.append(spell_name)
        cn = casting_number(self.wizard_type, spell_name)
        penalty = SCHOOL_PENALTY[relation]
        penalty_str = f" (+{penalty} por ser {relation})" if penalty > 0 else " (escuela propia)"
        return True, f"'{spell_name}' agregado. Número de conjuro: {cn}{penalty_str}."

    def remove_spell(self, index: int) -> tuple[bool, str]:
        if index < 0 or index >= len(self.spells):
            return False, "Índice de hechizo inválido."
        removed = self.spells.pop(index)
        return True, f"'{removed}' eliminado."

    def validate(self) -> list[str]:
        issues = []
        if not self.wizard_name:
            issues.append("El wizard no tiene nombre.")
        if not self.wizard_type:
            issues.append("El wizard no tiene tipo.")
        if self.gold_remaining < 0:
            issues.append("¡Oro negativo! Revisá los costos.")
        if self.wizard_type:
            spell_errors = validate_spell_selection(self.wizard_type, self.spells)
            issues.extend(spell_errors)
        return issues

    def to_dict(self) -> dict:
        return {
            "wizard_name": self.wizard_name,
            "wizard_type": self.wizard_type,
            "has_apprentice": self.has_apprentice,
            "soldiers": self.soldiers,
            "gold_spent": self.gold_spent,
            "spells": self.spells,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Warband":
        wb = cls()
        wb.wizard_name    = data.get("wizard_name", "")
        wb.wizard_type    = data.get("wizard_type", "")
        wb.has_apprentice = data.get("has_apprentice", False)
        wb.soldiers       = data.get("soldiers", [])
        wb.gold_spent     = data.get("gold_spent", 0)
        wb.spells         = data.get("spells", [])
        return wb

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> "Warband":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


# ─────────────────────────────────────────────
#  HELPERS DE DISPLAY
# ─────────────────────────────────────────────

BORDER = "═" * 62
LINE   = "─" * 62

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def header(title: str):
    print(f"\n{BORDER}")
    print(f"  ❄  FROSTGRAVE 2ª ED. — {title.upper()}")
    print(BORDER)

def ok(msg):   print(f"  ✔  {msg}")
def err(msg):  print(f"  ✘  {msg}")
def info(msg): print(f"     {msg}")

def press_enter():
    input("\n  [Enter para continuar]")

def rel_tag(relation: str) -> str:
    tags = {"own": "[PROPIA]", "aligned": "[ALIN +2]", "neutral": "[NEUT +4]", "opposed": "[OPUES +6]"}
    return tags.get(relation, "")

def print_warband_summary(wb: Warband):
    header("Resumen de Warband")
    if wb.wizard_name:
        print(f"\n  Wizard : {wb.wizard_name}  [{wb.wizard_type}]")
    else:
        print(f"\n  Wizard : (sin configurar)")

    print(f"  Aprendiz : {'✔ Contratado (100 gc)' if wb.has_apprentice else '✘ No contratado'}")

    # Hechizos
    print(f"\n  Hechizos ({len(wb.spells)}/8)")
    if wb.spells and wb.wizard_type:
        for spell_name in wb.spells:
            rel   = get_relation(wb.wizard_type, SPELLS[spell_name]["school"])
            cn    = casting_number(wb.wizard_type, spell_name)
            school = SPELLS[spell_name]["school"]
            print(f"    • {spell_name:<22} CN:{cn:>2}  {rel_tag(rel)}  [{school}]")
    elif wb.spells:
        for s in wb.spells:
            print(f"    • {s}")
    else:
        info("(ninguno)")

    print(f"\n  Soldados ({len(wb.soldiers)}/{MAX_SOLDIERS}) — Especialistas: {wb.specialist_count}/{MAX_SPECIALISTS}")
    if wb.soldiers:
        for i, s in enumerate(wb.soldiers):
            data = ALL_SOLDIERS[s["type"]]
            tag = "[ESP]" if data["Specialist"] else "[STD]"
            name_str = f" «{s['name']}»" if s["name"] else ""
            cost_str = f"{data['Cost']} gc" if data["Cost"] > 0 else "Gratis"
            print(f"    {i+1}. {tag} {s['type']}{name_str}  — {cost_str}")
    else:
        info("(ninguno)")

    print(f"\n  Oro gastado : {wb.gold_spent} / {STARTING_GOLD} gc")
    print(f"  Oro restante: {wb.gold_remaining} gc")
    print(f"  Figuras totales: {wb.total_figures}")

    issues = wb.validate()
    if issues:
        print(f"\n  ⚠  Advertencias:")
        for issue in issues:
            print(f"     • {issue}")
    else:
        print(f"\n  ✔  Lista válida y lista para jugar.")
    print(BORDER)

def print_soldier_tables():
    header("Tablas de Soldados")
    print("\n  SOLDADOS ESTÁNDAR")
    print(f"  {'Nombre':<18} {'M':>3} {'F':>5} {'S':>5} {'A':>6} {'W':>5} {'H':>6} {'Costo':>7}")
    print("  " + "─"*60)
    for name, d in STANDARD_SOLDIERS.items():
        cost = f"{d['Cost']} gc" if d["Cost"] > 0 else "Gratis"
        print(f"  {name:<18} {d['Move']:>3} {d['Fight']:>5} {d['Shoot']:>5} {d['Armour']:>6} {d['Will']:>5} {d['Health']:>6} {cost:>7}")
    print("\n  SOLDADOS ESPECIALISTAS (máx. 4 por warband)")
    print(f"  {'Nombre':<18} {'M':>3} {'F':>5} {'S':>5} {'A':>6} {'W':>5} {'H':>6} {'Costo':>7}")
    print("  " + "─"*60)
    for name, d in SPECIALIST_SOLDIERS.items():
        print(f"  {name:<18} {d['Move']:>3} {d['Fight']:>5} {d['Shoot']:>5} {d['Armour']:>6} {d['Will']:>5} {d['Health']:>6} {d['Cost']:>5} gc")
    print()

def export_list(wb: Warband) -> str:
    lines = []
    lines.append("=" * 58)
    lines.append("  FROSTGRAVE 2ª EDICIÓN — LISTA DE WARBAND")
    lines.append("=" * 58)
    lines.append(f"  Wizard   : {wb.wizard_name or '(sin nombre)'}  [{wb.wizard_type or '—'}]")
    d = WIZARD_BASE_STATS
    lines.append(f"  Stats    : M{d['Move']} F{d['Fight']} S{d['Shoot']} A{d['Armour']} W{d['Will']} H{d['Health']}")
    lines.append(f"  Items    : 5 slots (no armadura, no escudo)")

    if wb.has_apprentice:
        lines.append("")
        lines.append(f"  Aprendiz : (del wizard)  — 100 gc")
        d = APPRENTICE_BASE_STATS
        lines.append(f"  Stats    : M{d['Move']} F{d['Fight']} S{d['Shoot']} A{d['Armour']} W{d['Will']} H{d['Health']}")
        lines.append(f"  Hechizos : mismos que el wizard, con -2 al casteo")

    if wb.spells and wb.wizard_type:
        lines.append("")
        lines.append(f"  HECHIZOS ({len(wb.spells)}/8)")
        lines.append("-" * 58)
        for spell_name in wb.spells:
            rel    = get_relation(wb.wizard_type, SPELLS[spell_name]["school"])
            cn     = casting_number(wb.wizard_type, spell_name)
            school = SPELLS[spell_name]["school"]
            cat    = SPELLS[spell_name]["category"]
            pen    = SCHOOL_PENALTY[rel]
            pen_str = f"+{pen} {rel}" if pen > 0 else "propia"
            lines.append(f"  {spell_name}")
            lines.append(f"    [{school}]  CN:{cn} (base {SPELLS[spell_name]['base']} {pen_str})  {cat}")
            # Descripción con wrap a 56 chars
            desc = SPELL_DESCRIPTIONS.get(spell_name, "")
            words = desc.split()
            line_buf, col = "    ", 4
            for word in words:
                if col + len(word) + 1 > 58:
                    lines.append(line_buf.rstrip())
                    line_buf, col = "    ", 4
                line_buf += word + " "
                col += len(word) + 1
            if line_buf.strip():
                lines.append(line_buf.rstrip())
            lines.append("")

    lines.append("")
    lines.append(f"  SOLDADOS  ({len(wb.soldiers)}/{MAX_SOLDIERS})")
    lines.append("-" * 58)
    for s in wb.soldiers:
        data = ALL_SOLDIERS[s["type"]]
        tag = "[ESP]" if data["Specialist"] else "[STD]"
        name_str = f" «{s['name']}»" if s["name"] else ""
        cost_str = f"{data['Cost']} gc" if data["Cost"] > 0 else "Gratis"
        lines.append(f"  {tag} {s['type']}{name_str}")
        lines.append(f"       M{data['Move']} F{data['Fight']} S{data['Shoot']} A{data['Armour']} W{data['Will']} H{data['Health']}  — {cost_str}")
        lines.append(f"       {data['Notes']}")
    lines.append("-" * 58)
    lines.append(f"  Oro gastado : {wb.gold_spent} / {STARTING_GOLD} gc")
    lines.append(f"  Oro restante: {wb.gold_remaining} gc")
    lines.append(f"  Figuras     : {wb.total_figures}")
    lines.append("=" * 58)
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  MENÚ HECHIZOS
# ─────────────────────────────────────────────

def menu_spells(wb: Warband):
    if not wb.wizard_type:
        err("Primero configurá el tipo de wizard.")
        press_enter()
        return

    rel = SCHOOL_RELATIONS[wb.wizard_type]

    while True:
        header(f"Hechizos — {wb.wizard_type}")

        # Resumen de progreso
        own_sel     = sum(1 for s in wb.spells if get_relation(wb.wizard_type, SPELLS[s]["school"]) == "own")
        alin_sel    = sum(1 for s in wb.spells if get_relation(wb.wizard_type, SPELLS[s]["school"]) == "aligned")
        neut_sel    = sum(1 for s in wb.spells if get_relation(wb.wizard_type, SPELLS[s]["school"]) == "neutral")
        neut_schools = {SPELLS[s]["school"] for s in wb.spells if get_relation(wb.wizard_type, SPELLS[s]["school"]) == "neutral"}

        print(f"\n  Reglas de selección inicial (8 hechizos en total):")
        print(f"    Propios  (penalidad +0) : {own_sel}/3")
        print(f"    Alineados(penalidad +2) : {alin_sel}/3  (1 de cada escuela alineada)")
        print(f"    Neutrales(penalidad +4) : {neut_sel}/2  (de escuelas distintas)")
        print(f"    Total                   : {len(wb.spells)}/8")
        print(f"\n  Escuelas alineadas : {', '.join(rel['aligned'])}")
        print(f"  Escuelas neutrales : {', '.join(rel['neutral'])}")
        print(f"  Escuela opuesta    : {', '.join(rel['opposed'])}  (no disponible al inicio)")

        print(f"\n  Hechizos seleccionados:")
        if wb.spells:
            for i, spell_name in enumerate(wb.spells, 1):
                r  = get_relation(wb.wizard_type, SPELLS[spell_name]["school"])
                cn = casting_number(wb.wizard_type, spell_name)
                school = SPELLS[spell_name]["school"]
                print(f"    {i}. {spell_name:<22} CN:{cn:>2}  {rel_tag(r)}  [{school}]")
        else:
            info("(ninguno)")

        print(f"\n  1. Agregar hechizo")
        print(f"  2. Quitar hechizo")
        print(f"  3. Ver todos los hechizos disponibles")
        print(f"  4. Ver detalle de un hechizo seleccionado")
        print(f"  0. Volver")
        op = input("\n  > ").strip()

        if op == "1":
            _menu_add_spell(wb)

        elif op == "2":
            if not wb.spells:
                err("No hay hechizos para quitar.")
                press_enter()
                continue
            choice = input("  Número del hechizo a quitar: ").strip()
            try:
                idx = int(choice) - 1
                success, msg = wb.remove_spell(idx)
                ok(msg) if success else err(msg)
            except ValueError:
                err("Ingresá un número válido.")
            press_enter()

        elif op == "3":
            _print_spell_list(wb.wizard_type)
            press_enter()

        elif op == "4":
            if not wb.spells:
                err("No hay hechizos seleccionados todavía.")
                press_enter()
                continue
            print("\n  Hechizos seleccionados:")
            for i, sn in enumerate(wb.spells, 1):
                print(f"    {i}. {sn}")
            choice = input("\n  Número a ver en detalle: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(wb.spells):
                    print_spell_detail(wb.spells[idx], wb.wizard_type)
                else:
                    err("Número fuera de rango.")
            except ValueError:
                err("Ingresá un número válido.")
            press_enter()

        elif op == "0":
            break


def print_spell_detail(spell_name: str, wizard_type: str = ""):
    """Muestra el detalle completo de un hechizo."""
    if spell_name not in SPELLS:
        err(f"Hechizo desconocido: '{spell_name}'")
        return
    data = SPELLS[spell_name]
    desc = SPELL_DESCRIPTIONS.get(spell_name, "(descripción no disponible)")

    print(f"\n  {'─'*56}")
    print(f"  {spell_name.upper()}")
    print(f"  {'─'*56}")
    print(f"  Escuela   : {data['school']}")
    print(f"  Base CN   : {data['base']}")
    if wizard_type:
        rel = get_relation(wizard_type, data["school"])
        cn  = casting_number(wizard_type, spell_name)
        pen = SCHOOL_PENALTY[rel]
        pen_str = f"+{pen} ({rel})" if pen > 0 else "0 (propia)"
        print(f"  CN efectivo: {cn}  (base {data['base']} + penalidad {pen_str})")
    print(f"  Categoría : {data['category']}")
    print(f"\n  Descripción:")
    # Wrap a ~56 chars
    words = desc.split()
    line, col = "  ", 2
    for word in words:
        if col + len(word) + 1 > 60:
            print(line)
            line, col = "  ", 2
        line += word + " "
        col += len(word) + 1
    if line.strip():
        print(line)
    print(f"  {'─'*56}")


def _menu_add_spell(wb: Warband):
    """Sub-menú para agregar hechizos, filtrando por relación."""
    header("Agregar Hechizo")
    print(f"\n  Filtrar por:")
    print(f"  1. Propios     ({wb.wizard_type})")
    print(f"  2. Alineados   ({', '.join(SCHOOL_RELATIONS[wb.wizard_type]['aligned'])})")
    print(f"  3. Neutrales")
    print(f"  4. Todos (excluye opuestos)")
    print(f"  0. Cancelar")
    fop = input("\n  > ").strip()

    if fop == "0":
        return

    filter_relations = {
        "1": ["own"],
        "2": ["aligned"],
        "3": ["neutral"],
        "4": ["own", "aligned", "neutral"],
    }.get(fop)

    if not filter_relations:
        err("Opción inválida.")
        press_enter()
        return

    # Construir lista filtrada y ordenada por escuela
    available = []
    for spell_name, spell_data in sorted(SPELLS.items(), key=lambda x: (x[1]["school"], x[0])):
        rel = get_relation(wb.wizard_type, spell_data["school"])
        if rel in filter_relations and spell_name not in wb.spells:
            available.append(spell_name)

    if not available:
        info("No hay hechizos disponibles con ese filtro.")
        press_enter()
        return

    # Mostrar lista paginada de a 20
    PAGE = 20
    page = 0
    while True:
        start = page * PAGE
        end   = min(start + PAGE, len(available))
        print(f"\n  Hechizos disponibles ({start+1}–{end} de {len(available)}):")
        print(f"  {'N°':>3}  {'Nombre':<22} {'CN':>4}  {'Relación':<12}  {'Escuela'}")
        print("  " + "─"*60)
        for i, spell_name in enumerate(available[start:end], start + 1):
            rel    = get_relation(wb.wizard_type, SPELLS[spell_name]["school"])
            cn     = casting_number(wb.wizard_type, spell_name)
            school = SPELLS[spell_name]["school"]
            print(f"  {i:>3}. {spell_name:<22} {cn:>4}  {rel_tag(rel):<12}  {school}")

        nav = ""
        if len(available) > PAGE:
            nav = "  [s=siguiente / a=anterior] "
        choice = input(f"\n  Número para agregar, 'd<N>' para ver detalle {nav}(Enter para cancelar): ").strip()

        if choice == "":
            break
        if choice.lower() == "s":
            if end < len(available):
                page += 1
            continue
        if choice.lower() == "a":
            if page > 0:
                page -= 1
            continue
        # Prefijo "d" = ver detalle sin agregar
        show_only = choice.lower().startswith("d")
        clean = choice.lower().lstrip("d").strip()

        try:
            idx = int(clean) - 1
            if 0 <= idx < len(available):
                if show_only:
                    print_spell_detail(available[idx], wb.wizard_type)
                    press_enter()
                else:
                    success, msg = wb.add_spell(available[idx])
                    ok(msg) if success else err(msg)
                    press_enter()
                    break
            else:
                err("Número fuera de rango.")
                press_enter()
        except ValueError:
            err("Ingresá un número válido.")
            press_enter()


def _print_spell_list(wizard_type: str):
    """Muestra todos los hechizos disponibles (no opuestos) para un tipo de wizard."""
    header(f"Hechizos disponibles para {wizard_type}")
    last_school = ""
    for spell_name, spell_data in sorted(SPELLS.items(), key=lambda x: (x[1]["school"], x[0])):
        rel = get_relation(wizard_type, spell_data["school"])
        if rel == "opposed":
            continue
        if spell_data["school"] != last_school:
            print(f"\n  ── {spell_data['school'].upper()} ──  {rel_tag(rel)}")
            last_school = spell_data["school"]
        cn = casting_number(wizard_type, spell_name)
        print(f"    {spell_name:<22} CN:{cn:>2}  {spell_data['category']}")
    print()


# ─────────────────────────────────────────────
#  MENÚS EXISTENTES
# ─────────────────────────────────────────────

def menu_wizard(wb: Warband):
    while True:
        header("Configurar Wizard")
        print(f"\n  Nombre actual : {wb.wizard_name or '(sin nombre)'}")
        print(f"  Tipo actual   : {wb.wizard_type or '(sin tipo)'}")
        print(f"\n  1. Cambiar nombre")
        print(f"  2. Cambiar tipo de wizard")
        print(f"  0. Volver")
        op = input("\n  > ").strip()

        if op == "1":
            name = input("  Nombre del wizard: ").strip()
            if name:
                wb.wizard_name = name
                ok(f"Nombre guardado: {name}")
            else:
                err("Nombre vacío, no se guardó.")
            press_enter()

        elif op == "2":
            print("\n  Tipos de wizard:")
            for i, wt in enumerate(WIZARD_TYPES, 1):
                rel_info = SCHOOL_RELATIONS[wt]
                print(f"    {i:2}. {wt:<14}  Alineado: {', '.join(rel_info['aligned']):<35}  Opuesto: {rel_info['opposed'][0]}")
            choice = input("\n  Elegí un número: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(WIZARD_TYPES):
                    nuevo_tipo = WIZARD_TYPES[idx]
                    if nuevo_tipo != wb.wizard_type and wb.spells:
                        confirm = input(f"  Cambiar el tipo borrará los hechizos seleccionados. ¿Continuar? (s/n): ").strip().lower()
                        if confirm != "s":
                            info("Cambio cancelado.")
                            press_enter()
                            continue
                    wb.wizard_type = nuevo_tipo
                    wb.spells = []
                    ok(f"Tipo guardado: {wb.wizard_type}")
                else:
                    err("Número fuera de rango.")
            except ValueError:
                err("Ingresá un número válido.")
            press_enter()

        elif op == "0":
            break


def menu_soldiers(wb: Warband):
    while True:
        header("Gestionar Soldados")
        print(f"\n  Soldados: {len(wb.soldiers)}/{MAX_SOLDIERS}  |  Especialistas: {wb.specialist_count}/{MAX_SPECIALISTS}")
        print(f"  Oro restante: {wb.gold_remaining} gc\n")
        print("  1. Agregar soldado")
        print("  2. Quitar soldado")
        print("  3. Ver tablas de soldados")
        print("  0. Volver")
        op = input("\n  > ").strip()

        if op == "1":
            all_types = list(ALL_SOLDIERS.keys())
            print("\n  Soldados disponibles:")
            for i, (name, data) in enumerate(ALL_SOLDIERS.items(), 1):
                tag  = "[ESP]" if data["Specialist"] else "[STD]"
                cost = f"{data['Cost']} gc" if data["Cost"] > 0 else "Gratis"
                print(f"    {i:2}. {tag} {name:<18} {cost}")
            choice = input("\n  Elegí un número: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(all_types):
                    stype = all_types[idx]
                    sname = input(f"  Nombre para el {stype} (Enter para omitir): ").strip()
                    success, msg = wb.add_soldier(stype, sname)
                    ok(msg) if success else err(msg)
                else:
                    err("Número fuera de rango.")
            except ValueError:
                err("Ingresá un número válido.")
            press_enter()

        elif op == "2":
            if not wb.soldiers:
                err("No hay soldados para quitar.")
                press_enter()
                continue
            print("\n  Soldados actuales:")
            for i, s in enumerate(wb.soldiers, 1):
                name_str = f" «{s['name']}»" if s["name"] else ""
                print(f"    {i}. {s['type']}{name_str}")
            choice = input("\n  Número a quitar: ").strip()
            try:
                idx = int(choice) - 1
                success, msg = wb.remove_soldier(idx)
                ok(msg) if success else err(msg)
            except ValueError:
                err("Ingresá un número válido.")
            press_enter()

        elif op == "3":
            print_soldier_tables()
            press_enter()

        elif op == "0":
            break


def menu_save_load(wb: Warband):
    header("Guardar / Cargar")
    print("\n  1. Guardar lista")
    print("  2. Cargar lista")
    print("  3. Exportar como texto (.txt)")
    print("  0. Volver")
    op = input("\n  > ").strip()

    if op == "1":
        fname = input("  Nombre del archivo (sin extensión): ").strip()
        if not fname:
            err("Nombre vacío.")
            press_enter()
            return wb
        path = os.path.join(SCRIPT_DIR, f"{fname}.json")
        wb.save(path)
        ok(f"Lista guardada en '{path}'.")
        press_enter()

    elif op == "2":
        fname = input("  Nombre del archivo (sin extensión): ").strip()
        if not fname:
            err("Nombre vacío.")
            press_enter()
            return wb
        path = os.path.join(SCRIPT_DIR, f"{fname}.json")
        try:
            wb = Warband.load(path)
            ok(f"Lista cargada desde '{path}'.")
        except FileNotFoundError:
            err(f"Archivo '{path}' no encontrado.")
        except Exception as e:
            err(f"Error al cargar: {e}")
        press_enter()

    elif op == "3":
        fname = input("  Nombre del archivo (sin extensión): ").strip()
        if not fname:
            err("Nombre vacío.")
            press_enter()
            return wb
        path = os.path.join(SCRIPT_DIR, f"{fname}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(export_list(wb))
        ok(f"Lista exportada en '{path}'.")
        press_enter()

    return wb


# ─────────────────────────────────────────────
#  MENÚ PRINCIPAL
# ─────────────────────────────────────────────

def main():
    wb = Warband()

    while True:
        clear()
        print_warband_summary(wb)
        print(f"\n  MENÚ PRINCIPAL")
        print(f"  1. Configurar wizard")
        print(f"  2. {'Despedir aprendiz (100 gc)' if wb.has_apprentice else 'Contratar aprendiz (100 gc)'}")
        print(f"  3. Gestionar hechizos  ({len(wb.spells)}/8)")
        print(f"  4. Gestionar soldados")
        print(f"  5. Ver stats base (wizard / aprendiz)")
        print(f"  6. Guardar / Cargar / Exportar")
        print(f"  7. Nueva warband (reiniciar)")
        print(f"  0. Salir")

        op = input("\n  > ").strip()

        if op == "1":
            menu_wizard(wb)

        elif op == "2":
            if wb.has_apprentice:
                success, msg = wb.fire_apprentice()
            else:
                success, msg = wb.hire_apprentice()
            ok(msg) if success else err(msg)
            press_enter()

        elif op == "3":
            menu_spells(wb)

        elif op == "4":
            menu_soldiers(wb)

        elif op == "5":
            header("Stats Base")
            print("\n  WIZARD (todos los tipos arrancan igual)")
            d = WIZARD_BASE_STATS
            print(f"  M:{d['Move']}  F:{d['Fight']}  S:{d['Shoot']}  A:{d['Armour']}  W:{d['Will']}  H:{d['Health']}")
            print("\n  APRENDIZ (wizard -2 en F, W y H)")
            d = APPRENTICE_BASE_STATS
            print(f"  M:{d['Move']}  F:{d['Fight']}  S:{d['Shoot']}  A:{d['Armour']}  W:{d['Will']}  H:{d['Health']}")
            print()
            press_enter()

        elif op == "6":
            wb = menu_save_load(wb)

        elif op == "7":
            confirm = input("\n  ¿Seguro que querés reiniciar? (s/n): ").strip().lower()
            if confirm == "s":
                wb = Warband()
                ok("Warband reiniciada.")
                press_enter()

        elif op == "0":
            print("\n  ¡Hasta la próxima expedición a la Ciudad Helada!\n")
            break


if __name__ == "__main__":
    main()
