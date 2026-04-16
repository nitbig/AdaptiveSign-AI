#!/usr/bin/env python3
"""Fix memory file by swapping flipped hand labels (Left ↔ Right)"""
import json

memory_file = "hindsight_memory.json"

# Load memory
with open(memory_file, 'r') as f:
    memory = json.load(f)

# Swap all Left/Right labels
fixed_memory = {}
for key, value in memory.items():
    # Swap Left/Right in the key
    if key.startswith("Left:"):
        new_key = "Right:" + key[5:]
    elif key.startswith("Right:"):
        new_key = "Left:" + key[6:]
    else:
        new_key = key
    
    fixed_memory[new_key] = value

# Save corrected memory
with open(memory_file, 'w') as f:
    json.dump(fixed_memory, f, indent=2)

print(f"✅ Fixed memory file!")
print(f"Swapped {len(memory)} gesture entries")
print(f"\nExamples of fixes:")
for old_key in list(memory.keys())[:3]:
    if old_key.startswith("Left:"):
        new_key = "Right:" + old_key[5:]
    elif old_key.startswith("Right:"):
        new_key = "Left:" + old_key[6:]
    else:
        new_key = old_key
    print(f"  {old_key} → {new_key}")
