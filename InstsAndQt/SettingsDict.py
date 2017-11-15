import os
import time
import json
from PyQt5.QtCore import QTimer

class Settings(dict):
    """
    A subclass of dictionary which will automatically handle saving
    settings and loading settings
    """
    saveSettingsTimer = QTimer()
    def __init__(self, *args, **kwargs):
        self.skipKeys = []

        self.acceptableFileAge = 30 * 60 #30 min default
        self.filePath = None
        self.saveInterval = 10 * 60 * 1000 # 10 minute default
        self.saveSettingsTimer.timeout.connect(self.saveSettings)
        self.saveSettingsTimer.setInterval(self.saveInterval)
        self.saveSettingsTimer.start()
        super(Settings, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super(Settings, self).__setitem__(key, value)
        self.saveSettings()

    def setSavingInterval(self, interval=10*60*1000):
        self.saveInterval = interval
        self.saveSettingsTimer.setInterval(self.saveInterval)

    def saveSettings(self):
        if self.filePath is None: return
        try:
            saveDict = {k: v for k, v in self.items() if k not in self.skipKeys}
            with open(self.filePath, 'w') as fh:
                json.dump(saveDict, fh, separators=(',', ': '),
                          sort_keys=True, indent=4, default=lambda x: 'NotSerial')
        except AttributeError:
            pass

    def checkFile(self):
        """
        This will check to see wheteher there's a previous settings file,
        and if it's recent enough that it should be loaded
        :return:
        """
        if not os.path.isfile(self.filePath):
            # File doesn't exist
            return False
        if (time.time() - os.path.getmtime(self.filePath)) > self.acceptableFileAge:
            # It's been longer than 30 minutes and likely isn't worth
            # keeping open
            return False
        return True

    def loadSettings(self):
        if not self.checkFile(): return False

        with open(self.filePath, 'r') as fh:
            savedDict = json.load(fh)
        self.update(savedDict)
        return True