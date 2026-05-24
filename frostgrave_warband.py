#!/usr/bin/env python3
"""
Frostgrave 2ª Edición — Constructor de Warband
Basado en las reglas de Joseph A. McCullough (Osprey Games, 2020)
"""

import json
import os

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
            lines.append(f"  {spell_name:<22} CN:{cn:>2}  [{school}]  {cat}")

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

        elif op == "0":
            break


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
            nav = "  [s=siguiente página / a=anterior] "
        choice = input(f"\n  Número para agregar {nav}(Enter para cancelar): ").strip()

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

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available):
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
        wb.save(f"{fname}.json")
        ok(f"Lista guardada en '{fname}.json'.")
        press_enter()

    elif op == "2":
        fname = input("  Nombre del archivo (sin extensión): ").strip()
        if not fname:
            err("Nombre vacío.")
            press_enter()
            return wb
        path = f"{fname}.json"
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
        path = f"{fname}.txt"
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
