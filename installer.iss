[Setup]
AppName=ModernArchiver
AppVersion=1.0
DefaultDirName={pf}\ModernArchiver
DefaultGroupName=ModernArchiver
UninstallDisplayIcon={app}\ModernArchiver.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=ModernArchiver_Setup
PrivilegesRequired=admin

[Files]
Source: "dist\ModernArchiver.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion

[Icons]
Name: "{group}\ModernArchiver"; Filename: "{app}\ModernArchiver.exe"
Name: "{commondesktop}\ModernArchiver"; Filename: "{app}\ModernArchiver.exe"

[Registry]
; Ассоциации файлов
Root: HKCR; Subkey: ".zip"; ValueType: string; ValueName: ""; ValueData: "ModernArchiver.ZIP"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".rar"; ValueType: string; ValueName: ""; ValueData: "ModernArchiver.RAR"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".7z"; ValueType: string; ValueName: ""; ValueData: "ModernArchiver.7Z"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".tar"; ValueType: string; ValueName: ""; ValueData: "ModernArchiver.TAR"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".gz"; ValueType: string; ValueName: ""; ValueData: "ModernArchiver.GZ"; Flags: uninsdeletevalue
Root: HKCR; Subkey: ".bz2"; ValueType: string; ValueName: ""; ValueData: "ModernArchiver.BZ2"; Flags: uninsdeletevalue

; Описания типов файлов
Root: HKCR; Subkey: "ModernArchiver"; ValueType: string; ValueName: ""; ValueData: "Файл ModernArchiver"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Архив ModernArchiver"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.ZIP"; ValueType: string; ValueName: ""; ValueData: "ZIP Archive"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.RAR"; ValueType: string; ValueName: ""; ValueData: "RAR Archive"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.7Z"; ValueType: string; ValueName: ""; ValueData: "7-Zip Archive"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.TAR"; ValueType: string; ValueName: ""; ValueData: "TAR Archive"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.GZ"; ValueType: string; ValueName: ""; ValueData: "GZ Archive"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.BZ2"; ValueType: string; ValueName: ""; ValueData: "BZ2 Archive"; Flags: uninsdeletekey

; Команды открытия
Root: HKCR; Subkey: "ModernArchiver\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.ZIP\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.RAR\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.7Z\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.TAR\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.GZ\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.BZ2\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" ""%1"""; Flags: uninsdeletekey

; Иконки
Root: HKCR; Subkey: "ModernArchiver\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,0"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.ZIP\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,0"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.RAR\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,1"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.7Z\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,2"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.TAR\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,0"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.GZ\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,0"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.BZ2\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\ModernArchiver.exe,0"; Flags: uninsdeletekey

; Контекстное меню для архивов - Extract here
Root: HKCR; Subkey: "ModernArchiver.ZIP\shell\extracthere"; ValueType: string; ValueName: ""; ValueData: "Extract here"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.ZIP\shell\extracthere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.RAR\shell\extracthere"; ValueType: string; ValueName: ""; ValueData: "Extract here"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.RAR\shell\extracthere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.7Z\shell\extracthere"; ValueType: string; ValueName: ""; ValueData: "Extract here"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.7Z\shell\extracthere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.TAR\shell\extracthere"; ValueType: string; ValueName: ""; ValueData: "Extract here"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.TAR\shell\extracthere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.GZ\shell\extracthere"; ValueType: string; ValueName: ""; ValueData: "Extract here"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.GZ\shell\extracthere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.BZ2\shell\extracthere"; ValueType: string; ValueName: ""; ValueData: "Extract here"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ModernArchiver.BZ2\shell\extracthere\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --extract-here ""%1"""; Flags: uninsdeletekey

; Контекстное меню для файлов и папок - Compress
Root: HKCR; Subkey: "Directory\Background\shell\ModernArchiverCompress"; ValueType: string; ValueName: ""; ValueData: "Compress with ModernArchiver"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\Background\shell\ModernArchiverCompress\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --compress %V"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\ModernArchiverCompress"; ValueType: string; ValueName: ""; ValueData: "Compress with ModernArchiver"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\ModernArchiverCompress\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --compress ""%1"""; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\ModernArchiverCompress"; ValueType: string; ValueName: ""; ValueData: "Compress with ModernArchiver"; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\shell\ModernArchiverCompress\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ModernArchiver.exe"" --compress ""%1"""; Flags: uninsdeletekey

[Run]
Filename: "{app}\ModernArchiver.exe"; Description: "Запустить ModernArchiver"; Flags: postinstall nowait skipifsilent

[UninstallRun]
; Удаление ассоциаций при деинсталляции
Filename: "{cmd}"; Parameters: "/C ""reg delete HKCR\.zip /f 2>nul"""; Flags: runhidden
Filename: "{cmd}"; Parameters: "/C ""reg delete HKCR\.rar /f 2>nul"""; Flags: runhidden