userInfo = [
    ("https://someinstance1.service-now.com/", "", ""),
    ("https://someinstance2.service-now.com/", "", ""),
]

loggerLevel = "debug"

successCommand = """
terminal-notifier -message "%(filename)s" -title "File updated" -group codesync
"""

cannotUploadCommand = """
terminal-notifier -message "%(person)s updated it at %(remoteDate)s, your version is %(localDate)s" -title "Cannot upload file"  -group codesync
"""

warningCommand = """
terminal-notifier -message "%(msg)s" -title "%(title)s"  -group codesync
"""

ignoreDirs = ".git, .settings, .sass-cache"
