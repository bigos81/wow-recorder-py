# What the hell is this?
An effort to create linux (and maybe even cross-platform) version of WoW Recorder - https://github.com/aza547/wow-recorder

In order to achieve that the OBS integration is done by web socket to make this implementation free of platform code.

# Capabilities
The application is 
- Connecting to OBS Studio via web-socket client to be able to toggle the recording on and off and manage the completed recording afterward
- Monitoring World of Warcraft log file to figure out whether a significant activity is happening, significant activities include:
  - Mythic Plus key run start
  - Mythic Raid boss encounter start
- Monitoring World of Warcraft log file to gather significant events during the recording, significant events include:
  - Player death (both M+ and Raid)
  - Boss kill (M+ only)
  - Boss wipe (M+ only)
- Monitoring World of Warcraft log file to trigger end of a recording
- Handling the recorded OBS Studio video file by:
  - Moving it from OBS output folder to desired configured recorder output folder
  - Renaming the OBS output file to reflect the activity recorder
  - Storing `.evt` file containing timestamps of significant events during the recording, the time is expressed in time of the video file

# Quick start
1. Download the latest release from here: https://github.com/bigos81/wow-recorder-py/releases and unpack the contents, if you are willing to test latest version, use the latest GitHub Action artifacts, found here: https://github.com/bigos81/wow-recorder-py/actions

    Release archive should contain:
    - `wow-recorder-XXX-latest` binary, where XXX stands for platform the binary is created for
    - `wow_recorder_py.cfg` configuration file
    - `wow-recorder.desktop` linux only .desktop file to ensure running in terminal
2. Set up OBS web socket integration

   Enable WebSocket Server Settings here:
   
   ![image](https://github.com/user-attachments/assets/0468eced-5efc-4f46-a6fb-8212be5ca03c)

   Check the "Enable WebSocket server" check box, fill in Server Port edit box, check Enable Authentication check box, set up the Server Password
   
   ![image](https://github.com/user-attachments/assets/41f144d4-9151-4d58-bef5-beffca2aba69)

3. Set up OBS scene

   Make sure you OBS Studio is configured to capture the scene of the game when turned on. The recorder will only ask the OBS to start and end recording without setting the scene, overlays, audio options etc. This means it's up to you to configure the scene, audio and output video settings properly. It should look something like this:

   ![image](https://github.com/user-attachments/assets/95381855-5892-435f-889a-c203c421e891)

   Where the World of Warcraft window is selected as a scene, some overlay hiding the chat box (optional of course) and audio settings are set.

4. Set up the configuration in `wow_recorder_py.cfg`
   
    [OBS] section
   - `host` probably localhost in the way you want to go with, 127.0.0.1 should also work for OBS running at the same host as the recorder and WoW client
   - `port` port of communication with the OBS web socket. default is 4455
   - `password` password for the web socket client, the same you've provided in OBS settings in the previous step

    [WOW] section
    - `log_folder` folder where WOW is logging

    [RECORDER] section
    - `output_path` folder where the recorder will store resulting videos, keep in mind the recorder will attempt to create this folder and will create date subfolders there as well
    - `death_delay` amount of seconds to subtract from death event in the video, such that the timestamp is X seconds before the logged death event
    - `linger_time` amount of seconds to wait until finishing the recording after the activity ended
    - `reset_time` amount of seconds considered a length of activity to be considered as reset for a boss
5. Configure World of Warcraft

   It's important that your World of Warcraft will be running combat log logging, for the recorder to read. You can toggle logging manually by issuing a console command `/combatlog` or use any of existing addons to log your keys and raids for you. I'd recommend raider.io wow addon to do it for you (https://raider.io/addon). Any other addon will do, just make sure you are logging, otherwise the recorder will not have a clue where to start and end recording of your activities.
6. Run the recorder software - make sure you see it's console output, it will show you the status of recording etc. If you are fine, this is how the terminal should look like when running the software:

    ![image](https://github.com/user-attachments/assets/4457e894-2cf8-4c20-8232-bbe7944525c8)


# Expansion points
This is just a simple application for now, the additional features that can be added depend on whether I or anyone else would be interested in them. Handling more events, difficulties, raid types or arenas/battlegrounds are all on the table, provided anyone would use them :)
If you are interested in those - let me know via GitHub, it's always way more encouraging to work on something someone would actually use.

# Want to be nice?
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/bigos81)
