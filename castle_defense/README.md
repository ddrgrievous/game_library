# Castle Defense Game

A pygame-based tower defense game where you protect your castle from approaching enemies.

## Game Features
- Click enemies to damage them
- Buy upgrades between levels
- Place turrets on your castle for automatic defense
- Enemies get stronger as levels progress
- Strategic turret placement
- Health and fire rate upgrades

## Testing Parameters

When running the game, you can use the following command-line parameters for testing:

```bash
python castle_defense/castle.py [options]
```

### Available Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| --level | int | 1 | Set the starting level |
| --points | int | 0 | Set the starting points |
| --upgrade-store | flag | false | Start the game in the upgrade store |

### Example Uses

1. Start at level 3 with 30 points:
```bash
python castle_defense/castle.py --level 3 --points 30
```

2. Start in the upgrade store with 50 points:
```bash
python castle_defense/castle.py --points 50 --upgrade-store
```

3. Start at level 5 in the upgrade store with 100 points:
```bash
python castle_defense/castle.py --level 5 --points 100 --upgrade-store
```

## Game Mechanics

### Upgrades
- Health Upgrade: Costs 10 points
- Turret: Costs 10 points
  - Automatically targets nearest enemy
  - Bullets track enemies and deal 1 damage
  - Bullets can switch targets if original target dies

### Enemies

Regular Enemies:
- Health increases every 3 levels (max 5 health)
- Speed increases with level
- Red coloring, standard size
- Points awarded based on initial health when killed

Scout Enemies (Introduced at Level 3):
- Always have 1 health
- Move faster than regular enemies
- Light blue coloring, smaller size
- Appear more frequently at higher levels
- Can be killed by clicks or turret shots
- Spawn chance increases by 5% per level (max 40%)

Boss Enemies (Every 5th Level):
- Appear at 15 second mark
- Large purple enemies with golden crowns
- High health (10 + bonus health per 5 levels)
- Slower but steady movement
- Require coordinated turret and click attacks to defeat

### Testing Tips
1. Use `--upgrade-store` to test turret placement and upgrades
2. Higher levels spawn stronger and faster enemies
3. Start with extra points to test multiple upgrades quickly