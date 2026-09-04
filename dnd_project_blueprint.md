# Master Blueprint: Standalone D&D Voice Application

## 📁 System Architecture & Directory Mapping
- **Root Directory:** `dnd_voice_app_mobile`
- **Database Asset:** `dnd_campaign.db` (Mapped dynamically via local `BASE_DIR` paths to isolate environment builds).
  - *Schema Key Columns (`npcs`):* `npc_id`, `name`, `voice_id`, `personality_prompt`, `faction`, `motivation`, `secrets`.
  - *Schema Key Columns (`dialogue`):* `dialogue_id`, `session_id`, `npc_id`, `speaker_type`, `text_content`.
- **Offline TTS Engine:** `kokoro_onnx` (Using 330MB neural weight matrix `assets/kokoro-v0_19.onnx` and custom 3MB archetype layout `assets/voices/voices-v1.Bin`).
- **Media System Execution:** `pygame-ce` (Using dual-track alternating files `output_1.wav` and `output_2.wav` running explicit `.unload()` sequences to shatter Windows filesystem retention locks).
- **Text Reasoning Engine:** Local Ollama server interface routing back to a compressed 2k context configuration profile running a quad-threaded execution loop targeting `phi3:mini`.

## 🎛️ Voice Droplist Mapping Code Reference Table

| Dropdown Value | Label Description | Intended Roleplay Match |
| :--- | :--- | :--- |
| am_adam | Dwarf/Goblin (Deep Gravelly Male) | Gruff merchants, hardened blacksmiths |
| am_michael | Elf/Scholar (Ancient Wise Male) | High wizards, royal lore-keepers |
| am_echo | Orc/Barbarian (Booming Chest Male) | Clan chieftains, aggressive tavern keepers |
| pm_alex | Rogue/Smuggler (Low Raspy Male) | Street informants, black market contacts |
| bm_george | Noble/King (Haughty British Male) | Wealthy aristocrats, merchant kings |
| af_nicole | Goblin/Hag (Sharp Raspy Female) | Cackling swamp hags, fierce goblins |
| af_bella | Elf/Druid (Ethereal Melodic Female)| Grove keepers, high elven priestesses |
| af_sky | Orc/Commander (Stern Commanding Female)| Garrison captains, battle-scarred warriors |
| af_sarah | Rogue/Assassin (Deceptive Whisper Female)| Shadow agents, seductive court spies |
| bf_emma | Noble/Queen (Crisp Precise Female) | Elitist noblewomen, ruling queens |

## ⚙️ Core Stability Implementations
1. **Dynamic Database Ingestion:** Function parameters automatically execute database lookups on function initializations to match `npc_id` across UI scripts and the database backend, eliminating cross-module variable leaks.
2. **Crash-Proof Persona Seeding:** Leverages string hashing structures `hash(npc_name)` to force alphanumeric character titles cleanly into pure mathematical seeds without tripping value conversion blocks.
3. **Optimized Speech Processing Thresholds:** Audio speech capture pipelines include `recognizer.pause_threshold = 2.0` combined with short-burst ambient filtering blocks (`adjust_for_ambient_noise(duration=0.5)`) to ensure sentence capture runs smoothly even during narrative pauses.
