[center][img]https://raw.githubusercontent.com/nickan/cyberpunk-dreamvoice-text-fix-2.50/main/assets/banner.jpg[/img][/center]

[size=5][b]DreamVoice Phantom Liberty Russian Dub - Text Fix & Dogtown Sync (Patch 2.50+)[/b][/size]

[line]

[size=4][b]OVERVIEW[/b][/size]
When using the Russian voiceover mod for the Phantom Liberty DLC by DreamVoice on Cyberpunk 2077 Patch 2.50+, in-game text breaks. Menu items disappear, graphics settings (DLSS, FSR, Frame Generation) show blank spaces, and technical errors like UI-Script-Localization-String-NotFound appear in perk trees and quest logs.

This happens because the voiceover archive contains outdated UI and subtitle files from earlier versions of the game, which override the official 2.50 files due to mod load priority.

This micro-patch completely resolves both issues while keeping 100% of the Russian voiceover intact!

[line]

[size=4][b]KEY FEATURES[/b][/size]
- Full Patch 2.50 Text Restoration: Restores all updated UI elements, graphics settings, new perk descriptions, shards, and quest objectives.
- Dogtown Terminology Sync: In the official Russian localization, Dogtown was translated literally as "Hound Town", whereas the DreamVoice voice actors pronounce it as "Dogtown". This patch replaces all 1,100+ occurrences across all grammatical cases in text and subtitles so they perfectly match the spoken dialogue.
- 100% Voice Acting Preserved: All 27,500+ audio dialogue lines, facial lipsync animations, and sound maps from the DreamVoice mod remain fully functional.

[line]

[size=4][b]HOW IT WORKS[/b][/size]
The patch archive is named ###_DreamVoice_Fix_Text_2.50.archive (~5.9 MB).
Thanks to the ###_ prefix, REDengine 4 loads this archive alphabetically before the DreamVoice mod:
1. The game loads the up-to-date and synchronized 2.50 localization text.
2. The game then loads the DreamVoice archive: it skips the outdated text files but loads all the voice audio lines and animations.

[line]

[size=4][b]INSTALLATION[/b][/size]
1. Download DreamVoice_PhantomLiberty_TextFix_2.50.zip.
2. Extract the archive into your Cyberpunk 2077 root directory:
Cyberpunk 2077\archive\pc\mod\###_DreamVoice_Fix_Text_2.50.archive
3. Launch the game.

[size=4][b]UNINSTALLATION[/b][/size]
Simply delete ###_DreamVoice_Fix_Text_2.50.archive from your Cyberpunk 2077\archive\pc\mod\ directory.

[line]

[size=4][b]REQUIREMENTS[/b][/size]
- Cyberpunk 2077 (Patch 2.50 or newer)
- Phantom Liberty DLC
- DreamVoice Russian Dub mod (Rus_Dub_by_DreamVoice_v5.3.1.archive)

[line]

[size=4][b]CREDITS[/b][/size]
- DreamVoice Studio — for the tremendous work creating the Russian voice dub for Phantom Liberty.
- CD PROJEKT RED — for Cyberpunk 2077.
- WolvenKit Team — for the modding tools.
