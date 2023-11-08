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
- Ether disconnect when using the command `stop`
- Some big technical changes
    - Ether is now running lavalink by itself beside the bot
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
- Technical changes (Ether is now using a patch for mafic)

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