## 1.0.0rc2
- Music player update ratelimit hotfix

## 1.0.0rc1
- Fix something in on_member_join
- Bump wavelink to 3.1.0
- New `on_wavelink_extra_event` event supported

## 1.0.0b1 to 1.0.0b10
- Rename the `Image` cog to `Remix`
- Music cogs is now functional (in theory)
- Add a new `auto_play` parameter to the `music play` command that is set to `true` by default
- New `music loop_all`, `music history` and `music back` commands
- Command usage statistic
- Remove `ether/core/reddit.py` file
- New `utils uptime` command and `Utils.monitor_card_builder` task
- Some little changes on the `utils` cog
- Remove some useless/boring or empty commands
- Fix the `help` command
- Support root command in cogs
- New `TERM_OF_SERVICE.md` file
- New `PRIVACY_POLICY.md` file
- Command `play` work
- Rename the bot from Ether to Æther (possible step backwards)

- A lot of technical changes
    - Æther is now using discord.py (instead of py-cord)
    - Æther is now using wevelink (instead of mafic)
    - The above changes result in a rewriting of the bot
    - Rewrite parts like the base client and some events
    - Update the logging system
    - Update pre-commit
    - Ctrl+C close the bot "properly"
    - A lot of other changes
    - Update requirements.txt
    - Logging color changes
    - Fix command prefix error
    - Lavalink session id recovery system
    - Fix command not found error
    - Move filters to there own file
    - Fix playlist system
    - Bump wavelink to version 3.0.0
    - HotFix
    - Other minor changes
 and some events
- Rename the `Image` cog to `Remix`

## 0.20.3
- HotFix

## 0.20.2
- Remove the node host information in the player
- Technical changes
    - Prevent new nodes to have an already taken name
    - When a new node is ready it no longer log that all other nodes are ready

## 0.20.1
- Technical changes: Added a new loop to prevent lavalink from sleeping and find unavailable nodes

## 0.20.0
- Add filters for the music
- Add a new command `status`

## 0.19.3
- Technical changes
    - Remove the thread that run Lavalink
    - Update the Procfile
- Some HotFixes

## 0.19.2
- Hot Fix
    - Better handling of track finished for bad reasons
    - Fix the `pause` command

## 0.19.1
- Fix logging in `on_ready`
- Log an error if some lavalink files are not found
- Fix lavalink_request

## 0.19.0
- Æther disconnect when using the command `stop`
- Some big technical changes
    - Æther is now running lavalink by itself beside the bot
    - New logging in `on_ready`

## 0.18.0
- New `search_type` option for the command `play`
- Technical changes
    - Enhance the voice update function
    - Fix, prevent or log things in the node music system
    - Update urllib3 version to 2.0.7

## 0.17.0
- New Changelog
- Add the node label to the player and some error messages
- New `changelog` command

## 0.16.2
- Technical changes (Æther is now using a patch for mafic)

## 0.16.1
- Update support messages
- Technical changes (voice update fix and more)

## 0.16.0
- Fix and update DnD commands
    - Fix and update the `class infos` command
    - Add a new `class levels` command
    - Fix and update the `class spells` command
    - Fix and rename the `spells` command (previously `spell`)
    - Add a new `test` command for the owner
- Technical changes (voice update)
